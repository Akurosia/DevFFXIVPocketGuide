import os
from collections import OrderedDict
from .helper import getImage, deal_with_extras_in_text, LANGUAGES
from ffxiv_aku import storeFilesInTmp, loadDataTheQuickestWay, os
from operator import getitem

chocoboskills = None
chocoboitems = None
chocobochallange = None
buddyskill = None
actions = None
actiontransient = None
traits = None
traitstransient = None
job_translations = None


def cb_load_global_data(cb_actions, cb_actiontransient, cb_traits, cb_traitstransient):
    global chocoboskills
    global chocoboitems
    global chocobochallange
    global buddyskill
    global actions
    global actiontransient
    global traits
    global traitstransient
    origin = os.getcwd()
    os.chdir("..")
    storeFilesInTmp(False)

    actions = cb_actions
    actiontransient = cb_actiontransient
    traits = cb_traits
    traitstransient = cb_traitstransient
    chocoboskills = loadDataTheQuickestWay("ChocoboRaceAbility.json")
    chocoboitems = loadDataTheQuickestWay("ChocoboRaceItem.json")
    chocobochallange = loadDataTheQuickestWay("ChocoboRaceChallenge.json")
    buddyskill = loadDataTheQuickestWay("BuddySkill.json")

    os.chdir(origin)


