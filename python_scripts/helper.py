#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import os
import sys
from pathlib import Path
import math
from dataclasses import dataclass, field
from typing import List, Any, Dict
from ffxiv_aku import print_color_red, print_color_green, print_color_yellow, convert_single_image, print_color_blue
try:
    from python_scripts.fileimports import *
except Exception:
    from fileimports import *

_content_name_index: dict[str, dict[str, Any]] | None = None
_place_name_index: dict[str, dict[str, Any]] | None = None

@dataclass
class EntryType(dict):
    exclude: str = ""
    date: str = ""
    sortid: str = ""
    title: str = ""
    categories: str = ""
    slug: str = ""
    image: str = ""
    patchNumber: str = ""
    patchName: str = ""
    difficulty: str = ""
    CFC_ID: str = ""
    PN_ID: str = ""
    quest_id: str = ""
    gearset_loot: List[str] = field(default_factory=list)
    tt_card: str = ""
    orchestrion: List[str] = field(default_factory=list)
    orchestrion_material: str = ""
    mtqvid: List[str] = field(default_factory=list)
    mrhvid: List[str] = field(default_factory=list)
    hector: List[str] = field(default_factory=list)
    mount: List[str] = field(default_factory=list)
    minion: List[str] = field(default_factory=list)
    instanceType: str = ""
    mapid: str = ""
    bosse: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    teamcraftlink: str = ""
    garlandtoolslink: str = ""
    gamerescapelink: str = ""
    done: str = ""
    type: str = ""
    allianceraid: str = ""
    frontier: str = ""
    expert: str = ""
    guildhest: str = ""
    highlevelroulette: str = ""
    levelcaproulette: str = ""
    leveling: str = ""
    main: str = ""
    mentor: str = ""
    normalraid: str = ""
    trial: str = ""
    title_de: str = ""
    title_en: str = ""
    title_fr: str = ""
    title_ja: str = ""
    title_cn: str = ""
    title_ko: str = ""
    prev_content: str = ""
    next_content: str = ""
    line_index: int = 0
    adds: List[str] = field(default_factory=list)
    mechanics: List[str] = field(default_factory=list)
    quest: Dict[str, str] = field(default_factory=dict)
    quest_location: Dict[str, str] = field(default_factory=dict)
    quest_npc: Dict[str, str] = field(default_factory=dict)
    titles: Dict[str, str] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

# --- path helpers ---
def get_repo_root() -> Path:
    """Find repo root by looking for 'assets' folder upward from cwd."""
    p = Path.cwd()
    while p != p.parent:  # stop at filesystem root
        if (p / "assets").exists():
            return p
        p = p.parent
    return Path.cwd()  # fallback if not found

REPO_ROOT = get_repo_root()

def project_path_from_assets_like(url_path: str) -> Path:
    return REPO_ROOT / url_path.lstrip("/")

def path_exists_in_assets(url_path: str) -> bool:
    return project_path_from_assets_like(url_path).exists()

def is_repo_root() -> bool:
    # your repo is named DevFFXIVPocketGuide per your message
    return Path.cwd().name == "DevFFXIVPocketGuide"

def normalize_image_path(image: str | dict[str, Any], _type: str = "icon", ishr1: bool = True) -> str:
    if isinstance(image, dict):
        image = image.get("path_hr1" if ishr1 else "path", "") or image.get("path", "") or image.get("path_hr1", "")

    image = str(image).strip().strip('"').strip("'").replace("\\", "/")
    image = image.split("?", 1)[0].split("#", 1)[0]

    prefixes = [
        "../assets/img/game_assets/",
        "/assets/img/game_assets/",
        "assets/img/game_assets/",
        f"P:/extras/images/ui/{_type}/",
        f"/var/www/ffxiv/extras/images/ui/{_type}/",
        f"/Volumes/FFXIV/extras/images/ui/{_type}/",
        f"extras/images/ui/{_type}/",
        f"ui/{_type}/",
    ]
    if _type == "map":
        prefixes.extend(["map/", "/map/"])

    for prefix in prefixes:
        if image.startswith(prefix):
            image = image[len(prefix):]

    if "/assets/img/game_assets/" in image:
        image = image.split("/assets/img/game_assets/", 1)[1]
    if f"/extras/images/ui/{_type}/" in image:
        image = image.split(f"/extras/images/ui/{_type}/", 1)[1]

    if _type == "icon":
        image = image.replace("ui/icon/", "")

    image = image.lstrip("/")
    if _type == "map" and image.startswith("map/"):
        image = image[4:]

    for extension in (".tex", ".png", ".jpg", ".jpeg"):
        if image.lower().endswith(extension):
            image = image[: -len(extension)] + ".webp"
            break
    if not image.lower().endswith(".webp"):
        image += ".webp"

    if ishr1 and _type != "map" and not image.lower().endswith("_hr1.webp"):
        image = image[:-5] + "_hr1.webp"

    return image


def copy_and_return_image_as_hr(img: str | dict[str, Any], _type: str = "icon", ishr1: bool = True) -> str:
    img = normalize_image_path(img, _type=_type, ishr1=ishr1)
    dest_root = Path("assets/img/game_assets")
    if not is_repo_root():
        dest_root = Path("../assets/img/game_assets")
    if _type == "map":
        dest_root = dest_root / "map"
    return (dest_root / img).as_posix().replace("../", "")

