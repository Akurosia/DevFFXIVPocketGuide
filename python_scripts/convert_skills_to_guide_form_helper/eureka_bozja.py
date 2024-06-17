from .helper import getImage, deal_with_extras_in_text, LANGUAGES, getStatusKey
import re
import json
from ffxiv_aku import loadDataTheQuickestWay, os, storeFilesInTmp

actions = None
lo_actions = None
bo_actions = None
status = None
status_trans = None
actions_trans = None
actiontransient_trans = None
cjs = None

def prepare_eureka_bozja_data(eb_actions, eb_status, eb_status_trans, eb_actions_trans, eb_actiontransient_trans, eb_cjs):
    global actions
    global lo_actions
    global bo_actions
    global status
    global status_trans
    global actions_trans
    global actiontransient_trans
    global cjs
    origin = os.getcwd()
    os.chdir("..")
    storeFilesInTmp(True)

    actions = eb_actions
    lo_actions = loadDataTheQuickestWay("eurekamagiaaction.json")
    bo_actions = loadDataTheQuickestWay("MYCTemporaryItem.json")
    status = eb_status
    status_trans = eb_status_trans
    actions_trans = eb_actions_trans
    actiontransient_trans = eb_actiontransient_trans
    cjs = eb_cjs
    os.chdir(origin)


def getActionDataSet(name):
    for _ida, action in actions.items():
        if action["Name"] == name:
            return _ida, action


def getEurekaActionDetails():
    results = {}
    new_lo_actions = {}
    # get all eurekamagiaaction
    for x, v in lo_actions.items():
        _id = int(x.split(".")[0])
        new_lo_actions[_id] = v

    for k, i in actions.items():
        for k2, lo in new_lo_actions.items():
            if i["Name"] == lo["Action"] and not i["Name"] == "":
                if k2 not in results:
                    status_key = getStatusKey(i["Status"]['GainSelf'], status)
                    results[k] = {
                        "name": {},
                        "icon": i["Icon"].replace(".png", "_hr1.png"),
                        "type": i["ActionCategory"],
                        "cj": i["ClassJobCategory"],
                        "uses": lo["MaxUses"],
                        "status": {},
                        "status_icon": status_trans[status_key]['Icon'].replace(".tex", "_hr1.png").replace(".png", "_hr1.png"),
                        "description": {},
                    }
                    for lang in LANGUAGES:
                        results[k]['name'][lang] = deal_with_extras_in_text(actions_trans[k][f'Name_{lang}'])
                        results[k]['status'][lang] = deal_with_extras_in_text(status_trans[status_key][f'Name_{lang}'])
                        results[k]['description'][lang] = deal_with_extras_in_text(actiontransient_trans[k][f"Description_{lang}"])
                    break
                else:
                    print("Douplicate for " + str(k2))
                    continue
    return results


def addEurekaActions(job, eureka_actions, job_translations):
    global cjs
    result = False
    eureka_skills = []
    result_text = ""
    result_text += "    eureka:\n"
    _class = [v['Abbreviation'] for k, v in cjs.items() if v["Name"]['Value'] == job]
    for k, value in eureka_actions.items():
        if _class[0] in value['cj']:
            result = True
            # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
            eureka_skills.append(value["name"]["de"])
            result_text += '      - title:\n'
            for lang in LANGUAGES:
                result_text += f'          {lang}: "' + deal_with_extras_in_text(value["name"][lang]) + '"\n'
                job_translations[lang][f'Class_Skill_Name_{value["name"]["en"]}'] = value["name"][lang]
            result_text += '        status:\n'
            for lang in LANGUAGES:
                result_text += f'          {lang}: "' + deal_with_extras_in_text(value["name"][lang]) + '"\n'
            result_text += f'        status_icon: "{getImage(value["status_icon"])}"\n'
            result_text += f'        title_id: "{k}"\n'
            result_text += '        level: "70"\n'
            result_text += f'        icon: "{getImage(value["icon"])}"\n'
            result_text += '        description:\n'
            for lang in LANGUAGES:
                result_text += f'          {lang}: "' + deal_with_extras_in_text(value["description"][lang]) + '"\n'
                job_translations[lang][f'Class_Skill_Desc_{value["name"]["en"]}'] = value['description'][lang]
            result_text += f'        type: "{value["type"]}"\n'
            result_text += '        phases:\n'
            result_text += '          - phase: "06"\n'
    return result, result_text, eureka_skills


def getFrontsplitterEntry(name, result):
    if not name.startswith("Verschollen") and not name.startswith("Gemüt") or not name.startswith("Würfel "):
        return name
    if name.startswith("Gemüt") or name.startswith("Würfel "):
        return "Frontsplitter des " + name
    if name.startswith("Verschollen"):
        new_name = re.split("Verschollen(?:e|es|er) (.*)", name)[1]
        for x, x_data in result["Splitter"].items():
            for y in x_data["Frontsplitter"]:
                if new_name in y:
                    return y
    return ""


def getBozjaActionDetails():
    result = {}
    for _id, action in bo_actions.items():
        if action['Category'] == "":
            continue
        if action['Category'] == "Gegenstände":
            action['Category'] = "ZGegenstände"
        if not result.get(action['Category']):
            result[action['Category']] = {}
        b, a = getActionDataSet(action['Action'])
        icon = a["Icon"].replace(".tex", "_hr1.png")
        if action['Action'] == "Würfel des Schicksals":
            icon = "ui/icon/064000/064690_hr1.png"
        tmp = {
            "name": {},
            "icon": icon,
            "cj": a["ClassJobCategory"],
            "frontsplitter": getFrontsplitterEntry(action['Action'], result),
            "description": {},
        }
        for lang in LANGUAGES:
            tmp['name'][lang] = deal_with_extras_in_text(actions_trans[b][f'Name_{lang}'])
            tmp['description'][lang] = deal_with_extras_in_text(actiontransient_trans[b][f"Description_{lang}"])
        result[action['Category']][b] = tmp
    return json.loads(json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False))


def addBozjaActions(job, bozja_actions, job_translations):
    result = False
    bozja_skills = []
    result_text = ""
    result_text += "    bozja:\n"
    _class = [v['Abbreviation'] for k, v in cjs.items() if v["Name"]['Value'] == job]
    for categorie, data in bozja_actions.items():
        for k, value in data.items():
            if _class[0] in value['cj']:
                result = True
                # level = "0" if trait_data['Level'] == "99999" else trait_data['Level']
                bozja_skills.append(value["name"]["de"])
                result_text += '      - title:\n'
                for lang in LANGUAGES:
                    result_text += f'          {lang}: "' + deal_with_extras_in_text(value["name"][lang]) + '"\n'
                    job_translations[lang][f'Class_Skill_Name_{value["name"]["en"]}'] = value["name"][lang]
                result_text += f'        title_id: "{k}"\n'
                result_text += '        level: "80"\n'
                result_text += f'        icon: "{getImage(value["icon"])}"\n'
                result_text += '        description:\n'
                for lang in LANGUAGES:
                    result_text += f'          {lang}: "' + deal_with_extras_in_text(value["description"][lang]) + '"\n'
                    job_translations[lang][f'Class_Skill_Desc_{value["name"]["en"]}'] = value['description'][lang]
                result_text += f'        frontsplitter: "{value["frontsplitter"]}"\n'
                result_text += '        phases:\n'
                result_text += '          - phase: "07"\n'
    return result, result_text, bozja_skills
