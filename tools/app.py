"""app: the humanize kit in your browser. Check text, compare models and copy prompts with buttons.

Start it by double-clicking "Start Humanize" (Windows .bat, Mac .command) in the kit folder, or run:
    python tools/app.py                 # opens your browser
    python tools/app.py --port 9000 --no-browser

Runs on this computer only (127.0.0.1). API keys you type stay in your browser unless you tick "remember",
and even then they are saved only in this browser on this computer. Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import re
import secrets
import subprocess
import sys
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare_models as cm  # noqa: E402
import slop_check  # noqa: E402

KIT = HERE.parent
TOKEN = secrets.token_hex(16)
JOBS = {}

# Provider presets for the form. Model names change often; the form lets the user type any model.
PRESETS = [
    {"id": "openai", "label": "OpenAI", "base_url": "https://api.openai.com/v1", "model": "gpt-4.1",
     "key": True},
    {"id": "gemini", "label": "Google Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
     "model": "gemini-2.5-flash", "key": True},
    {"id": "claude", "label": "Anthropic Claude", "base_url": "https://api.anthropic.com/v1",
     "model": "claude-sonnet-5-5", "key": True, "extra": {"max_tokens": 2000}},
    {"id": "deepseek", "label": "DeepSeek", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat",
     "key": True},
    {"id": "openrouter", "label": "OpenRouter (many models, one key)", "base_url": "https://openrouter.ai/api/v1",
     "model": "meta-llama/llama-3.3-70b-instruct", "key": True},
    {"id": "ollama", "label": "Ollama (on this computer)", "base_url": "http://localhost:11434/v1",
     "model": "llama3.1:8b", "key": False, "extra": {"timeout": 600}},
    {"id": "lmstudio", "label": "LM Studio (on this computer)", "base_url": "http://localhost:1234/v1",
     "model": "", "key": False, "extra": {"timeout": 600}},
    {"id": "custom", "label": "Other (OpenAI-compatible)", "base_url": "", "model": "", "key": True},
]


def guide_prompts():
    """Pull every copyable prompt out of docs/*.md: the code blocks under '## Prompts to copy'."""
    out = []
    order = ["emails", "documents", "presentations", "video-scripts", "README"]
    for stem in order:
        p = KIT / "docs" / f"{stem}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        title = re.search(r"(?m)^# (.+)$", text).group(1)
        prompts, section, heading = [], "", ""
        for block in re.split(r"(?m)^(```[^\n]*\n.*?^```)\s*$", text, flags=re.S):
            if block.startswith("```"):
                body = block.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if section.lower().startswith(("prompts to copy", "plain-language")):
                    prompts.append({"title": heading or section, "text": body})
                continue
            for line in block.splitlines():
                if line.startswith("## "):
                    section, heading = line[3:].strip(), ""
                elif line.startswith("### "):
                    heading = line[4:].strip()
        if prompts:
            out.append({"guide": "Any format" if stem == "README" else title, "file": f"docs/{stem}.md",
                        "prompts": prompts})
    return out


def info():
    prompts = []
    for key, fname in cm.PROMPTS.items():
        t = (KIT / "prompts" / fname).read_text(encoding="utf-8")
        prompts.append({"id": key, "file": f"prompts/{fname}", "chars": len(t), "text": t})
    samples = [{"name": n, "text": t} for n, t in cm.load_samples(KIT / "samples")]
    return {"token": TOKEN, "presets": PRESETS, "prompts": prompts, "samples": samples, "guides": guide_prompts()}


def to_model(m):
    """Form model -> the dict compare_models.chat() expects (key passed directly, never via env)."""
    out = {"name": m["name"].strip() or m["model"], "base_url": m["base_url"].strip(), "model": m["model"].strip(),
           "api_key": m.get("api_key", "").strip()}
    preset = next((p for p in PRESETS if p["id"] == m.get("preset")), {})
    out.update(preset.get("extra", {}))
    if m.get("role") == "judge":
        out["temperature"] = 0
    return out


def run_job(job, models, judge_m, system, prompt_name, samples):
    out = KIT / "results" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    job["folder"] = str(out)
    tpl = (KIT / "prompts" / "judge_prompt.md").read_text(encoding="utf-8")
    for s in samples:
        before = slop_check.check(s["text"])
        for m in models:
            if job["cancel"]:
                break
            job["status"] = f"{m['name']} is rewriting {s['name']}"
            row = {"sample": s["name"], "model": m["name"], "original": s["text"], "before": before}
            try:
                rewrite, secs = cm.chat(m, system, f"Rewrite this:\n\n{s['text']}")
                row.update(rewrite=rewrite, seconds=secs, slop=slop_check.check(rewrite))
                if judge_m:
                    job["status"] = f"Judging {m['name']} on {s['name']}"
                    row["judge"] = cm.judge(judge_m, tpl, s["text"], rewrite)
            except Exception as e:  # one bad model should not sink the run
                row["error"] = str(e)
            job["rows"].append(row)
            job["done"] += 1
    (out / "results.json").write_text(json.dumps(job["rows"], indent=2, ensure_ascii=False), encoding="utf-8")
    cm.write_report(out, prompt_name, models, judge_m["name"] if judge_m else None, job["rows"])
    job["status"] = "Stopped" if job["cancel"] else "Done"
    job["finished"] = True


def start_run(req):
    models = [to_model(m) for m in req["models"] if m.get("role") != "judge" and m.get("model")]
    judges = [to_model(m) for m in req["models"] if m.get("role") == "judge" and m.get("model")]
    if not models:
        raise ValueError("Add at least one model to compare.")
    for m in models + judges:
        if not m["base_url"]:
            raise ValueError(f"{m['name']} needs an address (base URL).")
    names = [m["name"] for m in models]
    if len(set(names)) != len(names):
        raise ValueError("Two models have the same name. Give each one its own name.")
    samples = [s for s in req["samples"] if s.get("text", "").strip()]
    if not samples:
        raise ValueError("Pick at least one draft.")
    pid = req.get("prompt", "full")
    system = (KIT / "prompts" / cm.PROMPTS[pid]).read_text(encoding="utf-8")
    job = {"id": uuid.uuid4().hex[:8], "done": 0, "total": len(models) * len(samples), "rows": [],
           "status": "Starting", "finished": False, "cancel": False, "folder": None,
           "models": names, "judge": judges[0]["name"] if judges else None}
    JOBS[job["id"]] = job
    threading.Thread(target=run_job, args=(job, models, judges[0] if judges else None, system,
                                           cm.PROMPTS[pid], samples), daemon=True).start()
    return job


def open_folder(path):
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 (local folder the app created)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send(200, (HERE / "app.html").read_bytes(), "text/html")
        elif self.path == "/api/info":
            self.send(200, info())
        elif self.path.startswith("/api/job/"):
            job = JOBS.get(self.path.rsplit("/", 1)[1])
            self.send(200, job) if job else self.send(404, {"error": "No such run."})
        else:
            self.send(404, {"error": "Not found"})

    def do_POST(self):
        # Only this page may call the API: it sends the per-launch token in a custom header.
        if self.headers.get("X-Token") != TOKEN:
            return self.send(403, {"error": "Reload the page and try again."})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/check":
                self.send(200, slop_check.check(req.get("text", "")))
            elif self.path == "/api/run":
                self.send(200, start_run(req))
            elif self.path == "/api/stop":
                JOBS[req["id"]]["cancel"] = True
                self.send(200, {"ok": True})
            elif self.path == "/api/open":
                folder = JOBS[req["id"]]["folder"]
                if not folder:
                    raise ValueError("The report folder isn't ready yet.")
                open_folder(folder)
                self.send(200, {"ok": True})
            else:
                self.send(404, {"error": "Not found"})
        except ValueError as e:
            self.send(400, {"error": str(e)})
        except Exception as e:
            self.send(500, {"error": f"Something went wrong: {e}"})


def main():
    ap = argparse.ArgumentParser(description="Humanize kit in your browser")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    except OSError:
        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)  # port busy: take any free one
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"Humanize kit is running at {url}\nLeave this window open while you use it. Close it to stop.")
    if not a.no_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
