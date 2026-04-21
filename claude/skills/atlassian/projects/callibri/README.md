# Callibri (CAL)

- **Atlassian instance**: beka-software.atlassian.net
- **Cloud ID**: `76207aac-f8aa-4044-b242-2120ec188b3a`
- **Jira project key**: `CAL`
- **Bitbucket repo**: auto-detected from git remote
- **Base branches**: `main` (prod), `develop` (integration)

## Known users

| Name | Email | accountId | Common role |
|---|---|---|---|
| Andreas Hartl | andreas.hartl@beka-software.at | `557058:700dc9e0-88b3-47d9-95cb-04aa78106504` | user / assignee |
| Philipp Reisinger | philipp.reisinger@beka-software.at | `60eb38854257a90070903e50` | reviewer |
| Felix Medl | felix.medl@beka-software.at | `712020:4945cebc-6f7c-454f-856e-60960be164ce` | reviewer |
| Amor Lisic | amor.lisic@beka-software.at | `5a1d2c60151a4f1e363cce84` | reviewer |

`bb` accepts name, email, UUID, or accountId for reviewers. Jira MCP calls need the accountId.
For any other user, use `lookupJiraAccountId` with the `cloudId` above.

## Workflow

Full graph (forward + backward transitions + terminal states): [`workflow.dot`](workflow.dot) — render with `dot -Tpng workflow.dot -o workflow.png`.

Quick linear forward path:

```
In Analysis → [Ready4Planning] → Open
           → [Select 4 Development] → Selected for Development
           → [Start Progress] → In Progress
           → [Implementation Done] → In Code Review
           → [Code Reviewed] → Done
```

To go from "In Analysis" to "In Progress", all three transitions are needed (Ready4Planning → Select 4 Development → Start Progress).

## Branch naming

- Bug → `bugfix/CAL-XXX_Short_Description`
- Story/Task → `feature/CAL-XXX_Short_Description`

Derive `Short_Description` from the issue summary (PascalCase, underscores).