def addChocoboPartnerSkills():
    global actions
    global actions
    global actiontransient

    global buddyskill
    test = [ [ x['Attacker']['row_id'], x['Defender']['row_id'], x['Healer']['row_id'] ] for key, x in buddyskill.items() if x['IsActive'] == "True" and not key == "0" ]

    chocobo_skills = []
    for x in test:
        chocobo_skills += x
    chocobo_skillss = { key:actions[key] for key in chocobo_skills }
    #print(chocobo_skillss)
    ordered = OrderedDict(sorted(chocobo_skillss.items(), key=lambda x: int(x[0])))
    result = ""
    result += "    attacks:\n"
    for key, _ in ordered.items():
        t = actions[key]
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{t[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{t["Name_en"]}'] = t[f"Name_{lang}"]
        result += f'        icon: "/assets/img/game_assets{getImage(t["Icon"]['path'])}"\n'
        #result += f'        level: "{actions[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(actiontransient[key][f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{t["Name_en"]}'] = deal_with_extras_in_text(actiontransient[key][f"Description_{lang}"])
        result += '        phases:\n'
        result += '          - phase: "01"\n'
    return result


def addRennChocoboSkills():
    global chocoboskills
    ordered = OrderedDict(sorted(chocoboskills.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["Name_en"]}'] = value[f"Name_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "/assets/img/game_assets{getImage(value["Icon"]['path'])}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(value[f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{value["Name_en"]}'] = deal_with_extras_in_text(actiontransient[key][f"Description_{lang}"])
        result += '        phases:\n'
        result += '          - phase: "03"\n'
    return result


def addChocoboPartnerTraits():
    global traits
    global traits
    global traitstransient
    global buddyskill
    #test = [ [x['Attacker'], x['Defender'], x['Healer']] for key, x in buddyskill.items() if x['IsActive'] == "False" and not key == "0"]
    test = [ [ x['Attacker']['row_id'], x['Defender']['row_id'], x['Healer']['row_id'] ] for key, x in buddyskill.items() if x['IsActive'] == "False" and not key == "0" ]

    chocobo_traits = []
    for x in test:
        chocobo_traits += x
    chocobo_traits = sorted(chocobo_traits)
    chocobo_traits = { key:traits[key] for key in chocobo_traits }
    ordered = OrderedDict(sorted(chocobo_traits.items(), key=lambda x: int(getitem(x[1], 'Level'))))
    result = ""
    result += "    traits:\n"
    for key, _ in ordered.items():
        t = traits[key]
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{t[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Trait_Name_{t["Name_en"]}'] = t[f"Name_{lang}"]
        result += f'        icon: "/assets/img/game_assets{getImage(t["Icon"]['path'])}"\n'
        result += f'        level: "{traits[key]["Level"]}"\n'
        result += f'        title_id: "{key}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(traitstransient[key][f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Trait_Desc_{t["Name_en"]}'] = deal_with_extras_in_text(traitstransient[key][f"Description_{lang}"])
        result += '        phases:\n'
        result += '          - phase: "02"\n'
    return result


def addRennChocoboItems():
    global chocoboitems
    ordered = OrderedDict(sorted(chocoboitems.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Name_de"] == "":
            continue
        # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"Name_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["Name_en"]}'] = value[f"Name_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += f'        icon: "/assets/img/game_assets{getImage(value["Icon"]['path'])}"\n'
        result += '        description:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{deal_with_extras_in_text(value[f"Description_{lang}"])}"\n'
            job_translations[lang][f'Class_Skill_Desc_{value["Name_en"]}'] = deal_with_extras_in_text(value[f"Description_{lang}"])
        result += '        phases:\n'
        result += '          - phase: "04"\n'
    return result


def addRennChocoboMissions():
    global chocobochallange
    ordered = OrderedDict(sorted(chocobochallange.items(), key=lambda x: int(x[0])))
    result = ""
    for key, value in ordered.items():
        if value["Unknown0_de"] == "":
            continue
        result += '      - title:\n'
        for lang in LANGUAGES:
            result += f'          {lang}: "{value[f"Unknown0_{lang}"]}"\n'
            job_translations[lang][f'Class_Skill_Name_{value["Unknown0_en"]}'] = value[f"Unknown0_{lang}"]
        result += f'        title_id: "{key}"\n'
        result += '        phases:\n'
        result += '          - phase: "05"\n'
    return result


def addChocobo(actions, actiontransient, traits, traitstransient, klass_translations, callback_function, addExtraIcons):
    global job_translations
    cb_load_global_data(actions, actiontransient, traits, traitstransient)

    # prepare translation elements
    job_translations = {}
    for lang in LANGUAGES:
        job_translations[lang] = {}

    job = "Chocobo"
    job_d = {
        "Name_de": "Chocobo",
        "Name_en": "chocobo",
        "Name_fr": "chocobo",
        "Name_ja": "チョコボ",
    }
    filecontent = ""
    filecontent += '---\n'
    filecontent += 'wip: "True"\n'
    filecontent += 'title:\n'
    filecontent += f'  de: "{job_d["Name_de"]}"\n'
    filecontent += f'  en: "{job_d["Name_en"]}"\n'
    filecontent += f'  fr: "{job_d["Name_fr"]}"\n'
    filecontent += f'  ja: "{job_d["Name_ja"]}"\n'
    filecontent += 'layout: klassen\n'
    filecontent += 'page_type: guide\n'
    filecontent += f'roletypeinparty: "{job_d["Name_en"]}"\n'
    for lang in LANGUAGES:
        klass_translations[lang][f'Sidebar_Role_{job_d["Name_en"]}'] = job_d[f"Name_{lang}"]
    filecontent += 'categories: "klassenjobs"\n'
    filecontent += 'difficulty: "Normal"\n'
    filecontent += 'instanceType: "klassenjobs"\n'
    filecontent += 'date: "2013.01.01"\n'
    filecontent += 'patchNumber: "2.0"\n'
    filecontent += 'patchName: "A Realm Reborn"\n'
    filecontent += 'expac: "arr"\n'
    icon = getImage("062000/062143_hr1.webp")
    filecontent += f'jobicon: "/assets/img/game_assets{icon}"\n'

    filecontent += "extraicons:\n"
    filecontent += addExtraIcons(job, icon, icon)
    filecontent += 'slug: "klassen_und_jobs_' + job.lower() + '"\n'
    if os.path.exists(f"{os.getcwd()}/../assets/img/content/klassen/{job}.webp"):
        filecontent += f'image: "/assets/img/content/klassen/{job}.webp"\n'
    else:
        print(f"Missing img: {job}.webp")
    filecontent += 'terms:\n'
    filecontent += '    - term: "Klassen"\n'
    filecontent += '    - term: "Jobs"\n'
    filecontent += '    - term: "Skills"\n'
    filecontent += '    - term: "Status"\n'
    filecontent += '    - term: "Traits"\n'
    filecontent += f'    - term: "{job_d["Name_de"]}"\n'
    filecontent += f'    - term: "{job_d["Name_en"]}"\n'
    filecontent += f'    - term: "{job_d["Name_fr"]}"\n'
    filecontent += f'    - term: "{job_d["Name_ja"]}"\n'
    filecontent += 'sortid: 0\n'
    filecontent += 'order: 0\n'
    filecontent += 'plvl: 50\n'
    filecontent += "bosses:\n"
    filecontent += f'  - title: "{job_d["Name_en"]}"\n'
    for lang in LANGUAGES:
        klass_translations[lang][f'Content_Title_{job_d["Name_en"]}'] = job_d[f"Name_{lang}"]
    filecontent += "    id: \"" + "boss0\"\n"
    # todo add chocobo stuff
    filecontent += addChocoboPartnerSkills()
    filecontent += addRennChocoboSkills()
    # addRennChocoboStatus()
    filecontent += addRennChocoboItems()
    filecontent += addRennChocoboMissions()
    filecontent += addChocoboPartnerTraits()
    filecontent += "    sequence:" + "\n"
    filecontent += "      - phase: \"01\"\n"
    filecontent += "        name: \"Chocobo-Partner-Skills\"\n"
    filecontent += "      - phase: \"02\"\n"
    filecontent += "        name: \"Chocobo-Partner-Traits\"\n"
    filecontent += "      - phase: \"03\"\n"
    filecontent += "        name: \"Renn-Chocobo-Skills\"\n"
    # filecontent += "      - phase: \"04\"\n"
    # filecontent += "        name: \"Renn-Chocobo-Status\"\n"
    filecontent += "      - phase: \"04\"\n"
    filecontent += "        name: \"Renn-Chocobo-Items\"\n"
    filecontent += "      - phase: \"05\"\n"
    filecontent += "        name: \"Renn-Chocobo-Missions\"\n"
    filecontent += '---\n'

    callback_function(job_translations, "chocobo")

    filename = f"klassen_und_jobs/2013-01-01--2.0--0--{job}.md"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)
