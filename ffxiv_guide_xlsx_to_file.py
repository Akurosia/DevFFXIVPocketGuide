#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import copy
import os
from operator import itemgetter
import traceback
# traceback.print_exc()
import re
import errno
import yaml
from yaml.loader import SafeLoader
from collections import OrderedDict
import python_scripts.generatePatch as gp
from ffxiv_aku import *
from python_scripts.header import *
from python_scripts.helper import *
from python_scripts.constants import *
from python_scripts.custom_logger import *
from python_scripts.xlsx_entry_helper import *
import python_scripts.convert_skills_to_guide_form as csgf
import python_scripts.generateLinks as gl
import sys


logger = getLogger()
disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True

storeFilesInTmp(False)
# storeFilesInTmp(True)
logdata = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())
action = loadDataTheQuickestWay("action_all.json", translate=True)
#levels = loadDataTheQuickestWay("Level.json")
#maps = loadDataTheQuickestWay("Map.json")
bnpcname = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname = loadDataTheQuickestWay("eobjname_all.json", translate=True)
status = loadDataTheQuickestWay("status_all.json", translate=True)
enpcresident = loadDataTheQuickestWay("enpcresident_all.json", translate=True)


def get_old_content_if_file_is_found(_existing_filename):
    if os.path.exists(_existing_filename):
        with open(_existing_filename, encoding="utf8") as f:
            doc = list(yaml.load_all(f, Loader=SafeLoader))[0]
            return doc
    return {}


def try_to_create_file(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def cleanup_logdata(logdata_instance_content):
    try:
        del logdata_instance_content["combatants"]
    except Exception:
        pass
    try:
        del logdata_instance_content["zone"]
    except Exception:
        pass
    try:
        del logdata_instance_content["contentzoneid"]
    except Exception:
        pass
    music = None
    try:
        music = logdata_instance_content["music"]
        del logdata_instance_content["music"]
    except Exception:
        pass
    for enemy_name, enemy in logdata_instance_content.items():
        # try: del enemy["status"]
        # except Exception: pass
        try:
            del enemy["tether"]
        except Exception:
            pass
        try:
            del enemy["headmarker"]
        except Exception:
            pass
    new_lic = {}
    for k, v in logdata_instance_content.items():
        # if not k == "":
        new_lic[k] = v
    return new_lic, music


def getDataFromLogfile(entry):
    logdata_instance_content = None
    music = None
    contentzoneid = ""
    # get correct title capitalization to read data from logdata
    title = uglyContentNameFix(entry["title_de"].title(), entry["instanceType"], entry["difficulty"])
    # get the latest data from logdata
    if not entry["title_de"] == "" and logdata_lower.get(entry["title_de"].lower()):
        try:
            logdata_instance_content = dict(logdata[getContentName(title, lang="de")])
        except Exception:
            logdata_instance_content = dict(logdata[title])
        if logdata_instance_content.get('contentzoneid', None):
            contentzoneid = logdata_instance_content['contentzoneid']
        logdata_instance_content, music = cleanup_logdata(logdata_instance_content)
    return logdata_instance_content, music, contentzoneid


def delete_invalid_entries(tmp_attack):
    try:
        del tmp_attack['title_id']
    except Exception:
        pass
    try:
        del tmp_attack['damage_type']
    except Exception:
        pass
    try:
        del tmp_attack['roles']
    except Exception:
        pass
    try:
        del tmp_attack['tags']
    except Exception:
        pass
    return tmp_attack


def writeFileIfNoDifferent(filename, filedata):
    try:
        with open(filename, "r", encoding="utf8") as f:
            x_data = f.read()
    except:
        x_data = None

    if not filedata == x_data:
        with open(filename, "w", encoding="utf8") as fi:
            fi.write(filedata)
        print(f"Wrote new data to file {filename}")


# EVERYTHING RELATED TO GUIDE DATA
####################################################################################################################

def check_Mechanics(entry, old_mechanics):
    guide_data = ""
    # this contruct looks ugly but it forbidds the recreation of empty mechanics
    if old_mechanics:
        guide_data += "mechanics:\n"
        if old_mechanics:
            for mechanic in old_mechanics:
                guide_data += add_Mechanic(mechanic)
    # if no old mechanics are found and excel contains [] it will create the example mechanic
    elif entry["mechanics"] != "":
        guide_data += "mechanics:\n"
        mechanics = entry["mechanics"].strip("\"[").strip("]\"").split("\",\"")
        counter = 1
        for m in mechanics:
            mechanic = {
                "steps": [{
                    "step": "09",
                    "notes": [{"note": f"Mechanics-note {counter}", }],
                    "images": [{"url": "/assets/img/test.jpg", "alt": "/assets/img/test.jpg", "height": "250px", }],
                    "videos": [{"url": "https&#58;//akurosia.de/upload/test.mp4", }],
                }],
            }
            if mechanics == ['']:
                mechanic['title'] = f"Mechanic-Title {counter}"
            else:
                mechanic['title'] = m

            guide_data += add_Mechanic(mechanic)
            counter += 1
    return guide_data


def add_Mechanic(data):
    guide_data = ""
    guide_data += f"  - title: \"{data['title']}\"\n"
    if data.get("steps", None):
        guide_data += "    steps:\n"
        for step in data["steps"]:
            guide_data += f"      - step: \"{int(step['step']):02d}\"\n"

            if step.get("notes", None):
                guide_data += "        notes:\n"
                for note in step["notes"]:
                    guide_data += f"          - note: \"{note['note']}\"\n"

            if step.get("images", None):
                guide_data += "        images:\n"
                for image in step["images"]:
                    guide_data += f"          - url: \"{image['url']}\"\n"
                    guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                    guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

            if step.get("videos", None):
                guide_data += "        videos:\n"
                for video in step["videos"]:
                    guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack):
    for attack_id in new_enemy_data.get('skill', {}):
        for attack in old_enemy_data.get('attacks', []):
            if type(attack['title']) == str:
                _id = attack.get('title_id', None)
                if not attack.get('title_id', None):
                    if attack.get('variation', None):
                        _id = attack['variation'][0]['title_id']
                attack['title'] = addLanguageElements("action", _id, attack['title'])
            existing_attacks[attack['title']['de']] = attack['type']
            if attack_id == attack.get('title_id', None):
                remove_attack.append(attack_id)
            if attack.get("variation", None):
                for vari in attack.get("variation", None):
                    if attack_id == vari['title_id']:
                        remove_attack.append(attack_id)
    return existing_attacks, remove_attack


