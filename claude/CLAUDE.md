# CLAUDE.md

This file provides global guidance to Claude Code across all projects on this machine.

## File Deletion

Use `trash` instead of `rm` when deleting files. This puts files in the system trash rather than permanently deleting them.

## Git Workflow

Do not create git commits. Only stage files and suggest a commit message for the user to review and commit themselves.

Commit messages should follow these best practices:
- **Subject line**: Imperative mood ("Add feature", not "Added feature"), max ~50 chars, capitalized, no trailing period
- **Body** (separated by blank line): Explain *why*, not just *what*. Wrap at ~72 chars. Include issue/ticket references where applicable.
- Be specific — prefer "Fix null pointer in session cleanup on timeout" over "Fix bug"
- Use `pbcopy` to copy the suggested commit message into the clipboard so it has correct formatting. Write the message to a temp file first (e.g. `/tmp/commit-msg.txt`), then run `pbcopy < /tmp/commit-msg.txt` — don't use `printf` piping.

## PR Review

When asked to review a PR, follow this routine in order:
1. **Open the difftool.** First review of this PR → diff base..head. Subsequent review → diff previous-review-point..head (only what changed since the last look). Use Kaleidoscope (`git difftool`).
2. **Summarize + prose review.** State what the change is *supposed* to do, then write out the code review in prose (findings explained, not just a tool dump).
3. **Run the code-review skill** and show the results.

To scope a subsequent diff, a marker for where the last review ended (last-reviewed commit SHA) is needed — record it at the end of a review pass or ask for it.

## Code Quality

- Always run a sanity check (e.g. import, parse, build, or tests) before staging files. A commit must never leave the codebase in a broken state — if a change breaks tests, include the test fixes in the same commit.

## Diffing

- Use Kaleidoscope for visual diffs. It is configured globally in gitconfig — suggest `git difftool` or `git mergetool` commands.

## Code Navigation

- Prefer the LSP tool (goToDefinition, findReferences, incomingCalls, etc.) over grep for navigating code. Fall back to grep only for non-symbol searches (string literals, comments, patterns).

## Python Environment

Global Python packages are pinned in `~/.config/python/default-python-packages` and installed via `uv pip install --system --requirements ~/.config/python/default-python-packages`. Always available without a venv: `python-docx` (import as `docx`), `lxml`, `requests`, `beautifulsoup4`, `rich`, `z3-solver`, plus xonsh-related packages. Reach for these first instead of installing per-project; for .docx editing in particular, prefer `python-docx` over raw zip+XML manipulation unless byte-perfect template preservation is required.

## Bitbucket CLI (`bkt`)

Use `bkt` (avivsinai/bitbucket-cli) for all Bitbucket work — listing/creating/reviewing PRs, branches, pipelines, issues. Reach for the `bkt` skill for command reference and gotchas; do **not** use `bb` (removed).

### `bkt-pr` (system-wide helper)
- Lists open PRs grouped by: needs your review, your PRs, no reviewers assigned, other
- Single API call with participants included (no N+1 per-PR follow-ups)
- `bkt-pr` — default usage
