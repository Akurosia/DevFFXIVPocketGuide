#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
from ffxiv_aku import storeFilesInTmp, get_any_Logdata, loadDataTheQuickestWay, print_color_green, os, writeJsonFile, readJsonFile

try:
    from python_scripts.constants import EXAMPLE_SEQUENCE, EXAMPLE_ADD_SEQUENCE, LANGUAGES
    #from python_scripts.custom_logger import *
    from python_scripts.helper import getImage
    from python_scripts.guide_helper import setMultipleLanguageStrings, ugly_fix_enemy_data, workOnOldEnemies, workOnLogDataEnemies, logdata_lower, sort_status_ids
except Exception:
    from constants import EXAMPLE_SEQUENCE, EXAMPLE_ADD_SEQUENCE, LANGUAGES
    #from custom_logger import *
    from helper import getImage
    from guide_helper import setMultipleLanguageStrings, ugly_fix_enemy_data, workOnOldEnemies, workOnLogDataEnemies, logdata_lower, sort_status_ids

storeFilesInTmp(True)
# storeFilesInTmp(True)
logdata = get_any_Logdata()
#if os.path.exists("tmp/19/logdata_de.json"):
#    logdata = readJsonFile("tmp/19/logdata_de.json")
#else:
#    logdata = get_any_Logdata()
#    writeJsonFile("tmp/19/logdata_de.json", logdata)
status = loadDataTheQuickestWay("status_all.json", translate=True)

disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True


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
                        guide_data += f"          - url: \"{image['url']}\"\n"
                        guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                        guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

                if step.get("videos", None):
                    guide_data += "        videos:\n"
                    for video in step["videos"]:
                        guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Debuff(guide_data, debuff, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{debuff["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Status_{debuff["title"]["en"]}_Name"] = debuff["title"][lang]
    guide_data += f'        title_id: "{debuff["title_id"]}"\n'
    guide_data += f'        icon: "{getImage(debuff["icon"])}"\n'
    guide_data += f'        description: "{debuff["description"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Status_{debuff["title"]["en"]}_Desc"] = debuff["description"][lang]
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
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"][lang]
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
            guide_data += '            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += '        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'
    return guide_data


def add_variation_Attack(guide_data, attack, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{attack["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"][lang]
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
            guide_data += '            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
            #guide_data += f'          - title:\n'
            #guide_data = setMultipleLanguageStrings(guide_data, "title", variation, "              ")
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
                    guide_data += '                name:\n'
                    for lang in LANGUAGES:
                        guide_data += f'                 {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
            guide_data += f'            height: "{image.get("height", None) or "350px"}"\n'

    if attack.get('videos', None):
        guide_data += '        videos:\n'
        for video in attack.get('videos', {}):
            guide_data += f'          - url: "{video["url"]}"\n'

    return guide_data


def add_combo_Attack(guide_data, attack, enemy_type, enemy_name_en, content_translations):
    guide_data += f'      - title: "{attack["title"]["en"]}"\n'
    for lang in LANGUAGES:
        content_translations[lang][f"{enemy_type.title()}_{enemy_name_en}_Attack_{attack["title"]["en"]}"] = attack["title"][lang]
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
            guide_data += '            name:\n'
            for lang in LANGUAGES:
                guide_data += f'               {lang}: "' + s[f"Name_{lang}"] + '"\n'

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
            guide_data += f'          - url: "{image["url"]}"\n'
            guide_data += f'            alt: "{image.get("alt", None) or image["url"]}"\n'
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
                guide_data += f"          - url: \"{image['url']}\"\n"
                guide_data += f"            alt: \"{image.get('alt', image['url'])}\"\n"
                guide_data += f"            height: \"{image.get('height', '250px')}\"\n"

        if phase.get('videos', None):
            guide_data += "        videos:\n"
            for video in phase['videos']:
                guide_data += f"          - url: \"{video['url']}\"\n"
    return guide_data


def add_Enemy(enemy_data, enemy_type, new_enemy_data, content_translations):
    guide_data = ""
    enemy_data = ugly_fix_enemy_data(enemy_data, new_enemy_data)
    guide_data += '  - title:\n'
    for lang in LANGUAGES:
        #print(f"{enemy_data['title']} -> {enemy_type} -> ")
        content_translations[lang][f"{enemy_type.title()}_{enemy_data['title']['en']}_Name"] = enemy_data['title'][lang]
    guide_data = setMultipleLanguageStrings(guide_data, "title", enemy_data, "      ")

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
    if enemy_data.get("sequence", None):
        guide_data = add_Sequence(guide_data, enemy_data)
    else:
        if enemy_type == "bosse":
            guide_data = add_Sequence(guide_data, EXAMPLE_SEQUENCE)
        else:
            guide_data = add_Sequence(guide_data, EXAMPLE_ADD_SEQUENCE)
    return guide_data


def check_Enemy(entry, enemy_type, logdata_instance_content, old_enemies, content_translations):
    guide_data = ""
    if old_enemies == {} and logdata == {}:
        return guide_data
    guide_data += "bosses:\n" if enemy_type == "bosse" else "adds:\n"
    guide_data, empty_enemy_available = workOnOldEnemies(guide_data, entry, enemy_type, old_enemies, logdata_instance_content, content_translations, callback=add_Enemy)
    #print_color_yellow(guide_data, disable_yellow_print)
    guide_data += workOnLogDataEnemies(entry, enemy_type, logdata_instance_content, empty_enemy_available, content_translations, callback=add_Enemy)
    #print_color_blue(guide_data, disable_blue_print)
    return guide_data


# Notizen, Bosse und Adds
def addGuide(entry, old_data, logdata_instance_content, content_translations):
    guide_data = ""
    # add mechanics
    guide_data += check_Mechanics(entry, old_data.get('mechanics', None))
    print_color_green(f"Work on '{entry['title_de']}'", disable_green_print)
    guide_data += check_Enemy(entry, "bosse", logdata_instance_content, old_data.get('bosses', {}), content_translations)
    guide_data += check_Enemy(entry, "adds", logdata_instance_content, old_data.get('adds', {}), content_translations)
    return guide_data


if __name__ == "__main__":
    pass