#--- main API ---
def getImage(image: str, _type: str = "icon", ishr1=True) -> str:
    """
    Resolve the correct image path and ensure a HR webp exists, cross-platform.
    Returns a URL-ish path starting with '/assets/...'.
    """

    if not image:  # None or ""
        return ""

    image = normalize_image_path(image, _type=_type, ishr1=ishr1)
    if image == "assets/img/test.webp":
        return "/assets/img/test.webp"

    repo_rel = copy_and_return_image_as_hr(img=image, _type=_type, ishr1=ishr1)
    url_path = "/" + repo_rel.lstrip("/")
    return url_path.replace("/assets/img/game_assets", "")


def uglyContentNameFix(name: str, instanceType: str="", difficulty: str="") -> str:
    if difficulty == "Fatal" and instanceType == "ultimate" and "fatal" not in name.lower():
        name = f"{name} (fatal)"
    elif difficulty == "Episch" and instanceType in ["raid", "feldexkursion", "gewölbesuche"] and "episch" not in name.lower():
        name = f"{name} (episch)"
    elif difficulty == "Schwer" and instanceType == "dungeon" and "schwer" not in name.lower():
        name = f"{name} (schwer)"
    # handle stupid edge cases for primals
    elif name in ["Königliche Konfrontation", "Jagd auf Rathalos"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Memoria Misera"] and difficulty.lower() != "normal":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Krieger des Lichts"] and difficulty.lower() == "extrem":
        name = f"{name} ({difficulty.lower()})"
    elif name in ["Jagd Auf Wächter-Arkveld"] and difficulty.lower() == "schwer":
        name = f"{name} ({difficulty.lower()})"
    # handle edge cases PvP
    elif "(Flechtenhain)" in name:
        name = name.replace("(Flechtenhain)", "")
    elif "(Kampfplatz)" in name:
        name = name.replace("(Kampfplatz)", "")
    # placeholder
    elif name == "":
        return ""
    # make sure brackets are always lowercase
    name = name.replace("(Fatal)", "(fatal)").replace("(Episch)", "(episch)").replace("(Schwer)", "(schwer)").replace("(Extrem)", "(extrem)")

    return name


def getContentName(name: str, lang: str ="en", difficulty: str="", instanceType: str="") -> str:
    name = uglyContentNameFix(name, instanceType, difficulty)
    normalized_name = name.lower().strip()
    try:
        global _content_name_index
        global _place_name_index
        if _content_name_index is None:
            _content_name_index = {
                content["Name_de"].lower().strip(): content
                for content in contentfindercondition.values()
            }
        if _place_name_index is None:
            _place_name_index = {
                place["Name_de"].replace("­", "").lower().strip(): place
                for place in placename.values()
            }

        if "memoria" in normalized_name:
            for key, content in _content_name_index.items():
                if "memoria" in key:
                    return content[f"Name_{lang}"]

        content = _content_name_index.get(normalized_name)
        if content:
            return content[f"Name_{lang}"]

        place = _place_name_index.get(normalized_name)
        if place:
            return place[f"Name_{lang}"]
    except KeyError:
        traceback.print_exc()
        pass
    print_color_red(f"Could not translate: {name=} ({lang=})")
    return ""


def seperate_data_into_array(tag: str, entry: dict[str, str|list[str]]) -> str:
    if entry[tag]:
        entry[tag] = entry[tag].strip("'[").strip("]'").strip("\"[").strip("]\"").strip("[").strip("]").replace("\", \"", "', '").replace("\",\"", "', '").split("', '")
        entry[tag] = [b for b in entry[tag]]
    return entry[tag]

def _get_coords_relative(x: str, x_off: str, z: str, z_off: str, size: str, pixel: bool) -> tuple[float, float]:
    if pixel:
        new_x = truncate(ToMapPixel(float(x), float(x_off), float(size)))
        new_y = truncate(ToMapPixel(float(z), float(z_off), float(size)))
    else:
        new_x = truncate(ToMapCoordinate(float(x), float(size)))
        new_y = truncate(ToMapCoordinate(float(z), float(size)))
    return new_x, new_y

def truncate(f: float, n: float = 1) -> float:
    return math.floor(f * 10 ** n) / 10 ** n

def ToMapPixel(val: float, offset: float, sizefactor: float) -> float:
    c = sizefactor / 100.0
    return (val + offset) * c

def ToMapCoordinate(val: float, sizefactor: float) -> float:
    c = sizefactor / 100.0
    val *= c
    return round(((41.0 / c) * ((val + 1024.0) / 2048.0)) + 1, 2)

#mainly used for fates
def FromMapCoordinate(result: float, sizefactor: float) -> float:
    c = sizefactor / 100.0
    inverse_c = 1 / c  # Since val was multiplied by c
    val = ((result - 1) * (2048.0 / 41.0)) - 1024.0
    return round(val * inverse_c, 2)  # Round to 2 decimal places

def getCoordsFromLocationLevel(value_location_dict: dict, pixel: bool = False):
    x, y = _get_coords_relative(value_location_dict['X'], value_location_dict['Map']['OffsetX'], value_location_dict['Z'], value_location_dict['Map']['OffsetY'], value_location_dict['Map']['SizeFactor'], pixel=pixel)
    #coords: dict[str, dict[str, Any]] = f'{value_location_dict['Map']["PlaceName"][f'Name_en']} ({x}, {y})'
    return {"x": x, "y": y, "region": value_location_dict['Map']["PlaceNameRegion"][f'Name_de'], "placename": value_location_dict['Map']["PlaceName"][f'Name_de']}
