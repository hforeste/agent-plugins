---
name: sprite-workshop
description: Create a deterministic, consistent ASCII character sprite sheet for browser display. Use when the user asks for character poses, sprite sheets, service mascots, or simple character animation frames.
---

# Sprite Workshop

Use this skill when the user wants a consistent character shown in one or more
poses. The output is designed for browser agents and can be returned as
Markdown or as an SVG artifact.

Do not use this skill for:

- Photorealistic images or detailed illustration.
- Reproductions of copyrighted characters.
- Service-health summaries; use `ops-characters` for those.
- Free-form artwork when the user explicitly wants a nondeterministic design.

## Workflow

1. Determine the character name, requested poses, and output format.
2. Select poses from `idle`, `investigate`, `repair`, `celebrate`, and
   `warning`.
3. Run the bundled `scripts/render.py` with the available Python execution
   tool. When the plugin root is available, the command is:

   ```text
   python "${CLAUDE_PLUGIN_ROOT}/skills/sprite-workshop/scripts/render.py" --name "Service Bot" --poses "idle,repair" --format markdown
   ```

4. Do not draw or adjust the frames manually.
5. Prefer `markdown` when the result should appear directly in the conversation.
6. Prefer `svg` when the user wants a downloadable artifact, documentation
   asset, or browser-scalable image.
7. If the script rejects a pose, present the supported poses and select the
   closest one only when the user's intent is unambiguous.
8. If Python execution is unavailable, explain that deterministic rendering
   cannot run in the current host. Do not replace it with model-generated art.

## Defaults

- Character name: `Service Bot`
- Poses: `idle,investigate,repair,celebrate`
- Format: `svg`

## Output requirements

- Preserve the tool output exactly so alignment and determinism are retained.
- Include a short accessible description when presenting an SVG artifact.
- Never claim that an unsupported or manually edited pose came from the
  deterministic renderer.
