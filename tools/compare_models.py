"""compare_models: run the same drafts through several LLMs with the humanize prompt, then score them.

Works with any OpenAI-compatible chat API: OpenAI, OpenRouter, Google Gemini, Anthropic, DeepSeek, Groq,
Mistral, Together, LM Studio, Ollama and most others. Standard library only, nothing to pip install.

Usage:
    python compare_models.py --models models.json
    python compare_models.py --models models.json --judge gpt-judge --samples ../samples --prompt full

What it writes (in --out, default ./results/<timestamp>/):
    report.md      side-by-side table + every rewrite, easy to read or share
    results.json   the same data, machine-readable
    <sample>/<model>.md   each raw rewrite

Scores:
    slop      tells per 100 words from slop_check.py (lower is better). Same yardstick for every model.
    judge     /80 from judge_prompt.md, if you pass --judge (pick a model that is NOT one of the contestants
              when you can; models go easy on their own writing).
"""
import argparse
import datetime as dt
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slop_check  # noqa: E402

KIT = HERE.parent
PROMPTS = {"full": "humanize_full.md", "core": "humanize_core.md", "tiny": "humanize_tiny.txt"}


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def chat(m, system, user, retries=2):
    """One chat completion against an OpenAI-compatible endpoint. Returns (text, seconds)."""
    url = m["base_url"].rstrip("/") + "/chat/completions"
    key = os.environ.get(m["api_key_env"], "") if m.get("api_key_env") else m.get("api_key", "")
    if m.get("api_key_env") and not key:
        raise RuntimeError(f"environment variable {m['api_key_env']} is not set")
    body = {"model": m["model"], "messages": [{"role": "system", "content": system},
                                              {"role": "user", "content": user}]}
    if "temperature" in m:
        body["temperature"] = m["temperature"]
    if "max_tokens" in m:
        body["max_tokens"] = m["max_tokens"]
    body.update(m.get("extra_body", {}))
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    headers.update(m.get("headers", {}))
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    ctx = ssl_context() if url.startswith("https") else None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=m.get("timeout", 180), context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))
            text = data["choices"][0]["message"].get("content") or ""
            return strip_thinking(text), round(time.time() - t0, 1)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < retries:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None


def strip_thinking(text):
    """Drop <think>...</think> blocks that reasoning models put before the answer."""
    return re.sub(r"(?s)<think>.*?</think>\s*", "", text).strip()


def judge(jm, template, original, rewrite):
    prompt = template.replace("<<<ORIGINAL>>>", original).replace("<<<REWRITE>>>", rewrite)
    raw, _ = chat(jm, "You are a strict, fair writing judge. Reply with JSON only.", prompt)
    hit = re.search(r"\{.*\}", raw, re.S)
    if not hit:
        return {"error": "judge did not return JSON", "raw": raw[:200]}
    try:
        j = json.loads(hit.group(0))
    except json.JSONDecodeError:
        return {"error": "judge returned broken JSON", "raw": raw[:200]}
    dims = ["directness", "rhythm", "trust", "authenticity", "density", "specificity", "restraint", "voice"]
    if all(isinstance(j.get(d), (int, float)) for d in dims):
        j["total"] = sum(j[d] for d in dims)
        floors = {"specificity": 6, "voice": 6}
        j["pass"] = (j["total"] >= 56 and all(j[d] >= floors.get(d, 5) for d in dims)
                     and not j.get("invented_facts") and j.get("meaning_kept") is not False)
    return j


def load_samples(folder):
    files = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in (".txt", ".md"))
    if not files:
        sys.exit(f"No .txt or .md samples found in {folder}")
    return [(p.stem, p.read_text(encoding="utf-8").strip()) for p in files]


def cell(v):
    return "-" if v is None else str(v)


