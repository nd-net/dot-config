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

## Code Quality

- Always run a sanity check (e.g. import, parse, build, or tests) before staging files. A commit must never leave the codebase in a broken state — if a change breaks tests, include the test fixes in the same commit.

## Diffing

- Use Kaleidoscope for visual diffs. It is configured globally in gitconfig — suggest `git difftool` or `git mergetool` commands.

## Code Navigation

- Prefer the LSP tool (goToDefinition, findReferences, incomingCalls, etc.) over grep for navigating code. Fall back to grep only for non-symbol searches (string literals, comments, patterns).

## Bitbucket CLI (`bb`)

### Common commands
- `bb pullrequest list` — list open PRs (auto-detects repo from git remote)
- `bb pullrequest get <id>` — full PR details including reviewers
- `bb pullrequest comment list --pullrequest <id>` — list all comments on a PR
- `bb pullrequest activity list --pullrequest <id>` — activity log (buggy with JSON output)

### Gotchas
- `--output json` works on `list` and `get`, but NOT reliably on `activity list`
- `bb pullrequest list` does NOT include full reviewer data; use `get` per PR to check reviewers
- Subcommands use `--pullrequest <id>` flag, not positional args (e.g. `comment list --pullrequest 18`)

### `bb-pr` (system-wide helper)
- Lists open PRs grouped by: needs your review, your PRs, no reviewers assigned, other
- Auto-detects user from `bb profile`
- `bb-pr` — default usage
- `bb-pr --user "Name"` — override detected user
