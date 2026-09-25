"""Beastmaster sheet loading, isolated from the other job data loaders.

All Beastmaster data ultimately lives in the generated Beastmaster post under
_posts/klassen_und_jobs.  Jekyll does not depend on a separate _data file.
"""

import json
import re
from html import escape
from pathlib import Path


BEASTMASTER_DATA_DIR = Path(__file__).resolve().parents[2] / "tmp" / "Bestienbändiger_Files"


# Borgen is selected by the active beast's family/classification rather than
# Pet.Abilities. Keep this generation rule in Python; the resulting data is
# embedded into the generated Beastmaster post together with every other
# Beastmaster field.
BEAST_CLASSIFICATION_BY_NUMBER = {
    1: "Beastkin", 2: "Beastkin", 3: "Beastkin", 4: "Wavekin", 5: "Beastkin",
    6: "Cloudkin", 7: "Soulkin", 8: "Vilekin", 9: "Wavekin", 10: "Vilekin",
    11: "Cloudkin", 12: "Seedkin", 13: "Ashkin", 14: "Scalekin", 15: "Wavekin",
    16: "Vilekin", 17: "Ashkin", 18: "Soulkin", 19: "Cloudkin", 20: "Seedkin",
    21: "Scalekin", 22: "Seedkin", 23: "Soulkin", 24: "Cloudkin", 25: "Scalekin",
    26: "Beastkin", 27: "Wavekin", 28: "Vilekin", 29: "Soulkin", 30: "Beastkin",
    31: "Wavekin", 32: "Cloudkin", 33: "Beastkin", 34: "Scalekin", 35: "Scalekin",
    36: "Seedkin", 37: "Vilekin", 38: "Beastkin", 39: "Seedkin", 40: "Ashkin",
    41: "Wavekin", 42: "Scalekin", 43: "Scalekin", 44: "Vilekin", 45: "Ashkin",
    46: "Cloudkin", 47: "Soulkin", 48: "Wavekin", 49: "Seedkin", 50: "Beastkin",
}


BORROW_ACTION_BY_CLASSIFICATION = {
    "Beastkin": {
        "title": {"de": "Biesthaut", "en": "Beastskin"},
        "description": {
            "de": "Verringert erlittenen physischen Schaden und erhöht die kritische Trefferrate.",
            "en": "Reduces physical damage taken and increases critical hit rate.",
        },
    },
    "Vilekin": {
        "title": {"de": "Vileskin", "en": "Vileskin"},
        "description": {
            "de": "Verhindert die meisten Rückstoß- und Heranzieheffekte und erhöht die Blockrate.",
            "en": "Nullifies most knockback and draw-in effects and increases block rate.",
        },
    },
    "Cloudkin": {
        "title": {"de": "Cloud Skim", "en": "Cloud Skim"},
        "description": {
            "de": "Bewegt dich schnell in die gewählte Richtung und erhöht die Ausweichrate.",
            "en": "Moves quickly in the selected direction and increases evasion rate.",
        },
    },
    "Seedkin": {
        "title": {"de": "Seedsower", "en": "Seedsower"},
        "description": {
            "de": "Belegt Gegner in der Nähe mit einem Effekt, der ihren verursachten Schaden senkt und Schaden über Zeit verursacht.",
            "en": "Afflicts nearby enemies with an effect that reduces damage dealt and deals damage over time.",
        },
    },
    "Wavekin": {
        "title": {"de": "Brechende Welle", "en": "Quelling Wave"},
        "description": {
            "de": "Wasserbasierter Fernangriff. Erhöht TP und gewährt zusätzliche TP, wenn ein positiver Status des Ziels entfernt wird.",
            "en": "Deals water-aspected ranged damage. Increases TP and grants additional TP when a beneficial status is removed from the target.",
        },
    },
    "Scalekin": {
        "title": {"de": "Scaleskin", "en": "Scaleskin"},
        "description": {
            "de": "Erzeugt eine Barriere gegen magischen Schaden und gewährt TP, wenn sie vollständig verbraucht wird.",
            "en": "Creates a barrier against magical damage and grants TP when the barrier is fully consumed.",
        },
    },
    "Soulkin": {
        "title": {"de": "Seelenschmerz", "en": "Soul Crush"},
        "description": {
            "de": "Nahkampfangriff, der gegnerische Kommandos unterbrechen kann. Erfolgreiche Unterbrechungen erhöhen Schaden und TP-Gewinn.",
            "en": "A melee attack capable of interrupting enemy actions. A successful interrupt increases damage and TP gained.",
        },
    },
    "Ashkin": {
        "title": {"de": "Scouring Ash", "en": "Scouring Ash"},
        "description": {
            "de": "Entfernt einen negativen Status von dir oder einem Gruppenmitglied und stellt bei erfolgreicher Entfernung LP und TP wieder her.",
            "en": "Removes a detrimental status from self or a party member and restores HP and TP when successful.",
        },
    },
}


