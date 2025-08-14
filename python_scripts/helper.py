#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import os
import sys
import shutil
import math
from dataclasses import dataclass, field
from typing import List, Any, Dict
from ffxiv_aku import print_color_red, print_color_green, convert_single_image
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

def getImage(image: str, _type: str="icon") -> str:
    if image is None or image == "":
        return ""
    if isinstance(image, dict):
        image = image.get("path_hr1", image)
    if image.startswith("/../"):
        image = image.replace("/../", "/")
    # exit early if corret name format is found and file exixsts
    if "_hr1" in image and os.path.exists(".." + image) or "/content/" in image and os.path.exists(".." + image) or image == "/assets/img/test.webp":
        return image
    # get propper image extention as _hr1.png
    image = image.replace(".webp", ".png")
    image = image.replace(".tex", ".png")
    image = image.replace("test.jpg", "test.webp")
    if _type == "icon":
        image = image.replace(f"ui/{_type}/", "")
    image = copy_and_return_image_as_hr(img=image, _type=_type)
    if not image.startswith("/"):
        image = "/" + image
    if not os.path.exists(".." + image):
        image = image.replace("_hr1.webp", ".webp")
        print_color_green(image)
    return image


def copy_and_return_image_as_hr(img: str, _type: str="icon") -> str:
    if "_hr1" not in img and not _type == "map":
        img = img.replace(".png", "_hr1.png")

    basepath = None
    if os.name == 'nt':
        basepath = "P:/extras/images/ui/"
    elif sys.platform.startswith("linux"):
        basepath = "/var/www/ffxiv/extras/images/ui/"
    elif sys.platform == "darwin":
        basepath = "/Volumes/FFXIV/extras/images/ui/"

    if os.path.exists(f"{basepath}{_type}/" + img):
        new_path = "../assets/img/game_assets/"
        if os.getcwd().endswith("DevFFXIVPocketGuide"):
            new_path = "assets/img/game_assets/"
        if _type == "map":
            new_path += "map/"
        full_filepath: str = (new_path + img.replace(".png", ".webp")).replace("//", "/")
        if not os.path.exists(full_filepath):
            if not os.path.exists(os.path.dirname(new_path + img)):
                os.makedirs(os.path.dirname(new_path + img))
            convert_single_image(f"{basepath}{_type}/" + img, replace_dir=(f"{basepath}{_type}/", new_path))
            #shutil.copyfile(f"{basepath}{_type}/" + img, new_path + img)
        img = full_filepath
    else:
        print_color_red(f"{basepath}{_type}/" + img)
    return img.replace(".png", ".webp").replace("../", "")


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
    print_color_red("Could not translate: " + name)
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
