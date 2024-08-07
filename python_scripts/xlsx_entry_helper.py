#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import natsort
from collections import OrderedDict
from openpyxl import load_workbook
import os
from io import BytesIO
import requests
import logging
from ffxiv_aku import storeFilesInTmp, loadDataTheQuickestWay, print_color_red, getLevel
#getLevel?

try:
    from python_scripts.constants import DIFFERENT_PRONOUNS, DIFFERENT_PRONOUNSS, LANGUAGES
    from python_scripts.helper import getContentName, seperate_data_into_array
except Exception:
    from constants import DIFFERENT_PRONOUNS, DIFFERENT_PRONOUNSS, LANGUAGES
    from helper import getContentName, seperate_data_into_array

storeFilesInTmp(True)
quests = loadDataTheQuickestWay("Quest.de.json")
quests_all = loadDataTheQuickestWay("quest_all.json", translate=True)
questss = loadDataTheQuickestWay("Quest.de.json", exd="raw-exd-all")
enpcresidents = loadDataTheQuickestWay("Enpcresident.de.json")
enpcresidentss = loadDataTheQuickestWay("Enpcresident", translate=True)
contentfinderconditionX = loadDataTheQuickestWay("ContentFinderCondition.de.json")
logger = logging.getLogger()


def get_header_from_xlsx(sheet, max_column):
    result = []
    for j in range(1, max_column + 1):
        result.append(str(sheet.cell(row=int(1), column=int(j)).value).replace("None", "").strip())
    return result


def get_data_from_xlsx(sheet, max_column, i, elements):
    entry = {}
    # for every column in row add all elements into a dict:
    # max_column will ignore last column due to how range is working
    for j in range(1, max_column + 1):
        name = str(sheet.cell(row=int(i), column=int(j)).value).replace("None", "").strip()
        entry[elements[j - 1]] = name
    return entry


def clean_entries_from_single_quotes(entry):
    for key, value in entry.items():
        if value.startswith("'"):
            entry[key] = value[1:]
        if value.endswith("'"):
            entry[key] = value[:-1]
    return entry


def make_name_readable(entry, x):
    name = entry
    name = name.replace("[t]", DIFFERENT_PRONOUNS[x["Pronoun"]])
    name = name.replace("[a]", DIFFERENT_PRONOUNSS[x["Pronoun"]])
    return name


def workOnQuests(entry, quest_id):
    if quest_id == "":
        for lang in LANGUAGES:
            entry[f'quest_{lang}'] = ""
            entry[f'quest_location_{lang}'] = ""
            entry[f'quest_npc_{lang}'] = ""
        return entry
        
    # retriev quest from raw-exd to easily get all languages
    quest = questss[quest_id]
    for lang in LANGUAGES:
        entry[f'quest_{lang}'] = quests_all[quest_id][f'Name_{lang}'].replace(" ", "").replace(" ", "")
        
    issuer_id = quest['Issuer']['Start']
    for lang in LANGUAGES:
        npc = enpcresidentss[issuer_id][f"Singular_{lang}"]
        if "[a]" in npc or "[t]" in npc:
            npc = make_name_readable(npc, enpcresidents[issuer_id])
        entry[f'quest_npc_{lang}'] = npc
    
    level_id = quest['Issuer']['Location']
    for lang in LANGUAGES:
        try:
            level_data = getLevel(level_id, lang=lang)
            entry[f'quest_location_{lang}'] = f'{level_data["placename"]} ({level_data["x"]}, {level_data["y"]})'
        except KeyError:
            entry['quest_location'] = ""
            print_color_red(f"[workOnQuests] Error on loading: {quest['Issuer']['Location']} ({quest_id})")
    return entry


def getEntriesForRouletts(entry):
    global contentfinderconditionX
    for _, value in contentfinderconditionX.items():
        if value['Name'] == getContentName(entry["title"], "de", entry["difficulty"], entry["instanceType"]):
            entry['type'] = value['ContentType'].lower()
            entry['mapid'] = value['TerritoryType']
            entry['allianceraid'] = value['AllianceRoulette']
            entry['frontier'] = value['FeastTeamRoulette']
            entry['expert'] = value['ExpertRoulette']
            entry['guildhest'] = value['GuildHestRoulette']
            entry['highlevelroulette'] = value['HighLevelRoulette']
            entry['levelcaproulette'] = value['LevelCapRoulette']
            entry['leveling'] = value['LevelingRoulette']
            entry['main'] = value['MSQRoulette']
            entry['mentor'] = value['MentorRoulette']
            entry['normalraid'] = value['NormalRaidRoulette']
            entry['trial'] = value['TrialRoulette']
            return entry
    return entry


def getBeforeAndAfterContentEntries(orderedContent, entry):
    _previous = None
    _next = None
    _type = orderedContent[entry['instanceType']]
    _typeKeys = list(_type)
    for i, k in enumerate(_type):
        if _type[k].endswith(entry['slug']):
            if i - 1 >= 0:
                try:
                    _previous = _type[_typeKeys[i - 1]]
                except Exception:
                    pass
            try:
                _next = _type[_typeKeys[i + 1]]
            except Exception:
                pass
            return _previous, _next
    return None, None


def getEntryData(sheet, max_column, i, elements, orderedContent):
    entry = get_data_from_xlsx(sheet, max_column, i, elements)
    entry = clean_entries_from_single_quotes(entry)
    entry = workOnQuests(entry, entry["quest_id"])
    entry = getEntriesForRouletts(entry)
    for lang in LANGUAGES:
        entry[f"title_{lang}"] = getContentName(entry["title"], lang, entry["difficulty"], entry["instanceType"])
    _previous, _next = getBeforeAndAfterContentEntries(orderedContent, entry)
    # remove time from excel datetime
    entry["date"] = str(entry["date"]).replace(" 00:00:00", "").replace("-", ".")
    entry["prev_content"] = _previous
    entry["next_content"] = _next
    entry["line_index"] = i
    seperate_data_into_array("bosse", entry)
    seperate_data_into_array("tags", entry)
    entry['adds'] = []
    entry['mechanics'] = "[]"
    return entry


def getPrevAndNextContentOrder(sheet, elements, max_row):
    entry = {}
    for i in range(1, max_row + 1):
        instanceType = str(sheet.cell(row=int(i), column=int(elements.index('instanceType')) + 1).value).replace("None", "")
        if not entry.get(instanceType, None):
            entry[instanceType] = {}
        sortID = str(sheet.cell(row=int(i), column=int(3)).value).replace("None", "")
        addon = str(sheet.cell(row=int(i), column=int(5)).value).replace("None", "")
        slug = str(sheet.cell(row=int(i), column=int(6)).value).replace("None", "")
        entry[instanceType][sortID] = "/" + addon + "/" + slug
    return OrderedDict(natsort.natsorted(entry.items()))


def load_workbook_from_url(url):
    file = requests.get(url)
    return load_workbook(filename=BytesIO(file.content))


def read_xlsx_file():
    KEY = os.environ.get("GDRIVE_APIKEY")
    MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    SHEET = "11SBQWYyFnyh19Ku6T1Wr5tNAJvxdze8tvD6m4bzPGIA"
    r = f"https://www.googleapis.com/drive/v3/files/{SHEET}/export?key={KEY}&mimeType={MIME_TYPE}"
    wb = load_workbook_from_url(r)
    #wb = openpyxl.load_workbook('./guide_ffxiv.xlsx')
    sheet = wb['Tabelle1']
    max_row = sheet.max_row
    max_column = sheet.max_column
    return sheet, max_row, max_column
