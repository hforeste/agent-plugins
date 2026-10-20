from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path
from typing import Mapping, Sequence


STATE_CONFIG: dict[str, dict[str, object]] = {
    "healthy": {
        "color": "#15803d",
        "message": "All systems look steady.",
        "art": (
            "    .----.    ",
            "   / ^  ^ \\   ",
            "  |   --   |  ",
            "  |  [OK]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "deploying": {
        "color": "#0369a1",
        "message": "Changes are moving through.",
        "art": (
            "    .----.    ",
            "   / o  o \\   ",
            "  |   --   |  ",
            "  |  [>>]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "investigating": {
        "color": "#7e22ce",
        "message": "Following the evidence.",
        "art": (
            "    .----.  ? ",
            "   / o  O \\-- ",
            "  |   --   |  ",
            "  |  [??]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "degraded": {
        "color": "#a16207",
        "message": "Service is running below target.",
        "art": (
            "    .----.    ",
            "   / x  o \\   ",
            "  |   --   |  ",
            "  |  [!!]  |==}",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "critical": {
        "color": "#b91c1c",
        "message": "Immediate attention is required.",
        "art": (
            " !  .----.  ! ",
            "   / O  O \\   ",
            "  |   --   |  ",
            "  |  [XX]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "recovering": {
        "color": "#0f766e",
        "message": "Signals are moving toward normal.",
        "art": (
            "    .----.  + ",
            "   / o  ^ \\   ",
            "  |   --   |  ",
            "  |  [++]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
    "resolved": {
        "color": "#047857",
        "message": "The incident is resolved.",
        "art": (
            " \\  .----.  / ",
            "  \\ / ^  ^ \\/  ",
            "   |   --   |  ",
            "   |  [OK]  |  ",
            "    \\______/   ",
            "      /||\\     ",
            "      /  \\     ",
        ),
    },
    "unknown": {
        "color": "#475569",
        "message": "There is not enough data yet.",
        "art": (
            "    .----.  ? ",
            "   / ?  ? \\   ",
            "  |   --   |  ",
            "  |  [..]  |  ",
            "   \\______/   ",
            "     /||\\     ",
            "     /  \\     ",
        ),
    },
}

AVAILABLE_STATES = tuple(STATE_CONFIG)


def _model(
    service: str,
    state: str,
    summary: str,
    metrics: Mapping[str, str],
    suspected_cause: str,
    evidence: Sequence[str],
) -> dict[str, object]:
    normalized_service = service.strip()
    normalized_state = state.strip().lower()
    if not normalized_service:
        raise ValueError("Service name cannot be empty.")
    if normalized_state not in STATE_CONFIG:
        raise ValueError(
            f"Unsupported state: {state}. "
            f"Choose from: {', '.join(AVAILABLE_STATES)}."
        )

    clean_metrics = {
        str(key).strip(): str(value).strip()
        for key, value in metrics.items()
        if str(key).strip() and str(value).strip()
    }
    clean_evidence = [
        str(item).strip() for item in evidence if str(item).strip()
    ]
    config = STATE_CONFIG[normalized_state]
    return {
        "service": normalized_service,
        "state": normalized_state,
        "summary": summary.strip() or str(config["message"]),
        "metrics": dict(sorted(clean_metrics.items())),
        "suspectedCause": suspected_cause.strip(),
        "evidence": clean_evidence,
        "color": config["color"],
        "art": config["art"],
    }


def _detail_lines(model: dict[str, object]) -> list[str]:
    lines = [f"Summary: {model['summary']}"]
    metrics = model["metrics"]
    assert isinstance(metrics, dict)
    lines.extend(f"{key}: {value}" for key, value in metrics.items())
    if model["suspectedCause"]:
        lines.append(f"Suspected cause: {model['suspectedCause']}")
    evidence = model["evidence"]
    assert isinstance(evidence, list)
    lines.extend(f"Evidence: {item}" for item in evidence)
    return lines


def _render_markdown(model: dict[str, object]) -> str:
    width = 68
    heading = f"{model['service']} | {str(model['state']).upper()}"
    art = model["art"]
    assert isinstance(art, tuple)
    details = _detail_lines(model)
    card = [
        "+" + "-" * (width - 2) + "+",
        f"| {heading:<{width - 4}} |",
        "+" + "-" * (width - 2) + "+",
    ]
    for line in art:
        card.append(f"| {line:<{width - 4}} |")
    card.append("+" + "-" * (width - 2) + "+")
    for detail in details:
        wrapped = textwrap.wrap(detail, width=width - 6) or [""]
        card.extend(f"| {line:<{width - 4}} |" for line in wrapped)
    card.append("+" + "-" * (width - 2) + "+")
    description = (
        f"{model['service']} is {model['state']}. {model['summary']}"
    )
    return f"{description}\n\n```text\n" + "\n".join(card) + "\n```"


def _render_svg(model: dict[str, object]) -> str:
    details = _detail_lines(model)
    wrapped_details: list[str] = []
    for detail in details:
        wrapped_details.extend(textwrap.wrap(detail, width=68) or [""])

    width = 760
    detail_start = 270
    height = detail_start + len(wrapped_details) * 24 + 34
    service = html.escape(str(model["service"]))
    state = html.escape(str(model["state"]).upper())
    summary = html.escape(str(model["summary"]))
    color = html.escape(str(model["color"]))
    description = html.escape(
        f"{model['service']} is {model['state']}. {model['summary']}"
    )

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="title description">'
        ),
        f'<title id="title">{service} operational status</title>',
        f'<desc id="description">{description}</desc>',
        '<rect width="100%" height="100%" rx="14" fill="#ffffff" stroke="#cbd5e1"/>',
        f'<rect width="100%" height="64" rx="14" fill="{color}"/>',
        f'<rect y="50" width="100%" height="14" fill="{color}"/>',
        (
            f'<text x="24" y="40" font-family="system-ui, sans-serif" '
            f'font-size="22" font-weight="700" fill="#ffffff">{service}</text>'
        ),
        (
            f'<text x="736" y="40" text-anchor="end" '
            f'font-family="system-ui, sans-serif" font-size="18" '
            f'font-weight="700" fill="#ffffff">{state}</text>'
        ),
        (
            f'<text x="250" y="100" font-family="system-ui, sans-serif" '
            f'font-size="17" font-weight="600" fill="#0f172a">{summary}</text>'
        ),
    ]

    art = model["art"]
    assert isinstance(art, tuple)
    for row, line in enumerate(art):
        parts.append(
            f'<text x="32" y="{100 + row * 21}" '
            f'font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
            f'font-size="17" xml:space="preserve" fill="#0f172a">'
            f"{html.escape(line)}</text>"
        )

    for index, detail in enumerate(wrapped_details):
        parts.append(
            f'<text x="250" y="{132 + index * 24}" '
            f'font-family="system-ui, sans-serif" font-size="15" '
            f'fill="#334155">{html.escape(detail)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def render_ops_card(
    service: str,
    state: str,
    summary: str = "",
    metrics: Mapping[str, str] | None = None,
    suspected_cause: str = "",
    evidence: Sequence[str] | None = None,
    output_format: str = "svg",
) -> str:
    model = _model(
        service,
        state,
        summary,
        metrics or {},
        suspected_cause,
        evidence or [],
    )
    normalized_format = output_format.strip().lower()
    if normalized_format == "svg":
        return _render_svg(model)
    if normalized_format == "markdown":
        return _render_markdown(model)
    if normalized_format == "json":
        return json.dumps(model, indent=2, sort_keys=True)
    raise ValueError("Output format must be svg, markdown, or json.")


def _parse_metric(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Metrics must use NAME=VALUE.")
    name, metric_value = value.split("=", 1)
    if not name.strip() or not metric_value.strip():
        raise argparse.ArgumentTypeError("Metrics must use NAME=VALUE.")
    return name.strip(), metric_value.strip()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a deterministic operational character card."
    )
    parser.add_argument("--service", required=True)
    parser.add_argument("--state", choices=AVAILABLE_STATES, required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument(
        "--metric",
        action="append",
        type=_parse_metric,
        default=[],
        metavar="NAME=VALUE",
    )
    parser.add_argument("--cause", default="")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument(
        "--format",
        choices=("svg", "markdown", "json"),
        default="svg",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    output = render_ops_card(
        service=args.service,
        state=args.state,
        summary=args.summary,
        metrics=dict(args.metric),
        suspected_cause=args.cause,
        evidence=args.evidence,
        output_format=args.format,
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
