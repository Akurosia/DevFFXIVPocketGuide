#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import os
import sys
import shutil
from ffxiv_aku import storeFilesInTmp, loadDataTheQuickestWay, print_color_red

storeFilesInTmp(True)
contentfindercondition = loadDataTheQuickestWay("contentfindercondition_all.json", translate=True)
placename = loadDataTheQuickestWay("placename_all.json", translate=True)


def getImage(image: str, _type: str="icon") -> str:
    if image is None or image == "":
        return ""
    image = image.replace(".tex", "_hr1.png")
    if _type == "icon":
        image = image.replace(f"ui/{_type}/", "")
    image = copy_and_return_image_as_hr(img=image, _type=_type)
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
        if not os.path.exists(new_path + img):
            if not os.path.exists(os.path.dirname(new_path + img)):
                os.makedirs(os.path.dirname(new_path + img))
            shutil.copyfile(f"{basepath}{_type}/" + img, new_path + img)
    else:
        print_color_red(f"{basepath}{_type}/" + img)
    return img


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
            if place["Name_de"].lower().strip() == name.lower().strip():
                return place[f"Name_{lang}"]
    except KeyError:
        pass
    if name not in ['title']:
        print_color_red("Could not translate: " + name)
    return ""


def seperate_data_into_array(tag: str, entry: dict[str, str|list[str]]) -> str:
    if entry[tag]:
        entry[tag] = entry[tag].strip("'[").strip("]'").strip("\"[").strip("]\"").strip("[").strip("]").replace("\", \"", "', '").replace("\",\"", "', '").split("', '")
        entry[tag] = [b for b in entry[tag]]
    return entry[tag]
