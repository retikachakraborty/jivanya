# Agent Rules & Guidelines

## 1. Browser & UI Testing Policy (Strict)

- **NEVER use the automated browser subagent (`browser_subagent`) or open automated browser testing sessions unless the user explicitly asks for it.**
- **DO NOT create browser scratchpads** (e.g. `scratchpad_*.md`, `browser/scratchpad_*.md`) to test UI changes or click around the user's open browser.
- **DO NOT take over the user's screen or browser window.** The user prefers to test UI and workflow changes manually in their own browser.
- Verification by the agent must ONLY be performed through non-intrusive terminal checks:
  1. Build validation (e.g., `npm run build`)
  2. Automated test suites (e.g., `PYTHONPATH=backend .venv/bin/python -m unittest discover -s backend/tests`)
  3. Linter / type-checking
  4. Non-intrusive HTTP checks (e.g., `curl -s http://localhost:3000`)
- When a UI feature is completed, provide the user with clear instructions so **they** can test it in their browser at their own pace.
