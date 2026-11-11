# Documents

Reports, proposals, memos, how-tos, policies, bios and cover letters.

Load a prompt first (see the main [README](../README.md)). Then use one of the prompts below.

## What changes for documents

- **Keep the structure.** Headings, numbered steps, tables and figures stay where they are. Only the sentences
  inside them change.
- **Skip the post tricks.** No hook line and no closing question. The prompts below tell the model it's
  working on a document.
- **Put the conclusion first.** Busy readers read the headings and the first paragraph, then stop.
- **Headings say something.** "Results" tells the reader nothing. "Activation rose from 31% to 44%" tells them
  the section.
- **Keep some voice.** A report can say "we recommend" and why. "It is recommended that" hides who decided.
- **Send long documents a section at a time.** Most models drift after a few pages.

## Prompts to copy

### Rewrite a section

```
This is a document, not a post: no hook line and no closing question.
Rewrite the section below. Keep the headings, lists, tables and every number.
Lead with the main point. Plain professional voice. "We" is fine.

[paste the section]
```

### Executive summary

```
Write a five-sentence summary of this document for someone who will read nothing else.
Sentence one is the main finding or the ask. Use only facts from the document.
Don't open with "This document outlines".

[paste the document]
```

### Proposal

```
Rewrite this proposal section in this order: the client's problem in their words, what we'll do,
what they get and when. Cut any claim about past results that isn't in my draft, and put
[proof point] where one should go.

[paste the section]
```

### How-to or standard procedure

```
Rewrite these instructions as numbered steps. Each step starts with a verb and does one thing.
Put warnings right before the step they apply to. Keep every setting, name and number exactly
as written.

[paste the instructions]
```

### Memo or team update

```
Rewrite this update in this order: what changed, what it means for the reader, what they need to do
and by when. Under [200] words. No "I'm pleased to share".

[paste the draft]
```

### Cover letter or bio

```
Rewrite this in first person. Keep every job, date and achievement as written and add nothing.
Swap generic lines like "passionate about" or "results-driven" for the specific thing I did, taken
from the draft. If the draft doesn't say, leave a [placeholder].

[paste the draft]
```

### Match a house style

```
Here are two pages from a document my team already likes. Match its tone, sentence length
and how formal it is. Then rewrite the section at the bottom.

Example: [paste]

Section: [paste]
```

## Long documents, step by step

1. Load the full prompt (`humanize_full.md`) once at the start of the chat.
2. Send the first section with the "Rewrite a section" prompt.
3. For each later section, send `Same rules. Next section:` and the text.
4. At the end, ask: `List the headings and the first sentence of each section. Do they tell one story?`
   That catches sections that drifted.

**Word and Google Docs:** pasting into a chat can drop bold, links and tables. Ask for Markdown output if your
editor accepts it. Otherwise ask for plain text and put the formatting back yourself. Tables are safest
rewritten one cell at a time, or left alone.

## Before and after

Before:

```
In today's rapidly evolving business landscape, it is important to note that our organization
has made significant strides in enhancing operational efficiency. Moving forward, the team will
continue to leverage cutting-edge solutions to drive robust outcomes.
```

After:

```
We cut order processing from [X] days to [Y] last quarter. Next quarter we'll [next step].
```

The draft has no facts in it, so the rewrite is mostly brackets. That's useful. A vague document is usually
vague because the facts aren't in it yet, and the brackets show you which ones to go and get.

Try `samples/07_report_section.txt` to see the other case: a draft that does have real numbers, buried under
filler.

## Check it

```
python tools/slop_check.py report.md
```

It works on Markdown. Headings and table rows count as short sentences, so the rhythm line is less useful on
structured documents. Trust the tell count and the list of tells.
