"""Beastmaster sheet loading, isolated from the other job data loaders."""

import json
import re
from html import escape
from pathlib import Path


BEASTMASTER_DATA_DIR = Path(__file__).resolve().parents[2] / "tmp" / "Bestienbändiger_Files"


def load_beastmaster_data(filename: str, *, local_dir: Path | None = None) -> dict:
    """Prefer a local Beastmaster export; use the raw server sheet when absent.

    Blank/zero-filled exports remain authoritative when present. Invalid JSON
    raises an error instead of silently substituting a different data version.
    """
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
            "Id": str(key), "Name": {lang: row.get(f"Name_{lang}", "") for lang in languages},
            "Description": {lang: descriptions.get(str(key), {}).get(f"Description_{lang}", "").replace("\\n", "\n").replace("\n", "</br>") for lang in languages},
            "Kategorie": {lang: category.get(f"Name_{lang}", "") for lang in languages},
            "Level": str(row.get("ClassJobLevel", "0")),
            "Icon": row.get("Icon", {}).get("path_hr1", ""),
            "Type": "GCD" if reference_id(category) in ("2", "3") else "oGCD",
            "Range": f"{row.get('Range', '0')}y", "EffectRange": f"{row.get('EffectRange', '0')}y",
            "Cast": f"{int(row.get('Cast100ms', 0)) / 10:g}s",
            "Recast": f"{int(row.get('Recast100ms', 0)) / 10:g}s",
            "Cost": str(row.get("PrimaryCostValue", "0")),
            "SecondaryCostType": str(row.get("SecondaryCostType", "0")),
            "IsDamageSkill": False, "IsHealingSkill": False, "IsShieldSkill": False,
            "MitigationType": None, "MitigationValue": None,
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
        description = descriptions.get(action_id, {}).get("Description_de") or descriptions.get(action_id, {}).get("Description", "")
        description = description.replace("\\n", "\n")
        attacks.append({
            "title_id": action_id, "title": {"de": name, "en": name},
            "icon": ability.get("Icon", {}).get("path_hr1", "").replace("ui/icon/", "").replace(".tex", ".webp"),
            "description": {"de": escape(description).replace("\n", "<br>"), "en": escape(description).replace("\n", "<br>")},
            "range": f"{ability.get('Range', '0')}y",
            "effectrange": f"{ability.get('EffectRange', '0')}y",
            "cast": f"{int(ability.get('Cast100ms', 0)) / 10:g}s",
            "recast": f"{int(ability.get('Recast100ms', 0)) / 10:g}s",
            "kategorie": german_name(ability.get("ActionCategory", {})),
        })
    return attacks


def build_capture_list(xbm_pets, pets, places, duties, logs, descriptions=None):
    """Join the pet book to its hints and conservative name matches in logs.

    Pet ids are NOT BNpcName ids. Log matches are only sightings, never proof
    of capture eligibility. Only match within the sheet's location hint, and
    use word boundaries so Puk cannot match Spukgespenst.
    """
    zones = {name.strip().casefold(): enemies for name, enemies in logs.items()
             if name and isinstance(enemies, dict) and name != "Klassen"}
    result = []
    for key, row in sorted(xbm_pets.items(), key=lambda item: int(item[0])):
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
        pattern = re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)", re.IGNORECASE)
        sightings = []
        for enemy_name, enemy in zones.get(location_name.casefold(), {}).items():
            if not isinstance(enemy, dict) or not enemy.get("id") or not pattern.search(enemy_name):
                continue
            ids = enemy["id"] if isinstance(enemy["id"], list) else [enemy["id"]]
            sightings.append({"name": enemy_name, "enemy_ids": sorted({str(i) for i in ids})})
        result.append({
            "number": int(key), "pet_id": pet_id, "name": name,
            "description": row.get("Unknown0", ""),
            "icon": f"{int(row.get('Unknown3', 0)) // 1000 * 1000:06d}/{int(row.get('Unknown3', 0)):06d}_hr1.webp" if row.get("Unknown3") else "",
            "attacks": build_pet_attacks(pet, descriptions or {}),
            "location": location_name,
            "location_type": "Inhalt" if sheet == "ContentFinderCondition" else "Gebiet" if location_name else "",
            "sightings": sorted(sightings, key=lambda entry: entry["name"].casefold()),
        })
    if not result:
        raise ValueError("XBMPet contains no populated beasts; keeping the existing capture list")
    return result


def generate_capture_data(root, *, support_dir=None, logs=None):
    """Generate Jekyll data. support_dir permits rebuilding from saved sheets."""
    root = Path(root)
    def support(name):
        if support_dir is not None:
            return json.loads((Path(support_dir) / name).read_text(encoding="utf-8-sig"))
        return load_beastmaster_data(name, local_dir=root / "tmp" / "Bestienbändiger_Files")
    xbm_pets = load_beastmaster_data("XBMPet.json", local_dir=root / "tmp" / "Bestienbändiger_Files")
    if logs is None:
        if support_dir is not None:
            logs = support("logdata_de_minified.json")
        else:
            from ffxiv_aku import get_any_Logdata
            logs = get_any_Logdata()
    entries = build_capture_list(xbm_pets, support("Pet.json"), support("PlaceName.json"),
                                 support("ContentFinderCondition.json"), logs, support("ActionTransient.json"))
    target = root / "_data" / "beastmaster.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entries


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build the Beastmaster capture list")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--support-dir", type=Path, help="Saved Pet, PlaceName, ContentFinderCondition, ActionTransient and logdata_de_minified JSON files")
    args = parser.parse_args()
    entries = generate_capture_data(args.root, support_dir=args.support_dir)
    print(f"Generated {len(entries)} beasts, {sum(bool(e['sightings']) for e in entries)} with matching log sightings")
