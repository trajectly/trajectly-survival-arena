#!/usr/bin/env python3
"""Render a simple PNG death card from markdown text."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("Menlo.ttc", size=size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="trajectly_pr_comment.md")
    parser.add_argument("--output", default="death-card.png")
    parser.add_argument("--title", default="MERGE OR DIE - SNAPSHOT")
    parser.add_argument("--wrap-width", type=int, default=88)
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    text = input_path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = ["No failure content found."]

    wrapped_lines: list[str] = []
    for raw in lines:
        parts = textwrap.wrap(raw, width=max(30, args.wrap_width)) or [raw]
        wrapped_lines.extend(parts)

    width = 1280
    line_height = 28
    padding = 32
    header_height = 64
    height = max(460, (len(wrapped_lines) * line_height) + (padding * 2) + header_height)

    image = Image.new("RGB", (width, height), color=(15, 15, 18))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(34)
    body_font = _load_font(22)

    draw.text((padding, padding), args.title, fill=(245, 90, 90), font=title_font)

    y = padding + 54
    for line in wrapped_lines:
        draw.text((padding, y), line, fill=(230, 230, 235), font=body_font)
        y += line_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


if __name__ == "__main__":
    main()
