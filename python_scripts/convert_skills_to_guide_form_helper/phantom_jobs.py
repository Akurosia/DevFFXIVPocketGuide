from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ffxiv_aku import loadDataTheQuickestWay, storeFilesInTmp

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from python_scripts.convert_skills_to_guide_form_helper.helper import (
        LANGUAGES,
        LANGUAGES_MAPPING,
        deal_with_extras_in_text,
        getImage,
    )
else:
    from .helper import LANGUAGES, LANGUAGES_MAPPING, deal_with_extras_in_text, getImage


PHANTOM_BLUE_MAGE_JOB_ID = "21"
PHANTOM_BLUE_EXTRA_ACTIONS = {
    "49089": 2,  # Occult Aero II replaces Occult Aero after it is learned.
    "49091": 3,  # Occult Aero III replaces Occult Aero II after it is learned.
}

# The game sheets expose the player actions and enemy actions separately, but do
# not contain a relation between the two. These stable row IDs are the missing
# spellbook relation. Names are still resolved from localized game data.
PHANTOM_BLUE_LOCATIONS: dict[str, dict[str, Any]] = {
    "49085": {"kind": "initial"},
    "49086": {"kind": "critical_encounter", "event_id": "59", "enemy_id": "14714"},
    "49087": {"kind": "monster", "enemy_id": "14922", "knowledge_level": 29},
    "49088": {"kind": "monster", "enemy_id": "14860", "knowledge_level": 22},
    "49089": {"kind": "monster", "enemy_id": "14905", "knowledge_level": 32},
    "49090": {"kind": "monster", "enemy_id": "14923", "knowledge_level": 42},
    "49091": {"kind": "critical_encounter", "event_id": "51", "enemy_id": "14509"},
}

PAGE_TITLES = {
    "de": "Phantom-Job",
    "en": "Phantom Job",
    "fr": "Job fantôme",
    "ja": "サポートジョブ",
}
OCCULT_CRESCENT_NAMES = {
    "de": "Kreszentia",
    "en": "Occult Crescent",
    "fr": "Île de Lunule",
    "ja": "クレセントアイル",
}
LOCATION_HEADERS = {
    "de": ("Fundort", "Gegner", "Bedingung"),
    "en": ("Location", "Enemy", "Requirement"),
    "fr": ("Lieu", "Ennemi", "Condition"),
    "ja": ("場所", "敵", "条件"),
}
INITIAL_UNLOCK_TEXT = {
    "de": "Startkommando beim Freischalten des Phantom-Blaumagiers",
    "en": "Starting action when Phantom Blue Mage is unlocked",
    "fr": "Action initiale obtenue avec le job de Mage bleu fantôme",
    "ja": "サポート青魔道士の修得時から使用可能",
}
LEARNING_TEXT = {
    "de": "Kommando sehen und anschließend den Gegner besiegen",
    "en": "Witness the action, then defeat the enemy",
    "fr": "Voir l'action, puis vaincre l'ennemi",
    "ja": "技を見た後に敵を倒す",
}
KNOWLEDGE_LEVEL_TEXT = {
    "de": "Wissensstufe {level}",
    "en": "Knowledge level {level}",
    "fr": "Niveau de savoir {level}",
    "ja": "知識レベル{level}",
}
PATCH_METADATA = {
    "7.25": {"date": "2025.05.27", "job_ids": set(range(0, 13))},
    "7.4": {"date": "2025.12.16", "job_ids": {13, 14, 15}},
    "7.55": {"date": "2026.07.28", "job_ids": set(range(16, 24))},
}


def _numeric_key(value: Any) -> tuple[int, int | str]:
    text = str(value).split(".")[0]
    return (0, int(text)) if text.isdigit() else (1, str(value))


