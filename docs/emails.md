# Emails

Load a prompt first (see the main [README](../README.md)). Then use one of the prompts below.

## What changes for email

The main rules still apply. Email adds four of its own:

- **The first line says why you're writing.** Cut "I hope this finds you well" and "I wanted to reach out".
- **One ask, stated plainly, near the end.** Two asks means two emails.
- **Short.** Most emails should fit on a phone screen without scrolling.
- **End on the ask.** Posts end on a question to get comments. An email ends on what you want the person to
  do.

## Prompts to copy

### Rewrite a draft

```
Rewrite this email. Keep every fact, name and date. The first line says why I'm writing.
One clear ask at the end. Under [120] words. Put the subject line first, then the email.

[paste your draft]
```

### Write one from notes

```
Write an email from these notes. Use only what's in the notes, and put a [placeholder]
where something is missing.
To: [who, and how well I know them]
Goal: [what I want them to do]

Notes:
[your bullet points]
```

### Reply to an email

```
Write my reply to the email below. My answer: [yes / no / not yet], because [reason in a few words].
Match their level of formality. Don't repeat their email back to them.

Their email:
[paste it]
```

### Cold email

```
Rewrite this cold email. Open with something specific about them from my draft.
No compliments I can't back up and no claims about results unless my draft has them.
Ask for a reply, not a meeting. Under 90 words.

[paste your draft]
```

### Follow-up

```
Write a follow-up to my email below. They haven't answered in [number] days.
No "just bumping this" or "circling back". Add one new thing: [a detail, a deadline or an easier option].
Three sentences at most.

[paste your first email]
```

### Say no or give bad news

```
Rewrite this so the no is clear in the first two sentences. Give the real reason, then
[the alternative, if there is one]. Warm, without over-apologizing.

[paste your draft]
```

### Make it sound like you

```
Here are three emails I wrote myself. Match their voice: sentence length, greeting,
sign-off and how formal I am. Then rewrite the draft at the bottom.

Email 1: [paste]
Email 2: [paste]
Email 3: [paste]

Draft: [paste]
```

## Before and after

Before:

```
Subject: Quick Question

Hi Sarah,

I hope this email finds you well! I wanted to reach out regarding the upcoming Q3 planning
session. It's worth noting that our team has been working really hard to navigate the evolving
landscape, and we'd love to leverage your expertise. Would you be open to connecting at some
point to discuss further?

Best,
```

After:

```
Subject: Your input on Q3 planning before [date]?

Hi Sarah,

We're setting Q3 plans on [date], and I'd like your view on [the part you want her opinion on]
before we lock them in. Do you have 30 minutes on [day] or [day]?

Best,
```

The draft never said what the meeting was for or when it was. So the rewrite leaves brackets instead of
guessing. Fill those in and the email is done. If the model writes "Tuesday the 14th" when your draft didn't
say so, it broke the honesty rule. Try the full prompt or a different model.

## Check it

Save the result as a `.txt` file and run:

```
python tools/slop_check.py email.txt
```

In a short email one leftover phrase can push the score into "light". A 60-word email with one tell scores
1.7 per 100 words. Read the list of tells it prints, not only the grade.

## Common problems

- **A cheerful sign-off you didn't ask for** ("Looking forward to hearing from you!"). Add "no closing
  pleasantries" to the prompt.
- **It got longer.** Give a word limit. Models pad when they have room.
- **Subject lines.** Ask for three to choose from, then pick one yourself.