def remove_skills_from_list_if_found(remove_attack, new_enemy_data):
    for x in remove_attack:
        try:
            del new_enemy_data["skill"][x]
        except Exception:
            pass
    return new_enemy_data


def addSortName(old_enemy_data, type_):
    if old_enemy_data.get(type_, None):
        for i, attack in enumerate(old_enemy_data[type_]):
            if not old_enemy_data[type_][i].get('sortname', None):
                if type(old_enemy_data[type_][i]['title']) == str:
                    x = "status"
                    if type_ == "attacks":
                        x = "action"
                    if not old_enemy_data[type_][i].get('title_id', None):
                        if old_enemy_data[type_][i].get('variation', None):
                            _id = old_enemy_data[type_][i]['variation'][0]['title_id']
                    else:
                        _id = old_enemy_data[type_][i]['title_id']
                    old_enemy_data[type_][i]['title'] = addLanguageElements(x, _id, old_enemy_data[type_][i]['title'])
                old_enemy_data[type_][i]['sortname'] = old_enemy_data[type_][i]['title']['de']
    return old_enemy_data


def sort_list_of_skills(data):
    if data.get('attacks', None):
        data['attacks'] = sorted(data['attacks'], key=itemgetter('sortname'))
        unknown_attacks = []
        known_attacks = []
        for attack in data['attacks']:
            if attack['title']['de'].startswith("Unknown_"):
                unknown_attacks.append(attack)
            else:
                known_attacks.append(attack)
        data['attacks'] = unknown_attacks + known_attacks
    return data


def translateAttack(skill_id, _type=action, lang="en"):
    try:
        text = _type[str(int(skill_id, 16))][f"Name_{lang}"]
        text = fixCaptilaziationAndRomanNumerals(text)
        if text == "":
            text = f"Unknown_{skill_id}"
        return text
    except KeyError:
        return f"Unknown_{skill_id}"


def fixCaptilaziationAndRomanNumerals(text):
    text = text.title()
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)\. ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii|Iii|IIi|Vi|Vii|Viii|Iv|Ix|Xi|Xii|Xiii|Xliii|Iii-E|Xxiv|013Bl|Xii\.)$", lambda x:  x.group(0).upper(), text)
    text = re.sub(r" (Ii) ", lambda x:  x.group(0).upper(), text)
    text = re.sub(r"('[a-zA-Z])(?! )", lambda x:  x.group(0).upper(), text)
    text = re.sub(r"('[a-zA-Z]) ", lambda x:  x.group(0).lower(), text)
    text = text.replace('"', r'\"')
    text = text.replace("&#246;", "ö").replace("&#252;", "ü").replace("&#228;", "ä").replace("&#223;", "ß")
    return text


def get_fixed_status_description(_id):
    try:
        description = {}
        for lang in LANGUAGES:
            tmp = status[str(int(_id, 16))][f'Description_{lang}']
            tmp = re.sub('<UIForeground>[0-9A-F]{1,6}</UIForeground>', '', tmp)
            tmp = re.sub('<UIGlow>[0-9A-F]{1,6}</UIGlow>', '', tmp)
            tmp = tmp.replace("\n\n", "<br>")
            tmp = tmp.replace("\n", "<br>")
            description[lang] = tmp
        return description
    except KeyError:
        return {"de": f"Unknown_{_id}"}


ids_to_replace = ["10742", "11399", "10744", "11402"]
def getBnpcNameFromID(_id, aname, nname, lang="en"):
    global ids_to_replace
    bnew_name = ""
    enew_name = ""
    ennew_name = ""
    if nname == "???":
        nname = "\?\?\?"
    if type(_id) == list:
        _id = _id[0]
    _id = str(_id)
    try:
        bnew_name = bnpcname[_id]["Singular_de"]
        if _id in ids_to_replace:
            nname = nname.replace(" ii", "").replace(" i", "")
        m = re.search(nname, bnew_name, re.IGNORECASE)
        n = re.search(aname, bnew_name, re.IGNORECASE)
        if m or n:
            return bnpcname[_id][f"Singular_{lang}"]
    except Exception:
        if nname == bnew_name or aname == bnew_name:
            return bnpcname[_id][f"Singular_{lang}"]

    try:
        enew_name = eobjname[_id]["Singular_de"]
        m = re.search(nname, enew_name, re.IGNORECASE)
        n = re.search(aname, enew_name, re.IGNORECASE)
        if m or n:
            return eobjname[_id][f"Singular_{lang}"]
    except Exception:
        if nname == enew_name or aname == enew_name:
            return eobjname[_id][f"Singular_{lang}"]

    try:
        ennew_name = enpcresident[_id]["Singular_de"]
        m = re.search(nname, ennew_name, re.IGNORECASE)
        n = re.search(aname, ennew_name, re.IGNORECASE)
        if m or n:
            return enpcresident[_id][f"Singular_{lang}"]
    except Exception:
        if nname == ennew_name or aname == ennew_name:
            return enpcresident[_id][f"Singular_{lang}"]

    if "α" not in bnew_name and "β" not in bnew_name and "（仮）鎖" not in bnew_name:
        print_color_red(f"'{bnew_name}', '{enew_name}', '{ennew_name}' not found {aname} ({nname}) - ({_id})")
    return ""


