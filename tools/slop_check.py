"""slop_check: count AI-writing tells in text, with no model involved.

Same text in, same numbers out, so you can compare rewrites from different LLMs fairly.
It is a pattern counter, not a detector: it flags the tells the humanize rules ban.

Usage:
    python slop_check.py draft.txt                # report for one file
    python slop_check.py a.txt b.txt              # several files
    type draft.txt | python slop_check.py -       # stdin (Windows) / cat draft.txt | ... (Mac/Linux)
    python slop_check.py draft.txt --json         # machine-readable
"""
import json
import re
import statistics
import sys

# Hard tells: banned outright by the rules. Weight 1 each.
HARD = {
    "em_dash": [r"—", r"\s–\s", r"\s--\s"],
    "throat_clearing": [
        r"\bhere'?s the thing\b", r"\bhere'?s (?:what|why|how|this|that)\b", r"\bthe uncomfortable truth\b",
        r"\bit turns out\b", r"\blet me be clear\b", r"\bthe truth is\b", r"\bi'?ll say it again\b",
        r"\bi'?m going to be honest\b", r"\bcan we talk about\b", r"\bthe real \w+ (?:is|was)\b",
    ],
    "emphasis_crutch": [
        r"\bfull stop\.", r"\blet that sink in\b", r"\bthis matters because\b", r"\bmake no mistake\b",
        r"\bhere'?s why that matters\b", r"(?:^|\.\s+)period\.",
    ],
    "filler_phrase": [
        r"\bat its core\b", r"\bin today'?s\b", r"\b(?:it'?s )?worth noting\b", r"\bat the end of the day\b",
        r"\bwhen it comes to\b", r"\bin a world where\b", r"\bthe reality is\b",
    ],
    "meta_commentary": [
        r"\bhint:", r"\bplot twist\b", r"\bspoiler:", r"\byou already know this\b", r"\banother post\b",
        r"\ba feature,? not a bug\b", r"\bdressed up as\b", r"\bthe rest of this (?:essay|post|article)\b",
        r"\blet me walk you through\b", r"\bin this (?:section|post|article),? (?:we|i)'?ll\b",
        r"\bas we'?ll see\b", r"\bi want to explore\b",
    ],
    "jargon": [
        r"\bnavigat(?:e|es|ing)\b", r"\bunpack(?:s|ing)?\b", r"\blean(?:ing)? into\b", r"\blandscape\b",
        r"\bgame[- ]changer\b", r"\bdouble down\b", r"\bdeep dive\b", r"\btake a step back\b",
        r"\bmoving forward\b", r"\bcircle back\b", r"\bon the same page\b",
    ],
    "inflated_word": [
        r"\btestament\b", r"\bpivotal\b", r"\brevolutioni[sz]e|\brevolutionary\b", r"\bdelv(?:e|es|ing)\b",
        r"\btapestry\b", r"\brealm\b", r"\bseamless(?:ly)?\b", r"\brobust\b", r"\bunlock(?:s|ing)?\b",
        r"\bunleash(?:es|ing)?\b", r"\belevat(?:e|es|ing)\b", r"\bharness(?:es|ing)?\b", r"\bever-evolving\b",
        r"\bfast-paced\b", r"\bcutting-edge\b",
    ],
    "listed_adverb": [
        r"\b(?:really|just|literally|genuinely|honestly|simply|actually|deeply|truly|fundamentally|"
        r"inherently|inevitably|interestingly|importantly|crucially)\b",
    ],
    "binary_contrast": [
        r"\bnot because\b",
        r"\bnot (?:just|only|merely)\b[^.?!\n]{1,60}\bbut\b",
        r"\b(?:isn'?t|wasn'?t|aren'?t|is not|was not)\b[^.?!\n]{1,50}[.;,]\s*(?:it|that|this|they)(?:'s| is| was|'re| are)\b",
        r"\bit'?s not\b[^.?!\n]{1,50}[.;,]\s*it'?s\b",
        r"\bstops? being\b[^.?!\n]{1,40}\bstarts? being\b",
    ],
    "vague_declarative": [
        r"\bthe (?:implications|stakes|consequences|reasons) are (?:significant|high|real|structural|clear)\b",
        r"\bthis is the deepest problem\b",
    ],
    "hidden_actor": [
        r"\bit is (?:believed|thought|said|felt|widely known) that\b", r"\bmistakes were made\b",
    ],
    "rhetorical_setup": [
        r"\bthink about it[:.]", r"\band that'?s (?:okay|ok)\b", r"\bhere'?s what i mean\b",
        r"(?:^|[.!?]\s+)what if\b", r"\bthat'?s it\. that'?s the\b",
    ],
    "false_agency": [
        r"\bthe (?:data|numbers) (?:tells?|shows?) us\b",
        r"\bthe (?:culture|conversation|market|decision|complaint|bet)s? (?:will )?"
        r"(?:shifts?|moves?|rewards?|emerges?|becomes?|lives?)\b",
    ],
}

