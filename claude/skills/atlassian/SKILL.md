---
name: atlassian
description: Reference for working with the Bitbucket CLI (bkt), Jira (via MCP), and Confluence (via MCP). Covers commands, gotchas, and PR/ticket workflows. Project-specific details (Cloud IDs, user accounts, workflow transitions) live in the Projects section.
user-invocable: true
---

This is a quick reference for Atlassian tooling: **Bitbucket** (via the `bkt` CLI), **Jira** and **Confluence** (via the Atlassian MCP). The generic reference applies everywhere; project-specific details (Cloud IDs, user account IDs, workflow transitions) live in the [Projects](#projects) section at the bottom.

---

## Bitbucket CLI (`bkt`)

`bkt` is the [Bitbucket CLI](https://github.com/avivsinai/bitbucket-cli) — `gh`-style ergonomics for Bitbucket Cloud and Data Center. Subcommand: `pr` (no alias needed — already short). Workspace and repo auto-resolve from the active context (`bkt context list`) + git remote.

**Preferred entry point for surveying PRs: `bkt-pr`** — a system-wide helper that groups open PRs by: *needs your review*, *your PRs*, *no reviewers assigned*, *other*. Uses `bkt api` with `fields=+values.participants` to fetch everything (including per-reviewer approval state) in a single call. Auto-detects the current user by UUID — no override needed.

### Global output flags

- `--json` — JSON output (cleaner than raw API: stripped to useful fields, wrapped under `{ pull_request, repo, workspace }` or `{ pull_requests, repo, workspace }`).
- `--yaml` — YAML output.
- `--jq <expr>` — apply a jq expression to JSON output (requires `--json`). Avoids piping to external jq.
- `--template <go-template>` — render output with a Go text/template.

### Pull request commands

| Command | Purpose | Key flags |
|---|---|---|
| `bkt pr list` | List PRs (alias `ls`) | `--state OPEN\|MERGED\|DECLINED` (default OPEN), `--limit`, `--mine` |
| `bkt pr view <id>` | Full PR details incl. reviewers | (no extra flags beyond globals) |
| `bkt pr create` | Create PR | `--title`/`-t`, `--description`/`-b`/`--body`, `--source`, `--target`/`--destination`, `--reviewer <user\|{uuid}>` (repeatable), `--with-default-reviewers`, `--draft`/`-d`, `--close-source` |
| `bkt pr edit <id>` | Edit PR (alias `update`) | `--title`/`-t`, `--body`/`-b`/`--description`, `--reviewer` (add, repeatable), `--remove-reviewer` (repeatable), `--with-default-reviewers` |
| `bkt pr approve <id>` | Approve | — |
| `bkt pr decline <id>` | Decline | — |
| `bkt pr merge <id>` | Merge | — |
| `bkt pr reopen <id>` | Reopen a declined PR | — |
| `bkt pr publish <id>` | Mark a draft PR as ready | — |
| `bkt pr checkout <id>` | `git checkout` the PR's source branch locally | — |
| `bkt pr diff <id>` | Show the PR's diff | — |
| `bkt pr checks <id>` | Build/CI status | — |

### Comment commands

| Command | Purpose | Key flags |
|---|---|---|
| `bkt pr comments <id>` | **List** comments (plural) | `--state all\|resolved\|unresolved` (Cloud only), `--details` (show file, resolved, task status) |
| `bkt pr comment <id>` | **Add** comment (singular) | `--text <message>` (required), `--file <path>` + `--to-line <n>` or `--from-line <n>` (inline), `--parent <id>` (reply), `--pending` (draft review) |

### Raw API escape hatch

When a needed field isn't serialized by `bkt pr view`/`list` — notably `participants` with approval state, or `fields=` tricks — drop to `bkt api <path>`. Example:

```bash
bkt api "/2.0/repositories/<ws>/<repo>/pullrequests?state=OPEN&fields=%2Bvalues.participants"
```

`bkt-pr` uses this pattern internally.

### Gotchas

- **Plural/singular split for comments.** Listing is `bkt pr comments <id>` (plural); adding is `bkt pr comment <id>` (singular). Easy to flip.
- **Inline comment lines use `--to-line`/`--from-line`**, not `--line`. `--to-line` = new/added side, `--from-line` = old/removed side.
- **`create` uses `--reviewer` (repeatable)** — no `--add-reviewer` on create; that flag doesn't exist there. `--remove-reviewer` is `edit`-only.
- **Reviewer values accept a username OR `{uuid}`** (curly braces required for UUID form). When a name is ambiguous, prefer UUID.
- **`--state` on `pr list` wants uppercase** (`OPEN`, `MERGED`, `DECLINED`). Lowercase is rejected.
- **`pr list` is paginated** — default `--limit 20`; pass `--limit 0` for all.
- **`bkt pr view` and `bkt pr list --json` do NOT include `participants`/approval state.** Use `bkt api` with `fields=+values.participants` (list) or `fields=+participants` (single) when you need that.
- **Context + git remote handle most resolution automatically.** If it fails (unusual remote, no active context), explicit `--workspace` and `--repo` (or `--project` on DC) flags are available on every command.

### PR creation example (HEREDOC for multi-line description)

```bash
bkt pr create --title "[TICKET-XXX] Title" \
  --source feature/TICKET-XXX_Description --target develop \
  --reviewer alice-username \
  --description "$(cat <<'EOF'
## Summary

- Bullet point 1
- Bullet point 2

## Test plan

- [ ] Tests pass
EOF
)"
```

---

## Jira (MCP)

All tools are under the `mcp__plugin_atlassian_atlassian__` prefix. All require `cloudId` — look up in the [Projects](#projects) section.

### Looking up issues

- `getJiraIssue` — fetch a single issue by key (e.g. `CAL-555`)
- `searchJiraIssuesUsingJql` — JQL search, e.g. `project = CAL AND status = "In Progress"`

### Creating issues

- `createJiraIssue` — requires `projectKey`, `issueTypeName` (Bug, Task, Story), `summary`. Optional `description` (supports markdown via `contentFormat: "markdown"`).

### Transitioning issues

**Transitions must be fetched first — IDs vary per issue type, project, and current state:**

1. `getTransitionsForJiraIssue` — list available transitions from current state
2. `transitionJiraIssue` with the transition ID from step 1

Common workflow shape (exact transition names vary per project — see [Projects](#projects)):

```
In Analysis → Open → Selected for Development → In Progress → In Code Review → Done
```

### Assigning issues

- `editJiraIssue` with `fields: {"assignee": {"accountId": "..."}}`
- Look up accountId with `lookupJiraAccountId` if unknown

### Looking up users

- `lookupJiraAccountId` with a search string (name or email)

---

## Confluence (MCP)

- `getConfluenceSpaces` — list spaces
- `getConfluencePage` — fetch a page by ID
- `createConfluencePage` / `updateConfluencePage` — page CRUD
- `searchConfluenceUsingCql` — CQL search
- `createConfluenceFooterComment` / `createConfluenceInlineComment` — comments

For broad discovery across Jira + Confluence, use the unified `search` or `fetch` tools.

---

## Combined workflows

### Start working on a ticket

1. `getJiraIssue` to fetch type, summary, description
2. `editJiraIssue` to assign to the user
3. `git checkout <base-branch> && git pull && git checkout -b <prefix>/TICKET-XXX_Short_Description`
   - Bug → `bugfix/`, Story/Task → `feature/`
4. `getTransitionsForJiraIssue` + `transitionJiraIssue` to move to "In Progress" (may need multiple hops — see project workflow)
5. Rename the Claude session to the branch suffix
6. Report issue details

### Create a PR (after committing + pushing)

1. `bkt pr create` with HEREDOC description
2. Transition the Jira issue to "In Code Review"

### Review a PR

1. `bkt pr view <id>` — see PR details and reviewers
2. `bkt pr comments <id>` — existing comments (plural!)
3. `bkt pr diff <id>` or `git difftool <base>...HEAD` — visual diff
4. `bkt pr checks <id>` — CI status
5. `bkt pr checkout <id>` — check out locally to poke around
6. Use the `pr-review-toolkit:review-pr` skill for structured review

---

## Projects

Each project has its own folder under `projects/<project>/` containing at minimum a `README.md` with Cloud ID, project key, user accountIds, base branches, and workflow. Read the relevant project README when working on a ticket from that project.

| Project | Folder |
|---|---|
| Callibri (CAL) | [`projects/callibri/`](projects/callibri/) |

**To add a new project:** create `projects/<name>/README.md` with the same structure as the Callibri one, add a `workflow.dot` if the Jira workflow differs, and list it in the table above.
