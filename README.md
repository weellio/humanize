# Humanize kit

Prompts and tools that make LLM writing read like a person wrote it, plus a way to test which model does it
best.

The rules have two halves:

1. **Subtract** the AI tells: em dashes, "Here's the thing", "not X, it's Y", "delve", "navigate the
   landscape", tidy three-item lists, adverb padding.
2. **Add** the human: a real opinion, specifics, things at their actual size, a hook and a real question for
   posts.

One rule sits on top: **never invent facts.** When a rewrite needs a number or name the draft doesn't have, the
model writes a `[placeholder]` instead of making one up.

## What's inside

| Folder / file | What it is |
|---|---|
| `prompts/humanize_full.md` | The complete rules with examples (~12k characters). Best quality. |
| `prompts/humanize_core.md` | The same rules, compressed (~4k characters). Fits a Custom GPT or Gemini Gem. |
| `prompts/humanize_tiny.txt` | A short version (under 800 characters) for small "custom instructions" boxes. |
| `prompts/judge_prompt.md` | A prompt that makes any model score a rewrite /80 and flag invented facts. |
| `tools/slop_check.py` | Counts AI tells in any text. No model, no internet. Same score for every model. |
| `tools/compare_models.py` | Sends the same drafts to several models and writes a side-by-side report. |
| `tools/models.example.json` | Example settings for OpenAI, Gemini, Claude, DeepSeek, OpenRouter and Ollama. |
| `docs/` | How-to guides with copy-paste prompts for [emails](docs/emails.md), [documents](docs/documents.md) and [presentations](docs/presentations.md). |
| `samples/` | Seven deliberately AI-sounding drafts to test with: a post, an article opener, a cold email, a product blurb, a business update, a slide deck and a report section. |
| `skill-folders/` | The original skill folders (`SKILL.md` + references), for tools that load skill folders. |

The tools need Python 3.8 or newer and nothing else.

## Use it in a chat app (no code)

| App | What to do |
|---|---|
| ChatGPT, Custom GPT | Paste `humanize_core.md` into Instructions. Upload `humanize_full.md` as a Knowledge file. |
| ChatGPT, plain chat | Paste `humanize_tiny.txt` into Settings > Personalization > Custom instructions. Or paste `humanize_full.md` as your first message, then send drafts. |
| Gemini | Make a Gem. Paste `humanize_core.md` into its instructions and upload `humanize_full.md` as a file. |
| Claude.ai | Make a Project. Paste `humanize_full.md` into the project instructions. |
| Any other chat | Paste `humanize_full.md` first, then "Rewrite this:" plus your draft. |

Then send `Rewrite this:` with your draft. Add `score` to get the /80 table after the rewrite.

To make it sound like you, paste a few paragraphs you wrote yourself and say "match this voice". The prompt
copies your sentence lengths, word choice and punctuation habits.

### Emails, documents and slides

The prompts are tuned for posts and articles out of the box. Each of these formats needs a few changes, so
each one has a guide with ready-made prompts:

| Writing | Guide |
|---|---|
| Replies, cold emails, follow-ups, saying no | [docs/emails.md](docs/emails.md) |
| Reports, proposals, memos, how-tos, cover letters | [docs/documents.md](docs/documents.md) |
| Slide decks, speaker notes, talk scripts | [docs/presentations.md](docs/presentations.md) |

## Test the output (no model needed)

Paste any rewrite into a text file and run:

```
python tools/slop_check.py rewrite.txt
```

You get the tells left per 100 words: under 1.5 is clean, 1.5 to 4 is light, over 4 is heavy. It also lists
each tell it found. It is a pattern counter, not an AI detector: a low score means the banned habits are gone.
It can't tell you whether the writing is good. Use the judge for that.

Try it on the samples first to see what heavy looks like:

```
python tools/slop_check.py samples/*.txt
```

## Compare models side by side

1. Copy `tools/models.example.json` to `tools/models.json`. Delete the models you don't have. Check that each
   `model` name matches what your provider currently offers.
2. Set your API keys as environment variables (the `api_key_env` names in the file):

   ```
   # Mac / Linux
   export OPENAI_API_KEY=sk-...
   # Windows PowerShell
   $env:OPENAI_API_KEY = "sk-..."
   ```

   Local models through Ollama or LM Studio need no key.
3. Run it:

   ```
   cd tools
   python compare_models.py --models models.json --judge judge
   ```

4. Open `results/<date-time>/report.md`. It has a summary table per model, then every rewrite of every draft
   with the tells it left behind.

Useful options:

| Option | What it does |
|---|---|
| `--prompt core` or `--prompt tiny` | Test the shorter prompts. Small local models often do better with `core`. |
| `--prompt my_prompt.md` | Test your own version of the rules. |
| `--samples my_drafts/` | Use your own drafts (any `.txt` or `.md` files). |
| `--only gpt,gemini` | Run just some of the models. |
| `--judge judge` | Score with the model named `judge` in models.json. Leave it out to use slop_check only, which costs nothing extra. |

Any provider with an OpenAI-compatible `/chat/completions` endpoint works: add an entry with its `base_url`,
`model` and key variable. `<think>` blocks from reasoning models are stripped before scoring.

### Reading the results

- **Slop** is the fair, repeatable number. Every model is measured with the same patterns.
- **Judge /80** catches what patterns can't: flat voice, vague claims, lost meaning. Models go easy on their
  own writing, so use a judge that isn't one of the contestants, and set its temperature to 0.
- **Invented facts** should be 0. A model that scores well but invents numbers fails, and the report counts it
  as a fail.
- Run it twice before you trust a gap between two models. The same model can swing a few points from run to
  run.

## Credits and license

Built on two MIT-licensed projects: **stop-slop** by Hardik Pandya (hvpandya.com), which supplies the removal
rules, and **tagore** (github.com/apurvrdx1/tagore), which supplies voice calibration, substance scoring and
the self-audit. The engagement layer, the honesty rule, the scoring tools and the comparison runner were added
on top. See `LICENSE.md`.