def write_report(out, prompt_name, models, judge_name, rows):
    L = [f"# Humanize model comparison", "",
         f"- Run: {dt.datetime.now():%Y-%m-%d %H:%M}",
         f"- Prompt: `{prompt_name}`",
         f"- Models: {', '.join(m['name'] for m in models)}",
         f"- Judge: {judge_name or 'none (slop score only)'}", "",
         "**Slop** = AI tells per 100 words from slop_check (lower is better, under 1.5 is clean). "
         "**Judge** = /80, pass is 56+ with no dimension under its floor. "
         "**Invented** = facts in the rewrite that were not in the draft (should be 0).", ""]

    L += ["## Summary by model", "", "| Model | Avg slop | Avg judge /80 | Passes | Invented facts | Errors | Avg seconds |",
          "|---|---|---|---|---|---|---|"]
    for m in models:
        mine = [r for r in rows if r["model"] == m["name"]]
        ok = [r for r in mine if not r.get("error")]
        slop = [r["slop"]["tells_per_100_words"] for r in ok]
        js = [r["judge"]["total"] for r in ok if isinstance(r.get("judge", {}).get("total"), (int, float))]
        passes = sum(1 for r in ok if r.get("judge", {}).get("pass"))
        inv = sum(len(r.get("judge", {}).get("invented_facts") or []) for r in ok)
        secs = [r["seconds"] for r in ok]
        avg = lambda xs: round(sum(xs) / len(xs), 1) if xs else None
        L.append(f"| {m['name']} | {cell(avg(slop))} | {cell(avg(js))} | "
                 f"{passes if judge_name else '-'}/{len(ok) if judge_name else '-'} | "
                 f"{inv if judge_name else '-'} | {len(mine) - len(ok)} | {cell(avg(secs))} |")
    L.append("")

    for name in dict.fromkeys(r["sample"] for r in rows):
        group = [r for r in rows if r["sample"] == name]
        before = group[0]["before"]
        L += [f"## {name}", "", f"Draft slop: **{before['tells_per_100_words']}** per 100 words "
              f"({before['words']} words)", "", "| Model | Slop | Judge | Worst tell left | Words |",
              "|---|---|---|---|---|"]
        for r in group:
            if r.get("error"):
                L.append(f"| {r['model']} | error | | {r['error'][:80]} | |")
                continue
            j = r.get("judge", {})
            L.append(f"| {r['model']} | {r['slop']['tells_per_100_words']} | {cell(j.get('total'))} | "
                     f"{j.get('worst_tell', '-') if j else '-'} | {r['slop']['words']} |")
        L += ["", "<details><summary>Original draft</summary>", "", "```", group[0]["original"], "```",
              "", "</details>", ""]
        for r in group:
            if r.get("error"):
                continue
            L += [f"### {r['model']}", "", r["rewrite"], ""]
            if r["slop"]["hits"]:
                tells = ", ".join(f"{k} x{v['count']}" for k, v in r["slop"]["hits"].items())
                L += [f"_Tells left: {tells}_", ""]
            inv = r.get("judge", {}).get("invented_facts")
            if inv:
                L += [f"_Judge flagged invented facts: {'; '.join(map(str, inv))}_", ""]
    (out / "report.md").write_text("\n".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", required=True, help="JSON file listing the models (see models.example.json)")
    ap.add_argument("--samples", default=str(KIT / "samples"), help="folder of .txt/.md drafts")
    ap.add_argument("--prompt", default="full", help="full, core, tiny, or a path to your own prompt file")
    ap.add_argument("--judge", help="name of the model in models.json to use as judge (optional)")
    ap.add_argument("--only", help="comma-separated model names to run (default: all)")
    ap.add_argument("--out", help="output folder (default results/<timestamp>)")
    a = ap.parse_args()

    models = json.loads(Path(a.models).read_text(encoding="utf-8"))
    by_name = {m["name"]: m for m in models}
    judge_m = by_name.get(a.judge) if a.judge else None
    if a.judge and not judge_m:
        sys.exit(f"--judge {a.judge} is not a name in {a.models}")
    contestants = [m for m in models if not m.get("judge_only")]
    if a.only:
        keep = set(a.only.split(","))
        contestants = [m for m in contestants if m["name"] in keep]

    prompt_path = KIT / "prompts" / PROMPTS[a.prompt] if a.prompt in PROMPTS else Path(a.prompt)
    system = prompt_path.read_text(encoding="utf-8")
    judge_tpl = (KIT / "prompts" / "judge_prompt.md").read_text(encoding="utf-8")
    samples = load_samples(a.samples)
    out = Path(a.out) if a.out else HERE.parent / "results" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for sname, text in samples:
        before = slop_check.check(text)
        for m in contestants:
            row = {"sample": sname, "model": m["name"], "original": text, "before": before}
            print(f"[{sname}] {m['name']} ...", end=" ", flush=True)
            try:
                rewrite, secs = chat(m, system, f"Rewrite this:\n\n{text}")
                row.update(rewrite=rewrite, seconds=secs, slop=slop_check.check(rewrite))
                (out / sname).mkdir(exist_ok=True)
                (out / sname / f"{re.sub(r'[^A-Za-z0-9_.-]+', '_', m['name'])}.md").write_text(rewrite, encoding="utf-8")
                msg = f"slop {before['tells_per_100_words']} -> {row['slop']['tells_per_100_words']}"
                if judge_m:
                    row["judge"] = judge(judge_m, judge_tpl, text, rewrite)
                    msg += f", judge {row['judge'].get('total', row['judge'].get('error'))}"
                print(msg)
            except Exception as e:  # keep going; one bad model should not sink the run
                row["error"] = str(e)
                print(f"ERROR {e}")
            rows.append(row)

    (out / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(out, prompt_path.name, contestants, a.judge, rows)
    print(f"\nReport: {out / 'report.md'}")


if __name__ == "__main__":
    main()
