---
name: atlassian
description: Reference for working with the Bitbucket CLI (bb), Jira (via MCP), and Confluence (via MCP). Covers commands, gotchas, and PR/ticket workflows. Project-specific details (Cloud IDs, user accounts, workflow transitions) live in the Projects section.
user-invocable: true
---

This is a quick reference for Atlassian tooling: **Bitbucket** (via the `bb` CLI), **Jira** and **Confluence** (via the Atlassian MCP). The generic reference applies everywhere; project-specific details (Cloud IDs, user account IDs, workflow transitions) live in the [Projects](#projects) section at the bottom.

---

## Bitbucket CLI (`bb`)

`bb` is the [Bitbucket CLI](https://bitbucket.org/gildas_cherruel/bb). Aliases: `pullrequest` = `pr` = `pull-request`. Repository auto-detects from git remote. Profile auto-detected from `bb profile`.

**Preferred entry point for surveying PRs: `bb-pr`** — a system-wide helper that groups open PRs by: *needs your review*, *your PRs*, *no reviewers assigned*, *other*. Auto-detects user from `bb profile`. Override with `bb-pr --user "Name"`.

### Global output flags

- `--output json` (or `-o json`) — JSON output. Works on `list` and `get`, but **NOT reliably on `activity list`**.
- `--dry-run` / `--noop` / `--whatif` — preview without modifying.

### Pull request commands

| Command | Purpose | Key flags |
|---|---|---|
| `bb pullrequest list` | List PRs | `--state open\|merged\|declined\|all` (default `open`), `--query <filter>`, `--sort <col>`, `--columns <list>` |
| `bb pullrequest get <id>` | Full PR details incl. reviewers | `--columns <list>` |
| `bb pullrequest create` | Create PR | `--title`, `--source <branch>`, `--destination <branch>`, `--description <text>`, `--reviewer "Name"` (repeat or comma-sep; `default` picks repo defaults), `--draft`, `--close-source-branch` |
| `bb pullrequest update <id>` | Edit PR | `--title`, `--description`, `--destination`, `--add-reviewer "Name"`, `--remove-reviewer "Name"`, `--close-source-branch` |
| `bb pullrequest approve <id>` | Approve | — |
| `bb pullrequest unapprove <id>` | Remove approval | — |
| `bb pullrequest merge <id>` | Merge | — |
| `bb pullrequest decline <id>` | Decline | — |

### Comment commands

| Command | Purpose | Key flags |
|---|---|---|
| `bb pullrequest comment list` | List comments | `--pullrequest <id>` (required), `--query`, `--sort` |
| `bb pullrequest comment get <comment-id>` | Fetch one comment | `--pullrequest <id>` |
| `bb pullrequest comment create` | Add comment | `--pullrequest <id>`, `--file <path>` + `--line <n>` (inline), or `--from`/`--to` (range), `--parent <comment-id>` (reply). Message via stdin or positional. |
| `bb pullrequest comment resolve <comment-id>` / `reopen` / `update` / `delete` | Manage | `--pullrequest <id>` |

### Gotchas (things that cost me time in past sessions)

- **`create` uses `--reviewer` (singular).** `--add-reviewer` does NOT exist on `create` — that's for `update`.
- **`create` uses `--description`, not `--body`.**
- **`update` uses `--add-reviewer` / `--remove-reviewer`** (singular form only — plurals with `-s` don't work).
- **Comment subcommands take `--pullrequest <id>` as a flag**, not a positional arg. `bb pullrequest comment list --pullrequest 18` is correct; `bb pullrequest comment list 18` is wrong.
- **`bb pullrequest list` does NOT include reviewer data** — `get` each PR individually to check reviewers.

### PR creation example (HEREDOC for multi-line description)

```bash
bb pullrequest create --title "[TICKET-XXX] Title" \
  --source feature/TICKET-XXX_Description --destination develop \
  --reviewer "Name Name" \
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

1. `bb pullrequest create` with HEREDOC description
2. Transition the Jira issue to "In Code Review"

### Review a PR

1. `bb pullrequest get <id>` — see PR details and reviewers
2. `bb pullrequest comment list --pullrequest <id>` — existing comments
3. `git difftool <base>...HEAD` — visual diff
4. Use the `pr-review-toolkit:review-pr` skill for structured review

---

## Projects

Each project has its own folder under `projects/<project>/` containing at minimum a `README.md` with Cloud ID, project key, user accountIds, base branches, and workflow. Read the relevant project README when working on a ticket from that project.

| Project | Folder |
|---|---|
| Callibri (CAL) | [`projects/callibri/`](projects/callibri/) |

**To add a new project:** create `projects/<name>/README.md` with the same structure as the Callibri one, add a `workflow.dot` if the Jira workflow differs, and list it in the table above.
