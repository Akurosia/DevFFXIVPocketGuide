#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
from ffxiv_aku import storeFilesInTmp, loadDataTheQuickestWay, print_color_red
import os

storeFilesInTmp(True)
contentfindercondition = loadDataTheQuickestWay("contentfindercondition_all.json", translate=True)
placename = loadDataTheQuickestWay("placename_all.json", translate=True)


def getImage(image):
    if image is None:
        return None
    image = image.replace(".tex", "_hr1.png")
    image = image.replace("ui/icon/", "")
    image = copy_and_return_image_as_hr(image)
    return image

def copy_and_return_image_as_hr(img):
    if "_hr1" not in img:
        img = img.replace(".png", "_hr1.png")
    if os.path.exists("P:\\extras\\images\\ui\\icon\\" + img):
        #print(os.getcwd())
        if not os.path.exists("..\\assets\\img\\content_assets\\" + img):
            if not os.path.exists(os.path.dirname("..\\assets\\img\\content_assets\\" + img)):
                os.makedirs(os.path.dirname("..\\assets\\img\\content_assets\\" + img))
            shutil.copyfile("P:\\extras\\images\\ui\\icon\\" + img, "..\\assets\\img\\content_assets\\" + img)
    else:
        print_color_red(img)
    return img


def uglyContentNameFix(name, instanceType=None, difficulty=None):
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


def getContentName(name, lang="en", difficulty=None, instanceType=None):
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


def seperate_data_into_array(tag, entry):
    if entry[tag]:
        entry[tag] = entry[tag].strip("'[").strip("]'").strip("\"[").strip("]\"").strip("[").strip("]").replace("\", \"", "', '").replace("\",\"", "', '").split("', '")
        entry[tag] = [b for b in entry[tag]]
    return entry[tag]
