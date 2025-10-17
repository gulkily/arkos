# Calendar HTML View – Development Plan

## Stage 1 – Calendar message detection contract (≤2h)
- **Dependencies**: Existing FastAPI chat flow in `base_module_web/app.py`, chat rendering in `base_module_web/static/index.html`.
- **Changes**: Extend `ChatMessage` model to allow optional `render_type` and `payload`; update `_serialise_history` to preserve structured calendar data (fallback to plain text). Add helper to recognise a "calendar_week" response (initially via deterministic mock hook in app for testing).
- **Testing**: Manual API call (`curl`/`httpie`) to `/sessions` and `/sessions/{id}/message` verifying JSON now includes render metadata without breaking non-calendar replies.
- **Risks**: Overfitting to temporary mock detection; ensure backwards compatibility for existing messages.

## Stage 2 – Calendar HTML component (≤2h)
- **Dependencies**: Stage 1 JSON contract.
- **Changes**: Update `renderMessages` in `base_module_web/static/index.html` to branch on `render_type === 'calendar_week'`, inject new calendar markup, and add scoped CSS for layout (grid, typography). Ensure plain text messages untouched.
- **Testing**: Use mocked payload to render in browser (or local dev tools) ensuring layout handles 0–5 events/day, overflow, and dark theme alignment.
- **Risks**: Potential XSS if unsafe HTML inserted; rely on deterministic template generation, not raw LLM HTML.

## Stage 3 – Mock + fallback flow verification (≤2h)
- **Dependencies**: Stages 1–2 complete.
- **Changes**: Add temporary helper endpoint or dev toggle to produce sample calendar payload (e.g., intercept specific user phrase) so demo works end-to-end. Document usage in README snippet or `docs/base_module_web_compelling_ui.md`.
- **Testing**: Full chat flow in browser via `/static/index.html`, confirm calendar renders and non-calendar prompts still show plain bubbles. Verify console free of errors.
- **Risks**: Mock path might leak into production responses; gate via explicit keyword and document clearly.