def load_beastmaster_data(filename: str, *, local_dir: Path | None = None) -> dict:
    """Prefer a local Beastmaster export; use the raw server sheet when absent."""
    if not filename.endswith(".json"):
        filename += ".json"
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*\.json", filename):
        raise ValueError("Expected a sheet filename without a directory")

    path = (local_dir if local_dir is not None else BEASTMASTER_DATA_DIR) / filename
    try:
        with path.open(encoding="utf-8-sig") as source:
            data = json.load(source)
    except FileNotFoundError:
        from ffxiv_aku import loadDataTheQuickestWay
        data = loadDataTheQuickestWay(filename, translate=False)

    if not isinstance(data, dict):
        raise ValueError(f"Expected an object in Beastmaster sheet {filename}")
    return data


def reference_id(value):
    if isinstance(value, dict):
        value = value.get("row_id", value.get("value", "0"))
    return str(value or "0")


def german_name(row):
    return str(row.get("Name_de") or row.get("Name") or "").strip()


def build_borrow_action(beast_number: int) -> dict:
    classification = BEAST_CLASSIFICATION_BY_NUMBER.get(beast_number)
    if not classification:
        raise ValueError(f"Missing Borgen classification for beast #{beast_number}")

    source = BORROW_ACTION_BY_CLASSIFICATION[classification]
    return {
        "classification": classification,
        "title": dict(source["title"]),
        "description": dict(source["description"]),
    }


def build_beastmaster_job_skills(actions, descriptions):
    """Read player BST actions directly instead of the pre-release placeholder."""
    result = {}
    languages = ("de", "en", "fr", "ja")

    for key, row in actions.items():
        if reference_id(row.get("ClassJob")) != "43" or str(row.get("IsPvP")).lower() == "true":
            continue
        if str(row.get("IsPlayerAction")).lower() != "true":
            continue

        category = row.get("ActionCategory", {})
        result[str(key)] = {
            "Id": str(key),
            "Name": {lang: row.get(f"Name_{lang}", "") for lang in languages},
            "Description": {
                lang: descriptions.get(str(key), {})
                    .get(f"Description_{lang}", "")
                    .replace("\\n", "\n")
                    .replace("\n", "</br>")
                for lang in languages
            },
            "Kategorie": {lang: category.get(f"Name_{lang}", "") for lang in languages},
            "Level": str(row.get("ClassJobLevel", "0")),
            "Icon": row.get("Icon", {}).get("path_hr1", ""),
            "Type": "GCD" if reference_id(category) in ("2", "3") else "oGCD",
            "Range": f"{row.get('Range', '0')}y",
            "EffectRange": f"{row.get('EffectRange', '0')}y",
            "Cast": f"{int(row.get('Cast100ms', 0)) / 10:g}s",
            "Recast": f"{int(row.get('Recast100ms', 0)) / 10:g}s",
            "Cost": str(row.get("PrimaryCostValue", "0")),
            "SecondaryCostType": str(row.get("SecondaryCostType", "0")),
            "IsDamageSkill": False,
            "IsHealingSkill": False,
            "IsShieldSkill": False,
            "MitigationType": None,
            "MitigationValue": None,
        }

    if not result:
        raise ValueError("Action sheet contains no Beastmaster player skills")
    return result


