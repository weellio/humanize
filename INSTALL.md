# Install the skills in your AI tool

## The one-line way

Paste this into your AI coding tool: Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI or similar.

```
Install the humanize skills from https://github.com/weellio/humanize for me. Follow INSTALL.md in that repo.
```

The tool reads this file and does the rest. When it's done, start a new session so the tool picks up the skills.

## Steps for the AI doing the install

1. **Download the repo** to a temporary folder:
   `git clone --depth 1 https://github.com/weellio/humanize`.
   Without git, download `https://github.com/weellio/humanize/archive/refs/heads/main.zip` and unzip it.
2. **Find your skills folder** in the table below. Create it if it doesn't exist.
3. **Copy both skill folders,** `skills/humanize` and `skills/stop-slop`, whole, including their
   `references/` folders. If a skill with the same name is already there, ask the user before replacing it.
4. **Check it worked:** list the skills folder and confirm each copy has its `SKILL.md`.
5. **Delete the temporary download.**
6. **Tell the user** to start a new session, and show them the "Using the skills" section below.

| Tool | User-level skills folder |
|---|---|
| Claude Code (terminal, desktop app, VS Code and JetBrains extensions) | `~/.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` |
| GitHub Copilot (VS Code agent mode, Copilot CLI) | `~/.copilot/skills/` |
| Cursor | `~/.cursor/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Any other tool that reads `SKILL.md` folders | That tool's skills folder. Several tools share `~/.agents/skills/`. |

`~` is the user's home folder. On Windows that's `C:\Users\<name>`.

**For one project only:** copy the folders into the project instead: `.claude/skills/` for Claude Code,
`.agents/skills/` for Codex, Gemini and Cursor, `.github/skills/` for Copilot.

**If your tool has no skills support:** don't change its global instructions, because that would rewrite all
of the user's output. Tell the user to paste `prompts/humanize_full.md` at the start of a chat instead, as the
[README](README.md) explains.

## Claude Code: install as a plugin instead

Type these two commands in Claude Code:

```
/plugin marketplace add weellio/humanize
/plugin install humanize@weellio-humanize
```

To get updates later, run `/plugin marketplace update weellio-humanize`. Plugin skills carry the plugin's name
in front: `/humanize:humanize` and `/humanize:stop-slop`.

## Claude desktop app and claude.ai (no coding tool)

1. Download [humanize-skill.zip](https://github.com/weellio/humanize/releases/latest/download/humanize-skill.zip)
   and [stop-slop-skill.zip](https://github.com/weellio/humanize/releases/latest/download/stop-slop-skill.zip).
2. In Claude, open **Customize > Skills**, click **+**, then **Upload a skill**. Upload each zip.
3. Make sure the skill is switched on. It loads when you ask for writing help.

## Using the skills

- Ask in plain words: `Humanize this email:` and paste it, or `Use the humanize skill on this report.`
- Most tools load the skill on their own when you ask for writing or editing help.
- In Claude Code you can also type `/humanize`.
- **humanize** cleans up the AI tells and adds voice. **stop-slop** only removes the tells. Use it when you
  want the wording kept as close to yours as possible.

The prompts in the [guides](docs/README.md) work here too. Paste one and add your draft.

## Updating

Run the one-line prompt again and say `replace the old copies`.
