#!/usr/bin/env python3
"""Report guide-enemy image coverage and optionally build hosted-image data."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


IMAGE_NAME_RE = re.compile(r"__(\d+)__(\d+)__(\d+)$")
DEFAULT_WEBP_DIR = (
    Path(__file__).resolve().parents[2]
    / "Meddle"
    / "Meddle"
    / "Meddle.Plugin"
    / "bin"
    / "webp"
)
DEFAULT_IMAGE_BASE_URL = "https://ff14.akurosiakamo.de/extras/images/meddle/webp"


@dataclass(frozen=True)
class EnemyEntry:
    post: str
    page_title: str
    url: str
    section: str
    name: str
    ids: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("webp_dir", nargs="?", type=Path, default=DEFAULT_WEBP_DIR)
    parser.add_argument(
        "--guide-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--manifest",
        "--sync",
        dest="manifest",
        action="store_true",
        help="Create the _data/enemy_images.json website manifest using hosted URLs.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_IMAGE_BASE_URL,
        help=f"Hosted WebP base URL (default: {DEFAULT_IMAGE_BASE_URL}).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="JSON report path (default: <guide-root>/tmp/enemy-image-coverage/report.json).",
    )
    return parser.parse_args()


def front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    return yaml.load(parts[1], Loader=loader) or {}


def enemy_ids(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values: Iterable[Any] = value if isinstance(value, list) else str(value).split(",")
    result = []
    for item in values:
        value_string = str(item).strip()
        if value_string.isdecimal() and value_string not in result:
            result.append(value_string)
    return tuple(result)


def enemy_name(enemy: dict[str, Any]) -> str:
    title = enemy.get("title", {})
    if isinstance(title, dict):
        return str(title.get("en") or title.get("de") or "Unknown enemy")
    return str(title or "Unknown enemy")


def collect_enemies(guide_root: Path) -> list[EnemyEntry]:
    result = []
    posts_root = guide_root / "_posts"
    for post_path in sorted(posts_root.rglob("*.md")):
        data = front_matter(post_path)
        title = data.get("title", {})
        if isinstance(title, dict):
            page_title = str(title.get("en") or title.get("de") or post_path.stem)
        else:
            page_title = str(title or post_path.stem)
        category = data.get("categories", "")
        if isinstance(category, list):
            category = category[0] if category else ""
        slug = str(data.get("slug") or post_path.stem.split("--")[-1].replace("_", "-"))
        url = str(data.get("permalink") or f"/{category}/{slug}.html")
        for section in ("bosses", "adds"):
            enemies = data.get(section) or []
            if not isinstance(enemies, list):
                continue
            for enemy in enemies:
                if not isinstance(enemy, dict):
                    continue
                result.append(
                    EnemyEntry(
                        post=post_path.relative_to(guide_root).as_posix(),
                        page_title=page_title,
                        url=url,
                        section=section,
                        name=enemy_name(enemy),
                        ids=enemy_ids(enemy.get("enemy_id")),
                    )
                )
    return result


def collect_images(webp_dir: Path) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = defaultdict(list)
    for image_path in sorted(webp_dir.rglob("*.webp")):
        match = IMAGE_NAME_RE.search(image_path.stem)
        if match:
            result[match.group(1)].append(image_path)
    return dict(result)


def build_report(
    entries: list[EnemyEntry], images_by_id: dict[str, list[Path]], webp_dir: Path
) -> dict[str, Any]:
    entries_with_ids = [entry for entry in entries if entry.ids]
    covered_entries = [
        entry for entry in entries_with_ids if any(images_by_id.get(i) for i in entry.ids)
    ]
    fully_covered_entries = [
        entry for entry in entries_with_ids if all(images_by_id.get(i) for i in entry.ids)
    ]
    used_ids = sorted({enemy_id for entry in entries_with_ids for enemy_id in entry.ids}, key=int)
    covered_ids = [enemy_id for enemy_id in used_ids if images_by_id.get(enemy_id)]

    def entry_json(entry: EnemyEntry) -> dict[str, Any]:
        return {
            "post": entry.post,
            "page_title": entry.page_title,
            "url": entry.url,
            "section": entry.section,
            "name": entry.name,
            "enemy_ids": list(entry.ids),
            "missing_ids": [i for i in entry.ids if not images_by_id.get(i)],
        }

    eligible_count = len(entries_with_ids)
    total_count = len(entries)
    unique_count = len(used_ids)
    page_stats: dict[str, dict[str, Any]] = {}
    for entry in entries:
        stats = page_stats.setdefault(
            entry.post,
            {
                "post": entry.post,
                "page_title": entry.page_title,
                "url": entry.url,
                "enemy_entries": 0,
                "entries_without_id": 0,
                "entries_covered": 0,
                "entries_fully_covered": 0,
            },
        )
        stats["enemy_entries"] += 1
        if not entry.ids:
            stats["entries_without_id"] += 1
        if entry.ids and any(images_by_id.get(i) for i in entry.ids):
            stats["entries_covered"] += 1
        if entry.ids and all(images_by_id.get(i) for i in entry.ids):
            stats["entries_fully_covered"] += 1

    for stats in page_stats.values():
        stats["coverage_percent"] = round(
            100 * stats["entries_covered"] / max(1, stats["enemy_entries"]), 2
        )

    return {
        "webp_directory": str(webp_dir.resolve()),
        "summary": {
            "enemy_entries_total": len(entries),
            "enemy_entries_without_id": len(entries) - eligible_count,
            "enemy_entries_with_id": eligible_count,
            "enemy_entries_covered": len(covered_entries),
            "enemy_entries_fully_covered": len(fully_covered_entries),
            "enemy_entry_coverage_percent": round(
                100 * len(covered_entries) / max(1, total_count), 2
            ),
            "unique_enemy_ids": unique_count,
            "unique_enemy_ids_covered": len(covered_ids),
            "unique_enemy_id_coverage_percent": round(
                100 * len(covered_ids) / max(1, unique_count), 2
            ),
            "matching_webp_images": sum(len(images_by_id[i]) for i in covered_ids),
        },
        "uncovered_entries": [
            entry_json(entry)
            for entry in entries
            if not any(images_by_id.get(i) for i in entry.ids)
        ],
        "partially_covered_entries": [
            entry_json(entry)
            for entry in covered_entries
            if not all(images_by_id.get(i) for i in entry.ids)
        ],
        "pages": sorted(
            page_stats.values(), key=lambda page: (page["coverage_percent"], page["post"])
        ),
    }


def build_manifest(
    guide_root: Path,
    webp_dir: Path,
    used_ids: set[str],
    images_by_id: dict[str, list[Path]],
    base_url: str,
) -> dict[str, list[dict[str, str]]]:
    manifest: dict[str, list[dict[str, str]]] = {}
    base_url = base_url.rstrip("/")

    for enemy_id in sorted(used_ids, key=int):
        records = []
        for source in images_by_id.get(enemy_id, []):
            match = IMAGE_NAME_RE.search(source.stem)
            if not match:
                continue
            relative_source = source.relative_to(webp_dir).as_posix()
            display_name = source.stem.split("__", 1)[0]
            records.append(
                {
                    "src": f"{base_url}/{relative_source}",
                    "alt": display_name,
                    "source": relative_source,
                    "variant": f"base {match.group(2)}, model {match.group(3)}",
                }
            )
        if records:
            manifest[enemy_id] = records

    manifest_path = guide_root / "_data" / "enemy_images.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Enemy image coverage")
    print("====================")
    print(f"Enemy entries:          {summary['enemy_entries_total']}")
    print(f"Entries without ID:     {summary['enemy_entries_without_id']}")
    print(
        "Covered entries:       "
        f"{summary['enemy_entries_covered']}/{summary['enemy_entries_total']} "
        f"({summary['enemy_entry_coverage_percent']:.2f}%)"
    )
    print(
        "Covered unique IDs:    "
        f"{summary['unique_enemy_ids_covered']}/{summary['unique_enemy_ids']} "
        f"({summary['unique_enemy_id_coverage_percent']:.2f}%)"
    )
    print(f"Matching WebP images:   {summary['matching_webp_images']}")


def main() -> int:
    args = parse_args()
    guide_root = args.guide_root.resolve()
    webp_dir = args.webp_dir.resolve()
    if not webp_dir.is_dir():
        raise SystemExit(f"WebP directory not found: {webp_dir}")
    if not (guide_root / "_posts").is_dir():
        raise SystemExit(f"Guide repository not found: {guide_root}")

    entries = collect_enemies(guide_root)
    images_by_id = collect_images(webp_dir)
    report = build_report(entries, images_by_id, webp_dir)
    report_path = (
        args.report or guide_root / "tmp" / "enemy-image-coverage" / "report.json"
    ).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print_summary(report)
    print(f"Detailed report:        {report_path}")

    if args.manifest:
        used_ids = {enemy_id for entry in entries for enemy_id in entry.ids}
        manifest = build_manifest(
            guide_root, webp_dir, used_ids, images_by_id, args.base_url
        )
        print(f"Manifest enemy IDs:     {len(manifest)}")
        web_report_path = guide_root / "assets" / "data" / "enemy-image-coverage.json"
        web_report_path.parent.mkdir(parents=True, exist_ok=True)
        web_report = {
            "summary": report["summary"],
            "pages": report["pages"],
            "uncovered_entries": report["uncovered_entries"],
        }
        web_report_path.write_text(
            json.dumps(web_report, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        print(f"Web report data:        {web_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
