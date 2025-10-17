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

## Layout Blueprint
### Core layout
- **Header bar**: left-aligned ARK logotype, environment badge, and quick links (download transcript, open settings). Right side surfaces health status and user menu placeholder for future auth.
- **Conversation column**: stack of message bubbles with subtle separators for day/session boundaries. Reserve space for tool cards inline with assistant messages.
- **Context panel**: right column (collapsible on small screens) exposing memory summary, current system prompt, active tools, and latest tool outputs.
- **Composer rail**: bottom dock with multiline input, slash command hints, prompt chips, and send/stop buttons. Include secondary actions (retry, reset) as icon buttons with tooltips.

### Responsive behavior
- **Desktop ≥1280px**: three-column grid (session sidebar, conversation, context). Conversation gets 60 percent width for readability.
- **Tablet 768–1279px**: collapse context panel into tabs above the composer; session list becomes slide-out drawer.
- **Mobile ≤767px**: focus on conversation and composer; header condenses into icon-only controls, persistent floating button toggles session list.
- **High-contrast mode**: honor prefers-contrast media query and supply hardened tokens in CSS custom properties.

## Interaction Flows
### Message lifecycle
1. User submits message (optimistic bubble + typing indicator).
2. Frontend records a `message_sent` event and disables composer while awaiting response.
3. Backend responds with updated `SessionPayload` including `latency_ms`, `status`, and any `tool_events`.
4. UI swaps typing indicator for assistant bubble, renders tool cards inline, and re-enables composer with focus restoration.

### Tool reveal
1. When payload `tool_events` array is present, display accordion cards summarizing each tool call.
2. Expand-on-demand to show arguments, raw result, log excerpt, and “Copy result” button.
3. Surface errors with red accent, offer “Retry tool” action that resends the previous message with `force_tool` flag when supported.

### Session management
1. Session sidebar lists active sessions with `title`, `updated_at`, and status icon (active, archived, error).
2. Selecting a session loads history via GET `/sessions/{id}` and scrolls to latest entry.
3. “Reset session” triggers DELETE `/sessions/{id}`, confirms via modal, and clears conversation pane.
4. “Archive” toggles metadata flag and moves session to separate list; persists to CSV index for quick lookup.

### Settings and personalization
1. Settings drawer opens from header or keyboard shortcut (`Cmd/Ctrl + ,`).
2. Inputs for temperature, max tokens, top-p, and system prompt bind to local state with validation guard rails.
3. On save, issue PATCH `/sessions/{id}/settings`; optimistic UI updates and show toast on success/failure.
4. Tool toggles immediately send state update and annotate conversation with system message confirming change.

## Component Inventory
- `SessionSidebar`: searchable list, grouped into Active and Archived, with unread badges when assistant responded while closed.
- `ConversationTimeline`: renders `MessageBubble` components, groups by day, and handles optimistic entries.
- `MessageBubble`: variants for user/assistant/system/tool, supports markdown rendering, code copy buttons, and latency chip.
- `ToolCard`: collapsible panel summarizing tool call metadata, raw result, and optional preview (table, link, visualization).
- `Composer`: textarea with markdown toolbar, slash command parser, prompt template chips, and quick retry button.
- `SettingsDrawer`: tabbed modal covering Model, Tools, Appearance, and Advanced (logging toggle, export settings).
- `ToastCenter`: lightweight event bus powered toaster for success/error/info notifications.
- `HealthIndicator`: badge polling `/healthz` and exposing tooltip timeline of recent checks.

## Accessibility & Performance
- Ensure semantic landmarks (`main`, `nav`, `aside`) and correct ARIA roles for lists, accordions, and toasts.
- Meet WCAG 2.1 AA color contrast; provide focus outlines and skip-to-content link.
- Support full keyboard navigation, including trap-free modals and composer shortcuts.
- Respect prefers-reduced-motion by disabling animated gradients and easing heavy transitions accordingly.
- Lazy-load heavy assets (syntax highlighter, chart libs) and defer telemetry script initialization until user consents.
- Apply request coalescing to avoid duplicate fetches when users rapidly switch sessions.

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

### Calendar HTML demo trigger
- Start the web UI (`uvicorn base_module_web.app:app --host 0.0.0.0 --port 8100`) and open it in a browser.
- Send the prompt “View calendar for this week” in the chat window.
- ARK returns a structured weekly agenda rendered with the new calendar card; older clients fall back to the plain-text summary bundled in the same response.
- Pair this with your SSH tunnel or reverse proxy to demo the polished calendar experience to stakeholders.
