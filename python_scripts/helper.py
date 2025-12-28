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

#--- main API ---
def getImage(image: str, _type: str = "icon", ishr1=True) -> str:
    """
    Resolve the correct image path and ensure a HR webp exists, cross-platform.
    Returns a URL-ish path starting with '/assets/...'.
    """

    if not image:  # None or ""
        return ""

    if "assets/img/content" in image:
        return image

    # dict support
    if isinstance(image, dict):
        if ishr1:
            image = image.get("path_hr1", image)
        else:
            image = image.get("path", image)

    # cleanup
    image = image.replace("\\", "/")
    if image.startswith("/../"):
        image = image.replace("/../", "/")

    # Early exit when already good and present
    if (((ishr1 and "_hr1" in image) or ("/content/" in image)) and path_exists_in_assets(image)) or image == "/assets/img/test.webp":
        return image

    # Normalize extensions
    image = image.replace(".webp", ".png").replace(".tex", ".png").replace("test.jpg", "test.webp")

    # Ensure _hr1 for non-map
    if ((ishr1 and "_hr1" not in image) and _type != "map"):
        if image.lower().endswith(".png"):
            image = image[:-4] + "_hr1.png"

    # For icons drop 'ui/icon/' prefix if present
    if _type == "icon":
        image = image.replace("ui/icon/", "").replace("ui/{}/".format(_type), "")
    # Create/copy/convert and get a repo-relative assets path (no leading slash)
    repo_rel = copy_and_return_image_as_hr(img=image, _type=_type)  # e.g. 'assets/img/game_assets/061000/061880_hr1.webp'
    # Make it URL-ish
    url_path = "/" + repo_rel.lstrip("/")
    # Debug: show real resolved path & existence
    abs_path = project_path_from_assets_like(url_path)
    # Fallback to non-hr if hr missing
    if not abs_path.exists():
        url_path = url_path.replace("_hr1.webp", ".webp")
        print_color_green(url_path)
    return url_path

def copy_and_return_image_as_hr(img: str, _type: str = "icon") -> str:
    """
    Ensure a webp is present in assets/img/game_assets[/map]/..., converting from source if needed.
    Returns a repo-relative path like 'assets/img/game_assets/061000/061880_hr1.webp'
    """

    # Strip any site prefix and *remove leading slash* so joins don't reset the base path
    img = img.replace("/assets/img/game_assets", "").replace("\\", "/").lstrip("/")

    # Source base path by OS
    if os.name == "nt":
        basepath = Path("P:/extras/images/ui")
    elif sys.platform.startswith("linux"):
        basepath = Path("/var/www/ffxiv/extras/images/ui")
    elif sys.platform == "darwin":
        basepath = Path("/Volumes/FFXIV/extras/images/ui")
    else:
        basepath = Path("extras/images/ui")  # fallback

    # Full source file (png is your source format)
    # IMPORTANT: img must NOT start with '/', otherwise this would discard basepath/_type
    src_path = (basepath / _type / img).with_suffix(".png")

    # Destination root inside repo
    dest_root = Path("assets/img/game_assets")
    if not is_repo_root():
        # allow running from parent folder as in your original code
        dest_root = Path("../assets/img/game_assets")

    if _type == "map":
        dest_root = dest_root / "map"

    # Destination full path as webp
    dest_path = (dest_root / img).with_suffix(".webp")

    # Convert/copy if source exists and dest missing
    if src_path.exists():
        if not dest_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            # convert_single_image expects a filename and a replace_dir tuple just like your original code
            # We pass posix-style strings to keep it consistent across OSes.
            convert_single_image(
                src_path.as_posix(),
                replace_dir=((basepath / _type).as_posix() + "/", dest_root.as_posix().rstrip("/") + "/"),
            )
    else:
        print_color_red(f"Filename not found: {src_path.as_posix()}")

    # Return repo-relative path (strip any leading ../ that might exist)
    return dest_path.as_posix().replace("../", "")

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
    try:
        for _, content in contentfindercondition.items():
            if "memoria" in content["Name_de"].lower().strip() and "memoria" in name.lower().strip():
                return content[f"Name_{lang}"]
            if content["Name_de"].lower().strip() == name.lower().strip():
                return content[f"Name_{lang}"]
        for _, place in placename.items():
            # the replace is for the "shy" character that is sometimes in the names
            if place["Name_de"].replace("­", "").lower().strip() == name.lower().strip():
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
