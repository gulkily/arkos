# Base Module Web UI – Compelling Experience Blueprint

## Guiding Principles
1. **Fast feedback** – reduce perceived latency and keep users informed during agent turns.
2. **Context clarity** – show what the agent knows (memory, tools, system prompt) so users trust decisions.
3. **Delightful polish** – thoughtful interactions, cohesive ARK branding, and helpful defaults.

## Experience Pillars & Tasks
### 1. Conversation Surface
- **Optimistic updates**: render the user bubble immediately while the request is in flight; append a typing indicator that swaps to the assistant response.
- **Timestamps & latency**: display “ARK • 1.8 s” to highlight responsiveness; log round-trip latency in `SessionPayload`.
- **Tool call surfacing**: when the agent returns a tool message, present a collapsible card summarizing the tool name, parameters, and result.
- **Transcript export**: “Download conversation” button bundles current session history (CSV/JSON) for sharing.

### 2. Session Management
- **Sidebar listing**: show active and recent sessions with quick resume; store metadata in the existing `memory_*.csv` file or a lightweight index.
- **Session lifecycle controls**: add “Reset session” and “Archive session” buttons that call `DELETE /sessions/{id}` and optionally snapshot the memory file.
- **Environment banner**: highlight whether this is a staging or production server, using `ARK_WEB_VERSION` and env labels.

### 3. Controls & Personalization
- **Settings drawer** (modal or slide-out):
  - Temperature slider, max tokens, top-p toggle.
  - System prompt editor (persist to session state).
  - Tool toggles (enable/disable tool states before messages).
- **Slash commands**: allow `/reset`, `/memory`, `/help` inside the composer; map to backend endpoints.
- **Prompt templates**: quick-start chips (“Summarize meeting”, “Generate test plan”) pre-fill the message box.

### 4. Feedback & Reliability
- **Toast notifications**: success/error toasts instead of overwriting the status bar; rely on payload `status` field for context.
- **Health indicator**: poll `/healthz`; show red dot if degraded, with tooltip on latest failure reason.
- **Retry flows**: give users a “Retry last message” button when responses fail; keep the text editable.
- **Analytics hooks**: instrument events (message sent, tool used, retry) with a minimal event bus for later dashboarding.

### 5. Visual & Brand Polish
- Adopt ARK color palette and typography; integrate subtle gradients, logo lockup, and iconography.
- Adjust layout for large screens (two-column view with context panel) and mobile (collapse sidebar, sticky composer).
- Provide light/dark mode toggle using CSS variables.
- Add onboarding microcopy (“ARK remembers past sessions stored securely on this device/server”).

## Implementation Roadmap
1. **Payload enrichment**: extend `SessionPayload` (backend) to include `latency_ms`, `tool_events`, and server metadata; update `base_module_web/static/index.html` to render them.
2. **UI scaffolding**: refactor SPA into modular JS (or migrate to lightweight framework if desired) to handle toasts, modals, and session sidebar.
3. **Controls API**: build `/sessions/{id}/settings` and `/sessions/{id}/actions/{action}` in FastAPI; enforce validation with Pydantic models.
4. **Brand assets**: collaborate with design for color tokens, logos, and icon set; implement CSS custom properties.
5. **Quality loop**: gather feedback through embedded survey/prompt, iterate on friction points, and track usage metrics.

## Metrics to Watch
- Average agent round-trip time.
- Session retention (how many conversations are resumed vs reset).
- Frequency of tool usage and tool failures.
- Error rate (`status="error"`) per day.
- Conversion on suggested prompt chips.

## Demo Narrative (Pitch Deck Angle)
1. **OpenWebUI baseline**: mention we can deploy it quickly (see companion doc) for feature parity with market tools.
2. **Custom UI advantages**: walk through branded experience, control panel, memory transparency, and lighter footprint.
3. **Future hooks**: highlight roadmap items (streaming, multi-user auth, analytics), reassuring stakeholders we own the end-to-end UX.