def getBnpcName(name, _id, lang="en"):
    name = name.lower()
    aname = ""
    # take care of all the article cases
    name_match = re.search("^(der|die|das) ", name)
    if name_match:
        aname = name.replace("der ", r"(\[t\]|(der|die|das)) ").replace("die ", r"(\[t\]|(der|die|das)) ").replace("das ", r"(\[t\]|(der|die|das)) ")

    name_match = re.search(" (der|die|das)", name)
    if name_match:
        aname = name.replace(" der ", r" (\[t\]|(der|die|das)) ").replace(" die ", r" (\[t\]|(der|die|das)) ").replace(" das ", r" (\[t\]|(der|die|das)) ")

    if aname == "":
        aname = name

    # take care of the german gender cases
    nname = aname.replace("er ", r"(\[a\]|(e|es|er|en)) ").replace("es ", r"(\[a\]|(e|es|er|en)) ").replace("en ", r"(\[a\]|(e|es|er|en)) ").replace("e ", r"(\[a\]|(e|es|er|en)) ").replace("?", "\?")
    if nname.endswith("e"):
        nname = nname[:-1] + r"(\[a\]|(e|es|er|en))"
    elif nname.endswith("en") or nname.endswith("es") or nname.endswith("er"):
        nname = nname[:-2] + r"(\[a\]|(e|es|er|en))"

    if not _id == "":
        resultname = getBnpcNameFromID(_id, aname, nname, lang)
        if not resultname == "":
            return fixCaptilaziationAndRomanNumerals(resultname)
    # check results agains bnpcname
    if nname == "???":
        nname = "\?\?\?"
    for key, bnpc in bnpcname.items():
        m = re.search(nname, bnpc["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(bnpc[f"Singular_{lang}"])

    # check results agains eobjname
    for key, eobj in eobjname.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(eobj[f"Singular_{lang}"])

    # check results agains eobjname
    for key, eobj in enpcresident.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(eobj[f"Singular_{lang}"])
    # return anything, just in case
    print_color_yellow(f"Missing {name} examples where ({aname}) and ({nname})", disable_yellow_print)
    return ""


def merge_attacks(old_enemy_data, new_enemy_data, enemy_type):
    remove_attack = []
    existing_attacks = {}
    # comapre all skill ids
    existing_attacks, remove_attack = compare_skill_ids(old_enemy_data, new_enemy_data, existing_attacks, remove_attack)
    # remove skill ids if they were found before
    new_enemy_data = remove_skills_from_list_if_found(remove_attack, new_enemy_data)

    old_enemy_data = addSortName(old_enemy_data, "attacks")
    old_enemy_data = sort_list_of_skills(old_enemy_data)
    if not new_enemy_data.get('skill', None):
        return old_enemy_data
    # merge new keys
    for attack_id, attack in new_enemy_data['skill'].items():
        if attack["name"] == "":
            attack["name"] = "Unknown_" + attack_id
        if existing_attacks.get(attack['name'], None):
            # convert regular attk to variation
            if existing_attacks[attack['name']] == "regular":
                print_color_blue(f"\t\tNeed to convert: {attack['name']} ({attack_id})", disable_blue_print)
                # find attack
                attack_index = None
                x_attack_name = fixCaptilaziationAndRomanNumerals(attack['name'])
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', {}).get('de', None) == x_attack_name:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                tmp_attack['type'] = "variation"
                tmp_attack['notes'] = [{'note': 'Variation-note BIG'}]
                tmp = {
                    'title': {
                        'en': translateAttack(tmp_attack['title_id'], lang="en"),
                        'de': translateAttack(tmp_attack['title_id'], lang="de"),
                        'fr': translateAttack(tmp_attack['title_id'], lang="fr"),
                        'ja': translateAttack(tmp_attack['title_id'], lang="ja"),
                        'cn': translateAttack(tmp_attack['title_id'], lang="cn"),
                        'ko': translateAttack(tmp_attack['title_id'], lang="ko")
                    },
                    'title_id': tmp_attack['title_id'],
                    'damage_type': tmp_attack['damage_type'],
                    'single_or_aoe': attack['type_id']
                }
                if tmp_attack['title'] == "Attacke":
                    tmp['disable'] = 'false'
                if tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    try:
                        tmp["damage"]["min"] = tmp_attack['damage']['min']
                        tmp["damage"]["max"] = tmp_attack['damage']['max']
                    except:
                        tmp["damage"]["min"] = tmp_attack['damage'][0]['min']
                        tmp["damage"]["max"] = tmp_attack['damage'][1]['max']
                if tmp_attack.get('roles', None):
                    tmp['roles'] = list(tmp_attack.get('roles', None))
                    if tmp['roles'][0]['role'] == "role":
                        tmp['roles'][0]['role'] = "Variation-role 1"
                if tmp_attack.get('tags', None):
                    tmp['tags'] = list(tmp_attack.get('tags', None))
                    if tmp['tags'][0]['tag'] == "tag":
                        tmp['tags'][0]['tag'] = "Variation-tag 1"
                if tmp_attack.get('notes', None):
                    tmp['notes'] = [{'note': 'Variation-note BIG'}]
                    if tmp_attack['notes'][0]['note'] == "Variation-note BIG":
                        tmp['notes'][0]['note'] = "Variation-note 1"
                tmp_attack['variation'] = [tmp]

                # add new attack
                tmp2 = {
                    'title': {
                        'en': translateAttack(attack_id, lang="en"),
                        'de': translateAttack(attack_id, lang="de"),
                        'fr': translateAttack(attack_id, lang="fr"),
                        'ja': translateAttack(attack_id, lang="ja"),
                        'cn': translateAttack(attack_id, lang="cn"),
                        'ko': translateAttack(attack_id, lang="ko")
                    },
                    'title_id': attack_id,
                    'damage_type': attack['damage_type'],
                    'single_or_aoe': attack['type_id']
                }
                if tmp_attack.get('damage', None):
                    tmp2["damage"] = {}
                    try:
                        tmp2["damage"]["min"] = tmp_attack['damage']['min']
                        tmp2["damage"]["max"] = tmp_attack['damage']['max']
                    except:
                        tmp2["damage"]["min"] = tmp_attack['damage'][0]['min']
                        tmp2["damage"]["max"] = tmp_attack['damage'][1]['max']
                if tmp_attack.get('roles', None):
                    tmp2['roles'] = list(tmp_attack.get('roles', None))
                    if tmp2['roles'][0]['role'] == "role":
                        tmp2['roles'][0]['role'] = "Variation-role 1"
                if tmp_attack.get('tags', None):
                    tmp2['tags'] = list(tmp_attack.get('tags', None))
                    if tmp2['tags'][0]['tag'] == "tag":
                        tmp2['tags'][0]['tag'] = "Variation-tag 1"
                if tmp_attack.get('notes', None):
                    tmp2['notes'] = [{'note': 'Variation-note BIG'}]
                    if tmp_attack['notes'][0]['note'] == "Variation-note BIG":
                        tmp2['notes'][0]['note'] = "Variation-note 1"
                tmp_attack['variation'].append(tmp2)

                # delete old invalid entries
                tmp_attack = delete_invalid_entries(tmp_attack)
                existing_attacks[attack['name']] = 'variation'
            else:
                print_color_blue("\t\tNeed to add to variation: " + attack['name'], disable_blue_print)
                # find attack
                attack_index = None
                for i, old_attack in enumerate(old_enemy_data['attacks']):
                    if old_attack.get('title', {}).get('de', None) == attack['name']:
                        attack_index = i
                        break
                tmp_attack = old_enemy_data['attacks'][attack_index]
                # add new attack
                tmp = {
                    'title': {
                        'en': translateAttack(attack_id, lang="en"),
                        'de': translateAttack(attack_id, lang="de"),
                        'fr': translateAttack(attack_id, lang="fr"),
                        'ja': translateAttack(attack_id, lang="ja"),
                        'cn': translateAttack(attack_id, lang="cn"),
                        'ko': translateAttack(attack_id, lang="ko")
                    },
                    'title_id': attack_id,
                    'damage_type': attack['damage_type'],
                    'single_or_aoe': attack['type_id']
                }
                if tmp_attack['variation'][0].get('damage', None) or tmp_attack.get('damage', None):
                    tmp["damage"] = {}
                    try:
                        tmp["damage"]["min"] = tmp_attack['variation'][0].get('damage', {}).get('min', None) or tmp_attack.get('damage', {}).get('min', None)
                        tmp["damage"]["max"] = tmp_attack['variation'][0].get('damage', {}).get('max', None) or tmp_attack.get('damage', {}).get('max', None)
                    except:
                        tmp["damage"]["min"] = tmp_attack['variation'][0].get('damage', {})[0].get('min', None) or tmp_attack.get('damage', {})[0].get('min', None)
                        tmp["damage"]["max"] = tmp_attack['variation'][0].get('damage', {})[1].get('max', None) or tmp_attack.get('damage', {})[1].get('max', None)
                if tmp_attack['variation'][0].get('roles', None) or tmp_attack.get('roles', None):
                    tmp['roles'] = tmp_attack['variation'][0].get('roles', None) or tmp_attack.get('roles', None)
                if tmp_attack['variation'][0].get('tags', None) or tmp_attack.get('tags', None):
                    tmp['tags'] = tmp_attack['variation'][0].get('tags', None) or tmp_attack.get('tags', None)
                if tmp_attack['variation'][0].get('notes', None) or tmp_attack.get('notes', None):
                    tmp['notes'] = tmp_attack['variation'][0].get('notes', None) or tmp_attack.get('notes', None)
                tmp_attack['variation'].append(tmp)
        else:
            print_color_blue("\t\tAdded new entry for regular: " + attack['name'], disable_blue_print)
            # create new regular
            tmp = {
                'sortname': translateAttack(attack_id, lang="de"),
                'title': {
                    'en': translateAttack(attack_id, lang="en"),
                    'de': translateAttack(attack_id, lang="de"),
                    'fr': translateAttack(attack_id, lang="fr"),
                    'ja': translateAttack(attack_id, lang="ja"),
                    'cn': translateAttack(attack_id, lang="cn"),
                    'ko': translateAttack(attack_id, lang="ko")
                },
                'title_id': attack_id,
                'attack_in_use': 'false',
                'disable': 'false',
                'type': 'regular',
                'damage_type': attack['damage_type'],
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                'notes': [{'note': 'note'}],
                'single_or_aoe': attack['type_id']
            }
            if attack.get('damage', None):
                tmp["damage"] = {}
                tmp["damage"]["min"] = attack['damage']['min']
                tmp["damage"]["max"] = attack['damage']['max']

            if tmp['title']['de'] == "Attacke":
                tmp['attack_in_use'] = 'true'
                tmp['disable'] = 'true'
                tmp['roles'][0]['role'] = 'Tank'
                tmp['tags'][0]['tag'] = 'Auto-Angriff'
                del tmp['notes']

            if tmp['title']['de'].startswith("Unknown_"):
                tmp['disable'] = 'true'

            if enemy_type == "adds" and tmp.get("notes", None):
                del tmp['notes']
            if old_enemy_data.get('attacks', []) == []:
                old_enemy_data['attacks'] = []
            old_enemy_data['attacks'].append(tmp)

            existing_attacks[attack['name']] = 'regular'

    old_enemy_data = sort_list_of_skills(old_enemy_data)
    return old_enemy_data


def compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_debuff):
    for debuff_id in new_enemy_data.get('status', {}):
        for debuff in old_enemy_data.get('debuffs', {}):
            if type(debuff['title']) == str:
                debuff['title'] = addLanguageElements("status", debuff.get('title_id', None), debuff['title'])
            existing_debuffs[debuff['title']['de']] = ""
            if debuff_id == debuff.get('title_id', None):
                remove_debuff.append(debuff_id)
    return existing_debuffs, remove_debuff


def remove_status_from_list_if_found(remove_debuff, new_enemy_data):
    for x in remove_debuff:
        try:
            del new_enemy_data["status"][x]
        except Exception:
            pass
    return new_enemy_data


def fixDebuffDescription(debuff):
    if type(debuff['description']) == str:
        debuff['description'] = get_fixed_status_description(debuff['title_id'])
    return debuff


def merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last):
    remove_attack = []
    existing_debuffs = {}
    ignore_debuffs = ['130', '13d']
    obviouse_debuffs = ['82b', '82a', '82c', '9d4', '9d7', '95', '12', '38e', '828', '0e', '113', '06', '07', '01', '11', '282', 'ca', '11', '196', '1b6', '23c', '']
    # filter duplicate debuffs
    tmp_debuffs = []
    tmp_debuff_ids = []
    disable_yellow_print = False
    for x in old_enemy_data.get("debuffs", []):
        if x['title_id'] not in tmp_debuff_ids and x['title_id'] not in ignore_debuffs:
            saved_used_skills_to_ignore_in_last.append(x['title_id'])
            x = fixDebuffDescription(x)
            tmp_debuff_ids.append(x['title_id'])
            tmp_debuffs.append(x)
        else:
            print_color_yellow(f"Ignore Duplicate Debuff {x['title']}")
    disable_yellow_print = True
    old_enemy_data["debuffs"] = tmp_debuffs

    if not new_enemy_data.get('title', {}).get('de', "") == 'Unbekannte Herkunft':
        # remove debuffs already manually adjusted
        for debuff in saved_used_skills_to_ignore_in_last:
            try:
                del new_enemy_data.get("status", {})[debuff]
            except Exception:
                pass
        # comapre all skill ids
        existing_debuffs, remove_attack = compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_attack)
        # remove skill ids if they were found before
        new_enemy_data = remove_status_from_list_if_found(remove_attack, new_enemy_data)
    # comapre all skill ids
    existing_debuffs, remove_attack = compare_status_ids(old_enemy_data, new_enemy_data, existing_debuffs, remove_attack)
    # remove skill ids if they were found before
    new_enemy_data = remove_status_from_list_if_found(remove_attack, new_enemy_data)

    old_enemy_data = addSortName(old_enemy_data, "debuffs")
    # merge new keys
    if not old_enemy_data.get('debuffs', None):
        old_enemy_data['debuffs'] = []
    else:
        old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('sortname'))

    if not new_enemy_data.get('status', None):
        return old_enemy_data, saved_used_skills_to_ignore_in_last

    # get only status to make sorting easier
    new_enemy_data_status = new_enemy_data.get('status', {})

    # sort after the name key in subdicts
    new_enemy_data_status = OrderedDict(sorted(new_enemy_data_status.items(), key=lambda x: x[1]['name']))

    for status_id, status_data in new_enemy_data_status.items():
        if status_data['name'] == "":
            continue
        if status_id in obviouse_debuffs:
            tmp_status = addknowndebuff(status_id, status_data)
        else:
            descriptions = get_fixed_status_description(status_id)
            tmp_status = {
                'sortname': translateAttack(status_id, _type=status, lang="de"),
                'title': {
                    'en': translateAttack(status_id, _type=status, lang="en"),
                    'de': translateAttack(status_id, _type=status, lang="de"),
                    'fr': translateAttack(status_id, _type=status, lang="fr"),
                    'ja': translateAttack(status_id, _type=status, lang="ja"),
                    'cn': translateAttack(status_id, _type=status, lang="cn"),
                    'ko': translateAttack(status_id, _type=status, lang="ko")
                },
                'title_id': status_id,
                'icon': status_data['icon'],
                'description': {
                    'en': descriptions.get('en', ""),
                    'de': descriptions.get('de', ""),
                    'fr': descriptions.get('fr', ""),
                    'ja': descriptions.get('ja', ""),
                    'cn': descriptions.get('cn', ""),
                    'ko': descriptions.get('ko', "")
                },
                'debuff_in_use': 'false',
                'disable': 'false',
                #'damage_type': status_data['damage_type'],
                'phases': [{'phase': '09'}],
                'roles': [{'role': 'role'}],
                'tags': [{'tag': 'tag'}],
                'notes': [{'note': 'note'}]
            }
            if status_data.get('duration', None):
                tmp_status["durations"] = status_data['duration']
        old_enemy_data['debuffs'].append(tmp_status)
    old_enemy_data['debuffs'] = sorted(old_enemy_data['debuffs'], key=itemgetter('sortname'))
    return old_enemy_data, saved_used_skills_to_ignore_in_last


