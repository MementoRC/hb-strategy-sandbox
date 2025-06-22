# MCP Tools Reference

## 🎯 **MCP-FIRST STRATEGY**: 95% MCP coverage, 5% strategic Bash

## 🚨 **MANDATORY: NO BASH FOR GIT/GITHUB OPERATIONS**

❌ **NEVER USE**: `Bash(gh pr checks ...)` → ✅ Use `mcp__git__github_get_pr_checks()`
❌ **NEVER USE**: `Bash(git status)` → ✅ Use `mcp__git__git_status()`

## Enhanced Git MCP Server (PRIMARY)
- `mcp__git__git_status(repo_path)` - Working tree status
- `mcp__git__git_add(repo_path, files)` - Stage specific files
- `mcp__git__git_commit(repo_path, message, gpg_sign=True, gpg_key_id="C7927B4C27159961")` - Verified commits
- `mcp__git__git_push(repo_path, remote, branch, set_upstream=True)` - Push with upstream
- `mcp__git__git_pull(repo_path, remote, branch)` - Pull changes
- `mcp__git__git_create_branch(repo_path, branch_name)` - Create branches
- `mcp__git__git_checkout(repo_path, branch_name)` - Switch branches
- `mcp__git__git_diff_unstaged(repo_path)` - Show unstaged changes
- `mcp__git__git_diff_staged(repo_path)` - Show staged changes

## GitHub API Integration (PRIMARY)
- `mcp__git__github_list_pull_requests(repo_owner, repo_name, state, head, per_page)` - List PRs
- `mcp__git__github_get_pr_status(repo_owner, repo_name, pr_number)` - PR status/checks
- `mcp__git__github_get_pr_files(repo_owner, repo_name, pr_number, per_page, include_patch)` - PR files
- `mcp__git__github_get_pr_checks(repo_owner, repo_name, pr_number)` - Check runs
- `mcp__git__github_get_failing_jobs(repo_owner, repo_name, pr_number, include_logs, include_annotations)` - Failure analysis
- `mcp__git__github_get_pr_details(repo_owner, repo_name, pr_number, include_files)` - PR details

## Aider Development (PRIMARY)
- `mcp__aider__aider_ai_code(ai_coding_prompt, model, relative_editable_files, relative_readonly_files)` - Code implementation
- `mcp__aider__list_models(substring)` - Available models

## TaskMaster AI (PRIMARY)
- `mcp__taskmaster-ai__get_tasks(projectRoot)` - List tasks
- `mcp__taskmaster-ai__next_task(projectRoot)` - Get next task
- `mcp__taskmaster-ai__set_task_status(id, status, projectRoot)` - Update status

## Strategic Bash (5% - Package Manager Only)
- `${PKG_MANAGER} run test` - Test execution
- `${PKG_MANAGER} run ruff check --select=F,E9` - Critical lint
- `${PKG_MANAGER} run pre-commit run --all-files` - Hooks