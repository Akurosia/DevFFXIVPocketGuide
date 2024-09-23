from typing import Any
from functools import lru_cache
#from json import JSONDecoder
from collections import OrderedDict
from ffxiv_aku import *

LANGUAGES: list[str] = ["de", "en", "fr", "ja", "cn", "ko"]
addon_trans: dict[str, Any] = loadDataTheQuickestWay("addon", translate=True)

@lru_cache(maxsize=None)
def search_addon_translation(term: str) -> tuple[bool, str]:
    global addon_trans
    for key, value in addon_trans.items():
        #if "Kamerawinkel Verfolgerperspektive".lower() in value['Text_de'].lower():
        #    print(f"|{value['Text_de'].replace('\n', ' ')}|")
        if value['Text_de'].lower().replace("\n", " ").strip() == term.lower():
            return True, key#value['Text_en']
    return False, term


#def run() -> None:
#    with open(r"FFXIV_Charachter_Config.txt", encoding="utf8") as f:
#        ldata = f.readlines()
#    for line in ldata:
#        found, value = search_addon_translation(line.strip())
#        if found:
#            print_color_green(line.replace(line.strip(), value)[:-1])
#        else:
#            print_color_red(line.replace(line.strip(), value)[:-1])



def run2() -> dict[str, Any]:
    #customdecoder = JSONDecoder(object_pairs_hook=OrderedDict)

    with open(r"FFXIV_Charachter_Config.txt", encoding="utf8") as f:
        ldata: list[str] = f.readlines()

    lresults: dict[str, Any] = OrderedDict()
    last_value: dict[int, str] = {
        0: "",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
    }
    try:
        for line in ldata:
            line: str = line[:-1]
            #print(line.replace("    "*6, "").replace("    "*5, "").replace("    "*4, "").replace("    "*3, "").replace("    "*2, "").replace("    ", ""))
            found, value = search_addon_translation(line.strip())
            #value: str = value
            #value = line.replace(line.strip(), value)[:-1]
            if not found:
                print_color_red(value)

            if not line == line.replace("    "*7, ""):
                if not lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]][last_value[5]][last_value[6]].get(value):
                    lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]][last_value[5]][last_value[6]][value] = {}
                last_value[7] = value

            elif not line == line.replace("    "*6, ""):
                if not lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]][last_value[5]].get(value):
                    lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]][last_value[5]][value] = {}
                last_value[6] = value

            elif not line == line.replace("    "*5, ""):
                if not lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]].get(value):
                    lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][last_value[4]][value] = {}
                last_value[5] = value

            elif not line == line.replace("    "*4, ""):
                if not lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]].get(value):
                    lresults[last_value[0]][last_value[1]][last_value[2]][last_value[3]][value] = {}
                last_value[4] = value

            elif not line == line.replace("    "*3, ""):
                if not lresults[last_value[0]][last_value[1]][last_value[2]].get(value):
                    lresults[last_value[0]][last_value[1]][last_value[2]][value] = {}
                last_value[3] = value

            elif not line == line.replace("    "*2, ""):
                if not lresults[last_value[0]][last_value[1]].get(value):
                    lresults[last_value[0]][last_value[1]][value] = {}
                last_value[2] = value

            elif not line == line.replace("    ", ""):
                if not lresults[last_value[0]].get(value):
                    lresults[last_value[0]][value] = {}
                last_value[1] = value
            else:
                if not lresults.get(value):
                    lresults[value] = {}
                last_value[0] = value
    except:
        pass
    return lresults
    #print(results)
    #print(last_value)


def add_to_translate_element(translations: dict[str, Any] = {}, translate_string: str = "", value: str = "") -> dict[str, Any]:
    for lang in LANGUAGES:
        if not translations.get(lang, None):
            translations[lang] = {}
        if not translations[lang].get("settings", None):
            translations[lang]['settings'] = {}
        translations[lang]['settings'][f'{translate_string}'] = addon_trans[value][f'Text_{lang}'].replace("\n", " ")
    return translations


def getFinalContent(ltext: str, translations: dict[str, Any], subvalues3: dict[str, Any], translate_string: str, main_cat: str, sub_cat: str, sub_sub_cat: str) -> tuple[str, dict[str, Any]]:
    for value4, subvalues4 in subvalues3.items():
        try:
            int(value4)
            sub_sub_sub_cat = addon_trans[value4]['Text_en']
            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
            translations = add_to_translate_element(translations, translate_string, value4)
        except:
            sub_sub_sub_cat = value4
            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
        ltext += f'        <span class="attack-is-magic" style="padding-left: 2rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

        for value5, subvalues5 in subvalues4.items():
            try:
                int(value5)
                sub_sub_sub_cat = addon_trans[value5]['Text_en']
                translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                translations = add_to_translate_element(translations, translate_string, value5)
            except:
                sub_sub_sub_cat = value5
                translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
            ltext += f'        <span class="attack-is-magic" style="padding-left: 4rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

            for value6, subvalues6 in subvalues5.items():
                try:
                    int(value6)
                    sub_sub_sub_cat = addon_trans[value6]['Text_en']
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                    translations = add_to_translate_element(translations, translate_string, value6)
                except:
                    sub_sub_sub_cat = value6
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                ltext += f'        <span class="attack-is-magic" style="padding-left: 6rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'
    return ltext, translations


