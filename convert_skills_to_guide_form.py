#!/usr/bin/env python3
# coding: utf8
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python_module'))
from ffxiv_aku import *
import pyaml
import yaml
import json
from collections import OrderedDict
from operator import getitem


skills = get_skills_for_player()
logdata = get_any_Logdata()
cj = loadDataTheQuickestWay("classjob_all.json", translate=True)
cjs = loadDataTheQuickestWay("ClassJob.de.json")
actions = loadDataTheQuickestWay("action_all.json", translate=True)
craftactions = loadDataTheQuickestWay("craftaction_all.json", translate=True)
statuss = loadDataTheQuickestWay("status_all.json", translate=True)
statusss = loadDataTheQuickestWay("Status.de.json")
traits = loadDataTheQuickestWay("Trait.de.json")
traitss = loadDataTheQuickestWay("trait_all.json", translate=True)
traitstransient = loadDataTheQuickestWay("TraitTransient.de.json")
aozactions = loadDataTheQuickestWay("aozaction_all.json", translate=True)
aozactiontransient = loadDataTheQuickestWay("AozActionTransient.de.json")


def writeline(f, data):
    f.write(data)
    f.write("\n")


def getBLULocationsFromLogdata(name, locations):
    global logdata
    if not name:
        return locations
    nresult = locations
    for location_name, location_data in logdata.items():
        if not location_name:
            continue
        for enemy_name, enemy_data in location_data.items():
            if not enemy_name or type(enemy_data) == list:
                continue
            for skill_id, skill_data in enemy_data.get("skill", {}).items():
                if not skill_id or not skill_data:
                    continue
                if name.lower() == skill_data["name"].lower():
                    tmp = {"Ort": location_name, "Gegner": enemy_name}
                    if tmp not in nresult:
                        nresult.append(tmp)
    return nresult


