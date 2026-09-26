# Testing Rules

## Strictly Prohibit Automated Browser & Scratchpad Testing

1. **No Browser Subagent Invocations**:
   - Never call `browser_subagent` to test UI or interactive changes automatically.
   - Never create scratchpad files (`scratchpad_*.md`) for browser automated flows.
   - Do not open URLs, click DOM elements, or interact with browser windows on the user's desktop.

2. **User Manual UI Testing**:
   - The user tests all frontend and interactive features directly in their own browser.
   - The agent should only confirm code correctness using:
     - `npm run build`
     - Backend test suites (`unittest` / `pytest`)
     - Direct API curls if needed for sanity
   - Once verified through builds and unit tests, report the changes to the user so they can test it manually.
