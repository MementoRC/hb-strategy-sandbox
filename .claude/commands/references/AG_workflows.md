# Detailed Workflows

## Complete Task Implementation Workflow

### Phase 1: Preparation
1. **Branch Isolation**: Create dedicated feature branch using MCP Git
2. **File Analysis**: Use search tools to identify relevant files
3. **Context Preparation**: Separate editable vs readonly files for aider

### Phase 2: Implementation
1. **Model Selection**: Verify Gemini 2.5 Pro availability
2. **Aider Execution**: Run with comprehensive context
3. **Immediate Validation**: Quick syntax and import checks

### Phase 3: Quality Assurance
1. **Local Tests**: Full test suite execution
2. **Lint Validation**: Critical F,E9 violations check
3. **Pre-commit**: All hooks validation
4. **Git Status**: Clean working tree verification

### Phase 4: Deployment
1. **Selective Staging**: Stage only relevant files (never bulk add)
2. **Verified Commit**: GPG-signed with proper attribution
3. **Remote Push**: Push with upstream tracking
4. **CI Monitoring**: 120s wait + failure analysis loop

## CI Failure Resolution Workflow

### Phase 1: Analysis
1. **Status Check**: Get comprehensive PR status
2. **Failure Details**: Extract logs and annotations from failing jobs
3. **File Context**: Get changed files for targeted analysis
4. **Pattern Recognition**: Identify failure types and priorities

### Phase 2: Resolution
1. **AI Analysis**: Use pytest-analyzer for intelligent suggestions
2. **Priority Categorization**: HIGH → MEDIUM → LOW processing
3. **Aider Fixes**: Apply AI-recommended solutions
4. **Local Validation**: Verify fixes don't break existing functionality

### Phase 3: Iteration
1. **Commit Fixes**: GPG-signed commits with detailed descriptions
2. **Push Updates**: Trigger CI re-run
3. **Monitor Results**: 120s wait + re-analysis
4. **Repeat**: Until all CI checks pass or escalation needed

## MCP Git Safety Protocol

### Branch Management
- Always create feature branches for development
- Never work directly on main/development branches
- Use descriptive branch names: `aider/task-X-feature`

### Staging Protocol
- Stage specific files only: `files=["src/file.py", "tests/test.py"]`
- Never use bulk staging: `files=["."]`
- Verify .gitignore compliance before staging

### Commit Management
- Always use GPG signing: `gpg_sign=True, gpg_key_id="C7927B4C27159961"`
- Include proper attribution: `Co-Authored-By: Memento RC Mori`
- Link to TaskMaster tasks when applicable

### Recovery Options
- Minor issues: Targeted fixes with additional commits
- Major issues: `mcp__git__git_reset(repo_path=PROJECT_ROOT)`
- Complete failure: `mcp__git__git_checkout(repo_path=PROJECT_ROOT, branch_name="original-branch")`