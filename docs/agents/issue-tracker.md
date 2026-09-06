# Issue tracker：GitHub

本仓库的 Issues 和规格说明（specs）均记录在 GitHub Issues 中。所有相关操作都使用 `gh` CLI。

## 约定

- **创建 Issue**：`gh issue create --title "..." --body "..."`。多行 body 使用 heredoc。
- **读取 Issue**：`gh issue view <number> --comments`，并使用 `jq` 过滤评论，同时获取 labels。
- **列出 Issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，并根据需要添加 `--label` 和 `--state` 过滤条件。
- **评论 Issue**：`gh issue comment <number> --body "..."`。
- **添加或移除 label**：`gh issue edit <number> --add-label "..."` / `gh issue edit <number> --remove-label "..."`。
- **关闭 Issue**：`gh issue close <number> --comment "..."`。

从 `git remote -v` 推断仓库。只要在本仓库的 clone 目录中运行，`gh` 会自动识别仓库。

## 将 Pull Request 作为 triage 请求入口

**PR 作为请求入口：否。**（如果本仓库将外部 PR 视为功能请求，可将其改为 `yes`；`/triage` 会读取该配置。）

保持 `no`，不要默认开启。以后如果希望外部 PR 进入 triage 队列，可以直接修改本文件。

当该配置改为 `yes` 时，PR 会使用与 Issue 相同的 labels 和状态，并使用对应的 `gh pr` 命令：

- **读取 PR**：`gh pr view <number> --comments` 和 `gh pr diff <number>`。
- **列出需要 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，然后只保留 `authorAssociation` 为 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE` 的 PR，排除 `OWNER`、`MEMBER` 和 `COLLABORATOR`。
- **评论、添加或移除 label、关闭 PR**：使用 `gh pr comment`、`gh pr edit --add-label` / `--remove-label`、`gh pr close`。

GitHub 的 Issue 和 PR 共用编号空间，因此单独看到 `#42` 时，它可能指 Issue，也可能指 PR。应先运行 `gh pr view 42`，失败后再运行 `gh issue view 42`。

## Wayfinder 操作

Wayfinder 使用一个 Issue 作为 map，并使用子 Issue 作为 tickets。

- **Map**：创建一个带有 `wayfinder:map` label 的 Issue，内容包含 Notes、Decisions-so-far 和 Fog。
- **Child ticket**：将 Issue 作为 GitHub sub-issue 链接到 map。如果当前仓库未启用 sub-issues，则在 map body 中使用 task list，并在 child body 顶部添加 `Part of #<map>`。使用 `wayfinder:<type>` labels，其中 type 可以是 `research`、`prototype`、`grilling` 或 `task`。ticket 被认领后，分配给负责推进工作的开发者。
- **Blocking**：使用 GitHub 原生 Issue dependencies，这是在 UI 中可见的标准阻塞关系。通过以下命令添加依赖：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`。其中 `<blocker-db-id>` 是 blocker 的数字 database id，可通过 `gh api repos/<owner>/<repo>/issues/<n> --jq .id` 获取，不是 `#number` 或 `node_id`。GitHub 会报告 `issue_dependencies_summary.blocked_by`，其中只统计仍然 open 的 blockers，这是实时的阻塞条件。如果无法使用 dependencies，则退回到 child body 顶部的 `Blocked by: #<n>, #<n>`。当所有 blocker 都关闭后，ticket 才算解除阻塞。
- **Frontier query**：列出 map 中仍然 open 的 child tickets（或 task list），排除存在 open blocker 的 ticket（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 中存在 open Issue）和已经分配给某人的 ticket；按 map 顺序取第一个。
- **Claim**：`gh issue edit <n> --add-assignee @me`，这是当前 session 的第一次写操作。
- **Resolve**：使用 `gh issue comment <n> --body "<answer>"` 添加答案，然后使用 `gh issue close <n>` 关闭，最后将 context pointer（gist 和链接）追加到 map 的 Decisions-so-far 中。

## 当技能要求“发布到 issue tracker”时

创建一个 GitHub Issue。

## 当技能要求“获取相关 ticket”时

运行 `gh issue view <number> --comments`。