def addknowndebuff(status_id, status_data):
    descriptions = get_fixed_status_description(status_id)
    tmp_status = {
        'sortname': translateAttack(status_id, _type=status, lang="de"),
        'title': {
            'en': translateAttack(status_id, _type=status, lang="en"),
            'de': translateAttack(status_id, _type=status, lang="de"),
            'fr': translateAttack(status_id, _type=status, lang="fr"),
            'ja': translateAttack(status_id, _type=status, lang="ja"),
            'cn': translateAttack(status_id, _type=status, lang="cn"),
            'ko': translateAttack(status_id, _type=status, lang="ko")
        },
        'title_id': status_id,
        'icon': status_data['icon'],
        'description': {
            'en': descriptions.get('en', ""),
            'de': descriptions.get('de', ""),
            'fr': descriptions.get('fr', ""),
            'ja': descriptions.get('ja', ""),
            'cn': descriptions.get('cn', ""),
            'ko': descriptions.get('ko', "")
        },
        'debuff_in_use': 'true',
        'disable': 'false',
        #'damage_type': status_data['damage_type'],
        'phases': [{'phase': '09'}],
        'roles': [{'role': 'Alle'}],
        'tags': [{'tag': 'Common'}],
    }
    return tmp_status


def reorder_old_enemies(entry, enemy_type, old_enemies):
    # sort old enemies
    final_old_enemy = []

    # do this only for bosses as they will be reorderd in the same order as in the EXCEL file
    if entry.get(enemy_type, None) and enemy_type == "bosse":
        for enemy in entry[enemy_type]:
            for old_enemy_data in old_enemies:
                # if old title is empty set it to default
                if not old_enemy_data['title']:
                    old_enemy_data['title'] = UNKNOWNTITLE
                if type(old_enemy_data['title']) == str:
                    old_enemy_data['title'] = addLanguageElements("bnpc", old_enemy_data['enemy_id'], old_enemy_data['title'])
                if old_enemy_data['title'].get('de', "").lower() == enemy.lower():
                    final_old_enemy.append(old_enemy_data)

    # if you created a new order, apply it
    if not final_old_enemy == []:
        old_enemies = final_old_enemy
    return old_enemies