# Soft tells: often fine, suspicious in bulk. Weight 0.5 each.
SOFT = {
    "possible_passive": [r"\b(?:is|are|was|were|been|being)\s+(?:\w+ly\s+)?\w+ed\b(?!\s+(?:to|that)\b)"],
    "lazy_extreme": [r"\b(?:always|never|everyone|everybody|nobody|every single)\b"],
    "three_item_list": [r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3},? (?:and|or) [\w'-]+"],
    "so_or_look_opener": [r"(?m)^\s*(?:so|look),?\s"],
}

LY_OK = set("""only early daily weekly monthly yearly hourly family reply apply supply july italy rely ally fly
holy ugly belly jelly bully lily emily kelly assembly anomaly butterfly friendly lonely lovely likely unlikely
costly timely elderly silly curly oily chilly curly wobbly bubbly ghostly deadly lively orderly scholarly
quarterly manly womanly homely comply imply multiply sly shy dolly folly rally tally gully hilly""".split())

WH_OPENER = re.compile(r"^(?:what|when|where|which|who|why|how)\b", re.I)


def sentences(text):
    flat = re.sub(r"\s+", " ", text).strip()
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[#])", flat) if s]


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def check(text):
    hits = {}
    for weight, table in ((1.0, HARD), (0.5, SOFT)):
        for cat, pats in table.items():
            found = []
            for p in pats:
                found += [m.group(0).strip() for m in re.finditer(p, text, re.I)]
            if found:
                hits[cat] = {"weight": weight, "count": len(found), "examples": sorted(set(found))[:6]}

    ly = [w for w in words(text) if w.lower().endswith("ly") and len(w) > 4 and w.lower() not in LY_OK
          and not re.match(r"(?i)(?:really|just|literally|genuinely|honestly|simply|actually|deeply|truly|"
                           r"fundamentally|inherently|inevitably|interestingly|importantly|crucially)$", w)]
    if ly:
        hits["other_ly_word"] = {"weight": 0.5, "count": len(ly), "examples": sorted(set(ly))[:6]}

    sents = sentences(text)
    wh = [s[:40] for s in sents if WH_OPENER.match(s) and not s.rstrip().endswith("?")]
    if wh:
        hits["wh_opener"] = {"weight": 0.5, "count": len(wh), "examples": wh[:4]}

    lens = [len(words(s)) for s in sents if words(s)]
    run, longest = 1, 1
    for a, b in zip(lens, lens[1:]):
        run = run + 1 if abs(a - b) <= 2 else 1
        longest = max(longest, run)
    rhythm_cv = round(statistics.pstdev(lens) / statistics.mean(lens), 2) if len(lens) > 2 else None
    if longest >= 3:
        hits["same_length_run"] = {"weight": 0.5, "count": longest - 2,
                                   "examples": [f"{longest} sentences in a row within 2 words of each other"]}

    n_words = len(words(text))
    weighted = sum(h["weight"] * h["count"] for h in hits.values())
    per100 = round(weighted * 100 / n_words, 1) if n_words else 0.0
    grade = "clean" if per100 < 1.5 else "light" if per100 < 4 else "heavy"
    return {
        "words": n_words,
        "sentences": len(lens),
        "rhythm_cv": rhythm_cv,
        "tells_weighted": round(weighted, 1),
        "tells_per_100_words": per100,
        "grade": grade,
        "hits": hits,
    }


def report(name, r):
    out = [f"== {name}",
           f"   {r['words']} words, {r['sentences']} sentences, rhythm variation {r['rhythm_cv']} "
           f"(under 0.35 reads metronomic)",
           f"   tells: {r['tells_weighted']} weighted = {r['tells_per_100_words']} per 100 words -> {r['grade'].upper()}"]
    for cat, h in sorted(r["hits"].items(), key=lambda kv: -kv[1]["weight"] * kv[1]["count"]):
        tag = "" if h["weight"] == 1 else " (soft)"
        out.append(f"   - {cat}{tag}: {h['count']}  e.g. {', '.join(repr(e) for e in h['examples'][:3])}")
    return "\n".join(out)


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"] or ["-"]
    results = {}
    for p in paths:
        if p == "-":
            text = sys.stdin.read()
        else:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        results[p] = check(text)
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print("\n\n".join(report(k, v) for k, v in results.items()))


if __name__ == "__main__":
    main(sys.argv[1:])
