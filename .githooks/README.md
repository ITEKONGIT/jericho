# Git hooks

Version-controlled hooks for this repo. Git ignores this directory unless you
point it at the hooks path, which needs doing **once per clone**:

```bash
git config core.hooksPath .githooks
```

## `pre-commit`

Runs the quality gate before each commit, so a broken commit fails locally
instead of in CI:

1. `python3 -m compileall` over every first-party Python file
2. every discovered `test_*.py` directory, wherever it lives
3. `bash -n` over every tracked shell script

The authoritative gate for CI is `.github/workflows/quality-gate.yml`. This
hook is the same checks, earlier, so the feedback loop is seconds instead of a
push-and-wait.

To skip it for a single commit (rare — prefer fixing the failure):

```bash
git commit --no-verify
```
