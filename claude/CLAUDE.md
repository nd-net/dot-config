# CLAUDE.md

This file provides global guidance to Claude Code across all projects on this machine.

## File Deletion

Use `trash` instead of `rm` when deleting files. This puts files in the system trash rather than permanently deleting them.

## Git Workflow

Do not create git commits. Only stage files and suggest a commit message for the user to review and commit themselves. "Create a commit", "let's commit" and similar mean exactly that — stage the files and `pbcopy` the drafted message, then stop. Only run `git commit` when told to run it.

When creating a branch off a shared integration branch (`develop`/`main`), do **not** let it track that upstream — `git checkout -b foo origin/develop` makes a later `pull`/`push` touch the shared branch. Use `--no-track` (e.g. `git switch -c foo --no-track develop`) or `git branch --unset-upstream`.

**Never run a bare `git stash` or `git stash pop`.** Long-lived stashes are kept here, `git stash` is silent when there is nothing to save, and `git stash pop` always targets `stash@{0}` regardless of who put it there — so a pop can drop someone's months-old WIP into the tree. To read or run code from another branch use `git show <ref>:<path>` or `git worktree add` to a temp directory, never checkout+stash. If a stash is genuinely needed, push with a message and pop by explicit ref: `git stash push -m <label> -- <paths>` … `git stash pop stash@{n}` after confirming `n` with `git stash list`.

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

Review-comment style:
- **Never auto-post.** Before posting any Jira or PR comment, show a formatted draft and wait for approval.
- **Re-check for duplicates immediately before posting**, not just at the start of the review — Andreas reviews in parallel, so a finding may already have a comment.
- **Keep comments terse.** A heading plus 1–2 short sentences, no hedging. Put separate nits in their own separate comments.

Verification discipline — each of these has cost a retracted or wrong comment:
- **Check provenance, not shape.** Before endorsing a dedupe, a deletion, or a "redundant" simplification, `git log -S` the removed token. A duplicated condition is usually the fossil of a lost operand.
- **A rationale is a claim to verify.** When a comment, docstring, or PR description explains *why* something is safe, verify the mechanism it names — including rationales I write myself.
- **Don't generalise a framework rule from memory.** Probe the actual behaviour at the version in use. Over-applying a remembered rule produces confident, wrong findings.
- **Establish a baseline before reporting counts.** Run lint/tests on the base branch too, or the PR gets blamed for the repo's existing debt.
- **Verify a code-review-skill finding before relaying it.** The two passes check each other in both directions; the skill does produce false positives.
- **A mechanical rename is not mechanical if prose surrounds it.** When swapping a tool or symbol name in docs/config, read the neighbouring sentences: any behavioural claim about the old thing must be re-verified against the new one, not carried over.

Reviewing a *queue* of interdependent PRs, add a cross-PR pass — several real defects are invisible from inside any single diff:
- **Simulate the merge, don't infer it.** `git merge-tree --write-tree A B` answers "does this conflict" honestly. To test against a future state, build one: `T=$(git merge-tree --write-tree develop <pr1> | head -1)`, `S=$(git commit-tree $T -p develop -m sim)`, then merge-tree the next PR onto `$S`.
- **Ask whether each fix survives the next PR.** One PR adding an option and a later one replacing the same options object silently drops it. Compare the *final* shape of every field each PR touches.
- **Verify a rebase preserved content** with `git show <old> | git patch-id --stable` against the new commit, rather than eyeballing a diff whose offsets and blob hashes all moved.
- **Prove a large mechanical migration mechanically.** Count distinct changed-line patterns (`grep '^[-+]' | sed 's/[0-9]\+/N/g' | sort | uniq -c`) and per-file insert/delete shapes instead of reading hundreds of regenerated files.
- **Watch for one decision spread across several PRs** — settle it once in the earliest PR and say so in the others, so it doesn't read as pedantry.

## Code Quality

- Always run a sanity check (e.g. import, parse, build, or tests) before staging files. A commit must never leave the codebase in a broken state — if a change breaks tests, include the test fixes in the same commit.
- **Reproduce bugs through the real code path.** Drive the actual dependency (real or shimmed) rather than injecting synthetic values into an internal/debug seam, even when the injection is simpler — a test that sets a debug variable to a value nobody would use obscures what the bug is. Fall back to injection only when the harness makes the real path impossible. Spell out any remaining limitation of a fix in a comment, and show the empirical check for edge cases.
- **Name things positively.** Name a boolean, constant or predicate for what its members *are* (`READ_ONLY`, `ALLOWED`, `isWritable`), not what they are not (`NOT_WRITABLE`, `DISALLOWED`, `isNotWritable`). Never a negated name read through a `!` — that double negative has to be inverted twice at every call site. Applies to my own code, not only to review suggestions.

## Code Comments

- Don't reference tickets/PRs in permanent comments — the commit history already records that, and the reference rots. The only exception is a transient marker slated for removal: `TODO(CAL-NNN)` / `FIXME(...)`. Scan freshly-written comments for stray `CAL-`/ticket refs before staging.

## Writing Style

- Never use ß/ẞ — always write Swiss-German "ss" (e.g. "muss", "dass", "grösser") in any text produced in the user's voice: commit messages, code comments, Jira/PR text, docs.

## Diffing

- Use Kaleidoscope for visual diffs. It is configured globally in gitconfig — suggest `git difftool` or `git mergetool` commands.

## Code Navigation

- Prefer the LSP tool (goToDefinition, findReferences, incomingCalls, etc.) over grep for navigating code. Fall back to grep only for non-symbol searches (string literals, comments, patterns).

## Python Environment

Global Python packages are pinned in `~/.config/python/default-python-packages` and installed via `uv pip install --system --requirements ~/.config/python/default-python-packages`. Always available without a venv: `python-docx` (import as `docx`), `lxml`, `requests`, `beautifulsoup4`, `rich`, `z3-solver`, plus xonsh-related packages. Reach for these first instead of installing per-project; for .docx editing in particular, prefer `python-docx` over raw zip+XML manipulation unless byte-perfect template preservation is required.

## Shell (xonsh)

The interactive shell is **xonsh** — Python under the hood, so `$VAR` env references are Python values. To expand a variable inside a command:
- **Bare `$VAR`** when nothing follows it.
- **f-string `f"{$VAR}..."`** when the variable is immediately followed by `:` or other text — a plain double-quoted `"$VAR:literal"` mis-parses (the `:` and following text get swallowed). Applies to git `ref:path`, `host:port`, `python -c` payloads, etc.
- **`~` is not expanded inside a quoted string.** `$KUBECONFIG = "~/.kube/x"` keeps the tilde literal and the tool silently falls back to its default. Use a path literal `p"~/.kube/x"` (expands `~`, returns a `Path`) or `f"{$HOME}/.kube/x"`.
- Env vars are set as `$VAR = "value"`, not `export VAR=value`.

Other Python string constructs work in commands too (triple-quoted multi-line strings, r-strings like `r"\d+"` for regex args) — reach for these instead of shell-quoting gymnastics.

## Bitbucket CLI (`bkt`)

Use `bkt` (avivsinai/bitbucket-cli) for all Bitbucket work — listing/creating/reviewing PRs, branches, pipelines, issues. Reach for the `bkt` skill for command reference and gotchas; do **not** use `bb` (removed).

### `bkt-pr` (system-wide helper)
- Lists open PRs grouped by: needs your review, your PRs, no reviewers assigned, other
- Single API call with participants included (no N+1 per-PR follow-ups)
- `bkt-pr` — default usage
