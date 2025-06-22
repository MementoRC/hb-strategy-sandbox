# Detailed Code Examples

## Repository Context Setup
```python
GITHUB_REPO = ARGS[0]  # "MementoRC/repo-name"
REPO_OWNER = GITHUB_REPO.split('/')[0]
REPO_NAME = GITHUB_REPO.split('/')[1]
PROJECT_ROOT = "."

# Get current branch
status_result = mcp__git__git_status(repo_path=PROJECT_ROOT)
CURRENT_BRANCH = status_result.current_branch

# Auto-detect PR
open_prs = mcp__git__github_list_pull_requests(
    repo_owner=REPO_OWNER, repo_name=REPO_NAME, 
    state="open", head=f"{REPO_OWNER}:{CURRENT_BRANCH}",
    per_page=5
)
WORKING_PR = open_prs.items[0].number if open_prs.items else None
```

## CI Status Checking
```python
# Check PR status
pr_status = mcp__git__github_get_pr_status(
    repo_owner=REPO_OWNER, repo_name=REPO_NAME, pr_number=WORKING_PR
)

# Get failing jobs with logs
if pr_status.state == "failure":
    failing_jobs = mcp__git__github_get_failing_jobs(
        repo_owner=REPO_OWNER, repo_name=REPO_NAME, pr_number=WORKING_PR,
        include_logs=True, include_annotations=True
    )
```

## Aider Implementation
```python
# Standard aider call
mcp__aider__aider_ai_code(
    ai_coding_prompt="Implement feature X with requirements...",
    model="gemini/gemini-2.5-pro-preview-06-05",
    relative_editable_files=["src/module.py", "tests/test_module.py"],
    relative_readonly_files=["src/existing.py", "tests/conftest.py"]
)
```

## Git Workflow
```python
# Create feature branch
mcp__git__git_create_branch(repo_path=PROJECT_ROOT, branch_name="feature/task-X")
mcp__git__git_checkout(repo_path=PROJECT_ROOT, branch_name="feature/task-X")

# Stage specific files
mcp__git__git_add(repo_path=PROJECT_ROOT, files=["src/file.py", "tests/test.py"])

# Verified commit
mcp__git__git_commit(
    repo_path=PROJECT_ROOT,
    message="feat: implement Task X\n\n✅ Quality validated\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Memento RC Mori <https://github.com/MementoRC>",
    gpg_sign=True, gpg_key_id="C7927B4C27159961"
)

# Push with upstream
mcp__git__git_push(
    repo_path=PROJECT_ROOT, remote="origin", 
    branch="feature/task-X", set_upstream=True
)
```

## Quality Validation
```python
# Run tests
subprocess.run([f"{PKG_MANAGER}", "run", "test"], check=True)

# Critical lint
subprocess.run([f"{PKG_MANAGER}", "run", "ruff", "check", "--select=F,E9"], check=True)

# Pre-commit hooks
subprocess.run([f"{PKG_MANAGER}", "run", "pre-commit", "run", "--all-files"], check=True)

# Git status verification
git_status = mcp__git__git_status(repo_path=PROJECT_ROOT)
```