def _yaml_quote(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def find_mkd_data_dir(explicit: str | os.PathLike[str] | None = None) -> Path:
    candidates = [
        explicit,
        os.environ.get("FFXIV_MKD_DATA_DIR"),
        r"N:\ff14.akurosiakamo.de\extras\json\xivapi_data2",
        r"P:\extras\json\xivapi_data2",
        "/var/www/ffxiv/extras/json/xivapi_data2",
        "/Volumes/FFXIV/extras/json/xivapi_data2",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if (path / "MKDSupportJob.json").is_file() and (path / "MKDTrait.json").is_file():
            return path
    raise FileNotFoundError(
        "Could not find MKDSupportJob.json and MKDTrait.json. "
        "Pass mkd_data_dir or set FFXIV_MKD_DATA_DIR."
    )


def _localized_value(data: dict[str, Any], field: str, lang: str) -> str:
    return str(data.get(f"{field}_{lang}", data.get(field, "")) or "")


def _localized_bnpc_name(data: dict[str, Any], lang: str) -> str:
    name = _localized_value(data, "Singular", lang).replace("[p]", "")
    if lang == "de":
        pronoun = str(data.get("Pronoun", "0"))
        name = name.replace("[a]", {"0": "er", "1": "e", "2": "es"}.get(pronoun, ""))
        name = name.replace("[t]", {"0": "Der", "1": "Die", "2": "Das"}.get(pronoun, ""))
    return name.replace("[a]", "").replace("[t]", "")


def _patch_metadata(job_id: str) -> tuple[str, str]:
    numeric_id = int(job_id)
    for patch, metadata in PATCH_METADATA.items():
        if numeric_id in metadata["job_ids"]:
            return patch, str(metadata["date"])
    return "7.25", "2025.05.27"


def _load_remote_trait_localizations() -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {}
    endpoint = "https://v2.xivapi.com/api/sheet/MKDTrait"
    for lang in LANGUAGES:
        query = urlencode({
            "limit": 100,
            "fields": "Name,Description",
            "language": lang,
        })
        request = Request(
            f"{endpoint}?{query}",
            headers={"User-Agent": "DevFFXIVPocketGuide/1.0"},
        )
        with urlopen(request, timeout=15) as response:
            rows = json.load(response)["rows"]
        for row in rows:
            row_id = str(row["row_id"])
            fields = row["fields"]
            result.setdefault(row_id, {})[lang] = {
                "Name": str(fields.get("Name", "") or ""),
                "Description": str(fields.get("Description", "") or ""),
            }
    return result


def load_trait_localizations(
    mkd_data_dir: Path,
    traits: dict[str, Any],
    allow_remote: bool = True,
) -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {}
    localized_path = mkd_data_dir.parent / "xivapi_data" / "MKDTrait.json"
    if localized_path.is_file():
        localized_traits = _read_json(localized_path)
        for row_id, trait in localized_traits.items():
            for lang in LANGUAGES:
                result.setdefault(str(row_id), {})[lang] = {
                    "Name": _localized_value(trait, "Name", lang),
                    "Description": _localized_value(trait, "Description", lang),
                }
    elif allow_remote:
        try:
            result = _load_remote_trait_localizations()
        except Exception as error:
            raise RuntimeError(
                "Could not load localized MKDTrait text from XIVAPI. "
                "Export a localized xivapi_data/MKDTrait.json or use "
                "--no-remote-localization for the German-only fallback."
            ) from error

    for row_id, trait in traits.items():
        for lang in LANGUAGES:
            result.setdefault(str(row_id), {}).setdefault(lang, {
                "Name": str(trait.get("Name", "") or ""),
                "Description": str(trait.get("Description", "") or ""),
            })
    return result


def _format_seconds(value: Any) -> str:
    try:
        return f"{int(value) / 10:.1f}s"
    except (TypeError, ValueError):
        return "0.0s"


def _format_yalms(value: Any) -> str:
    return f"{value or 0}y"


def _get_action_names(action: dict[str, Any]) -> dict[str, str]:
    return {
        lang: deal_with_extras_in_text(_localized_value(action, "Name", lang))
        for lang in LANGUAGES
    }


def _get_action_descriptions(
    action_id: str,
    action_transient: dict[str, Any],
) -> dict[str, str]:
    transient = action_transient.get(action_id, {})
    return {
        lang: deal_with_extras_in_text(_localized_value(transient, "Description", lang))
        for lang in LANGUAGES
    }


def _build_location_table(
    action_id: str,
    lang: str,
    bnpc_names: dict[str, Any],
    dynamic_events: dict[str, Any],
    content_finder: dict[str, Any],
) -> str:
    location = PHANTOM_BLUE_LOCATIONS.get(action_id)
    if not location:
        return ""

    headers = LOCATION_HEADERS[lang]
    table = (
        "<br/>#########################################<br/>"
        f"<br/>LOCATIONS:<table class='table-striped table-dark table-hover "
        "bg-charcoal text-light border-gold-metallic'><thead><td>"
        f"{headers[0]}</td><td>{headers[1]}</td><td>{headers[2]}</td></thead><tbody>"
    )
    if location["kind"] == "initial":
        page_name = PAGE_TITLES[lang]
        return (
            table
            + f"<tr><td>{OCCULT_CRESCENT_NAMES[lang]}</td><td>{page_name}</td>"
            + f"<td>{INITIAL_UNLOCK_TEXT[lang]}</td></tr></tbody></table>"
        )

    zone = _localized_value(content_finder.get("1093", {}), "Name", lang)
    enemy = _localized_bnpc_name(bnpc_names.get(str(location["enemy_id"]), {}), lang)
    source = zone
    if location["kind"] == "critical_encounter":
        event = _localized_value(dynamic_events.get(str(location["event_id"]), {}), "Name", lang)
        source = f"{zone} — {event}"

    requirement = LEARNING_TEXT[lang]
    if location.get("knowledge_level"):
        level_text = KNOWLEDGE_LEVEL_TEXT[lang].format(level=location["knowledge_level"])
        requirement = f"{level_text}; {requirement}"
    return (
        table
        + f"<tr><td>{source}</td><td>{enemy}</td><td>{requirement}</td></tr>"
        + "</tbody></table>"
    )


def _action_level(job_id: str, index: int, job: dict[str, Any], action_id: str) -> int:
    if action_id in PHANTOM_BLUE_EXTRA_ACTIONS:
        return PHANTOM_BLUE_EXTRA_ACTIONS[action_id]
    levels = job.get("LevelUnlock", [])
    try:
        return int(levels[index])
    except (IndexError, TypeError, ValueError):
        return 0


def _job_actions(job_id: str, job: dict[str, Any]) -> list[tuple[int, str]]:
    actions: list[tuple[int, str]] = []
    for index, action_ref in enumerate(job.get("Action", [])):
        action_id = str(action_ref.get("row_id", action_ref.get("value", "0")))
        if action_id != "0":
            actions.append((index, action_id))
    if job_id == PHANTOM_BLUE_MAGE_JOB_ID:
        actions.extend((len(actions) + offset, action_id) for offset, action_id in enumerate(PHANTOM_BLUE_EXTRA_ACTIONS))
    return sorted(
        actions,
        key=lambda item: (
            _action_level(job_id, item[0], job, item[1]),
            _numeric_key(item[1]),
        ),
    )


def _add_actions(
    job_id: str,
    job: dict[str, Any],
    actions: dict[str, Any],
    action_transient: dict[str, Any],
    bnpc_names: dict[str, Any],
    dynamic_events: dict[str, Any],
    content_finder: dict[str, Any],
    translations: dict[str, dict[str, str]],
) -> str:
    result = "    attacks:\n"
    for index, action_id in _job_actions(job_id, job):
        action = actions.get(action_id, {})
        if not action:
            print(f"Missing Action row {action_id} for {job.get('Name', job_id)}")
            continue
        names = _get_action_names(action)
        descriptions = _get_action_descriptions(action_id, action_transient)
        level = _action_level(job_id, index, job, action_id)
        category = action.get("ActionCategory", {})
        category_id = str(category.get("row_id", category.get("value", "0")))
        action_type = "oGCD" if category_id == "4" else "GCD"

        result += "      - title:\n"
        for lang in LANGUAGES:
            result += f'          {lang}: "{_yaml_quote(names[lang])}"\n'
            translations[lang][f"Class_Skill_Name_{names['en']}"] = names[lang]
        result += f'        title_id: "{action_id}"\n'
        result += f'        level: "{level}"\n'
        result += f'        type: "{action_type}"\n'
        result += f'        icon: "{getImage(action.get("Icon", {}))}"\n'
        result += f'        range: "{_format_yalms(action.get("Range"))}"\n'
        result += f'        effectrange: "{_format_yalms(action.get("EffectRange"))}"\n'
        result += f'        cast: "{_format_seconds(action.get("Cast100ms"))}"\n'
        result += f'        cost: "{action.get("PrimaryCostValue", 0)}"\n'
        result += f'        recast: "{_format_seconds(action.get("Recast100ms"))}"\n'
        result += f'        secondarycost: "{action.get("SecondaryCostType", 0)}"\n'
        result += f'        kategorie: "{_yaml_quote(_localized_value(category, "Name", "de"))}"\n'
        result += "        description:\n"
        for lang in LANGUAGES:
            description = descriptions[lang]
            if job_id == PHANTOM_BLUE_MAGE_JOB_ID:
                description += _build_location_table(
                    action_id, lang, bnpc_names, dynamic_events, content_finder
                )
            result += f'          {lang}: "{_yaml_quote(description)}"\n'
            translations[lang][f"Class_Skill_Desc_{names['en']}"] = description
        result += "        phases:\n"
        result += '          - phase: "01"\n'
    return result


def _add_traits(
    job_id: str,
    traits: dict[str, Any],
    trait_localizations: dict[str, dict[str, dict[str, str]]],
    translations: dict[str, dict[str, str]],
) -> str:
    job_traits = [
        (row_id, trait)
        for row_id, trait in traits.items()
        if str(trait.get("MKDSupportJob", {}).get("row_id", "")) == job_id
        and str(trait.get("Name", "")).strip()
    ]
    if not job_traits:
        return ""

    result = "    traits:\n"
    for row_id, trait in sorted(
        job_traits,
        key=lambda item: (int(item[1].get("LevelUnlock", 0)), _numeric_key(item[0])),
    ):
        localized = trait_localizations[str(row_id)]
        result += "      - title:\n"
        for lang in LANGUAGES:
            name = deal_with_extras_in_text(localized[lang]["Name"])
            result += f'          {lang}: "{_yaml_quote(name)}"\n'
            translations[lang][f"Class_Trait_Name_{localized['en']['Name']}"] = name
        result += f'        title_id: "mkd-trait-{row_id}"\n'
        result += f'        level: "{trait.get("LevelUnlock", 0)}"\n'
        result += f'        icon: "{getImage(trait.get("Icon", {}))}"\n'
        result += "        description:\n"
        for lang in LANGUAGES:
            description = deal_with_extras_in_text(localized[lang]["Description"])
            result += f'          {lang}: "{_yaml_quote(description)}"\n'
            translations[lang][f"Class_Trait_Desc_{localized['en']['Name']}"] = description
        result += "        phases:\n"
        result += '          - phase: "02"\n'
    return result

name_to_icon = {
    "Phantom-Freiberufler": "/216000/216871_hr1.webp",
    "Phantom-Ritter": "/216000/216872_hr1.webp",
    "Phantom-Berserker": "/216000/216873_hr1.webp",
    "Phantom-Mönch": "/216000/216874_hr1.webp",
    "Phantom-Jäger": "/216000/216875_hr1.webp",
    "Phantom-Samurai": "/216000/216876_hr1.webp",
    "Phantom-Barde": "/216000/216877_hr1.webp",
    "Phantom-Geomant": "/216000/216878_hr1.webp",
    "Phantom-Zeitmagier": "/216000/216879_hr1.webp",
    "Phantom-Grenadier": "/216000/216880_hr1.webp",
    "Phantom-Alchemist": "/216000/216881_hr1.webp",
    "Phantom-Seher": "/216000/216882_hr1.webp",
    "Phantom-Dieb": "/216000/216883_hr1.webp",
    "Phantom-Paladin": "/216000/216884_hr1.webp",
    "Phantom-Gladiator": "/216000/216885_hr1.webp",
    "Phantom-Tänzer": "/216000/216886_hr1.webp",
    "Phantom-Ninja": "/216000/216887_hr1.webp",
    "Phantom-Weißmagier": "/216000/216888_hr1.webp",
    "Phantom-Schwarzmagier": "/216000/216889_hr1.webp",
    "Phantom-Dragoon": "/216000/216890_hr1.webp",
    "Phantom-Beschwörer": "/216000/216891_hr1.webp",
    "Phantom-Blaumagier": "/216000/216892_hr1.webp",
    "Phantom-Rotmagier": "/216000/216893_hr1.webp",
    "Phantom-Nekromant": "/216000/216894_hr1.webp",
}

def _build_page(
    job_id: str,
    job: dict[str, Any],
    localized_job: dict[str, Any],
    traits: dict[str, Any],
    trait_localizations: dict[str, dict[str, dict[str, str]]],
    actions: dict[str, Any],
    action_transient: dict[str, Any],
    bnpc_names: dict[str, Any],
    dynamic_events: dict[str, Any],
    content_finder: dict[str, Any],
    klass_translations: dict[str, dict[str, str]],
) -> tuple[str, dict[str, dict[str, str]], str]:
    names = {
        lang: _localized_value(localized_job, "Name", lang) or str(job.get("Name", ""))
        for lang in LANGUAGES
    }
    english_name = names["en"]
    slug_name = english_name.lower()
    translations: dict[str, dict[str, str]] = {lang: {} for lang in LANGUAGES}
    first_action = next((actions.get(action_id, {}) for _, action_id in _job_actions(job_id, job)), {})
    icon = name_to_icon[names["de"]]
    max_level = int(job.get("LevelMax", 0) or 0)
    patch_number, release_date = _patch_metadata(job_id)

    page = "---\n"
    page += 'wip: "True"\n'
    page += "title:\n"
    for lang in LANGUAGES:
        page += f'  {lang}: "{_yaml_quote(names[lang])}"\n'
        klass_translations[lang][f"Sidebar_Title_Full_{english_name}"] = names[lang]
        klass_translations[lang][f"Content_Title_{english_name}"] = names[lang]
        translations[lang][f"Content_Title_{english_name}"] = names[lang]
    page += "layout: klassen\n"
    page += "page_type: guide\n"
    page += 'roletypeinparty: "Phantom Job"\n'
    for lang in LANGUAGES:
        klass_translations[lang]["Sidebar_Role_Phantom Job"] = PAGE_TITLES[lang]
    page += 'categories: "klassenjobs"\n'
    page += 'difficulty: "Normal"\n'
    page += 'instanceType: "klassenjobs"\n'
    page += f'date: "{release_date}"\n'
    page += f'patchNumber: "{patch_number}"\n'
    page += 'patchName: "Dawntrail"\n'
    page += 'expac: "dt"\n'
    page += f'slug: "klassen_und_jobs_{slug_name.replace(" ", "_")}"\n'
    if icon:
        page += f'jobicon: "{icon}"\n'
    phantom_icon = names["de"].removeprefix("Phantom-").lower()
    page += f'phantomicon: "{_yaml_quote(phantom_icon)}"\n'
    page += "extraicons:\n"
    page += "terms:\n"
    for term in ["Klassen", "Jobs", "Skills", "Traits", "Phantom Jobs", "Occult Crescent"]:
        page += f'    - term: "{term}"\n'
    for lang in LANGUAGES:
        page += f'    - term: "{_yaml_quote(names[lang])}"\n'
        page += f'    - term: "{_yaml_quote(OCCULT_CRESCENT_NAMES[lang])}"\n'
    sort_id = 100 + int(job.get("JobIndex", job_id) or 0)
    page += f"sortid: {sort_id}\n"
    page += f"order: {sort_id}\n"
    page += f"plvl: {max_level}\n"
    english_short_name = english_name.replace("Phantom ", "Ph. ", 1)
    page += f'abbreviations: "{_yaml_quote(english_short_name)}"\n'
    page += "bosses:\n"
    page += f'  - title: "{_yaml_quote(english_name)}"\n'
    page += f'    id: "phantom-job-{job_id}"\n'
    page += _add_actions(
        job_id,
        job,
        actions,
        action_transient,
        bnpc_names,
        dynamic_events,
        content_finder,
        translations,
    )
    trait_text = _add_traits(job_id, traits, trait_localizations, translations)
    page += trait_text
    page += "    sequence:\n"
    page += '      - phase: "01"\n'
    page += '        name: "Skills"\n'
    if trait_text:
        page += '      - phase: "02"\n'
        page += '        name: "Traits"\n'
    page += "---\n"
    return page, translations, slug_name


def _write_if_changed(path: Path, content: str) -> None:
    old_content = path.read_text(encoding="utf-8") if path.is_file() else None
    if old_content != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _write_translations(
    repo_root: Path,
    translations: dict[str, dict[str, str]],
    slug_name: str,
) -> None:
    directory = repo_root / "assets" / "translations" / "klassen" / slug_name
    for lang in LANGUAGES:
        path = directory / f"{LANGUAGES_MAPPING[lang]}.json"
        content = json.dumps(
            translations[lang],
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"
        _write_if_changed(path, content)


def addPhantomJobs(
    main_script: str | os.PathLike[str],
    actions: dict[str, Any],
    action_transient: dict[str, Any],
    klass_translations: dict[str, dict[str, str]],
    mkd_data_dir: str | os.PathLike[str] | None = None,
    allow_remote_localization: bool = True,
    translation_callback: Callable[[dict[str, dict[str, str]], str], None] | None = None,
) -> list[Path]:
    repo_root = Path(main_script)
    source_dir = find_mkd_data_dir(mkd_data_dir)
    support_jobs = _read_json(source_dir / "MKDSupportJob.json")
    traits = _read_json(source_dir / "MKDTrait.json")
    trait_localizations = load_trait_localizations(
        source_dir, traits, allow_remote=allow_remote_localization
    )

    storeFilesInTmp(False)
    localized_jobs = loadDataTheQuickestWay("MKDSupportJob.json")
    bnpc_names = loadDataTheQuickestWay("BNpcName.json")
    dynamic_events = loadDataTheQuickestWay("DynamicEvent.json")
    content_finder = loadDataTheQuickestWay("ContentFinderCondition.json")

    written: list[Path] = []
    for job_id, job in sorted(
        support_jobs.items(),
        key=lambda item: int(item[1].get("JobIndex", item[0]) or 0),
    ):
        localized_job = localized_jobs.get(str(job_id), {})
        page, translations, slug_name = _build_page(
            str(job_id),
            job,
            localized_job,
            traits,
            trait_localizations,
            actions,
            action_transient,
            bnpc_names,
            dynamic_events,
            content_finder,
            klass_translations,
        )
        safe_name = str(job.get("Name", f"Phantom-Job-{job_id}")).replace("/", "-")
        patch_number, release_date = _patch_metadata(str(job_id))
        filename_date = release_date.replace(".", "-")
        filename = (
            repo_root
            / "_posts"
            / "klassen_und_jobs"
            / (
                f"{filename_date}--{patch_number}--"
                f"{100 + int(job.get('JobIndex', job_id) or 0)}--{safe_name}.md"
            )
        )
        _write_if_changed(filename, page)
        if translation_callback:
            translation_callback(translations, slug_name)
        else:
            _write_translations(repo_root, translations, slug_name)
        written.append(filename)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Phantom Job class guides.")
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--mkd-data-dir")
    parser.add_argument(
        "--no-remote-localization",
        action="store_true",
        help="Use German MKDTrait text as fallback instead of querying XIVAPI.",
    )
    args = parser.parse_args()

    storeFilesInTmp(False)
    actions = loadDataTheQuickestWay("Action.json")
    action_transient = loadDataTheQuickestWay("ActionTransient.json")
    klass_translations = {lang: {} for lang in LANGUAGES}
    paths = addPhantomJobs(
        args.repo,
        actions,
        action_transient,
        klass_translations,
        mkd_data_dir=args.mkd_data_dir,
        allow_remote_localization=not args.no_remote_localization,
    )
    print(f"Generated {len(paths)} Phantom Job guides.")


if __name__ == "__main__":
    main()