def build_pet_attacks(pet, descriptions):
    attacks = []
    seen = set()

    for ability in pet.get("Abilities", []):
        action_id = reference_id(ability)
        name = german_name(ability)
        if action_id == "0" or action_id in seen or not name:
            continue

        seen.add(action_id)
        description = (
            descriptions.get(action_id, {}).get("Description_de")
            or descriptions.get(action_id, {}).get("Description", "")
        ).replace("\\n", "\n")

        attacks.append({
            "title_id": action_id,
            "title": {"de": name, "en": name},
            "icon": (
                ability.get("Icon", {})
                .get("path_hr1", "")
                .replace("ui/icon/", "")
                .replace(".tex", ".webp")
            ),
            "description": {
                "de": escape(description).replace("\n", "<br>"),
                "en": escape(description).replace("\n", "<br>"),
            },
            "range": f"{ability.get('Range', '0')}y",
            "effectrange": f"{ability.get('EffectRange', '0')}y",
            "cast": f"{int(ability.get('Cast100ms', 0)) / 10:g}s",
            "recast": f"{int(ability.get('Recast100ms', 0)) / 10:g}s",
            "kategorie": german_name(ability.get("ActionCategory", {})),
        })

    return attacks


def build_capture_list(xbm_pets, pets, places, duties, logs, descriptions=None):
    """Build all captured-beast data used by the Beastmaster post."""
    zones = {
        name.strip().casefold(): enemies
        for name, enemies in logs.items()
        if name and isinstance(enemies, dict) and name != "Klassen"
    }

    result = []

    for key, row in sorted(xbm_pets.items(), key=lambda item: int(item[0])):
        beast_number = int(key)
        pet_id = reference_id(row.get("Pet"))
        if pet_id == "0":
            continue

        pet = dict(pets.get(pet_id, {}))
        if isinstance(row.get("Pet"), dict):
            pet.update(row["Pet"])

        name = german_name(pet)
        if not name:
            raise ValueError(f"Missing name for XBMPet {key}, Pet {pet_id}")

        ref = row.get("Location", {})
        location_id = reference_id(ref)
        sheet = ref.get("sheet", "") if isinstance(ref, dict) else ""

        if location_id != "0" and sheet not in ("PlaceName", "ContentFinderCondition"):
            raise ValueError(f"Unsupported location sheet for XBMPet {key}: {sheet}")

        location = dict((places if sheet == "PlaceName" else duties).get(location_id, {}))
        if isinstance(ref, dict):
            location.update(ref)

        location_name = german_name(location) if location_id != "0" else ""
        if location_id != "0" and not location_name:
            raise ValueError(f"Missing location for XBMPet {key}: {sheet} {location_id}")

        pattern = re.compile(
            r"(?<!\w)" + re.escape(name) + r"(?!\w)",
            re.IGNORECASE,
        )

        sightings = []
        for enemy_name, enemy in zones.get(location_name.casefold(), {}).items():
            if not isinstance(enemy, dict) or not enemy.get("id") or not pattern.search(enemy_name):
                continue

            ids = enemy["id"] if isinstance(enemy["id"], list) else [enemy["id"]]
            sightings.append({
                "name": enemy_name,
                "enemy_ids": sorted({str(i) for i in ids}),
            })

        result.append({
            "number": beast_number,
            "pet_id": pet_id,
            "name": name,
            "description": row.get("Unknown0", ""),
            "icon": (
                f"{int(row.get('Unknown3', 0)) // 1000 * 1000:06d}/"
                f"{int(row.get('Unknown3', 0)):06d}_hr1.webp"
                if row.get("Unknown3")
                else ""
            ),
            "attacks": build_pet_attacks(pet, descriptions or {}),
            "borrow": build_borrow_action(beast_number),
            "location": location_name,
            "location_type": (
                "Inhalt"
                if sheet == "ContentFinderCondition"
                else "Gebiet"
                if location_name
                else ""
            ),
            "sightings": sorted(
                sightings,
                key=lambda entry: entry["name"].casefold(),
            ),
        })

    if not result:
        raise ValueError("XBMPet contains no populated beasts")
    return result