def addLanguageElements(_type, _id, ori_value):
    if _type == "bnpc":
        data = bnpcname
        field = "Singular"
    if _type == "action":
        data = action
        field = "Name"
        _id = str(int(_id, 16))
    if _type == "status":
        data = status
        field = "Name"
        _id = str(int(_id, 16))

    if _id:
        return {
            'en': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_en']),
            'de': fixCaptilaziationAndRomanNumerals(ori_value),
            'fr': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_fr']),
            'ja': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ja']),
            'cn': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_cn']),
            'ko': fixCaptilaziationAndRomanNumerals(data[_id][f'{field}_ko']),
        }
    return UNKNOWNTITLE


def workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content):
    empty_enemy_available = False
    if old_enemies:
        print_color_red(f"\tStart looking at old_enem {enemy_type}", disable_red_print)
        old_enemies = reorder_old_enemies(entry, enemy_type, old_enemies)

        saved_used_skills_to_ignore_in_last = []
        for i, old_enemy_data in enumerate(old_enemies):
            if type(old_enemy_data['title']) == str:
                old_enemy_data['title'] = addLanguageElements("bnpc", old_enemy_data['enemy_id'], old_enemy_data['title'])
            if old_enemy_data['title']['de'] == "":
                continue
            elif old_enemy_data['title']['de'] == "Unbekannte Herkunft":
                empty_enemy_available = True

            old_enemy_data['title']['de'] = fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])
            print_color_yellow(f"\tWork on '{old_enemy_data['title']['de']}'", disable_yellow_print)
            empty_enemy_data = {}
            try:
                new_enemy_data = logdata_instance_content[old_enemy_data['title']['de']]
                if enemy_type == 'bosse' and len(old_enemies) == i + 1:
                    empty_enemy_data = logdata_instance_content['']
            except Exception as e:
                # print(logdata_instance_content)
                if not old_enemy_data['title']['de'] == "Unbekannte Herkunft":
                    print(f"Could not find {old_enemy_data['title']['de']} in logdata")
                new_enemy_data = {}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})

            # get enemy attacks and debuffs for all enemies with a name
            old_enemy_data["enemy_id"] = new_enemy_data.get("id", old_enemy_data.get('enemy_id', ""))

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                old_enemy_data["hp"] = {}
                old_enemy_data["hp"]["min"] = new_enemy_data.get("minHP", "")
                old_enemy_data["hp"]["max"] = new_enemy_data.get("maxHP", "")

            old_enemy_data = merge_attacks(old_enemy_data, new_enemy_data, enemy_type)
            old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, new_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

            guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c)

            # this try catch will remove enemy from logdata, so it wont be readded later on
            try:
                if old_enemy_data['title']['de'].title() == "Hesperos I":
                    del logdata_instance_content["Hesperos"]
                elif old_enemy_data['title']['de'].title() == "Hephaistos I":
                    del logdata_instance_content["Hephaistos"]
            except:
                print_color_red("!Could not remove enemy: Hesperos", disable_red_print)

            try:
                del logdata_instance_content[fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])]
            except Exception as e:
                print_color_red("Could not remove enemy: " + old_enemy_data['title']['de'], disable_red_print)

            # handle enemy if name is ""
            if not empty_enemy_data == {}:
                empty_enemy_available = True
                base_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = {'title': UNKNOWNTITLE, 'id': f"boss0{i+2}", "sequence": [{"phase": "09"}], 'debuffs': []}
                old_enemy_data = merge_attacks(old_enemy_data, empty_enemy_data, enemy_type)
                old_enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(old_enemy_data, empty_enemy_data, enemy_type, saved_used_skills_to_ignore_in_last)

                if not old_enemy_data == base_data:
                    guide_data += add_Enemy(old_enemy_data, enemy_type, new_enemy_data_c)
    return guide_data, empty_enemy_available


def workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available):
    guide_data = ""
    if logdata_instance_content != {}:
        print_color_red(f"\t Start looking at logdata {enemy_type}", disable_red_print)
        counter = 0
        if logdata_instance_content is None:
            return guide_data

        # the array is used to sort bosses
        enemies_to_add = []
        empty_enemy = None
        for i, enemy in enumerate(logdata_instance_content, 1):
            if enemy == "" and enemy_type == 'adds':
                continue
            print_color_yellow(f"\tWork on '{enemy}'", disable_yellow_print)
            # for bosses, only write bosses, for adds skip bosse
            lower_enemy_list = [x.lower() for x in entry[enemy_type]]
            lower_boss_list = [x.lower() for x in entry['bosse']]
            lower_enemy_list.append("")
            if (enemy_type == 'bosse' and enemy.lower() not in lower_enemy_list) or (enemy_type == 'adds' and enemy.lower() in lower_boss_list):
                logger.debug(f"Skip {enemy} ({enemy_type}) -> " + str(enemy.lower() not in lower_enemy_list))
                continue
            counter = counter + 1
            new_enemy_data = logdata_instance_content.get(enemy, "Unknown_")
            if new_enemy_data == {}:
                new_enemy_data = {'skill': {}}
            new_enemy_data_c = copy.deepcopy({**{}, **new_enemy_data})
            # create new template file to merge against
            enemy_id = new_enemy_data.get("id", "")
            de_and_sort_name = enemy if enemy != "" else "Unbekannte Herkunft"
            tmp = {
                "sortname": de_and_sort_name,
                "title": {
                    "en": getBnpcName(enemy, enemy_id, "en") if enemy != "" else "Unknown Source",
                    "de": de_and_sort_name,
                    "fr": getBnpcName(enemy, enemy_id, "fr") if enemy != "" else "Unknown Source",
                    "ja": getBnpcName(enemy, enemy_id, "ja") if enemy != "" else "Unknown Source",
                    "cn": getBnpcName(enemy, enemy_id, "cn") if enemy != "" else "Unknown Source",
                    "ko": getBnpcName(enemy, enemy_id, "ko") if enemy != "" else "Unknown Source"
                },
                "enemy_id": enemy_id,
                "id": f"{enemy_type[:-1]}{counter:02d}",
                "attacks": [],
                "debuffs": []
            }

            if new_enemy_data.get("minHP", None) or new_enemy_data.get("maxHP", None):
                tmp["hp"] = {}
                tmp["hp"]["min"] = new_enemy_data.get("minHP", "")
                tmp["hp"]["max"] = new_enemy_data.get("maxHP", "")

            enemy_data = merge_attacks(tmp, new_enemy_data, enemy_type)
            enemy_data['attacks'] = sorted(enemy_data['attacks'], key=itemgetter('sortname'))

            enemy_data, saved_used_skills_to_ignore_in_last = merge_debuffs(tmp, new_enemy_data, enemy_type, [])
            enemy_data['debuffs'] = sorted(enemy_data['debuffs'], key=itemgetter('sortname'))
            if enemy == "":
                empty_enemy = enemy_data
            else:
                tmp_guide_data_from_enemy = add_Enemy(enemy_data, enemy_type, new_enemy_data_c)
                enemies_to_add.append(tmp_guide_data_from_enemy)

        # this will add bosses in order as specified and add adds in order they were added to the array
        if enemy_type == 'bosse':
            for boss in entry['bosse']:
                for e in enemies_to_add:
                    if f'      de: "{boss}"' in e:
                        guide_data += e
                        break
        else:
            for e in enemies_to_add:
                guide_data += e

        if empty_enemy and not empty_enemy_available:
            if empty_enemy.get("attacks", None) or empty_enemy.get("debuffs", None):
                guide_data += add_Enemy(empty_enemy, "bosse", new_enemy_data_c)
    return guide_data


