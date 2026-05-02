from ffxiv_aku import loadDataTheQuickestWay

try:
    from helper import getImage
except ImportError:
    from .helper import getImage

LANGUAGES = {
    "de": "Bestiarium",
    "en": "Bestiary",
    "fr": "Bestiaire",
    "ja": "モンスターノート",
}

CATEGORY_ORDER = [
    ("Gladiator", "Gladiator", "/062000/062101_hr1.webp"),
    ("Faustkämpfer", "Faustkämpfer", "/062000/062102_hr1.webp"),
    ("Marodeur", "Marodeur", "/062000/062103_hr1.webp"),
    ("Pikenier", "Pikenier", "/062000/062104_hr1.webp"),
    ("Waldläufer", "Waldläufer", "/062000/062105_hr1.webp"),
    ("Druide", "Druide", "/062000/062106_hr1.webp"),
    ("Thaumaturg", "Thaumaturg", "/062000/062107_hr1.webp"),
    ("Hermetiker", "Hermetiker", "/062000/062126_hr1.webp"),
    ("Schurke", "Schurke", "/062000/062129_hr1.webp"),
    ("Mahlstrom", "Mahlstrom", "/083000/083301_hr1.webp"),
    ("Bruderschaft der Morgenviper", "Morgenviper", "/083000/083351_hr1.webp"),
    ("Legion der Unsterblichen", "Unsterblichen", "/083000/083401_hr1.webp"),
]


def yaml_quote(value):
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def normalize_icon_path(path):
    if not path:
        return ""
    normalized = str(path).replace("ui/icon/", "").replace("_hr1.tex", "_hr1.webp").replace(".tex", ".webp")
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized


def parse_count(value):
    try:
        return int(str(value or "0"))
    except ValueError:
        return 0


def unique_non_empty(values):
    result = []
    for value in values:
        if not value:
            continue
        if value not in result:
            result.append(value)
    return result


def has_meaningful_target(target):
    if not target:
        return False
    row_id = str(target.get("row_id", target.get("value", "0")))
    bnpc = target.get("BNpcName", {})
    name = bnpc.get("Singular", "") or bnpc.get("Plural", "")
    return row_id != "0" and bool(name)


def build_target_lookup():
    targets = loadDataTheQuickestWay("MonsterNoteTarget", translate=False)
    return {str(key): value for key, value in targets.items()}


def build_category_meta():
    meta = {}
    for index, (key, label, icon) in enumerate(CATEGORY_ORDER):
        meta[key] = {
            "label": label,
            "icon": icon,
            "order": index,
        }
    return meta


