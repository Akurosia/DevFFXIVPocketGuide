#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import re
import copy
from operator import itemgetter
from collections import OrderedDict
from ffxiv_aku import *
try:
    from python_scripts.constants import *
    from python_scripts.custom_logger import *
    from python_scripts.helper import *
except:
    from constants import *
    from custom_logger import *
    from helper import *


logger = getLogger()
storeFilesInTmp(False)
# storeFilesInTmp(True)
logdata = get_any_Logdata()
logdata_lower = dict((k.lower(), v) for k, v in logdata.items())
action = loadDataTheQuickestWay("action_all.json", translate=True)
bnpcname = loadDataTheQuickestWay("bnpcname_all.json", translate=True)
eobjname = loadDataTheQuickestWay("eobjname_all.json", translate=True)
status = loadDataTheQuickestWay("status_all.json", translate=True)
enpcresident = loadDataTheQuickestWay("enpcresident_all.json", translate=True)

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True


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
    for new_attack_id, new_attack in new_enemy_data.get('skill', {}).items():
        for attack in old_enemy_data.get('attacks', []):
            # fix skill title if it has no translations
            if type(attack['title']) == str:
                _id = attack.get('title_id', None)
                if not attack.get('title_id', None):
                    if attack.get('variation', None):
                        _id = attack['variation'][0]['title_id']
                attack['title'] = addLanguageElements("action", _id, attack['title'])
            existing_attacks[attack['title']['de']] = attack['type']
            # add ids to remove_attack array
            if new_attack_id == attack.get('title_id', None):
                remove_attack.append(new_attack_id)
            if attack.get("variation", None):
                for vari in attack.get("variation", None):
                    if new_attack_id == vari['title_id']:
                        remove_attack.append(new_attack_id)
            # add status if available
            if new_attack_id == attack.get('title_id', None):
                #if attack.get("add_status", None):
                #    if new_attack.get("add_status", None):
                if new_attack.get("add_status", None):
                    attack['add_status'] = new_attack['add_status']
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
    for _, bnpc in bnpcname.items():
        m = re.search(nname, bnpc["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(bnpc[f"Singular_{lang}"])

    # check results agains eobjname
    for _, eobj in eobjname.items():
        m = re.search(nname, eobj["Singular_de"].lower())
        if m:
            return fixCaptilaziationAndRomanNumerals(eobj[f"Singular_{lang}"])

    # check results agains eobjname
    for _, eobj in enpcresident.items():
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
    #remove_attack = []
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
                    'add_status': tmp_attack.get("add_status", []),
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
                    'single_or_aoe': attack['type_id'],
                    'add_status': attack.get("add_status", [])
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
                'add_status': attack.get("add_status", []),
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
    for x in old_enemy_data.get("debuffs", []):
        if x['title_id'] not in tmp_debuff_ids and x['title_id'] not in ignore_debuffs:
            saved_used_skills_to_ignore_in_last.append(x['title_id'])
            x = fixDebuffDescription(x)
            tmp_debuff_ids.append(x['title_id'])
            tmp_debuffs.append(x)
        else:
            print_color_yellow(f"Ignore Duplicate Debuff {x['title']}")
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
        print_color_red(f"\t [workOnOldEnemies] Start looking at old_enem {enemy_type}", disable_red_print)
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
            print_color_yellow(f"\t [workOnOldEnemies] Work on '{old_enemy_data['title']['de']}'", disable_yellow_print)
            empty_enemy_data = {}
            try:
                new_enemy_data = logdata_instance_content[old_enemy_data['title']['de']]
                if enemy_type == 'bosse' and len(old_enemies) == i + 1:
                    empty_enemy_data = logdata_instance_content['']
            except Exception as e:
                # print(logdata_instance_content)
                if not old_enemy_data['title']['de'] == "Unbekannte Herkunft":
                    print(f" [workOnOldEnemies] Could not find {old_enemy_data['title']['de']} in logdata")
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
                print_color_red(" [workOnOldEnemies] !Could not remove enemy: Hesperos", disable_red_print)

            try:
                del logdata_instance_content[fixCaptilaziationAndRomanNumerals(old_enemy_data['title']['de'])]
            except Exception as e:
                print_color_red(" [workOnOldEnemies] Could not remove enemy: " + old_enemy_data['title']['de'], disable_red_print)

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
        print_color_red(f"\t [workOnLogDataEnemies] Start looking at logdata {enemy_type}", disable_red_print)
        counter = 0
        if logdata_instance_content is None:
            print_color_red(f"\t [workOnLogDataEnemies] Skip because logdata_instance_content was not found", disable_red_print)
            return guide_data

        # the array is used to sort bosses
        enemies_to_add = []
        empty_enemy = None
        for enemy in logdata_instance_content:
            print_color_blue(f"\t [workOnLogDataEnemies] Start looking at enemy {enemy}", disable_blue_print)
            if enemy == "" and enemy_type == 'adds':
                continue
            print_color_yellow(f"\t [workOnLogDataEnemies] Work on '{enemy}'", disable_yellow_print)
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
                "debuffs": [],
                "add_status": []
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

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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

            if variation.get('add_status', None):
                guide_data += f'            add_status:\n'
                for e in variation['add_status']:
                    s = status[str(int(e, 16))]
                    guide_data += f'              - status: {e}\n'
                    guide_data += f'                icon: "{getImage(s["Icon"])}"'
                    guide_data += f'                name:\n'
                    for lang in LANGUAGES:
                        guide_data += f'                 {lang}: "' + s[f"Name_{lang}"] + '"\n'

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

    if attack.get('add_status', None):
        guide_data += f'        add_status:\n'
        for e in attack['add_status']:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"'
            guide_data += f'            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
    #print_color_yellow(guide_data, disable_yellow_print)
    guide_data += workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available)
    #print_color_blue(guide_data, disable_blue_print)
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


if __name__ == "__main__":
    a = {'title': {'de': 'Hephaistos I', 'en': 'Hephaistos', 'fr': 'Héphaïstos', 'ja': 'ヘファイストス'}, 'enemy_id': '11399', 'id': 'boss02', 'hp': {'min': 55874848, 'max': 55874848}, 'attacks': [{'title': {'de': 'Unknown_7108', 'en': 'Unknown_7108', 'fr': 'Unknown_7108', 'ja': 'Unknown_7108', 'cn': 'Unknown_7108', 'ko': 'Unknown_7108'}, 'attack_in_use': 'false', 'disable': 'true', 'type': 'variation', 'phases': [{'phase': '10'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7108', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7108', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Unknown_793B', 'en': 'Unknown_793B', 'fr': 'Unknown_793B', 'ja': 'Unknown_793B', 'cn': 'Unknown_793B', 'ko': 'Unknown_793B'}, 'attack_in_use': 'false', 'disable': 'true', 'type': 'variation', 'phases': [{'phase': '10'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '793B', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793B', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Unknown_793C', 'en': 'Unknown_793C', 'fr': 'Unknown_793C', 'ja': 'Unknown_793C', 'cn': 'Unknown_793C', 'ko': 'Unknown_793C'}, 'attack_in_use': 'false', 'disable': 'true', 'type': 'variation', 'phases': [{'phase': '10'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '793C', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793C', 'damage_type': 'None', 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Unknown_7947', 'en': 'Unknown_7947', 'fr': 'Unknown_7947', 'ja': 'Unknown_7947', 'cn': 'Unknown_7947', 'ko': 'Unknown_7947'}, 'attack_in_use': 'false', 'disable': 'true', 'type': 'variation', 'phases': [{'phase': '10'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7947', 'damage_type': 'Magical', 'damage': [{'min': 35}, {'max': 1264099}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7947', 'damage_type': 'Magical', 'damage': [{'min': 35}, {'max': 1264099}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Unknown_7949', 'en': 'Unknown_7949', 'fr': 'Unknown_7949', 'ja': 'Unknown_7949', 'cn': 'Unknown_7949', 'ko': 'Unknown_7949'}, 'attack_in_use': 'false', 'disable': 'true', 'type': 'variation', 'phases': [{'phase': '10'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7949', 'damage_type': 'Blunt', 'damage': [{'min': 197}, {'max': 44470}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7949', 'damage_type': 'Blunt', 'damage': [{'min': 197}, {'max': 44470}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Ausbreitende Viper', 'en': 'Nest Of Flamevipers', 'fr': 'Vipère Élancée', 'ja': 'スプレッドヴァイパー', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791F', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7920', 'damage_type': 'Magical', 'damage': [{'min': 1582}, {'max': 2047395}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791F', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7920', 'damage_type': 'Magical', 'damage': [{'min': 1582}, {'max': 2047395}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Ektothermos', 'en': 'Ektothermos', 'fr': "Vague D'Énergie Explosive", 'ja': '爆炎波動', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '79EA', 'damage_type': 'Magical', 'damage': [{'min': 584}, {'max': 76303}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '79EA', 'damage_type': 'Magical', 'damage': [{'min': 584}, {'max': 76303}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Erhöhung', 'en': 'Uplift', 'fr': 'Exhaussement', 'ja': '隆起', 'cn': 'Unknown_7935', 'ko': 'Unknown_7935'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '05'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7935', 'damage_type': 'Magical', 'damage': [{'min': 26}, {'max': 730935}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7935', 'damage_type': 'Magical', 'damage': [{'min': 26}, {'max': 730935}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Fackelnde Füße', 'en': 'Blazing Footfalls', 'fr': 'Pas Ardents', 'ja': 'ブレイジングフィート', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7938', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7938', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Fataler Stampfer', 'en': 'Stomp Dead', 'fr': 'Piétinement Mortel', 'ja': 'フェイタルストンプ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '05'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7936', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7937', 'damage_type': 'Blunt', 'damage': [{'min': 323}, {'max': 4412821}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7936', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7937', 'damage_type': 'Blunt', 'damage': [{'min': 323}, {'max': 4412821}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Feuersturm', 'en': 'Abyssal Fires', 'fr': 'Tempête Enflammée', 'ja': '炎嵐', 'cn': 'Unknown_7954', 'ko': 'Unknown_7954'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7954', 'damage_type': 'Magical', 'damage': [{'min': 19}, {'max': 21126}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7954', 'damage_type': 'Magical', 'damage': [{'min': 19}, {'max': 21126}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flammende Genesis', 'en': 'Genesis Of Flame', 'fr': 'Flammes De La Création', 'ja': '創世の真炎', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '04'}, {'phase': '09'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7944', 'damage_type': 'Magical', 'damage': [{'min': 34}, {'max': 76894}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794A', 'damage_type': 'Piercing', 'damage': [{'min': 154}, {'max': 76894}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7944', 'damage_type': 'Magical', 'damage': [{'min': 34}, {'max': 76894}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794A', 'damage_type': 'Piercing', 'damage': [{'min': 34}, {'max': 76894}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flammender Pfad', 'en': 'Trailblaze', 'fr': 'Traînée Ardente', 'ja': 'トレイルブレイズ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7939', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793D', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793E', 'damage_type': 'None', 'damage': [{'min': 195}, {'max': 196}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7939', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793D', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793E', 'damage_type': 'None', 'damage': [{'min': 195}, {'max': 196}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flammender Zahn', 'en': 'Scorching Fang', 'fr': 'Crocs Embrasants', 'ja': '炎の牙', 'cn': 'Unknown_7912', 'ko': 'Unknown_7912'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7912', 'damage_type': 'None', 'damage': [{'min': 12359}, {'max': 71219}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7912', 'damage_type': 'None', 'damage': [{'min': 12359}, {'max': 71219}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flammenreigen Der Schöpfung', 'en': 'Sunforge', 'fr': 'Bête Enflammée', 'ja': '創獣炎舞', 'cn': 'Unknown_7910', 'ko': 'Unknown_7910'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7910', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7911', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7910', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7911', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Flammenviper', 'en': 'Flameviper', 'fr': 'Serpent-Canon', 'ja': '炎蛇砲', 'cn': 'Unknown_7945', 'ko': 'Unknown_7945'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '06'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7945', 'damage_type': 'Magical', 'damage': [{'min': 220}, {'max': 136669}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7946', 'damage_type': 'Magical', 'damage': [{'min': 2951}, {'max': 2599559}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7945', 'damage_type': 'Magical', 'damage': [{'min': 220}, {'max': 136669}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7946', 'damage_type': 'Magical', 'damage': [{'min': 2951}, {'max': 2599559}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Fußmalmer', 'en': 'Quadrupedal Crush', 'fr': 'Écrasement Quadrupède', 'ja': 'フィートクラッシュ', 'cn': 'Unknown_7105', 'ko': 'Unknown_7105'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7105', 'damage_type': 'Blunt', 'damage': [{'min': 178}, {'max': 64508}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7107', 'damage_type': 'Blunt', 'damage': [{'min': 178}, {'max': 66582}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793F', 'damage_type': 'None', 'damage': [{'min': 178}, {'max': 63931}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A05', 'damage_type': 'None', 'damage': [{'min': 178}, {'max': 63931}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7105', 'damage_type': 'Blunt', 'damage': [{'min': 178}, {'max': 64508}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7107', 'damage_type': 'Blunt', 'damage': [{'min': 178}, {'max': 66582}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793F', 'damage_type': 'None', 'damage': [{'min': 178}, {'max': 64508}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A05', 'damage_type': 'None', 'damage': [{'min': 178}, {'max': 64508}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Fußschock', 'en': 'Footprint', 'fr': 'Choc Quadrupède', 'ja': 'フィートショック', 'cn': 'Unknown_7109', 'ko': 'Unknown_7109'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '05'}, {'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7109', 'damage_type': 'Blunt', 'damage': [{'min': 75}, {'max': 7443}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7109', 'damage_type': 'Blunt', 'damage': [{'min': 75}, {'max': 7443}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Fußstampfer', 'en': 'Quadrupedal Impact', 'fr': 'Impact Quadrupède', 'ja': 'フィートインパクト', 'cn': 'Unknown_7104', 'ko': 'Unknown_7104'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7104', 'damage_type': 'Blunt', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7106', 'damage_type': 'None', 'damage': [{'min': 35}, {'max': 7285}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793A', 'damage_type': 'None', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A04', 'damage_type': 'None', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7104', 'damage_type': 'Blunt', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7106', 'damage_type': 'None', 'damage': [{'min': 35}, {'max': 7285}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '793A', 'damage_type': 'None', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7A04', 'damage_type': 'None', 'damage': [{'min': 25}, {'max': 7346}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gleißender Amok', 'en': 'Rearing Rampage', 'fr': 'Cabrage Ravageur', 'ja': 'リアリングランページ', 'cn': 'Unknown_7933', 'ko': 'Unknown_7933'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '05'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7933', 'damage_type': 'Blunt', 'damage': [{'min': 9}, {'max': 34253}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7934', 'damage_type': 'Blunt', 'damage': [{'min': 46}, {'max': 34389}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7955', 'damage_type': 'None', 'damage': [{'min': 153}, {'max': 34015}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7933', 'damage_type': 'Blunt', 'damage': [{'min': 9}, {'max': 34253}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7934', 'damage_type': 'Blunt', 'damage': [{'min': 46}, {'max': 34389}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7955', 'damage_type': 'None', 'damage': [{'min': 153}, {'max': 34015}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Glutfeuer', 'en': 'Torch Flame', 'fr': 'Explosion De Braises', 'ja': '熾炎', 'cn': 'Unknown_7927', 'ko': 'Unknown_7927'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '04'}, {'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7927', 'damage_type': 'None', 'damage': [{'min': 121255}, {'max': 252337}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7927', 'damage_type': 'None', 'damage': [{'min': 121255}, {'max': 252337}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gorgons Fluch', 'en': 'Gorgomanteia', 'fr': 'Malédiction De Gorgone', 'ja': 'ゴルゴンの呪詛', 'cn': 'Unknown_791A', 'ko': 'Unknown_791A'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791A', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791A', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gorgons Schlangengift', 'en': 'Blood Of The Gorgon', 'fr': 'Venin Reptilien De Gorgone', 'ja': 'ゴルゴンの蛇毒', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '792F', 'damage_type': 'Magical', 'damage': [{'min': 691}, {'max': 9999897}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '792F', 'damage_type': 'Magical', 'damage': [{'min': 691}, {'max': 9999897}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gorgons Steinauge', 'en': 'Eye Of The Gorgon', 'fr': 'Œil Pétrifiant De Gorgone', 'ja': 'ゴルゴンの石眼', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '792D', 'damage_type': 'None', 'damage': [{'min': 3007}, {'max': 3007}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '792D', 'damage_type': 'None', 'damage': [{'min': 3007}, {'max': 3007}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gorgons Steinlicht', 'en': 'Crown Of The Gorgon', 'fr': 'Lueur Pétrifiante De Gorgone', 'ja': 'ゴルゴンの石光', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '792E', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '792E', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Gorgons Übelgift', 'en': 'Breath Of The Gorgon', 'fr': 'Poison Insidieux De Gorgone', 'ja': 'ゴルゴンの邪毒', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7930', 'damage_type': 'None', 'damage': [{'min': 742}, {'max': 9999897}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7930', 'damage_type': 'None', 'damage': [{'min': 742}, {'max': 9999897}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Hemitheos-Flare', 'en': "Hemitheos's Flare", 'fr': "Brasier D'Hémithéos", 'ja': 'ヘーミテオス・フレア', 'cn': 'Unknown_72CE', 'ko': 'Unknown_72CE'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '72CE', 'damage_type': 'Magical', 'damage': [{'min': 2192}, {'max': 1970082}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '72CE', 'damage_type': 'Magical', 'damage': [{'min': 2192}, {'max': 1970082}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Illusionsschatten', 'en': 'Illusory Creation', 'fr': "Création D'Ombres", 'ja': '幻影創造', 'cn': 'Unknown_791C', 'ko': 'Unknown_791C'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791C', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7931', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791C', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7931', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'In Die Schatten', 'en': 'Into The Shadows', 'fr': "Dans L'Ombre", 'ja': 'イントゥシャドウ', 'cn': 'Unknown_792A', 'ko': 'Unknown_792A'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '792A', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '792A', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Konzeptionelle Diflare', 'en': 'Conceptual Diflare', 'fr': 'Dibrasier Conceptuel', 'ja': 'ディフレア・コンシーヴ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7917', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7917', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Konzeptionelle Oktaflare', 'en': 'Conceptual Octaflare', 'fr': 'Octobrasier Conceptuel', 'ja': 'オクタフレア・コンシーヴ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7914', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7914', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Konzeptionelle Tetraflare', 'en': 'Conceptual Tetraflare', 'fr': 'Tetrabrasier Conceptuel', 'ja': 'テトラフレア・コンシーヴ', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7915', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7916', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7915', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7916', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Lodernde Schlange', 'en': 'Cthonic Vent', 'fr': 'Serpents De Flammes Ascendants', 'ja': '噴炎昇蛇', 'cn': 'Unknown_78F0', 'ko': 'Unknown_78F0'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '78F0', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '78F0', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Mannigfaltige Flammen', 'en': 'Manifold Flames', 'fr': 'Flammes Orientées Multiples', 'ja': '多重操炎', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7921', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7922', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7921', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7922', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Mutierte Schöpfung', 'en': 'Reforged Reflection', 'fr': 'Mutation Corporelle', 'ja': '変異創身', 'cn': 'Unknown_794B', 'ko': 'Unknown_794B'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '05'}, {'phase': '07'}, {'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '794B', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794C', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794B', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794C', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Natterntritt', 'en': 'Snaking Kick', 'fr': 'Coup De Pied Du Serpent', 'ja': 'スネークキック', 'cn': 'Unknown_7929', 'ko': 'Unknown_7929'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '03'}, {'phase': '07'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7929', 'damage_type': 'Blunt', 'damage': [{'min': 135031}, {'max': 269673}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7929', 'damage_type': 'Blunt', 'damage': [{'min': 135031}, {'max': 269673}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Oktaflare', 'en': 'Octaflare', 'fr': 'Octobrasier', 'ja': 'オクタフレア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791D', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791D', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Schöpfungsauftrag', 'en': 'Creation On Command', 'fr': 'Ordre De Création', 'ja': '創造命令', 'cn': 'Unknown_794F', 'ko': 'Unknown_794F'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '794F', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '794F', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Steigende Diflare', 'en': 'Emergent Diflare', 'fr': 'Dibrasier Émergent', 'ja': 'エマージ・ディフレア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '08'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791B', 'damage_type': 'Magical', 'damage': [{'min': 1964}, {'max': 4075105}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791B', 'damage_type': 'Magical', 'damage': [{'min': 1964}, {'max': 4075105}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Steigende Oktaflare', 'en': 'Emergent Octaflare', 'fr': 'Octobrasier Émergent', 'ja': 'エマージ・オクタフレア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7918', 'damage_type': 'Magical', 'damage': [{'min': 208}, {'max': 2023526}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7918', 'damage_type': 'Magical', 'damage': [{'min': 208}, {'max': 2023526}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Steigende Tetraflare', 'en': 'Emergent Tetraflare', 'fr': 'Tetrabrasier Émergent', 'ja': 'エマージ・テトラフレア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7919', 'damage_type': 'Magical', 'damage': [{'min': 113}, {'max': 2047085}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7919', 'damage_type': 'Magical', 'damage': [{'min': 113}, {'max': 2047085}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Tetraflare', 'en': 'Tetraflare', 'fr': 'Tetrabrasier', 'ja': 'テトラフレア', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '791E', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '791E', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Versengte Schwinge', 'en': "Sun's Pinion", 'fr': 'Aile Embrasante', 'ja': '炎の翼', 'cn': 'Unknown_7913', 'ko': 'Unknown_7913'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '02'}, {'phase': '04'}, {'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '7913', 'damage_type': 'Magical', 'damage': [{'min': 11886}, {'max': 72880}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '7913', 'damage_type': 'Magical', 'damage': [{'min': 11886}, {'max': 72880}], 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'AoE'}, {'tag': 'AoE'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Vierfacher Feuersturm', 'en': 'Fourfold Fires', 'fr': 'Quadruple Tempête Enflammée', 'ja': '四重炎嵐', 'cn': 'Unknown_78F2', 'ko': 'Unknown_78F2'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '06'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '78F2', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '78F2', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}, {'title': {'de': 'Vulkanfackel', 'en': 'Volcanic Torches', 'fr': 'Boutefeux Magiques', 'ja': '熾炎創火', 'cn': 'Unknown_78F7', 'ko': 'Unknown_78F7'}, 'attack_in_use': 'true', 'disable': 'false', 'type': 'variation', 'phases': [{'phase': '01'}], 'notes': [{'note': 'Variation-note BIG'}], 'variation': [{'title_id': '78F7', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}, {'title_id': '78F7', 'damage_type': 'None', 'roles': [{'role': 'Variation-role 1'}], 'tags': [{'tag': 'Variation-tag 1'}, {'tag': 'Single'}, {'tag': 'Single'}], 'notes': [{'note': 'Variation-note 1'}]}]}], 'debuffs': [{'title': {'de': 'Blutung', 'en': 'Bleeding', 'fr': 'Saignement', 'ja': 'ペイン', 'cn': '出血', 'ko': '고통'}, 'title_id': 'B87', 'icon': '015000/015530_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Sustaining damage over time.', 'fr': 'Des dégâts périodiques neutres sont subis.', 'ja': '無属性ダメージにより、ＨＰが徐々に失われる状態。', 'cn': '无属性持续伤害，体力逐渐流失', 'ko': '무속성 피해로 HP가 서서히 줄어드는 상태.'}, 'durations': [15], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erdresistenz - (Stark)', 'en': 'Earth Resistance Down II', 'fr': 'Résistance À La Terre Réduite+', 'ja': '土属性耐性低下［強］', 'cn': 'Unknown_D2C', 'ko': 'Unknown_D2C'}, 'title_id': 'D2C', 'icon': '015000/015722_hr1.png', 'description': {'de': 'Resistenz gegen Erde ist stark verringert.', 'en': 'Earth resistance is significantly reduced.', 'fr': "La résistance à l'élément terre est considérablement réduite.", 'ja': '土属性に対する耐性が著しく低下した状態。'}, 'durations': [12], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité Magique Augmentée', 'ja': '被魔法ダメージ増加', 'cn': '魔法受伤加重', 'ko': '받는 마법 피해량 증가'}, 'title_id': 'B7D', 'icon': '015000/015057_hr1.png', 'description': {'de': 'Erlittener Magieschaden ist erhöht.', 'en': 'Magic damage taken is increased.', 'fr': 'Les dégâts magiques reçus sont augmentés.', 'ja': '受ける魔法ダメージが増加する状態。', 'cn': '受到魔法攻击的伤害增加', 'ko': '마법 공격으로 받는 피해량이 증가하는 상태.'}, 'durations': [2, 4, 7], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erhöhte Magie-Verwundbarkeit', 'en': 'Magic Vulnerability Up', 'fr': 'Vulnérabilité Magique Augmentée', 'ja': '被魔法ダメージ増加', 'cn': 'Unknown_D56', 'ko': 'Unknown_D56'}, 'title_id': 'D56', 'icon': '015000/015057_hr1.png', 'description': {'de': 'Erlittener Magieschaden ist erhöht.', 'en': 'Magic damage taken is increased.', 'fr': 'Les dégâts magiques reçus sont augmentés.', 'ja': '受ける魔法ダメージが増加する状態。'}, 'durations': [7], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erhöhte Physische Verwundbarkeit', 'en': 'Physical Vulnerability Up', 'fr': 'Vulnérabilité Physique Augmentée', 'ja': '被物理ダメージ増加', 'cn': '物理受伤加重', 'ko': '받는 물리 피해량 증가'}, 'title_id': 'B7C', 'icon': '015000/015053_hr1.png', 'description': {'de': 'Erlittener physischer Schaden ist erhöht.', 'en': 'Physical damage taken is increased.', 'fr': 'Les dégâts physiques reçus sont augmentés.', 'ja': '受ける物理ダメージが増加する状態。', 'cn': '受到物理攻击的伤害增加', 'ko': '물리 공격으로 받는 피해량이 증가하는 상태.'}, 'durations': [9], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '05'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Erstes Ziel', 'en': 'First In Line', 'fr': 'Première Cible', 'ja': 'ファーストターゲット', 'cn': '第一目标', 'ko': 'Unknown_BBC'}, 'title_id': 'BBC', 'icon': '015000/015401_hr1.png', 'description': {'de': 'Ist das erste anvisierte Angriffsziel.', 'en': 'Marked as target #1.', 'fr': "Sera la première cible de l'attaque.", 'ja': '1番目のターゲットとして、狙いをつけられている状態。', 'cn': '被选为了第一目标'}, 'durations': [9999], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Gorgons Fluch: Schlangengift', 'en': 'Blood Of The Gorgon', 'fr': 'Malédiction De Gorgone: Venin Reptilien', 'ja': 'ゴルゴンの呪詛：蛇毒', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'CFE', 'icon': '015000/015487_hr1.png', 'description': {'de': 'Sprüht nach Ablauf die Umgebung mit Gift ein.', 'en': 'Cursed to unleash poison in the surrounding area when this effect expires.', 'fr': "Déclenche une attaque empoisonnée dans les alentours lorsque la durée de l'effet s'est écoulée.", 'ja': 'ゴルゴンの呪いを受けた状態。効果時間が終了すると、周囲に毒の攻撃を放つ。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [17, 23, 25, 26, 29, 34], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Gorgons Fluch: Steinauge', 'en': 'Eye Of The Gorgon', 'fr': 'Malédiction De Gorgone: Œil Pétrifiant', 'ja': 'ゴルゴンの呪詛：石眼', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D17', 'icon': '015000/015587_hr1.png', 'description': {'de': 'Entfesselt nach Ablauf einen versteinernden Angriff nach vorne.', 'en': 'Cursed to unleash a petrifying attack in the direction of gaze when this effect expires.', 'fr': "Déclenche une attaque pétrifiante en ligne droite vers l'avant lorsque la durée de l'effet s'est écoulée.", 'ja': 'ゴルゴンの呪いを受けた状態。効果時間が終了すると、前方に石化の攻撃を放つ。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [14, 21, 22, 23, 29, 31], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Gorgons Fluch: Steinlicht', 'en': 'Crown Of The Gorgon', 'fr': 'Malédiction De Gorgone: Lueur Pétrifiante', 'ja': 'ゴルゴンの呪詛：石光', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'D18', 'icon': '015000/015588_hr1.png', 'description': {'de': 'Entfesselt nach Ablauf ein versteinerndes Licht auf die Umgebung', 'en': 'Cursed to unleash a petrifying light upon those nearby when this effect expires.', 'fr': "Émet une lueur pétrifiante alentour lorsque la durée de l'effet s'est écoulée.", 'ja': 'ゴルゴンの呪いを受けた状態。効果時間が終了すると、周囲に石化の光を放つ。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [38], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Gorgons Fluch: Übelgift', 'en': 'Breath Of The Gorgon', 'fr': 'Malédiction De Gorgone: Poison Insidieux', 'ja': 'ゴルゴンの呪詛：邪毒', 'cn': '_Rsv_', 'ko': '_Rsv_'}, 'title_id': 'CFF', 'icon': '015000/015488_hr1.png', 'description': {'de': 'Sprüht nach Ablauf die Umgebung mit Gift ein.', 'en': 'Cursed to unleash poison in the surrounding area when this effect expires.', 'fr': "Déclenche une attaque empoisonnée dans les alentours lorsque la durée de l'effet s'est écoulée.", 'ja': 'ゴルゴンの呪いを受けた状態。効果時間が終了すると、周囲に毒の攻撃を放つ。', 'cn': '_rsv_', 'ko': '_rsv_'}, 'durations': [39], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'In Ereignis', 'en': 'In Event', 'fr': 'Événement', 'ja': 'イベント中', 'cn': '过场剧情中', 'ko': '이벤트 중'}, 'title_id': 'BB7', 'icon': '015000/015765_hr1.png', 'description': {'de': 'Nimmt an einem Spielereignis teil.', 'en': 'Participating in an in-game event.', 'fr': 'Participe à un événement.', 'ja': 'イベントが発生している状態。', 'cn': '正处于过场剧情中', 'ko': '이벤트가 발생한 상태.'}, 'durations': [9999], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '09'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Schaden -', 'en': 'Damage Down', 'fr': 'Malus De Dégâts', 'ja': 'ダメージ低下', 'cn': '伤害降低', 'ko': '주는 피해량 감소'}, 'title_id': 'B5F', 'icon': '015000/015520_hr1.png', 'description': {'de': 'Ausgeteilter Schaden ist verringert.', 'en': 'Damage dealt is reduced.', 'fr': 'Les dégâts infligés sont réduits.', 'ja': '与ダメージが低下した状態。', 'cn': '攻击所造成的伤害降低', 'ko': '적에게 주는 피해량이 감소하는 상태.'}, 'durations': [1, 5, 13, 30], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Schaden Über Zeit', 'en': 'Sustained Damage', 'fr': 'Dégâts Continus', 'ja': '継続ダメージ', 'cn': '持续伤害', 'ko': '지속 피해'}, 'title_id': 'B77', 'icon': '015000/015067_hr1.png', 'description': {'de': 'Erleidet schrittweise Schaden.', 'en': 'Sustaining damage over time.', 'fr': 'Des dégâts périodiques neutres sont subis.', 'ja': '無属性ダメージにより、ＨＰが徐々に失われる状態。', 'cn': '无属性持续伤害，体力逐渐流失', 'ko': '무속성 피해로 HP가 서서히 줄어드는 상태.'}, 'durations': [30], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Stein', 'en': 'Petrification', 'fr': 'Pétrification', 'ja': '石化', 'cn': '石化', 'ko': '석화'}, 'title_id': 'BBF', 'icon': '015000/015001_hr1.png', 'description': {'de': 'Die Versteinerung des Körpers verhindert das Ausführen jeglicher Kommandos.', 'en': 'Stone-like rigidity is preventing the execution of actions.', 'fr': 'Une rigidité semblable à celle de la pierre empêche toute action.', 'ja': '手足が石化し、行動できなくなった状態。', 'cn': '手足被石化，无法做出任何行动', 'ko': '손발이 석화되어 행동이 불가능한 상태.'}, 'durations': [12], 'debuff_in_use': 'false', 'disable': 'false', 'phases': [{'phase': '10'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}, {'title': {'de': 'Zweites Ziel', 'en': 'Second In Line', 'fr': 'Deuxième Cible', 'ja': 'セカンドターゲット', 'cn': '第二目标', 'ko': 'Unknown_BBD'}, 'title_id': 'BBD', 'icon': '015000/015402_hr1.png', 'description': {'de': 'Ist das zweite anvisierte Angriffsziel.', 'en': 'Marked as target #2.', 'fr': "Sera la deuxième cible de l'attaque.", 'ja': '2番目のターゲットとして、狙いをつけられている状態。', 'cn': '被选为了第二目标'}, 'durations': [9999], 'debuff_in_use': 'true', 'disable': 'false', 'phases': [{'phase': '03'}, {'phase': '07'}], 'roles': [{'role': 'role'}], 'tags': [{'tag': 'tag'}], 'notes': [{'note': 'note'}]}], 'sequence': [{'phase': '01', 'name': 'Anfang', 'attacks': [{'attack': 'Flammende Genesis'}, {'attack': 'Konzeptionelle Oktaflare/Konzeptionelle Tetraflare'}, {'attack': 'Vulkanfackel'}, {'attack': 'Glutfeuer'}, {'attack': 'Flammenreigen der Schöpfung'}]}, {'phase': '02', 'name': 'Form: Mensch', 'attacks': [{'attack': 'Flammender Zahn/Versengte Schwinge'}, {'attack': 'Steigende Oktaflare/Steigende Tetraflare'}, {'attack': 'Flammenviper x2'}]}, {'phase': '03', 'name': 'Form: Schlange oder Bestie', 'attacks': [{'attack': 'Mutierte Schöpfung'}, {'attack': 'Natterntritt'}, {'attack': 'Gorgons Fluch'}, {'attack': 'In die Schatten'}, {'attack': 'Versteinerung 1'}, {'attack': 'Gorgons Steinauge 1'}, {'attack': 'Gorgons Schlangengift 1'}, {'attack': 'Versteinerung 2'}, {'attack': 'Gorgons Steinauge 2'}, {'attack': 'Gorgons Schlangengift 2'}, {'attack': 'Ektothermos'}]}, {'phase': '04', 'name': 'Form: Mensch', 'attacks': [{'attack': 'Illusionsschatten'}, {'attack': 'Schöpfungsauftrag'}, {'attack': 'Flammenreigen der Schöpfung'}, {'attack': 'Mannigfaltige Flammen'}, {'attack': 'Flammender Zahn'}, {'attack': 'Versengte Schwinge'}, {'attack': 'Hemitheos-Flare'}, {'attack': 'Mannigfaltige Flammen'}, {'attack': 'Ausbreitende Viper'}, {'attack': 'Flammenreigen der Schöpfung'}, {'attack': 'Tetraflare/Ausbreitende Viper'}, {'attack': 'Flammender Zahn/Versengte Schwinge'}, {'attack': 'Steigende Oktaflare/Steigende Tetraflare'}, {'attack': 'Glutfeuer'}, {'attack': 'Flammende Genesis'}]}, {'phase': '05', 'name': 'Form: Bestie oder Schlange', 'attacks': [{'attack': 'Mutierte Schöpfung'}, {'attack': 'Fußschock'}, {'attack': 'Gleißender Amok x4'}, {'attack': 'Fataler Stampfer x4'}]}, {'phase': '06', 'name': 'Form: Mensch', 'attacks': [{'attack': 'Konzeptionelle Oktaflare/Konzeptionelle Tetraflare'}, {'attack': 'Vierfacher Feuersturm'}, {'attack': 'Feuersturm'}, {'attack': 'Lodernde Schlange 1'}, {'attack': 'Lodernde Schlange 2'}, {'attack': 'Tetraflare/Oktaflare'}, {'attack': 'Lodernde Schlange 3'}, {'attack': 'Flammenreigen der Schöpfung'}, {'attack': 'Flammender Zahn/Versengte Schwinge'}, {'attack': 'Steigende Oktaflare/Steigende Tetraflare'}, {'attack': 'Flammenviper 1'}, {'attack': 'Flammenviper 2'}]}, {'phase': '07', 'name': 'Form: Schlange 2 oder Bestie 2', 'attacks': [{'attack': 'Mutierte Schöpfung'}, {'attack': 'Natterntritt'}, {'attack': 'Gorgons Fluch'}, {'attack': 'In die Schatten'}, {'attack': 'Versteinerung'}, {'attack': 'Gorgons Speichel (Draußen)'}, {'attack': 'Gorgons Schlangengift 1'}, {'attack': 'Gorgons Steinauge 1'}, {'attack': 'Illusionsschatten'}, {'attack': 'Gorgons Schlangengift 2'}, {'attack': 'Gorgons Steinauge 2'}, {'attack': 'Gorgons Speichel (Linie)'}, {'attack': 'Gorgons Steinlicht'}, {'attack': 'Gorgons Übelgift'}, {'attack': 'Flammenviper 1'}, {'attack': 'Flammenviper 2'}]}, {'phase': '08', 'name': 'Form: Bestie 2 oder Schlange 2', 'attacks': [{'attack': 'Mutierte Schöpfung'}, {'attack': 'Fußschock'}, {'attack': 'Fußstampfer/Fußmalmer'}, {'attack': 'Konzeptionelle Diflare/Konzeptionelle Tetraflare'}, {'attack': 'Fackelnde Füße'}, {'attack': 'Flammender Pfad 1'}, {'attack': 'Steigende Diflare/Steigende Tetraflare'}, {'attack': 'Fußstampfer/Fußmalmer'}, {'attack': 'Flammender Pfad 2'}, {'attack': 'Fußstampfer/Fußmalmer'}, {'attack': 'Glutfeuer'}]}, {'phase': '09', 'name': 'Form: Mensch', 'attacks': [{'attack': 'Flammende Genesis'}, {'attack': 'Flammende Genesis (Finalangriff)'}]}, {'phase': '10', 'name': 'phase_name', 'alerts': [{'alert': 'Die folgenden Angriffe haben sind entweder unbekannt oder haben keine klare Herkunft'}], 'mechanics': [{'title': 'sequence-mechanic-01', 'notes': [{'note': 'sequence-mechanic-note-01'}]}], 'attacks': [{'attack': 'sequence-attack-01'}], 'images': [{'url': '/assets/img/test.jpg', 'alt': '/assets/img/test.jpg', 'height': '250px'}], 'videos': [{'url': 'https&#58;//ffxivguide.akurosia.de/upload/test.mp4'}]}]}
    b = {'id': '11399', 'maxHP': 55874848, 'minHP': 55874848, 'skill': {'7104': {'damage': {'max': 7346, 'min': 25}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Fußstampfer', 'type_id': '22'}, '7105': {'add_status': ['B5F'], 'damage': {'max': 64508, 'min': 178}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Fußmalmer', 'type_id': '22'}, '7106': {'damage': {'max': 7285, 'min': 35}, 'damage_type': 'None', 'element': 'None', 'name': 'Fußstampfer', 'type_id': '22'}, '7107': {'add_status': ['B5F'], 'damage': {'max': 66582, 'min': 178}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Fußmalmer', 'type_id': '22'}, '7108': {'damage_type': 'None', 'element': 'None', 'name': '', 'type_id': '21'}, '7109': {'damage': {'max': 7443, 'min': 75}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Fußschock', 'type_id': '22'}, '72CE': {'add_status': ['D56'], 'damage': {'max': 1970082, 'min': 2192}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Hemitheos-Flare', 'type_id': '22'}, '78F0': {'damage_type': 'None', 'element': 'Unaspected', 'name': 'Lodernde Schlange', 'type_id': '21'}, '78F2': {'damage_type': 'None', 'element': 'Unaspected', 'name': 'Vierfacher Feuersturm', 'type_id': '21'}, '78F7': {'damage_type': 'None', 'element': 'Unaspected', 'name': 'Vulkanfackel', 'type_id': '21'}, '7910': {'damage_type': 'None', 'element': 'None', 'name': 'Flammenreigen Der Schöpfung', 'type_id': '21'}, '7911': {'damage_type': 'None', 'element': 'None', 'name': 'Flammenreigen Der Schöpfung', 'type_id': '21'}, '7912': {'add_status': ['B5F'], 'damage': {'max': 71219, 'min': 12359}, 'damage_type': 'None', 'element': 'None', 'name': 'Flammender Zahn', 'type_id': '22'}, '7913': {'add_status': ['B5F'], 'damage': {'max': 72880, 'min': 11886}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Versengte Schwinge', 'type_id': '22'}, '7914': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptionelle Oktaflare', 'type_id': '21'}, '7915': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptionelle Tetraflare', 'type_id': '21'}, '7916': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptionelle Tetraflare', 'type_id': '21'}, '7917': {'damage_type': 'None', 'element': 'None', 'name': 'Konzeptionelle Diflare', 'type_id': '21'}, '7918': {'add_status': ['B7D'], 'damage': {'max': 2023526, 'min': 208}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Steigende Oktaflare', 'type_id': '22'}, '7919': {'add_status': ['B7D'], 'damage': {'max': 2047085, 'min': 113}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Steigende Tetraflare', 'type_id': '22'}, '791A': {'damage_type': 'None', 'element': 'None', 'name': 'Gorgons Fluch', 'type_id': '21'}, '791B': {'add_status': ['B7D'], 'damage': {'max': 4075105, 'min': 1964}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Steigende Diflare', 'type_id': '22'}, '791C': {'damage_type': 'None', 'element': 'None', 'name': 'Illusionsschatten', 'type_id': '21'}, '791D': {'damage_type': 'None', 'element': 'None', 'name': 'Oktaflare', 'type_id': '21'}, '791E': {'damage_type': 'None', 'element': 'None', 'name': 'Tetraflare', 'type_id': '21'}, '791F': {'damage_type': 'None', 'element': 'None', 'name': 'Ausbreitende Viper', 'type_id': '21'}, '7920': {'add_status': ['B7D'], 'damage': {'max': 2047395, 'min': 1582}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Ausbreitende Viper', 'type_id': '22'}, '7921': {'damage_type': 'None', 'element': 'None', 'name': 'Mannigfaltige Flammen', 'type_id': '21'}, '7922': {'damage_type': 'None', 'element': 'None', 'name': 'Mannigfaltige Flammen', 'type_id': '21'}, '7927': {'add_status': ['B5F'], 'damage': {'max': 252337, 'min': 121255}, 'damage_type': 'None', 'element': 'None', 'name': 'Glutfeuer', 'type_id': '22'}, '7929': {'add_status': ['B5F'], 'damage': {'max': 269673, 'min': 135031}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Natterntritt', 'type_id': '22'}, '792A': {'damage_type': 'None', 'element': 'None', 'name': 'In Die Schatten', 'type_id': '21'}, '792D': {'add_status': ['BBF'], 'damage': {'max': 3007, 'min': 3007}, 'damage_type': 'None', 'element': 'None', 'name': 'Gorgons Steinauge', 'type_id': '22'}, '792E': {'add_status': ['BBF'], 'damage_type': 'None', 'element': 'None', 'name': 'Gorgons Steinlicht', 'type_id': '22'}, '792F': {'add_status': ['B7D'], 'damage': {'max': 9999897, 'min': 691}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': 'Gorgons Schlangengift', 'type_id': '22'}, '7930': {'add_status': ['B7D'], 'damage': {'max': 9999897, 'min': 742}, 'damage_type': 'None', 'element': 'None', 'name': 'Gorgons Übelgift', 'type_id': '22'}, '7931': {'damage_type': 'None', 'element': 'None', 'name': 'Illusionsschatten', 'type_id': '21'}, '7933': {'damage': {'max': 34253, 'min': 9}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Gleißender Amok', 'type_id': '22'}, '7934': {'damage': {'max': 34389, 'min': 46}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Gleißender Amok', 'type_id': '22'}, '7935': {'add_status': ['D2C'], 'damage': {'max': 730935, 'min': 26}, 'damage_type': 'Magical', 'element': 'Stone', 'name': 'Erhöhung', 'type_id': '22'}, '7936': {'damage_type': 'None', 'element': 'None', 'name': 'Fataler Stampfer', 'type_id': '21'}, '7937': {'add_status': ['B7C'], 'damage': {'max': 4412821, 'min': 323}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': 'Fataler Stampfer', 'type_id': '22'}, '7938': {'damage_type': 'None', 'element': 'None', 'name': 'Fackelnde Füße', 'type_id': '21'}, '7939': {'damage_type': 'None', 'element': 'None', 'name': 'Flammender Pfad', 'type_id': '21'}, '793A': {'damage_type': 'None', 'element': 'None', 'name': 'Fußstampfer', 'type_id': '21'}, '793B': {'damage_type': 'None', 'element': 'None', 'name': '', 'type_id': '21'}, '793C': {'damage_type': 'None', 'element': 'None', 'name': '', 'type_id': '22'}, '793D': {'damage_type': 'None', 'element': 'None', 'name': 'Flammender Pfad', 'type_id': '22'}, '793E': {'damage': {'max': 196, 'min': 195}, 'damage_type': 'None', 'element': 'None', 'name': 'Flammender Pfad', 'type_id': '22'}, '793F': {'damage_type': 'None', 'element': 'None', 'name': 'Fußmalmer', 'type_id': '21'}, '7944': {'damage': {'max': 76894, 'min': 34}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Flammende Genesis', 'type_id': '22'}, '7945': {'add_status': ['B7D', 'B87'], 'damage': {'max': 136669, 'min': 220}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Flammenviper', 'type_id': '22'}, '7946': {'add_status': ['B7D', 'B87'], 'damage': {'max': 2599559, 'min': 2951}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Flammenviper', 'type_id': '22'}, '7947': {'damage': {'max': 1264099, 'min': 35}, 'damage_type': 'Magical', 'element': 'Unaspected', 'name': '', 'type_id': '21'}, '7949': {'damage': {'max': 44470, 'min': 197}, 'damage_type': 'Blunt', 'element': 'Unaspected', 'name': '', 'type_id': '21'}, '794A': {'damage_type': 'Piercing', 'element': 'Water', 'name': 'Flammende Genesis', 'type_id': '22'}, '794B': {'damage_type': 'None', 'element': 'None', 'name': 'Mutierte Schöpfung', 'type_id': '21'}, '794C': {'damage_type': 'None', 'element': 'None', 'name': 'Mutierte Schöpfung', 'type_id': '21'}, '794F': {'damage_type': 'None', 'element': 'None', 'name': 'Schöpfungsauftrag', 'type_id': '21'}, '7954': {'damage': {'max': 21126, 'min': 19}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Feuersturm', 'type_id': '22'}, '7955': {'damage': {'max': 34015, 'min': 153}, 'damage_type': 'None', 'element': 'None', 'name': 'Gleißender Amok', 'type_id': '22'}, '79EA': {'damage': {'max': 76303, 'min': 584}, 'damage_type': 'Magical', 'element': 'Fire', 'name': 'Ektothermos', 'type_id': '22'}, '7A04': {'damage_type': 'None', 'element': 'None', 'name': 'Fußstampfer', 'type_id': '21'}, '7A05': {'damage_type': 'None', 'element': 'None', 'name': 'Fußmalmer', 'type_id': '21'}}, 'status': {'8E1': {'duration': [9999], 'icon': '', 'name': '', 'type_id': '30'}, 'B5F': {'duration': [1, 5, 13, 16, 30], 'icon': 'ui/icon/015000/015520_hr1.png', 'name': 'Schaden -', 'type_id': '30'}, 'B77': {'duration': [30], 'icon': 'ui/icon/015000/015067_hr1.png', 'name': 'Schaden Über Zeit', 'type_id': '30'}, 'B7C': {'duration': [9], 'icon': 'ui/icon/015000/015053_hr1.png', 'name': 'Erhöhte Physische Verwundbarkeit', 'type_id': '30'}, 'B7D': {'duration': [2, 4, 7], 'icon': 'ui/icon/015000/015057_hr1.png', 'name': 'Erhöhte Magie-Verwundbarkeit', 'type_id': '30'}, 'B87': {'duration': [15], 'icon': 'ui/icon/015000/015530_hr1.png', 'name': 'Blutung', 'type_id': '30'}, 'BBF': {'duration': [12], 'icon': 'ui/icon/015000/015001_hr1.png', 'name': 'Stein', 'type_id': '30'}, 'D2C': {'duration': [12], 'icon': 'ui/icon/015000/015722_hr1.png', 'name': 'Erdresistenz - (Stark)', 'type_id': '30'}, 'D56': {'duration': [7], 'icon': 'ui/icon/015000/015057_hr1.png', 'name': 'Erhöhte Magie-Verwundbarkeit', 'type_id': '30'}}, 'text': ['Dieser Kerker wird euer Grab sein!', 'Züngelnde Flammen!', 'Wetze deine reißenden Klauen an ihnen!', 'Seht, was aus mir geworden ist!', 'Wie fühlt es sich an, malträtiert zu werden?', 'Nur zu, lasst euch zermalmen! ', 'Nur ein Narr stellt sich einem Gott!', 'Mein Wunsch wird schon bald in Erfüllung gehen.', 'In der Glut sollt ihr schmoren!', 'Zerfleische sie, bis nichts mehr übrig ist!', 'An meine Seite, Bestie des Feuers!', 'Sterbt!', 'Eure niedere Existenz hat nun ein Ende.', 'Es ist an der Zeit, meine Grenzen hinter mir zu lassen! ', 'Und wenn ich dafür diesen Körper opfern muss.', 'Meine neue Gestalt wird alles in den Schatten stellen!', 'Verfaulen sollt ihr, allesamt!', 'Athena ... wo ist Athena?', 'Niedere ... Kreaturen!', 'Wie kleine, tanzende Marionetten ...', 'Werdet ... zu einem Teil von mir!']}
    c = "bosse"
    print(merge_attacks(a, b, c))
