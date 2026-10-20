# Agent Art Studio

This repository is a sample plugin marketplace for browser-based agents. It
contains two skills backed by bundled, deterministic Python renderers:

- `sprite-workshop` renders a consistent service-bot in multiple poses.
- `ops-characters` renders service-health information as an accessible status
  card.

Both plugins can return Markdown for direct conversation display or SVG for a
downloadable browser artifact. The renderers use only the Python standard
library and do not require an MCP server or third-party package.

## Marketplace layout

```text
.claude-plugin/marketplace.json
plugins/
  sprite-workshop/
  ops-characters/
```

Add the marketplace to Claude Code with:

```text
claude plugin marketplace add .
```

Azure SRE Agent users can register the repository URL from **Builder >
Plugins > Add marketplace**.

## Local development

The renderers can be exercised directly without installing dependencies:

```text
python plugins/sprite-workshop/skills/sprite-workshop/scripts/render.py --format markdown
python plugins/ops-characters/skills/ops-characters/scripts/render.py --service checkout-api --state degraded --metric "Error rate=8.4%" --metric "P95 latency=1.8 s" --cause "Database connection-pool exhaustion" --format markdown
```

The hosting agent needs access to a Python execution environment to run the
renderers. If script execution is unavailable, the skill should report that
limitation rather than substituting nondeterministic artwork.

Run the tests with:

```text
python -m unittest discover -s tests -v
```