def build_bestiarium_data():
    notes = loadDataTheQuickestWay("MonsterNote", translate=False)
    target_lookup = build_target_lookup()
    category_meta = build_category_meta()
    grouped = {}

    for key, note in notes.items():
        name = str(note.get("Name", "")).strip()
        if not name:
            continue

        parts = name.rsplit(" ", 1)
        category_name = parts[0] if len(parts) == 2 and parts[1].isdigit() else name
        note_number = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
        rank = ((note_number - 1) // 10) + 1 if note_number > 0 else 1
        counts = note.get("Count", [])
        reward = parse_count(note.get("Reward", "0"))
        raw_targets = note.get("MonsterNoteTarget", [])

        targets = []
        for index, raw_target in enumerate(raw_targets):
            row_id = str(raw_target.get("row_id", raw_target.get("value", "0")))
            merged_target = dict(target_lookup.get(row_id, {}))
            merged_target.update(raw_target)
            if not has_meaningful_target(merged_target):
                continue

            bnpc = merged_target.get("BNpcName", {})
            target_name = bnpc.get("Singular", "") or bnpc.get("Plural", "")
            locations = unique_non_empty([entry.get("Name", "") for entry in merged_target.get("PlaceNameLocation", [])])
            zones = unique_non_empty([entry.get("Name", "") for entry in merged_target.get("PlaceNameZone", [])])
            town = merged_target.get("Town", {})
            targets.append({
                "id": row_id,
                "name": target_name,
                "icon": getImage(normalize_icon_path(merged_target.get("Icon", {}).get("path_hr1", ""))),
                "location": " / ".join(locations),
                "zone": " / ".join(zones),
                "town_name": town.get("Name", ""),
                "count": parse_count(counts[index] if index < len(counts) else 0),
            })

        if not targets:
            continue

        entry = {
            "id": str(key),
            "name": name,
            "note_number": note_number,
            "rank": rank,
            "reward": reward,
            "target_total": sum(target["count"] for target in targets),
            "targets": targets,
        }
        grouped.setdefault(category_name, []).append(entry)

    categories = []
    for category_name, entries in grouped.items():
        entries.sort(key=lambda entry: entry["note_number"])
        ranks = {}
        for entry in entries:
            ranks.setdefault(entry["rank"], []).append(entry)

        meta = category_meta.get(category_name, {
            "label": category_name,
            "icon": "/000000/000000_hr1.webp",
            "order": len(category_meta) + len(categories),
        })

        categories.append({
            "name": category_name,
            "label": meta["label"],
            "icon": getImage(meta["icon"]),
            "order": meta["order"],
            "total_reward": sum(entry["reward"] for entry in entries),
            "total_targets": sum(len(entry["targets"]) for entry in entries),
            "entries": entries,
            "ranks": [{"rank": rank, "count": len(rank_entries)} for rank, rank_entries in sorted(ranks.items())],
        })

    categories.sort(key=lambda category: (category["order"], category["name"]))
    return categories


def append_target_yaml(lines, target, indent="          "):
    lines.append(f"{indent}- id: {yaml_quote(target['id'])}\n")
    lines.append(f"{indent}  name: {yaml_quote(target['name'])}\n")
    lines.append(f"{indent}  icon: {yaml_quote(target['icon'])}\n")
    lines.append(f"{indent}  location: {yaml_quote(target['location'])}\n")
    lines.append(f"{indent}  zone: {yaml_quote(target['zone'])}\n")
    lines.append(f"{indent}  town_name: {yaml_quote(target['town_name'])}\n")
    lines.append(f"{indent}  count: {target['count']}\n")


def append_entry_yaml(lines, entry, indent="      "):
    lines.append(f"{indent}- id: {yaml_quote(entry['id'])}\n")
    lines.append(f"{indent}  name: {yaml_quote(entry['name'])}\n")
    lines.append(f"{indent}  note_number: {entry['note_number']}\n")
    lines.append(f"{indent}  rank: {entry['rank']}\n")
    lines.append(f"{indent}  reward: {entry['reward']}\n")
    lines.append(f"{indent}  target_total: {entry['target_total']}\n")
    lines.append(f"{indent}  targets:\n")
    for target in entry["targets"]:
        append_target_yaml(lines, target, indent=f"{indent}    ")


def append_rank_yaml(lines, rank, indent="      "):
    lines.append(f"{indent}- rank: {rank['rank']}\n")
    lines.append(f"{indent}  count: {rank['count']}\n")


def build_front_matter(categories):
    lines = [
        "---\n",
        "layout: bestiarium\n",
        "title:\n",
    ]
    for lang, title in LANGUAGES.items():
        lines.append(f"  {lang}: {yaml_quote(title)}\n")
    lines.extend([
        "last_modified_at: 2026-05-02\n",
        "permalink: /bestiarium/\n",
        'description: "Browse the Final Fantasy XIV hunting log and Grand Company hunting notes."\n',
        "page_type: index\n",
        "page_category: bestiarium\n",
        "bestiarium_categories:\n",
    ])

    for category in categories:
        lines.append(f"  - name: {yaml_quote(category['name'])}\n")
        lines.append(f"    label: {yaml_quote(category['label'])}\n")
        lines.append(f"    icon: {yaml_quote(category['icon'])}\n")
        lines.append(f"    order: {category['order']}\n")
        lines.append(f"    total_reward: {category['total_reward']}\n")
        lines.append(f"    total_targets: {category['total_targets']}\n")
        lines.append("    ranks:\n")
        for rank in category["ranks"]:
            append_rank_yaml(lines, rank)
        lines.append("    entries:\n")
        for entry in category["entries"]:
            append_entry_yaml(lines, entry)

    lines.append("---\n")
    return "".join(lines)


def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    categories = build_bestiarium_data()
    content = build_front_matter(categories)
    output_file = f"{main_script}/_pages/bestiarium/index.html"

    current_content = ""
    try:
        with open(output_file, encoding="utf8") as file_handle:
            current_content = file_handle.read()
    except FileNotFoundError:
        pass

    if current_content != content:
        with open(output_file, "w", encoding="utf8") as file_handle:
            file_handle.write(content)


if __name__ == "__main__":
    run()