def addBlueAttackDetails(f, job_data):
    global actions
    global aozactions
    global aozactiontransient
    writeline(f, "    attacks:")
    # get special aoz action data from correct files e.g. number in blu spell book and description
    for x, y in job_data.items():
        for key, value in aozactions.items():
            if y['Name'] == value['Name_de']:
                if not aozactiontransient[key]['Location'] == "":
                    job_data[x]["Location"] = {"Ort": aozactiontransient[key]['Location'], "Gegner": "(InGame Hinweis)"}
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = aozactiontransient[key]['Number']
                job_data[x]["Description"] += "\n\n#########################################\n\n" + aozactiontransient[key]['Description']
            elif y['Name'] == "Weißer Tod":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "84"
            elif y['Name'] == "Göttlicher Katarakt":
                job_data[x]["Number"] = job_data[x]["Level"]
                job_data[x]["Level"] = "89"

        if not y.get("Number", None):
            job_data[x]["Number"] = job_data[x]["Level"]
            job_data[x]["Level"] = "90" + job_data[x]["Level"]
    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        locations = []
        if skill_data.get('Location', None):
            locations.append(skill_data['Location'])
        en_name = actions.get(skill_data['id'], {}).get("Name_en", "")
        if en_name == "":
            en_name = craftactions[skill_data['id'] + ".0"]["Name_en"]
        level = skill_data['Level']
        desc = skill_data["Description"]
        locations = getBLULocationsFromLogdata(skill_data["Name"], locations)
        locations = sorted(locations, key=lambda x: x['Ort'])
        max_zone_length = 0
        max_enemyname_length = 0
        for location in locations:
            if len(location['Ort']) > max_zone_length:
                max_zone_length = len(location['Ort'])
            if len(location['Gegner']) > max_enemyname_length:
                max_enemyname_length = len(location['Gegner'])
        if not locations == []:
            desc += "\n\n#########################################\n\nLOCATIONS:\n" + "&emsp;Zone".ljust(max_zone_length) + " -> " + "Gegnername".ljust(max_enemyname_length) + ":"
        for location in locations:
            desc += "\n&emsp;" + location["Ort"].ljust(max_zone_length) + " -> " + location["Gegner"].ljust(max_enemyname_length)
        desc = desc.replace("\n", "</br>")
        if skill_data.get("Number", None) and int(level) < 901:
            writeline(f, f'      - title: "{level}. {skill_data["Name"]}"')
        else:
            writeline(f, f'      - title: "{skill_data["Name"]}"')
        writeline(f, f'        title_id: "{skill_data["id"].split(".")[0]}"')
        writeline(f, f'        title_en: "{en_name}"')
        if skill_data.get("Number", None):
            writeline(f, f'        level: "{skill_data["Number"]}"')
        else:
            writeline(f, f'        level: "{level}"')
        writeline(f, f'        icon: "{skill_data["Icon"]}"')
        writeline(f, f'        range: "{skill_data["Range"]}"')
        writeline(f, f'        effectrange: "{skill_data["EffectRange"]}"')
        writeline(f, f'        cast: "{skill_data["Cast"]}"')
        writeline(f, f'        recast: "{skill_data["Recast"]}"')
        writeline(f, f'        kategorie: "{skill_data["Kategorie"]}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        writeline(f, f'          - phase: "01"')


def addAttackDetails(f, job_data):
    global actions
    global craftactions
    writeline(f, "    attacks:")
    job_data = OrderedDict(sorted(job_data.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, skill_data in job_data.items():
        en_name = actions.get(skill_data['id'], {}).get("Name_en", "")
        if en_name == "":
            en_name = craftactions[skill_data['id'] + ".0"]["Name_en"]
        level = "0" if skill_data['Level'] == "99999" else skill_data['Level']
        desc = skill_data["Description"].replace("\n", "</br>")
        writeline(f, f'      - title: "{skill_data["Name"]}"')
        writeline(f, f'        title_id: "{skill_data["id"].split(".")[0]}"')
        writeline(f, f'        title_en: "{en_name}"')
        writeline(f, f'        level: "{level}"')
        writeline(f, f'        icon: "{skill_data["Icon"]}"')
        writeline(f, f'        range: "{skill_data["Range"]}"')
        writeline(f, f'        effectrange: "{skill_data["EffectRange"]}"')
        writeline(f, f'        cast: "{skill_data["Cast"]}"')
        writeline(f, f'        recast: "{skill_data["Recast"]}"')
        writeline(f, f'        kategorie: "{skill_data["Kategorie"]}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        writeline(f, f'          - phase: "01"')


def addStatusDetails(f, job):
    global logdata
    global statusss
    jobstatusdata = logdata["Klassen"].get(job, {}).get("status", {})
    if not jobstatusdata == {}:
        jobstatusdata = OrderedDict(sorted(jobstatusdata.items(), key=lambda x: getitem(x[1], 'name')))
        writeline(f, "    debuffs:")
        for key, status in jobstatusdata.items():
            _id = str(int(key, 16)) + ".0"
            desc = statusss[_id]["Description"].replace("\n", "</br>")
            writeline(f, f'      - title: "{status["name"]}"')
            writeline(f, f'        title_id: "{key}"')
            writeline(f, f'        title_en: "{statuss[_id]["Name_en"]}"')
            writeline(f, f'        icon: "{status["icon"]}"')
            writeline(f, f'        description: "{desc}"')
            writeline(f, f'        durations: {status["duration"]}')
            writeline(f, '        phases:')
            writeline(f, '          - phase: "02"')


def addTraitDetails(f, job):
    global traits
    # TODO get traits by class
    writeline(f, "    traits:")
    _class = [v['ClassJob_Parent_'] for k, v in cjs.items() if v["Name"] == job]
    traitsss = {k: v for k, v in traits.items() if v["ClassJob"] in ([job] + _class)}
    job_trait_data = OrderedDict(sorted(traitsss.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    for _id, trait_data in job_trait_data.items():
        if not trait_data.get("Icon", None):
            continue
        en_name = traitss[_id]["Name_en"]
        desc = traitstransient[_id]["Description"].replace("\n", "</br>")
        level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        writeline(f, f'      - title: "{trait_data["Name"]}"')
        writeline(f, f'        title_id: "{_id.split(".")[0]}"')
        writeline(f, f'        title_en: "{en_name}"')
        writeline(f, f'        level: "{level}"')
        writeline(f, f'        icon: "{trait_data["Icon"].replace(".tex", "_hr1.png")}"')
        writeline(f, f'        description: "{desc}"')
        writeline(f, f'        phases:')
        writeline(f, f'          - phase: "03"')


def main():
    global cj
    counter = 0
    # for job, job_data in skills.items():
    cj = sorted(cj.items(), key=lambda item: int(item[0].split(".")[0]))
    maxlvl = ""
    for k in cj:
        job_d = k[1]
        job = job_d['Name_de']
        job_data = skills.get(job, None)
        if not job_data:
            continue

        tmpmaxlvl = str(max([int(data["Level"]) for key, data in job_data.items() if int(data['Level']) < 99999]))
        if job == "Blaumagier":
            maxlvl = "70"
        else:
            maxlvl = tmpmaxlvl if tmpmaxlvl > maxlvl else maxlvl

        gear = ffxiv_aku_api.get_gear(lvl_from=1, lvl_to=maxlvl, ilvl_from=1, classjob=job_d['Abbreviation_de'], category="Rumpf")
        maxilvl = str(max([int(e["Level_Item"]) for e in gear]))

        counter += 1
        with open(f"klassen_und_jobs/2013-01-01--2.0--{counter}--{job}.md", "w", encoding="utf8") as f:
            writeline(f, '---')
            writeline(f, 'wip: "True"')
            writeline(f, f'title: "{job}"')
            writeline(f, f'title_de: "{job}"')
            writeline(f, f'title_en: "{job_d["Name_en"]}"')
            writeline(f, 'layout: klassen')
            writeline(f, 'page_type: guide')
            writeline(f, 'excel_line: "0"')
            writeline(f, 'categories: "klassenjobs"')
            # writeline(f, 'patchNumber: "0.0"')
            writeline(f, 'difficulty: "Normal"')
            writeline(f, 'instanceType: "klassenjobs"')
            writeline(f, 'date: "2013.01.01"')
            writeline(f, 'slug: "klassen_und_jobs_' + job.lower() + '"')
            writeline(f, 'image:')
            writeline(f, f'    - urlSmall: "/assets/img/content/klassen/{job}.png"')
            writeline(f, f'    - url: "/assets/img/content/klassen/{job}.png"')
            writeline(f, 'terms:')
            writeline(f, '    - term: "Klassen"')
            writeline(f, '    - term: "Jobs"')
            writeline(f, '    - term: "Skills"')
            writeline(f, f'    - term: "{job}"')
            writeline(f, 'patchName: "Reflections in Crystal"')
            writeline(f, f'sortid: {counter}')
            writeline(f, f'order: {counter}')
            writeline(f, f'plvl: {maxlvl}')
            writeline(f, f'ilvl: {maxilvl}')
            writeline(f, "bosses:")
            writeline(f, "  - title: \"" + job + "\"")
            writeline(f, "    title_en: \"" + job_d["Name_en"] + "\"")
            writeline(f, "    id: \"" + "boss" + str(counter) + "\"")
            if job == "Blaumagier":
                addBlueAttackDetails(f, job_data)
            else:
                addAttackDetails(f, job_data)
            addStatusDetails(f, job)
            addTraitDetails(f, job)
            writeline(f, "    sequence:" + "")
            writeline(f, "      - phase: \"01\"")
            writeline(f, "        name: \"Skills\"")
            writeline(f, "      - phase: \"02\"")
            writeline(f, "        name: \"Status\"")
            writeline(f, "      - phase: \"03\"")
            writeline(f, "        name: \"Traits\"")
            writeline(f, '---')


if __name__ == "__main__":
    os.chdir("./_posts")
    main()