def yaml_scalar(value) -> str:
    """Return a JSON-quoted scalar; JSON strings are valid YAML scalars."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def yaml_lines(value, indent=0):
    """Tiny deterministic YAML writer for dict/list/scalar generated data."""
    pad = " " * indent

    if isinstance(value, dict):
        lines = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.extend(yaml_lines(child, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(child)}")
        return lines

    if isinstance(value, list):
        lines = []
        for child in value:
            if isinstance(child, dict):
                items = list(child.items())
                if not items:
                    lines.append(f"{pad}- {{}}")
                    continue

                first_key, first_value = items[0]
                if isinstance(first_value, (dict, list)):
                    lines.append(f"{pad}- {first_key}:")
                    lines.extend(yaml_lines(first_value, indent + 4))
                else:
                    lines.append(f"{pad}- {first_key}: {yaml_scalar(first_value)}")

                for key, item_value in items[1:]:
                    if isinstance(item_value, (dict, list)):
                        lines.append(f"{pad}  {key}:")
                        lines.extend(yaml_lines(item_value, indent + 4))
                    else:
                        lines.append(f"{pad}  {key}: {yaml_scalar(item_value)}")
            elif isinstance(child, list):
                lines.append(f"{pad}-")
                lines.extend(yaml_lines(child, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(child)}")
        return lines

    return [f"{pad}{yaml_scalar(value)}"]


def beastmaster_post_path(root: Path) -> Path:
    candidates = sorted(
        (root / "_posts" / "klassen_und_jobs").glob("*Bestienbändiger.md")
    )

    if len(candidates) != 1:
        raise RuntimeError(
            "Expected exactly one generated Bestienbändiger post in "
            "_posts/klassen_und_jobs, found "
            f"{len(candidates)}"
        )

    return candidates[0]


def replace_generated_beasts(frontmatter: str, entries: list[dict]) -> str:
    """Replace the generator-owned `beasts:` block in YAML frontmatter.

    The block is always appended at root level. Because it is generated after
    addKlassJobs(), no hand-maintained Beastmaster data needs to survive here.
    """
    # Remove a previous generated root-level beasts block if present.
    match = re.search(r"(?m)^beasts:\s*$", frontmatter)
    if match:
        start = match.start()
        next_root = re.search(
            r"(?m)^(?![ \t#-])(?:[A-Za-z_][A-Za-z0-9_-]*):",
            frontmatter[match.end():],
        )
        if next_root:
            end = match.end() + next_root.start()
            frontmatter = frontmatter[:start] + frontmatter[end:]
        else:
            frontmatter = frontmatter[:start].rstrip() + "\n"

    block = "beasts:\n" + "\n".join(yaml_lines(entries, 2)) + "\n"
    return frontmatter.rstrip() + "\n" + block


def write_beasts_into_generated_post(root: Path, entries: list[dict]) -> Path:
    """Store generated beast data inside the Beastmaster post frontmatter."""
    post = beastmaster_post_path(root)
    content = post.read_text(encoding="utf-8")

    if not content.startswith("---"):
        raise RuntimeError(f"{post} has no YAML frontmatter")

    closing = content.find("\n---", 3)
    if closing == -1:
        raise RuntimeError(f"{post} has no closing YAML frontmatter delimiter")

    frontmatter = content[4:closing]
    body = content[closing + 4:]

    new_frontmatter = replace_generated_beasts(frontmatter, entries)

    post.write_text(
        "---\n" + new_frontmatter + "---" + body,
        encoding="utf-8",
    )

    return post


def generate_capture_data(root, *, support_dir=None, logs=None):
    """Generate Beastmaster data and embed it into the generated class post.

    No _data/beastmaster.json is created.
    """
    root = Path(root)

    def support(name):
        if support_dir is not None:
            return json.loads(
                (Path(support_dir) / name).read_text(encoding="utf-8-sig")
            )
        return load_beastmaster_data(
            name,
            local_dir=root / "tmp" / "Bestienbändiger_Files",
        )

    xbm_pets = load_beastmaster_data(
        "XBMPet.json",
        local_dir=root / "tmp" / "Bestienbändiger_Files",
    )

    if logs is None:
        if support_dir is not None:
            logs = support("logdata_de_minified.json")
        else:
            from ffxiv_aku import get_any_Logdata
            logs = get_any_Logdata()

    entries = build_capture_list(
        xbm_pets,
        support("Pet.json"),
        support("PlaceName.json"),
        support("ContentFinderCondition.json"),
        logs,
        support("ActionTransient.json"),
    )

    post = write_beasts_into_generated_post(root, entries)

    # Remove obsolete generated files from the previous architecture.
    for obsolete in (
        root / "_data" / "beastmaster.json",
        root / "_data" / "beastmaster_borrow.json",
    ):
        if obsolete.exists():
            obsolete.unlink()

    return entries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Beastmaster post data"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--support-dir",
        type=Path,
    )
    args = parser.parse_args()

    entries = generate_capture_data(
        args.root,
        support_dir=args.support_dir,
    )

    print(
        f"Generated {len(entries)} beasts inside "
        "_posts/klassen_und_jobs/Bestienbändiger post"
    )
