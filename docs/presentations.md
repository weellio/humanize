# Presentations

Slide decks, speaker notes, talk scripts and webinar outlines.

Load a prompt first (see the main [README](../README.md)). Then use one of the prompts below.

## What changes for slides

- **Titles are claims.** "Q3 Results" says nothing. "Churn fell to 4% in Q3" says what the slide shows.
  Someone who reads only the titles should get the whole talk.
- **One idea per slide.** A slide that needs two titles is two slides.
- **Bullets are short fragments,** under about 8 words. Fragments are fine on slides. The "no dramatic
  fragments" rule is for prose.
- **Use as many bullets as the content has.** AI decks put three bullets on every slide. Real content comes
  in ones, twos and fives.
- **Speaker notes are spoken.** Write them the way you'd say them: contractions, short sentences, "you".
- **Cut slides that repeat.** A "Key takeaways" slide that restates the titles can go. So can an agenda for
  a ten-minute talk.

## Get the text out of your slides

The model works best when it gets the slides as text in a fixed shape:

```
Slide 1
Title: ...
Bullets:
- ...
Notes: ...
```

- **PowerPoint:** View > Outline View shows every title and bullet. Copy it all.
- **Google Slides:** File > Download > Plain Text (.txt).
- **Speaker notes** may need copying slide by slide.

Do the wording as text first. Once it reads right, paste it back into your slides. If your chat app can make
files (ChatGPT can make a .pptx), you can ask for one at the end. Fixing words inside a file is slower.

## Prompts to copy

### Rewrite a deck

```
This is a slide deck, not a post. Rewrite each slide in the same format I sent.
Titles: a claim under 10 words that says what the slide shows.
Bullets: fragments under 8 words, only as many as the content needs.
Notes: how I'd say it out loud, in first person.
Keep every number and name. Don't add or remove slides.

[paste your slides]
```

### Outline to slides

```
Turn this outline into [10] slides, each with a title, up to 4 bullets and speaker notes.
Use only what's in the outline. Put a [placeholder] wherever a slide needs a number or
example I didn't give you.

[paste your outline]
```

### Titles only (the fastest fix)

```
Rewrite only these slide titles. Each title states what the audience should conclude from that
slide, in under 10 words. Return them as a numbered list.

[paste your titles]
```

### Speaker notes or a talk script

```
Rewrite these speaker notes as something I'd say out loud to [audience]. Short sentences,
contractions, "you". About [90] seconds per slide. Never "In this slide, we'll look at".

[paste the notes]
```

### Opening and closing

```
Using only facts from this deck, write the first 30 seconds of the talk. Start with the most
surprising fact or the audience's problem. No "Today I'm going to talk about".
Then write the last slide: the one thing I want them to do, and one real question to open Q&A.

[paste your slides]
```

## Before and after

Before:

```
Slide 4
Title: Key Benefits
- Enhanced efficiency
- Seamless integration
- Robust scalability
Notes: In this slide, we'll explore the key benefits of our solution. It's worth noting that
these benefits can be truly transformative for organizations.
```

After:

```
Slide 4
Title: [Product] works with the tools you already use
- [Task] goes from [before] to [after]
- Connects to [system]
- Handles [number] users
Notes: If you're wondering whether this means replacing your current tools, it doesn't. It
connects to [system]. The time you get back is in [task]: [before] down to [after].
```

Three vague bullets became claims with brackets. The brackets are the work the deck still needs. Try
`samples/06_slide_deck.txt` for a whole deck with the usual problems.

## Check it

```
python tools/slop_check.py slides.txt
```

Bullets are short on purpose, so ignore the rhythm line for slides. Look at the list of tells. If you want a
rhythm reading on your speaker notes, paste only the notes into a separate file and check that.
