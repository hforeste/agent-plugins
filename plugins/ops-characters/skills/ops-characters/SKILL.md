---
name: ops-characters
description: Render service health, incidents, and deployment states as deterministic browser-friendly character cards. Use when the user wants a visual operational summary that preserves metrics, evidence, and uncertainty.
---

# Ops Characters

Use this skill when the user asks for a visual summary of service health,
incident status, deployment progress, recovery, or resolution. The card is
designed for browser display and can be returned as Markdown or as an SVG
artifact.

Do not use this skill:

- As a substitute for investigating an incident.
- To infer a root cause that is not supported by available evidence.
- When the user requests only raw metrics or a conventional table.
- For general character sprite sheets; use `sprite-workshop` instead.

## Workflow

1. Gather the service name, operational state, summary, metrics, suspected
   cause, and evidence from the conversation or connected monitoring tools.
2. Never invent missing measurements. Omit values that are not available.
3. Choose one of the supported states listed below.
4. Run the bundled `scripts/render.py` with the available Python execution
   tool. For example:

   ```text
   python "${CLAUDE_PLUGIN_ROOT}/skills/ops-characters/scripts/render.py" --service "checkout-api" --state degraded --metric "Error rate=8.4%" --cause "Connection-pool exhaustion" --format markdown
   ```

5. Do not draw or edit the card manually.
6. Prefer `markdown` for an inline conversation response.
7. Prefer `svg` for an artifact, incident document, dashboard, or status post.
8. Present the technical facts before offering interpretation.
9. If Python execution is unavailable, explain that deterministic rendering
   cannot run in the current host. Do not replace it with model-generated art.

## Supported states

- `healthy`
- `deploying`
- `investigating`
- `degraded`
- `critical`
- `recovering`
- `resolved`
- `unknown`

## Evidence and uncertainty

- Pass possible causes through `suspected_cause`; the renderer labels them as
  suspected.
- Include concrete observations, alert IDs, query results, or links through
  `evidence`.
- Do not change `suspected cause` to `root cause` unless a separate
  investigation has established it.
- If status data conflicts or is insufficient, use `unknown` or
  `investigating`.

## Output requirements

- Preserve the tool output exactly.
- Do not rely on color or character expression as the only severity signal.
- Ensure the service name, textual state, summary, and important metrics remain
  visible.
- Include a short accessible description when presenting an SVG artifact.