def ugly_fix_enemy_data(enemy_data, new_enemy_data):
    for attack in enemy_data.get('attacks', []):
        if attack['type'] in ["variation", "combo"]:
            for action in attack[attack['type']]:
                if new_enemy_data.get("skill", {}).get(action["title_id"], None):
                    x = new_enemy_data.get("skill", {}).get(action["title_id"], {})
                    if x.get("damage", {}).get("min", None) or x.get("damage", {}).get("max", None):
                        action['damage'] = {}
                        action['damage']['min'] = x.get("damage", {}).get("min", None)
                        action['damage']['max'] = x.get("damage", {}).get("max", None)
        elif attack['type'] == "regular":
            if new_enemy_data.get("skill", {}).get(attack["title_id"], None):
                x = new_enemy_data.get("skill", {}).get(attack["title_id"], {})
                if x.get("damage", {}).get("min", None) or x.get("damage", {}).get("max", None):
                    attack['damage'] = {}
                    attack['damage']['min'] = x.get("damage", {}).get("min", None)
                    attack['damage']['max'] = x.get("damage", {}).get("max", None)
    return enemy_data


def setMultipleLanguageStrings(guide_data, elementName, elemntArray, spaces):
    for lang in LANGUAGES:
        if type(elemntArray[elementName]) == str or type(elemntArray[elementName]) == None:
            continue
        if elemntArray[elementName].get(f"{lang}", None):
            guide_data += f'{spaces}{lang}: "{elemntArray[elementName][lang]}"\n'
    return guide_data


def add_Debuff(guide_data, debuff, enemy_type):
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", debuff, "          ")
    guide_data += f'        title_id: "{debuff["title_id"]}"\n'
    guide_data += f'        icon: "{getImage(debuff["icon"])}"\n'
    guide_data += f'        description:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "description", debuff, "          ")
    if debuff.get("durations", None):
        guide_data += f'        durations: {debuff["durations"]}\n'
    guide_data += f'        debuff_in_use: "{debuff["debuff_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{debuff["disable"] or "false"}"\n'
    #guide_data += f'        damage_type: "{debuff["damage_type"] or "None"}"\n'

    if debuff.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in debuff.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if debuff["title"]['de'].startswith("Unknown_"):
        return guide_data

    if debuff.get('roles', None):
        guide_data += f'        roles:\n'
        for role in debuff.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if debuff.get('tags', None):
        guide_data += f'        tags:\n'
        for tag in debuff.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'

    if debuff.get('notes', None):
        guide_data += f'        notes:\n'
        for note in debuff.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if debuff.get('videos', None):
        guide_data += f'        videos:\n'
        for video in debuff.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_regular_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        title_id: "{attack["title_id"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'
    guide_data += f'        damage_type: "{attack.get("damage_type", None)}"\n'

    if attack.get('damage', None):
        guide_data += f'        damage:\n'
        try:
            guide_data += f'          - min: {attack["damage"]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"]["max"] or "None"}\n'
        except TypeError:
            guide_data += f'          - min: {attack["damage"][0]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"][1]["max"] or "None"}\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if attack["title"]['de'].startswith("Unknown_"):
        return guide_data

    if attack.get('roles', None):
        guide_data += f'        roles:\n'
        for role in attack.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if attack.get('tags', None):
        guide_data += f'        tags:\n'
        for tag in attack.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'
        if attack.get('single_or_aoe', None):
            x = "AoE" if attack["single_or_aoe"] == "22" else "Single"
            guide_data += f'          - tag: "{x}"\n'

    if attack.get('notes', None):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_variation_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('variation', None):
        guide_data += f'        variation:\n'
        for variation in attack.get('variation', {}):
            #guide_data += f'          - title:\n'
            #guide_data = setMultipleLanguageStrings(guide_data, "title", variation, "              ")
            guide_data += f'          - title_id: "{variation["title_id"]}"\n'
            guide_data += f'            damage_type: "{variation.get("damage_type", None)}"\n'

            # print_color_yellow(variation)
            if variation.get('damage', None):
                guide_data += f'            damage:\n'
                try:
                    guide_data += f'              - min: {variation["damage"]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"]["max"] or "None"}\n'
                except TypeError:
                    guide_data += f'              - min: {variation["damage"][0]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"][1]["max"] or "None"}\n'

            if variation.get('roles', None):
                guide_data += f'            roles:\n'
                for role in variation.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if variation.get('tags', None):
                guide_data += f'            tags:\n'
                for tag in variation.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'
                if variation.get('single_or_aoe', None):
                    x = "AoE" if variation["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

            if variation.get('notes', None) and enemy_type != "adds":
                guide_data += f'            notes:\n'
                for note in variation.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_combo_Attack(guide_data, attack, enemy_type):
    guide_data += f'      - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", attack, "          ")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('phases', None):
        guide_data += f'        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += f'        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('combo', None):
        guide_data += f'        combo:\n'
        for combo in attack.get('combo', {}):
            guide_data += f'          - title: "{combo["title"]}"\n'
            guide_data += f'            title_id: "{combo["title_id"]}"\n'
            guide_data += f'            damage_type: "{combo["damage_type"]}"\n'

            if combo.get('damage', None):
                guide_data += f'            damage:\n'
                guide_data += f'              - min: {combo["damage"]["min"] or "None"}\n'
                guide_data += f'              - max: {combo["damage"]["max"] or "None"}\n'

            if combo.get('roles', None):
                guide_data += f'            roles:\n'
                for role in combo.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if combo.get('tags', None):
                guide_data += f'            tags:\n'
                for tag in combo.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'
                if combo.get('single_or_aoe', None):
                    x = "AoE" if combo["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

            if combo.get('notes', None) and enemy_type != "adds":
                guide_data += f'            notes:\n'
                for note in combo.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += f'        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += f'        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_Sequence(guide_data, data):
    guide_data += "    sequence:\n"
    for phase in data['sequence']:
        guide_data += f"      - phase: \"{phase['phase']}\"\n"
        if phase.get('name', None):
            guide_data += f"        name: \"{phase['name']}\"\n"

        if phase.get('alerts', None):
            guide_data += "        alerts:\n"
            for alert in phase['alerts']:
                guide_data += f"          - alert: \"{alert['alert']}\"\n"

        if phase.get('toolbox', None):
            guide_data += "        toolbox:\n"
            for toolbox in phase['toolbox']:
                guide_data += f"          - link: \"{toolbox['link']}\"\n"
                guide_data += f"            name: \"{toolbox['name']}\"\n"

        if phase.get('mechanics', None):
            guide_data += "        mechanics:\n"
            for mechanic in phase['mechanics']:
                guide_data += f"          - title: \"{mechanic['title']}\"\n"
                if mechanic.get('notes', None):
                    guide_data += f"            notes:\n"
                    for note in mechanic['notes']:
                        guide_data += f"              - note: \"{note['note']}\"\n"

        if phase.get('attacks', None):
            guide_data += "        attacks:\n"
            for attack in phase['attacks']:
                guide_data += f"          - attack: \"{attack['attack']}\"\n"

        if phase.get('images', None):
            guide_data += "        images:\n"
            for image in phase['images']:
                guide_data += f"          - url: \"{image['url']}\"\n"
                guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

        if phase.get('videos', None):
            guide_data += "        videos:\n"
            for video in phase['videos']:
                guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Enemy(enemy_data, enemy_type, new_enemy_data):
    guide_data = ""
    enemy_data = ugly_fix_enemy_data(enemy_data, new_enemy_data)
    guide_data += f'  - title:\n'
    guide_data = setMultipleLanguageStrings(guide_data, "title", enemy_data, "      ")
    if type(enemy_data.get("enemy_id", "")) == list:
        guide_data += f'    enemy_id: "{", ".join(enemy_data.get("enemy_id", ""))}"\n'
    else:
        guide_data += f'    enemy_id: "{enemy_data.get("enemy_id", "")}"\n'
    guide_data += f'    id: "{enemy_data["id"]}"\n'

    if enemy_data.get('hp', None):
        guide_data += f'    hp:\n'
        try:
            guide_data += f'      - min: {enemy_data["hp"]["min"] or "None"}\n'
            guide_data += f'      - max: {enemy_data["hp"]["max"] or "None"}\n'
        except TypeError:
            guide_data += f'      - min: {enemy_data["hp"][0]["min"] or "None"}\n'
            guide_data += f'      - max: {enemy_data["hp"][1]["max"] or "None"}\n'
    if enemy_data.get("attacks", None):
        guide_data += '    attacks:\n'
        for attack in enemy_data["attacks"]:
            if attack["type"] == "regular":
                guide_data = add_regular_Attack(guide_data, attack, enemy_type)
            elif attack["type"] == "variation":
                guide_data = add_variation_Attack(guide_data, attack, enemy_type)
            elif attack["type"] == "combo":
                guide_data = add_combo_Attack(guide_data, attack, enemy_type)
    if enemy_data.get("debuffs", None):
        guide_data += '    debuffs:\n'
        for debuff in enemy_data["debuffs"]:
            guide_data = add_Debuff(guide_data, debuff, enemy_type)
    if enemy_data.get("sequence", None):
        guide_data = add_Sequence(guide_data, enemy_data)
    else:
        if enemy_type == "bosse":
            guide_data = add_Sequence(guide_data, EXAMPLE_SEQUENCE)
        else:
            guide_data = add_Sequence(guide_data, EXAMPLE_ADD_SEQUENCE)
    return guide_data


def check_Enemy(entry, enemy_type, logdata_instance_content, old_enemies):
    guide_data = ""
    if old_enemies == {} and logdata == {}:
        return guide_data
    guide_data += "bosses:\n" if enemy_type == "bosse" else "adds:\n"
    guide_data, empty_enemy_available = workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content)
    print_color_yellow(guide_data, disable_yellow_print)
    guide_data += workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available)
    print_color_blue(guide_data, disable_blue_print)
    return guide_data


