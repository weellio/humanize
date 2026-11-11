# Short video scripts

YouTube Shorts, Reels, TikTok and any clip under about a minute.

Load a prompt first (see the main [README](../README.md)). Then use one of the prompts below.

## What changes for short video

Short scripts follow HIDE:

| Part | What it does |
|---|---|
| **Hook** | On-screen text that works with the sound off. A promise that doesn't give the answer away. Never the product or feature name. |
| **Intrigue** | Line one names the viewer's problem, so they think "that's me". No instructions yet. |
| **Delivery** | One idea. A second idea is a second video. |
| **Exit** | One thing the viewer can do today: try it, or answer a question in the comments. |

Two more rules:

- **Talk beside the viewer.** "You", not "I built".
- **Never "most people".** It puts the viewer outside the group you're talking about.

## Prompts to copy

### Rewrite a script

```
Rewrite this short video script using HIDE: Hook, Intrigue, Delivery, Exit.
Hook: on-screen text, under 8 words, a promise that doesn't give the answer away and doesn't
name the product. Intrigue: line one names the viewer's problem. Delivery: one idea only.
Exit: one thing they can do today. About [40] seconds spoken. Keep every fact from my draft.

[paste the script]
```

### Script from a feature or tip

```
Write a [30]-second script about this. Start from the problem it solves for the viewer, not
from the feature. Use HIDE. Give me three hook options, then the script.

What it is: [one or two sentences]
Who it's for: [the viewer]
```

### Split a long script

```
This script has more than one idea. Split it into separate short scripts, one idea each, every
one with its own hook and exit. Don't add anything that isn't in the draft.

[paste the script]
```

## Before and after

Before:

```
Hook: Introducing Smart Folders!
Hi everyone! In this video, I'm going to show you our new Smart Folders feature. Click the
folder icon, then select "New Smart Folder". Most people don't know this exists, but it's a
real game-changer for staying organized.
```

After:

```
Hook: Find any file in two clicks
You saved it last week. Now it's buried in [number] folders.
[Show: click the folder icon, pick "New Smart Folder", type the client's name]
Every file with that name, in one place.
Try it on your messiest project today.
```

The hook makes a promise instead of naming the feature. Line one is the viewer's problem. The draft never said
how many folders, so the model left a `[placeholder]` for you to fill in.

## Check it

```
python tools/slop_check.py script.txt
```

Spoken scripts are short, so a single tell moves the grade. Read the list it prints.
