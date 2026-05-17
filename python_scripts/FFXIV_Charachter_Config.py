from typing import Any
from functools import lru_cache
#from json import JSONDecoder
from collections import OrderedDict
from ffxiv_aku import *
import html
import re
try:
    from .fileimports import *
except:
    from fileimports import *
LANGUAGES: list[str] = ["de", "en", "fr", "ja"]
path_of_main_script = ""
#addon = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\Addon.json")


def normalize_addon_text(value: str) -> str:
    value = html.unescape(str(value))
    value = re.sub(r"=<Gui\(\d+\)/>", " ", value)
    value = value.replace("\n", " ").replace("_", " ").replace("=", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


@lru_cache(maxsize=1)
def addon_text_index() -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in addon.items():
        for field_name, field_value in value.items():
            if not field_name.startswith("Text"):
                continue
            normalized = normalize_addon_text(field_value)
            if normalized and normalized not in result:
                result[normalized] = key
    return result


@lru_cache(maxsize=None)
def search_addonlation(term: str) -> tuple[bool, str]:
    if term in addon:
        return True, term
    key = addon_text_index().get(normalize_addon_text(term))
    if key:
        return True, key
    return False, term


def addon_text(value: str, lang: str = "en") -> str:
    if value in addon:
        return str(addon[value].get(f"Text_{lang}", addon[value].get("Text_en", ""))).replace("\n", " ")
    return str(value)


def addon_text_html(value: str, lang: str = "en") -> str:
    return html.escape(addon_text(value, lang))


def print_missing_addon(value: str) -> None:
    printable = str(value).encode("cp1252", errors="backslashreplace").decode("cp1252")
    print_color_yellow(f"[FCC] No Addon translation id for literal label: {printable}")


def run2() -> dict[str, Any]:
    #customdecoder = JSONDecoder(object_pairs_hook=OrderedDict)

    with open(f"{path_of_main_script}/python_scripts/FFXIV_Charachter_Config.txt", encoding="utf8") as f:
        ldata: list[str] = f.readlines()

    lresults: dict[str, Any] = OrderedDict()
    stack: list[dict[str, Any]] = [lresults]
    for raw_line in ldata:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue

        depth = (len(line) - len(line.lstrip(" "))) // 4
        found, value = search_addonlation(line.strip())
        if not found:
            print_missing_addon(value)

        while depth + 1 > len(stack):
            stack.append(OrderedDict())
        stack = stack[:depth + 1]

        parent = stack[depth]
        if value not in parent:
            parent[value] = OrderedDict()
        stack.append(parent[value])
    return lresults
    #print(results)
    #print(last_value)


def add_to_translate_element(translations: dict[str, Any], translate_string: str = "", value: str = "") -> dict[str, Any]:
    for lang in LANGUAGES:
        if not translations.get(lang, None):
            translations[lang] = {}
        if not translations[lang].get("settings", None):
            translations[lang]['settings'] = {}
        translations[lang]['settings'][f'{translate_string}'] = addon_text(value, lang)
    return translations


def getFinalContent(ltext: str, translations: dict[str, Any], subvalues3: dict[str, Any], translate_string: str, main_cat: str, sub_cat: str, sub_sub_cat: str) -> tuple[str, dict[str, Any]]:
    for value4, subvalues4 in subvalues3.items():
        if value4 in addon:
            sub_sub_sub_cat = addon_text_html(value4)
            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
            translations = add_to_translate_element(translations, translate_string, value4)
        else:
            sub_sub_sub_cat = html.escape(value4)
            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
        ltext += f'        <span class="attack-is-magic" style="padding-left: 2rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

        for value5, subvalues5 in subvalues4.items():
            if value5 in addon:
                sub_sub_sub_cat = addon_text_html(value5)
                translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                translations = add_to_translate_element(translations, translate_string, value5)
            else:
                sub_sub_sub_cat = html.escape(value5)
                translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
            ltext += f'        <span class="attack-is-magic" style="padding-left: 4rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

            for value6, subvalues6 in subvalues5.items():
                if value6 in addon:
                    sub_sub_sub_cat = addon_text_html(value6)
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                    translations = add_to_translate_element(translations, translate_string, value6)
                else:
                    sub_sub_sub_cat = html.escape(value6)
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                ltext += f'        <span class="attack-is-magic" style="padding-left: 6rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

                for value7, subvalues7 in subvalues6.items():
                    if value7 in addon:
                        sub_sub_sub_cat = addon_text_html(value7)
                        translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                        translations = add_to_translate_element(translations, translate_string, value7)
                    else:
                        sub_sub_sub_cat = html.escape(value7)
                        translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                    ltext += f'        <span class="attack-is-magic" style="padding-left: 8rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'

                    for value8, subvalues8 in subvalues7.items():
                        if value8 in addon:
                            sub_sub_sub_cat = addon_text_html(value8)
                            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                            translations = add_to_translate_element(translations, translate_string, value8)
                        else:
                            sub_sub_sub_cat = html.escape(value8)
                            translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_sub_cat}'
                        ltext += f'        <span class="attack-is-magic" style="padding-left: 10rem;" data-translate="{translate_string}">    {sub_sub_sub_cat}</span>\n'
    return ltext, translations


def custom_print_results(lresults: dict[str, Any], ltext: str = "", translations: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]]:
    if translations is None:
        translations = {}
    ltext += f'<div class="setting_container">\n'

    for value, subvalues in lresults.items():
        main_cat = addon_text_html(value)
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
            sub_cat = addon_text_html(value2)
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
                if value3 in addon:
                    sub_sub_cat = addon_text_html(value3)
                    translate_string: str = f'Settings_{main_cat}_{sub_cat}_{sub_sub_cat}'
                    translations = add_to_translate_element(translations, translate_string, value3)
                else:
                    sub_sub_cat = html.escape(value3)
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


def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide", translations: dict[str, Any]=None):
    global path_of_main_script
    path_of_main_script = main_script
    results: dict[str, Any] = run2()
    # the following code will print the result that is seen on the page in the end
    otext, translations = custom_print_results(lresults=results, ltext="", translations=translations)
    with open(f'{path_of_main_script}/_includes/single_pages/settings.html', "w", encoding="utf8") as f:
        f.write(otext)
    #print(translations)


if __name__ == "__main__":
    run(r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide", {})