# Notizen, Bosse und Adds
def addGuide(entry, old_data, logdata_instance_content):
    guide_data = ""
    # add mechanics
    guide_data += check_Mechanics(entry, old_data.get('mechanics', None))
    print_color_green(f"Work on '{entry['title_de']}'", disable_green_print)
    guide_data += check_Enemy(entry, "bosse", logdata_instance_content, old_data.get('bosses', {}))
    guide_data += check_Enemy(entry, "adds", logdata_instance_content, old_data.get('adds', {}))
    return guide_data


####################################################################################################################


def write_content_to_file(entry, filename, old_data):
    logdata_instance_content, music, contentzoneid = getDataFromLogfile(entry)
    filedata = '---\n'
    filedata += addHeader(entry, old_data, music, contentzoneid)
    filedata += addGuide(entry, old_data, logdata_instance_content)
    filedata += '---'
    filedata += '\n'
    writeFileIfNoDifferent(filename, filedata)


def run(sheet, max_row, max_column, elements, orderedContent):
    # for every row do:
    for i in range(2, max_row):
        try:
            # comment the 2 line out to filter fo a specific line, numbering starts with 1 like it is in excel
            #if i not in [426]:
            #   continue
            entry = getEntryData(sheet, max_column, i, elements, orderedContent)
            logger.info(pretty_json(entry))
            # if the done collumn is not prefilled
            if entry["exclude"] == "end":
                print("END FLAG WAS FOUND!")
                sys.exit(0)
            if not (entry["exclude"] or entry["done"]):
                filename = f"{entry['categories']}_new/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                existing_filename = f"{entry['categories']}/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                old_data = get_old_content_if_file_is_found(existing_filename)
                # if old file was found, replace filename to save
                if not old_data == {}:
                    filename = existing_filename
                    # logger.info(pretty_json(old_data))
                try_to_create_file(filename)
                write_content_to_file(entry, filename, old_data)
        except Exception as e:
            logger.critical(f"Error when handeling '{filename}' with line id '{i}' ({e})")
            traceback.print_exception(*sys.exc_info())


if __name__ == "__main__":
    logger.critical('START')
    sheet, max_row, max_column = read_xlsx_file()
    # change into _posts dir
    os.chdir("./_posts")
    # first run to create all files
    orderedContent = getPrevAndNextContentOrder(sheet, XLSXELEMENTS, max_row)
    logger.debug(orderedContent)
    run(sheet, max_row, max_column, XLSXELEMENTS, orderedContent)
    # csgf needs also to run from posts dir
    csgf.run()
    # move back to DEVPOCKETGUIDE dir
    os.chdir("..")
    gl.run()
    gp.run()
    logger.critical('STOP')
