#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import re
from ffxiv_aku import print_color_green, print_color_red, readJsonFile, print_color_yellow
from typing import Any
try:
    from python_scripts.constants import EXAMPLE_SEQUENCE, EXAMPLE_ADD_SEQUENCE, LANGUAGES
    #from python_scripts.custom_logger import *
    from python_scripts.helper import getImage
    from python_scripts.fileimports import logdata, status, ces, ces_type, ces_trans, fates, fates_trans, ENTRY_DATA, npcyell, instancecontenttextdata, fateevent
    from python_scripts.guide_helper import ugly_fix_enemy_data, workOnOldEnemies, workOnLogDataEnemies, sort_status_ids
except Exception:
    from constants import EXAMPLE_SEQUENCE, EXAMPLE_ADD_SEQUENCE, LANGUAGES
    #from custom_logger import *
    from helper import getImage
    from fileimports import logdata, status, ces, ces_type, ces_trans, fates, fates_trans, ENTRY_DATA, npcyell, instancecontenttextdata, fateevent
    from guide_helper import ugly_fix_enemy_data, workOnOldEnemies, workOnLogDataEnemies, sort_status_ids

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True


def check_Mechanics(entry: ENTRY_DATA, old_mechanics):
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
    if data.get("preset"):
        guide_data += f"  - preset: \"{data['preset']}\"\n"
    else:
        guide_data += "  - title:\n"
        x = data['title'] if isinstance(data['title'], dict) else {'de': data['title']}
        for lang in LANGUAGES:
            z = x.get(lang, x['de']).replace('"', '\\"').strip()
            guide_data += f"      {lang}: \"{z}\"\n"
        if x.get('icon', None):
            guide_data += f"      icon: \"{x['icon']}\"\n"
        if data.get("steps", None):
            guide_data += "    steps:\n"
            for step in data["steps"]:
                guide_data += f"      - step: \"{int(step['step']):02d}\"\n"

                if step.get("notes", None):
                    guide_data += "        notes:\n"
                    for note in step["notes"]:
                        guide_data += "          - note:\n"
                        y = note['note'] if isinstance(note['note'], dict) else {'de': note['note']}
                        for lang in LANGUAGES:
                            w = y.get(lang, y['de']).replace('"', '\\"').strip()
                            guide_data += f"              {lang}: \"{w}\"\n"

                if step.get("images", None):
                    guide_data += "        images:\n"
                    for image in step["images"]:
                        guide_data += f"          - url: \"{getImage(image['url'])}\"\n"
                        guide_data += f"            alt: \"{getImage(image.get('alt', image['url']))}\"\n"
                        guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

                if step.get("videos", None):
                    guide_data += "        videos:\n"
                    for video in step["videos"]:
                        guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Debuff(guide_data, debuff, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{debuff["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Status_{debuff["title"]["en"]}_Name"] = debuff["title"].get(lang, "")
    guide_data += f'        title_id: "{debuff["title_id"]}"\n'
    guide_data += f'        icon: "{getImage(debuff["icon"])}"\n'
    guide_data += f'        description: "{debuff["description"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Status_{debuff["title"]["en"]}_Desc"] = debuff["description"].get(lang, "")
    if debuff.get("durations", None):
        guide_data += f'        durations: {debuff["durations"]}\n'
    guide_data += f'        debuff_in_use: "{debuff["debuff_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{debuff["disable"] or "false"}"\n'
    #guide_data += f'        damage_type: "{debuff["damage_type"] or "None"}"\n'

    if debuff.get('phases', None):
        guide_data += '        phases:\n'
        for phase in debuff.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if debuff["title"]['de'].startswith("Unknown_"):
        return guide_data

    if debuff.get('roles', None):
        guide_data += '        roles:\n'
        for role in debuff.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if debuff.get('tags', None):
        guide_data += '        tags:\n'
        for tag in debuff.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'

    if debuff.get('notes', None):
        guide_data += '        notes:\n'
        for note in debuff.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if debuff.get('videos', None):
        guide_data += '        videos:\n'
        for video in debuff.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_regular_Attack(guide_data, attack, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{attack["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"].get(lang, "")
    guide_data += f'        title_id: "{attack["title_id"]}"\n'
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'
    guide_data += f'        damage_type: "{attack.get("damage_type", None)}"\n'

    if attack.get('add_status', None):
        guide_data += '        add_status:\n'
        sort_attacks = sort_status_ids(attack["add_status"])
        for e in sort_attacks:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name: "{s[f"Name_en"]}"\n'
            #for lang in LANGUAGES:
            #    guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

    if attack.get('damage', None):
        guide_data += '        damage:\n'
        try:
            guide_data += f'          - min: {attack["damage"]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"]["max"] or "None"}\n'
        except TypeError:
            guide_data += f'          - min: {attack["damage"][0]["min"] or "None"}\n'
            guide_data += f'          - max: {attack["damage"][1]["max"] or "None"}\n'

    if attack.get('phases', None):
        guide_data += '        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if attack["title"]['de'].startswith("Unknown_"):
        return guide_data

    if attack.get('roles', None):
        guide_data += '        roles:\n'
        for role in attack.get('roles', {}):
            guide_data += f'          - role: "{role["role"]}"\n'

    if attack.get('tags', None):
        guide_data += '        tags:\n'
        for tag in attack.get('tags', {}):
            guide_data += f'          - tag: "{tag["tag"]}"\n'
        if attack.get('single_or_aoe', None):
            x = "AoE" if attack["single_or_aoe"] == "22" else "Single"
            guide_data += f'          - tag: "{x}"\n'

    if attack.get('notes', None):
        guide_data += '        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += '        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{getImage(image["url"])}"\n'
            guide_data += f'            alt: "{getImage(image.get("alt", None)) or getImage(image["url"])}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += '        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_variation_Attack(guide_data, attack, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{attack["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"].get(lang, "")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack.get("disable", "false")}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('add_status', None):
        guide_data += '        add_status:\n'
        sort_attacks = sort_status_ids(attack["add_status"])
        for e in sort_attacks:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name: "{s[f"Name_en"]}"\n'
            #for lang in LANGUAGES:
            #    guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

    if attack.get('phases', None):
        guide_data += '        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += '        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('variation', None):
        guide_data += '        variation:\n'
        for variation in attack.get('variation', {}):
            guide_data += f'          - title_id: "{variation["title_id"]}"\n'
            guide_data += f'            damage_type: "{variation.get("damage_type", None)}"\n'

            if variation.get('add_status', None):
                guide_data += '            add_status:\n'
                sort_attacks = sort_status_ids(variation["add_status"])
                for e in sort_attacks:
                    try:
                        s = status[str(int(e, 16))]
                    except Exception:
                        s = status[str(int(str(e['status']), 16))]
                    guide_data += f'              - status: {s["0xID"]}\n'
                    guide_data += f'                icon: "{getImage(s["Icon"])}"\n'
                    guide_data += f'                name: "{s[f"Name_en"]}"\n'
                    #for lang in LANGUAGES:
                    #    guide_data += f'                 {lang}: "' + s[f"Name_{lang}"] + '"\n'

            # print_color_yellow(variation)
            if variation.get('damage', None):
                guide_data += '            damage:\n'
                try:
                    guide_data += f'              - min: {variation["damage"]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"]["max"] or "None"}\n'
                except TypeError:
                    guide_data += f'              - min: {variation["damage"][0]["min"] or "None"}\n'
                    guide_data += f'              - max: {variation["damage"][1]["max"] or "None"}\n'

            if variation.get('roles', None):
                guide_data += '            roles:\n'
                for role in variation.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if variation.get('tags', None):
                guide_data += '            tags:\n'
                for tag in variation.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'
                if variation.get('single_or_aoe', None):
                    x = "AoE" if variation["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

            if variation.get('notes', None) and enemy_type != "adds":
                guide_data += '            notes:\n'
                for note in variation.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += '        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{getImage(image["url"])}"\n'
            guide_data += f'            alt: "{getImage(image.get("alt", None)) or getImage(image["url"])}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += '        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_combo_Attack(guide_data, attack, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{attack["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"].get(lang, "")
    guide_data += f'        attack_in_use: "{attack["attack_in_use"] or "false"}"\n'
    guide_data += f'        disable: "{attack["disable"] or "false"}"\n'
    guide_data += f'        type: "{attack["type"] or "regular"}"\n'

    if attack.get('add_status', None):
        guide_data += '        add_status:\n'
        sort_attacks = sort_status_ids(attack["add_status"])
        for e in sort_attacks:
            s = status[str(int(e, 16))]
            guide_data += f'          - status: {e}\n'
            guide_data += f'            icon: "{getImage(s["Icon"])}"\n'
            guide_data += f'            name: "{s[f"Name_en"]}"\n'
            #for lang in LANGUAGES:
            #    guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

    if attack.get('phases', None):
        guide_data += '        phases:\n'
        for phase in attack.get('phases', {}):
            guide_data += f'          - phase: "{int(phase["phase"]):02d}"\n'

    if (attack.get('notes', None) and enemy_type != "adds") or (attack.get('notes', None) and enemy_type == "adds" and attack.get('notes', [{}])[0].get("note", None) != "Variation-note BIG"):
        guide_data += '        notes:\n'
        for note in attack.get('notes', {}):
            guide_data += f'          - note: "{note["note"]}"\n'

    if attack.get('combo', None):
        guide_data += '        combo:\n'
        for combo in attack.get('combo', {}):
            guide_data += f'          - title: "{combo["title"]}"\n'
            guide_data += f'            title_id: "{combo["title_id"]}"\n'
            guide_data += f'            damage_type: "{combo["damage_type"]}"\n'

            if combo.get('damage', None):
                guide_data += '            damage:\n'
                guide_data += f'              - min: {combo["damage"]["min"] or "None"}\n'
                guide_data += f'              - max: {combo["damage"]["max"] or "None"}\n'

            if combo.get('roles', None):
                guide_data += '            roles:\n'
                for role in combo.get('roles', {}):
                    guide_data += f'              - role: "{role["role"]}"\n'

            if combo.get('tags', None):
                guide_data += '            tags:\n'
                for tag in combo.get('tags', {}):
                    guide_data += f'              - tag: "{tag["tag"]}"\n'
                if combo.get('single_or_aoe', None):
                    x = "AoE" if combo["single_or_aoe"] == "22" else "Single"
                    guide_data += f'              - tag: "{x}"\n'

            if combo.get('notes', None) and enemy_type != "adds":
                guide_data += '            notes:\n'
                for note in combo.get('notes', {}):
                    guide_data += f'              - note: "{note["note"]}"\n'

    if attack.get('images', None):
        guide_data += '        images:\n'
        for image in attack.get('images', {}):
            guide_data += f'          - url: "{getImage(image["url"])}"\n'
            guide_data += f'            alt: "{getImage(image.get("alt", None)) or getImage(image["url"])}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += '        videos:\n'
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
                    guide_data += "            notes:\n"
                    for note in mechanic['notes']:
                        guide_data += f"              - note: \"{note['note']}\"\n"

        if phase.get('attacks', None):
            guide_data += "        attacks:\n"
            for attack in phase['attacks']:
                guide_data += f"          - attack: \"{attack['attack']}\"\n"

        if phase.get('images', None):
            guide_data += "        images:\n"
            for image in phase['images']:
                guide_data += f"          - url: \"{getImage(image['url'])}\"\n"
                guide_data += f"            alt: \"{getImage(image.get('alt', image['url']))}\"\n"
                guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

        if phase.get('videos', None):
            guide_data += "        videos:\n"
            for video in phase['videos']:
                guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Enemy(enemy_data, enemy_type, new_enemy_data, content_translations):
    guide_data = ""
    enemy_data = ugly_fix_enemy_data(enemy_data, new_enemy_data)
    enemy_name_en = enemy_data['title']['en']
    guide_data += f'  - title:\n'
    #print(enemy_name_en)
    #print(new_enemy_data)
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Name"] = enemy_data['title'].get(lang, "")
        if enemy_data is None:
            guide_data += f'      {lang}: "{enemy_data["title"][lang]}"\n'
        elif type(enemy_data["title"]) == str or type(enemy_data["title"]) is None:
            continue
        elif enemy_data["title"].get(f"{lang}", None):
            guide_data += f'      {lang}: "{enemy_data["title"][lang]}"\n'


    if isinstance(enemy_data.get("enemy_id", ""), list):
        hex_id_list = [str(hex(int(i))).replace("0x", "").upper() for i in enemy_data.get("enemy_id", [])]
        guide_data += f'    enemy_id: "{", ".join(enemy_data.get("enemy_id", ""))}"\n'
        guide_data += f'    enemy_hex_id: "{", ".join(hex_id_list)}"\n'
    else:
        hex_id = "" if enemy_data.get("enemy_id", "") == "" else str(hex(int(enemy_data.get("enemy_id", 0)))).replace("0x", "").upper()
        guide_data += f'    enemy_id: "{enemy_data.get("enemy_id", "")}"\n'
        guide_data += f'    enemy_hex_id: "{hex_id}"\n'
    guide_data += f'    id: "{enemy_data["id"]}"\n'

    if enemy_data.get('hp', None):
        guide_data += '    hp:\n'
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
                guide_data = add_regular_Attack(guide_data, attack, enemy_type, enemy_data['title']['en'], content_translations)
            elif attack["type"] == "variation":
                guide_data = add_variation_Attack(guide_data, attack, enemy_type, enemy_data['title']['en'], content_translations)
            elif attack["type"] == "combo":
                guide_data = add_combo_Attack(guide_data, attack, enemy_type, enemy_data['title']['en'], content_translations)

    if enemy_data.get("debuffs", None):
        guide_data += '    debuffs:\n'
        for debuff in enemy_data["debuffs"]:
            guide_data = add_Debuff(guide_data, debuff, enemy_type, enemy_data['title']['en'], content_translations)

    #Handle text
    if enemy_data.get("text", None):
        try:
            del enemy_data['text']['old']
        except: pass
        guide_data += '    text:\n'
        for cat, text_ids in enemy_data["text"].items():
            if cat == "old":
                continue
            if text_ids == []:
                continue
            guide_data += f'      {cat[:-4].title()}:\n'
            for _id in text_ids:
                guide_data += f'        - id: "{_id}"\n'
                guide_data += f'          text: "{getTextFromCatAndID(cat, _id, content_translations)}"\n'
    if enemy_data.get("sequence", None):
        guide_data = add_Sequence(guide_data, enemy_data)
    else:
        if enemy_type == "bosse":
            guide_data = add_Sequence(guide_data, EXAMPLE_SEQUENCE)
        else:
            guide_data = add_Sequence(guide_data, EXAMPLE_ADD_SEQUENCE)
    return guide_data

enemy_line_itterator: dict[str, Any] = {
    "Npcyell": npcyell,
    "Instancecontenttextdata": instancecontenttextdata,
    "Fateevent": fateevent,
}
def getTextFromCatAndID(cat: str, _id: str, content_translations: dict[str, Any]) -> str:
    global enemy_line_itterator
    n_cat = cat[:-4].title()
    if n_cat != "Fateevent":
        text: str = enemy_line_itterator[n_cat][_id]['Text_en'].replace("\n\n", " ").replace("\n", "")
        for lang in LANGUAGES:
            content_translations[lang][f"{n_cat}_{_id}_Text"] = enemy_line_itterator[n_cat][_id][f'Text_{lang}'].replace("\n\n", " ").replace("\n", "")
    else:
        text: str = enemy_line_itterator[n_cat][_id]['Text_0_en'].replace("\n\n", " ").replace("\n", "")
        for lang in LANGUAGES:
            content_translations[lang][f"{n_cat}_{_id}_Text"] = enemy_line_itterator[n_cat][_id][f'Text_0_{lang}'].replace("\n\n", " ").replace("\n", "")
    return text

def check_Enemy(entry: ENTRY_DATA, enemy_type, logdata_instance_content, old_enemies, content_translations):
    guide_data = ""
    if old_enemies == {} and logdata == {}:
        return guide_data
    guide_data += "bosses:\n" if enemy_type == "bosse" else "adds:\n"
    guide_data, empty_enemy_available = workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content, content_translations, callback=add_Enemy)
    #print_color_yellow(guide_data, disable_yellow_print)
    guide_data += workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available, content_translations, callback=add_Enemy)
    #print_color_blue(guide_data, disable_blue_print)
    return guide_data


fatetypes: dict[str, str] = {
    "ui/icon/060000/060721.tex": "Gegner Besiegen",
    "ui/icon/060000/060722.tex": "Boss besiegen",
    "ui/icon/060000/060723.tex": "Sammeln",
    "ui/icon/060000/060724.tex": "Verteidigen",
    "ui/icon/060000/060725.tex": "Eskortieren",
    "ui/icon/060000/060726.tex": "Event",
    "ui/icon/060000/060727.tex": "Verfolgen",
    "ui/icon/060000/060728.tex": "Festival",

    "ui/icon/060000/060852.tex": "Boss besiegen",

    "ui/icon/063000/063909.tex": "CE Boss besiegen",
    "ui/icon/063000/063910.tex": "CE Solo Kampf",
    "ui/icon/063000/063911.tex": "CE Gegner Wellen",

    "ui/icon/063000/063914.tex": "Gegner Besiegen",
    "ui/icon/063000/063915.tex": "Boss besiegen",
    "ui/icon/063000/063916.tex": "Sammeln",
    "ui/icon/063000/063917.tex": "Verteidigen",

    "ui/icon/060000/060806.tex": "Unkown_060806"
}
fateNames: dict[str, str] = {
    "Gegner Besiegen": "Slay enemies",
    "Boss besiegen": "Notorious monster",
    "Sammeln": "Gather",
    "Verteidigen": "Defense",
    "Eskortieren": "Escort",
    "Event": "Event",
    "Verfolgen": "Chase",
    "Festival": "Festival",
    "CE Boss besiegen": "CE Notorious monster",
    "CE Solo Kampf": "CE Solo Fight",
    "CE Gegner Wellen": "CE Eney Waves",
    "Unkown_060806": "Unkown_060806"
}
additional_fate_data: dict[str, Any] = readJsonFile("python_scripts/FatesFromConsoleWiki.json")
def add_leves(lfates: list[str], content_translations: dict[str, Any], entry) -> str:
    lguide_data: str = ""
    name = entry['titles']['en'].replace("the Forbidden Land, ", "")
    if name.startswith("the "):
        name = name.replace("the ", "The ")
    add_data: Any = additional_fate_data.get(name, None)
    if not lfates and not add_data:
        return lguide_data
    if not lfates:
        lfates = []

    ce_ids = []
    if add_data:
        fate_ids: list[str] = [k for k,v in add_data.items() if v.get("Fate Type", "") != "CE"]
        ce_ids: list[str] = [k for k,v in add_data.items() if v.get("Fate Type", "") == "CE"]
        lfates = sorted(list(set(lfates + fate_ids)))

    #sort fates by type
    fates_by_type: dict[str, list[str]] = {}
    for fate_id in lfates:
        #print(fate_id)
        _id: str = fates[fate_id]['Icon']['Objective'] # type: ignore
        _type = fatetypes[_id]
        if not fates_by_type.get(_type, None):
            fates_by_type[_type] = []
        fates_by_type[_type].append(fate_id)

    ces_by_type: dict[str, list[str]] = {}
    for ce_id in ce_ids:
        #print(ce_id)
        _id: str = ces_type[ces[ce_id]['EventType'].replace("DynamicEventType#", "")]['Icon']['Objective']['1'] # type: ignore
        _type = fatetypes[_id]
        if not ces_by_type.get(_type, None):
            ces_by_type[_type] = []
        ces_by_type[_type].append(ce_id)

    #add fates by type
    lguide_data += "fates:\n"
    for fatetype, fate_data in fates_by_type.items():
        lguide_data += f'  - title:\n'
        lguide_data += f'      de: "{fatetype}"\n'
        lguide_data += f'      en: "{fateNames[fatetype]}"\n'
        content_translations['de'][f"FATEs_{fateNames[fatetype]}_Name"] = fatetype
        lguide_data += f'    fates:\n'
        for fate_id in fate_data:
            name_en = fates_trans[fate_id]["Name_en"]
            desc_en = fates_trans[fate_id]['Description_en']
            lguide_data += f'      - title: "{name_en}"\n'
            lguide_data += f'        title_id: "{fate_id}"\n'
            lguide_data += f'        icon: "{getImage(fates[fate_id]['Icon']['Objective'])}"\n'
            lguide_data += f'        description: "{desc_en}"\n'
            lguide_data += '        phases:\n'
            lguide_data += '          - phase: "01"\n'
            lguide_data += '        roles:\n'
            lguide_data += f'          - role: "Lvl: {fates[fate_id]['ClassJobLevel']['Value']}"\n'
            lguide_data += f'          - role: "Lvl-Sync: {fates[fate_id]['ClassJobLevel']['Max']}"\n'
            if add_data is None:
                print(f"No additional Fate data for {name} -> FateID: {fate_id}")
            elif add_data.get(fate_id, None):
                lguide_data += '        tags:\n'
                if add_data[fate_id].get('Experience', None):
                    lguide_data += f'          - tag: "EXP: {add_data[fate_id]['Experience']}"\n'
                if add_data[fate_id].get('Elemental EXP', None):
                    lguide_data += f'          - tag: "EXP: {add_data[fate_id]['Elemental EXP']}"\n'
                if add_data[fate_id].get('Gil', None):
                    lguide_data += f'          - tag: "{add_data[fate_id]['Gil']}"\n'
                    lguide_data += f'            icon: "{getImage("065000/065002_hr1.webp")}"\n'
                    lguide_data += f'            icon-title: "Gil"\n'
                lguide_data += f'          - tag: "Location: {add_data[fate_id]['Location']}"\n'
                if add_data[fate_id].get('Company Seals', None):
                    lguide_data += f'          - tag: "{add_data[fate_id]['Company Seals']}"\n'
                    lguide_data += f'            icon: "{getImage("065000/065004_hr1.webp")}"\n'
                    lguide_data += f'            icon-title: "Company Seals"\n'
                if add_data[fate_id].get('Gemstones', None):
                    lguide_data += f'          - tag: "{add_data[fate_id]['Gemstones']}"\n'
                    lguide_data += f'            icon: "{getImage("065000/065071_hr1.webp")}"\n'
                    lguide_data += f'            icon-title: "Gemstones"\n'
                if add_data[fate_id].get('Lockboxes/Crystals', None):
                    text = add_data[fate_id]['Lockboxes/Crystals']
                    text = re.sub(r"^(\d+)   ", r"\1 ", text)
                    text = re.sub(r"(\d+)   ", r" / \1 ", text)
                    lguide_data += f'          - tag: "Lockboxes/Crystals: {text}"\n'
                if add_data[fate_id].get('Notable Rewards', None):
                    text = add_data[fate_id]['Notable Rewards']
                    text = re.sub(r"^(\d+)   ", r"\1 ", text)
                    text = re.sub(r"(\d+)   ", r" / \1 ", text)
                    lguide_data += f'          - tag: "Notable Rewards: {text}"\n'
                if add_data[fate_id].get('Notorious Monster', None):
                    lguide_data += f'          - tag: "Notorious Monster: {add_data[fate_id]['Notorious Monster']}"\n'
                if add_data[fate_id].get('Spawn Mob', None):
                    lguide_data += f'          - tag: "Spawn Mob: {add_data[fate_id]['Spawn Mob']}"\n'
                if add_data[fate_id].get('Tomestones', None):
                    lguide_data += f'          - tag: "{add_data[fate_id]['Tomestones']}"\n'
                    lguide_data += f'            icon: "{getImage("065000/065023_hr1.webp")}"\n'
                    lguide_data += f'            icon-title: "Tomestones"\n'
            else:
                print(f"No additional Fate data for {name} -> FateID: {fate_id}")
            for lang in LANGUAGES:
                content_translations[lang][f"FATEs_{fateNames[fatetype]}_{name_en}_Name"] = fates_trans[fate_id][f'Name_{lang}']
                content_translations[lang][f"FATEs_{fateNames[fatetype]}_{name_en}_Desc"] = fates_trans[fate_id][f'Description_{lang}']
        lguide_data += '    sequence:\n'
        lguide_data += '      - phase: "01"\n'

    for cetype, ce_data in ces_by_type.items():
        lguide_data += f'  - title:\n'
        lguide_data += f'      de: "{cetype}"\n'
        lguide_data += f'      en: "{fateNames[cetype]}"\n'
        content_translations['de'][f"FATEs_{fateNames[cetype]}_Name"] = cetype
        lguide_data += f'    fates:\n'
        for ce_id in ce_data:
            name_en = ces_trans[ce_id]["Name_en"]
            desc_en = ces_trans[ce_id]['Description_en']
            lguide_data += f'      - title: "{name_en}"\n'
            lguide_data += f'        title_id: "{ce_id}"\n'
            lguide_data += f'        icon: "{getImage(ces_type[ces[ce_id]["EventType"].replace("DynamicEventType#", "")]["Icon"]["Objective"]["1"])}"\n'
            lguide_data += f'        description: "{desc_en}"\n'
            lguide_data += '        phases:\n'
            lguide_data += '          - phase: "01"\n'
            lguide_data += '        tags:\n'
            if add_data[ce_id].get('Lockboxes/Crystals', None):
                text = add_data[ce_id]['Lockboxes/Crystals']
                text = re.sub(r"^(\d+)   ", r"\1 ", text)
                text = re.sub(r"(\d+)   ", r" / \1 ", text)
                lguide_data += f'          - tag: "Lockboxes/Crystals: {text}"\n'
            if add_data[ce_id].get('Notable Rewards', None):
                text = add_data[ce_id]['Notable Rewards']
                text = re.sub(r"^(\d+)   ", r"\1 ", text)
                text = re.sub(r"(\d+)   ", r" / \1 ", text)
                lguide_data += f'          - tag: "Notable Rewards: {text}"\n'
            if add_data[ce_id].get('Notorious Monster', None):
                lguide_data += f'          - tag: "Notorious Monster: {add_data[ce_id]['Notorious Monster']}"\n'
            if add_data[ce_id].get('Spawn Mob', None):
                lguide_data += f'          - tag: "Spawn Mob: {add_data[ce_id]['Spawn Mob']}"\n'
            if add_data[ce_id].get('Tomestones', None):
                lguide_data += f'          - tag: "{add_data[ce_id]['Tomestones']}"\n'
                lguide_data += f'            icon: "{getImage("065000/065023_hr1.webp")}"\n'
                lguide_data += f'            icon-title: "Tomestones"\n'
            for lang in LANGUAGES:
                content_translations[lang][f"FATEs_{fateNames[cetype]}_{name_en}_Name"] = ces_trans[ce_id][f'Name_{lang}']
                content_translations[lang][f"FATEs_{fateNames[cetype]}_{name_en}_Desc"] = ces_trans[ce_id][f'Description_{lang}']
        lguide_data += '    sequence:\n'
        lguide_data += '      - phase: "01"\n'
    return lguide_data


# Notizen, Bosse und Adds
def addGuide(entry: ENTRY_DATA, old_data, logdata_instance_content, lfates, content_translations):
    guide_data = ""
    # add mechanics
    guide_data += check_Mechanics(entry, old_data.get('mechanics', None))
    print_color_green(f"Work on '{entry['titles']['de']}'", disable_green_print)
    guide_data += check_Enemy(entry, "bosse", logdata_instance_content, old_data.get('bosses', {}), content_translations)
    guide_data += check_Enemy(entry, "adds", logdata_instance_content, old_data.get('adds', {}), content_translations)
    guide_data += add_leves(lfates, content_translations, entry)
    return guide_data


if __name__ == "__main__":
    pass