def custom_print_results(lresults: dict[str, Any], ltext: str = "", translations: dict[str, Any] = {}) -> tuple[str, dict[str, Any]]:
    ltext += f'<div class="setting_container">\n'

    for value, subvalues in lresults.items():
        main_cat = addon_trans[value]['Text_en']
        translate_string: str = f'Settings_{main_cat}'
        translations = add_to_translate_element(translations, translate_string, value)
        ltext += f'<div section="{main_cat}" style="width: 49%;">\n'
        ltext += '    <div class="guide__accordion-trigger--01-grid active">\n'
        ltext += '        <i class="Dropdown material-icons" style="display: none;">\n'
        ltext += '            <ion-icon size="large" name="chevron-down-outline" style="color: white !important" role="img" class="md icon-large hydrated" aria-label="chevron down outline"></ion-icon>\n'
        ltext += '        </i>\n'
        ltext += f'        <div class="Names" data-translate="{translate_string}">{main_cat}</div>\n'
        ltext += '    </div>\n'
        for value2, subvalues2 in subvalues.items():
            sub_cat = addon_trans[value2]['Text_en']
            translate_string: str = f'Settings_{main_cat}_{sub_cat}'
            translations = add_to_translate_element(translations, translate_string, value2)
            ltext += '    <div class="guide__accordion-trigger--02-grid active">\n'
            ltext += '        <i class="Dropdown material-icons" style=""><ion-icon size="large" name="chevron-down-outline" style="color: white !important" role="img" class="md icon-large hydrated" aria-label="chevron down outline"></ion-icon></i>\n'
            ltext += f'        <div class="EnemyNames"><h3 class="guide__accordion-trigger-title" data-translate="{translate_string}">{sub_cat}</h3></div>\n'
            ltext += '    </div>\n'
            ltext += '    <div class="guide__accordion-content--02 active" style="border: white 1px solid;">\n'
            if value == "4000":
                ltext += '        <div class="guide__accordion-copy-wrapper active">\n'

            for value3, subvalues3 in subvalues2.items():
                try:
                    int(value3)
                    sub_sub_cat = addon_trans[value3]['Text_en']
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_cat}'
                    translations = add_to_translate_element(translations, translate_string, value3)
                except:
                    sub_sub_cat = value3
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_cat}'

                #handle first elements for system configuration
                if value == "4000":
                    ltext += '        <div style="display: grid;">\n'
                    ltext += f'        <span class="attack-is-magic" data-translate="{translate_string}">{sub_sub_cat}</span>\n'
                    ltext, translations = getFinalContent(ltext, translations, subvalues3, translate_string, main_cat, sub_cat, sub_sub_cat)
                    ltext += '        </div>\n'

                #handle first elements for charachter configuration
                else:
                    ltext += '        <div class="guide__accordion-trigger--03--grid_attack--ignore active">\n'
                    ltext += '            <i class="Dropdown material-icons" style="">\n'
                    ltext += '                <ion-icon size="large" name="chevron-down-outline" style="color: white !important" role="img" class="md icon-large hydrated" aria-label="chevron down outline"></ion-icon>\n'
                    ltext += '            </i>\n'
                    ltext += '            <div class="Names">\n'
                    ltext += f'                <span class="attack-is-magic" data-translate="{translate_string}">{sub_sub_cat}</span>\n'
                    ltext += '            </div>\n'
                    ltext += '        </div>\n'

                    ltext += '        <div class="guide__accordion-content--03--ignore active" style="">\n'
                    ltext += '            <div class="guide__accordion-copy-wrapper" style="display: grid;">\n'
                    ltext, translations = getFinalContent(ltext, translations, subvalues3, translate_string, main_cat, sub_cat, sub_sub_cat)
                    ltext += '            </div>\n'
                    ltext += '        </div>\n'

            if value == "4000":
                ltext += '        </div>\n'
            ltext += '    </div>\n'
        ltext += '</div>\n'

    ltext += "</div>\n"
    return ltext, translations


def run(translations: dict[str, Any]) -> None:
    if not "python_scripts" in os.getcwd():
        if "_posts" in os.getcwd():
            os.chdir('../python_scripts')

    results: dict[str, Any] = run2()
    writeJsonFile("FFXIV_Charachter_Config.json", results)


    # the following code will print the result that is seen on the page in the end
    otext, translations = custom_print_results(lresults=results, ltext="", translations=translations)
    with open('../_includes/settings.html', "w", encoding="utf8") as f:
        f.write(otext)
    if "python_scripts" in os.getcwd():
        if "_posts" in os.getcwd():
            os.chdir('../_posts')
    #print(translations)


if __name__ == "__main__":
    run({})
