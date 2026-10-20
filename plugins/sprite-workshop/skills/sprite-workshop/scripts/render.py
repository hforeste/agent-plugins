from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Sequence


POSES: dict[str, tuple[str, ...]] = {
    "idle": (
        "    .----.    ",
        "   / o  o \\   ",
        "  |   --   |  ",
        "  |  [==]  |  ",
        "   \\______/   ",
        "     /||\\     ",
        "     /  \\     ",
    ),
    "investigate": (
        "    .----.  ? ",
        "   / o  O \\-- ",
        "  |   --   |  ",
        "  |  [==]  |  ",
        "   \\______/   ",
        "     /||\\     ",
        "     /  \\     ",
    ),
    "repair": (
        "    .----.    ",
        "   / o  o \\   ",
        "  |   --   |  ",
        "  |  [==]  |==}",
        "   \\______/   ",
        "     /||\\     ",
        "     /  \\     ",
    ),
    "celebrate": (
        " \\  .----.  / ",
        "  \\ / ^  ^ \\/  ",
        "   |   --   |  ",
        "   |  [==]  |  ",
        "    \\______/   ",
        "      /||\\     ",
        "      /  \\     ",
    ),
    "warning": (
        "    .----.  ! ",
        "   / O  O \\   ",
        "  |   --   |  ",
        "  |  [!!]  |  ",
        "   \\______/   ",
        "     /||\\     ",
        "     /  \\     ",
    ),
}

AVAILABLE_POSES = tuple(POSES)


def _validated_poses(poses: Sequence[str]) -> list[str]:
    if not poses:
        raise ValueError("At least one pose is required.")

    normalized = [pose.strip().lower() for pose in poses]
    unknown = sorted(set(normalized) - set(POSES))
    if unknown:
        raise ValueError(
            f"Unsupported pose(s): {', '.join(unknown)}. "
            f"Choose from: {', '.join(AVAILABLE_POSES)}."
        )
    return normalized


def _sheet_model(character_name: str, poses: Sequence[str]) -> dict[str, object]:
    name = character_name.strip()
    if not name:
        raise ValueError("Character name cannot be empty.")

    selected = _validated_poses(poses)
    frame_width = max(
        len(line) for pose in selected for line in POSES[pose]
    )
    frames = [
        {
            "pose": pose,
            "lines": [line.ljust(frame_width) for line in POSES[pose]],
        }
        for pose in selected
    ]
    return {
        "character": name,
        "frameWidth": frame_width,
        "frameHeight": len(POSES[selected[0]]),
        "poses": frames,
    }


def _render_markdown(model: dict[str, object]) -> str:
    frames = model["poses"]
    assert isinstance(frames, list)
    width = int(model["frameWidth"])
    gap = "   "
    labels = gap.join(
        str(frame["pose"]).upper().center(width) for frame in frames
    )
    rows = [
        gap.join(str(frame["lines"][row]) for frame in frames)
        for row in range(int(model["frameHeight"]))
    ]
    description = (
        f"{model['character']} sprite sheet with "
        f"{', '.join(str(frame['pose']) for frame in frames)} poses."
    )
    return f"{description}\n\n```text\n{labels}\n" + "\n".join(rows) + "\n```"


def _render_svg(model: dict[str, object]) -> str:
    frames = model["poses"]
    assert isinstance(frames, list)
    char_width = 9
    line_height = 18
    padding = 20
    label_height = 34
    frame_width = int(model["frameWidth"]) * char_width + padding * 2
    frame_height = int(model["frameHeight"]) * line_height + label_height + padding
    width = frame_width * len(frames)
    height = frame_height + 46
    character = html.escape(str(model["character"]))
    pose_names = ", ".join(str(frame["pose"]) for frame in frames)
    description = html.escape(
        f"{model['character']} sprite sheet with {pose_names} poses."
    )

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="title description">'
        ),
        f"<title id=\"title\">{character} sprite sheet</title>",
        f"<desc id=\"description\">{description}</desc>",
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        (
            f'<text x="{padding}" y="30" font-family="system-ui, sans-serif" '
            f'font-size="20" font-weight="700" fill="#0f172a">{character}</text>'
        ),
    ]

    for index, frame in enumerate(frames):
        x = index * frame_width
        parts.append(
            f'<rect x="{x + 4}" y="42" width="{frame_width - 8}" '
            f'height="{frame_height - 4}" rx="10" fill="#ffffff" '
            f'stroke="#cbd5e1"/>'
        )
        parts.append(
            f'<text x="{x + frame_width / 2}" y="70" text-anchor="middle" '
            f'font-family="system-ui, sans-serif" font-size="14" '
            f'font-weight="700" fill="#334155">'
            f'{html.escape(str(frame["pose"]).upper())}</text>'
        )
        for row, line in enumerate(frame["lines"]):
            y = 96 + row * line_height
            parts.append(
                f'<text x="{x + padding}" y="{y}" '
                f'font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
                f'font-size="16" xml:space="preserve" fill="#0f172a">'
                f"{html.escape(str(line))}</text>"
            )

    parts.append("</svg>")
    return "\n".join(parts)


def render_sprite_sheet(
    character_name: str,
    poses: Sequence[str],
    output_format: str = "svg",
) -> str:
    model = _sheet_model(character_name, poses)
    normalized_format = output_format.strip().lower()
    if normalized_format == "svg":
        return _render_svg(model)
    if normalized_format == "markdown":
        return _render_markdown(model)
    if normalized_format == "json":
        return json.dumps(model, indent=2, sort_keys=True)
    raise ValueError("Output format must be svg, markdown, or json.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a deterministic service-bot sprite sheet."
    )
    parser.add_argument("--name", default="Service Bot")
    parser.add_argument(
        "--poses",
        default="idle,investigate,repair,celebrate",
        help=f"Comma-separated poses: {', '.join(AVAILABLE_POSES)}",
    )
    parser.add_argument(
        "--format",
        choices=("svg", "markdown", "json"),
        default="svg",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    output = render_sprite_sheet(
        args.name,
        [pose.strip() for pose in args.poses.split(",") if pose.strip()],
        args.format,
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
