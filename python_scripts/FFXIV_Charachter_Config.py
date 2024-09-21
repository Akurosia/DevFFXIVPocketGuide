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


def custom_print_results(lresults: dict[str, Any], ltext: str = "", spaces: int=0, main_cat: str = "", sub_cat: str = "", translations: dict[str, Any] = {}) -> tuple[str, dict[str, Any]]:
    counter = 0
    if spaces == 0:
        ltext += f'{"\t" * (spaces-1)}<div class="setting_container">\n'
    elif spaces < 3:
        ltext += f'{"\t" * (spaces-1)}<div class="setting_container_inner">\n'

    for value, subvalues in lresults.items():
        if spaces == 0:
            main_cat = addon_trans[value]['Text_en']
            ltext += '\t<div style="background-color: cadetblue;border: 2px solid black;border-radius: 5px;padding: 5px">\n'
        if spaces == 1:
            sub_cat = addon_trans[value]['Text_en']
        counter += 1

        translate_string: str = f'Settings_{main_cat}_{sub_cat}_{spaces}spaces_{counter}counter'
        if isinstance(value, str): # type: ignore
            try:
                for lang in LANGUAGES:
                    if not translations.get(lang, None):
                        translations[lang] = {}
                    if not translations[lang].get("settings", None):
                        translations[lang]['settings'] = {}
                    translations[lang]['settings'][f'{translate_string}'] = text = addon_trans[value][f'Text_{lang}'].replace("\n", " ")
                text = addon_trans[value]['Text_de'].replace("\n", " ")
                ltext += f"{'\t' * spaces}<span style='margin-right: {0*spaces*16}'>{'&nbsp;'*spaces*2}</span><span data-translate='{translate_string}'>{text}</span>\n{'\t' * spaces}</br>\n"
            except:
                ltext += f"{'\t' * spaces}<span  style='margin-right: {0*spaces*16}'>{'&nbsp;'*spaces*2}</span><span data-translate='{translate_string}'>{value}</span>\n{'\t' * spaces}</br>\n"
        elif isinstance(value, dict):
            ltext += f"{'\t' * spaces}<span  style='margin-right: {0*spaces*16}'>{'&nbsp;'*spaces*2}</span><span data-translate='{translate_string}'>{value}</span>\n{'\t' * spaces}</br>\n"
        if not subvalues == {}:
            ltext, translations = custom_print_results(lresults=subvalues, ltext=ltext, spaces=spaces+1, main_cat=main_cat, sub_cat=sub_cat, translations=translations)
        if spaces == 0:
            ltext += "\t</div>\n"

    if spaces < 3:
        ltext += f"{'\t' * (spaces-1)}</div>\n"
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
