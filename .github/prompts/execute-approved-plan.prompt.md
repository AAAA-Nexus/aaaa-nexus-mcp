---
name: "Execute Approved Hive Plan"
description: "Sync tasks from an approved plan and begin execution."
agent: "hive"
model: "gpt-5.4"
tools:
  - "read"
  - "search"
  - "tctinh.vscode-hive/hiveStatus"
  - "tctinh.vscode-hive/hiveTasksSync"
  - "tctinh.vscode-hive/hiveWorktreeStart"
---

Confirm the plan is approved, sync tasks with hive_tasks_sync, then start the next runnable task with hive_worktree_start.

Preserve Hive guardrails: follow task dependencies, keep planning and execution separate, and delegate implementation to workers rather than doing it inline.

If the work involves browser behavior, web flows, or end-to-end validation, prefer built-in browser tools and Playwright MCP where available instead of inventing extension-only browser helpers.
