import json
import os
from ffxiv_aku import *
from datetime import datetime, date
try:
    import convertTranslationJsons as ctj
except:
    import python_scripts.convertTranslationJsons as ctj


LANGUAGES = ["de", "en", "fr", "ja", "cn", "ko"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
    "cn": "cn-CN",
    "ko": "ko-KR"
}
klass_translations = None
def get_class_translation_data():
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        klass_translations[lang] = readJsonFile(f'assets/translations/patches/{LANGUAGES_MAPPING[lang]}.json')
        #klass_translations[lang] = {}


def write_class_translation_data(data):
    origin = os.getcwd()
    os.chdir("..")
    print(os.getcwd())
    for lang in LANGUAGES:
        klass_translations[lang] = writeJsonFile(f'assets/translations/patches/{LANGUAGES_MAPPING[lang]}.json', data[lang])
    os.chdir(origin)


def nextRelease(value):
    try:
        if value.get("date", None):
            today = datetime.today()
            date = datetime.strptime(value['date'].replace(".", "/"), '%Y/%m/%d')
            diff = date - today
            if diff.days < 21:
                return True
    except: pass
    return False


def patches_overview():
    versions = get_any_Versiondata()
    filecontent = ""
    filecontent += '---\n'
    filecontent += 'layout: patches\n'
    filecontent += 'title: Patches\n'
    filecontent += 'last_modified_at: 2022-03-17\n'
    filecontent += 'permalink: /patches/\n'
    filecontent += 'description: "Search through class and jobs guides on the FFXIV Pocket Guide."\n'
    filecontent += 'page_type: index\n'
    filecontent += 'page_category: patches\n'
    filecontent += 'patches:\n'
    old_date = ""
    major_patches = []
    minor_patches = []
    for key, value in versions.items():
        if value.get('disabled', False) == "true" and not nextRelease(value):
            continue
        #print(value)

        new_date = datetime.strptime(value['date'].replace(".", "/"), '%Y/%m/%d')
        if old_date == "":
            old_date = new_date
        datediff = new_date - old_date
        old_date = new_date
        if key.endswith("0"):
            key = key[:-1]

        filecontent += f"    - name: {value['name']}\n"
        filecontent += f"      patchnumber: \"{key}\"\n"
        filecontent += f"      date: {value['date']}\n"
        filecontent += f"      dslr: {datediff.days}\n"
        filecontent += f"      pname: {value['pname']}\n"
        if value.get('link_to_patch', None):
            filecontent += f"      link_to_patch: {value['link_to_patch']}\n"
        if value.get('link_to_special_page', None):
            filecontent += f"      link_to_special_page: {value['link_to_special_page']}\n"

        ma_p, mi_p = key.split(".")
        if not ma_p in major_patches and not ma_p == "1":
            major_patches.append(ma_p)
        if not mi_p in minor_patches and not ma_p == "1":
            minor_patches.append(mi_p)

    filecontent += 'major_patches:\n'
    for patch in sorted(major_patches):
        filecontent += f'    - "{patch}"\n'

    filecontent += 'minor_patches:\n'
    for patch in sorted(minor_patches):
        filecontent += f'    - "{patch}"\n'
    filecontent += '---\n'

    filename = f"_pages/patches/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)


def single_patch_file():
    logos= {
        "ff14": "title_logoonline_hr1.tex.png",
        "arr": "title_logo_hr1.tex.png",
        "hw": "title_logo300_hr1.tex.png",
        "sb": "title_logo400_hr1.tex.png",
        "shb": "title_logo500_hr1.tex.png",
        "ew": "title_logo600_hr1.tex.png",
        "dw": "title_logo700_hr1.tex.png"
    }
    versions = get_any_Versiondata()
    #print_pretty_json(versions)
    exversion_trans = loadDataTheQuickestWay("exversion", translate=True)
    exversion = loadDataTheQuickestWay("exversion", translate=False)
    for key, value in exversion_trans.items():
        #print(exversion[key])
        n_version = versions[str(int(key)+2) + ".00"]
        #print(n_version)
        filecontent = ""
        filecontent += '---\n'
        filecontent += 'wip: "True"\n'
        filecontent += f'title: "{value["Name_en"]}"\n'
        for lang in LANGUAGES:
            klass_translations[lang][f'Patches_{int(key)+2}.x - {value["Name_en"]}'] = f'{int(key)+2}.x - {value["Name_"+lang]}'
            #filecontent += f'  {lang}: "{value["Name_"+lang]}"\n'
        filecontent += 'layout: klassen\n'
        filecontent += 'page_type: guide\n'
        filecontent += 'categories: "patch_details"\n'
        filecontent += 'difficulty: "Normal"\n'
        filecontent += 'instanceType: "patch_details"\n'
        filecontent += 'date: "2013.01.01"\n'
        filecontent += f'patchNumber: "{int(key)+2}.0"\n'
        filecontent += f'patchName: "{value["Name_de"]}"\n'
        filecontent += f'expac: "{n_version["pname"]}"\n'
        filecontent += f'slug: "{value["Name_de"].lower().replace(" ", "_")}"\n'
        filecontent += f'image: "/assets/img/titel-logo/{logos[n_version["pname"]]}"\n'
        filecontent += '---\n'

        filename = f'_posts/patch_details/{n_version["date"].replace(".", "-")}--{str(int(key)+2)+".0"}--{key}-{value["Name_de"].lower().replace(" ", "_")}.html'
        try:
            with open(filename, encoding="utf8") as f:
                doc = f.read()
        except:
            doc = ""
        if not doc == filecontent:
            with open(filename, "w", encoding="utf8") as f:
                f.write(filecontent)
        #print(filecontent)


def run():
    get_class_translation_data()
    patches_overview()
    single_patch_file()
    os.chdir("_posts")
    write_class_translation_data(klass_translations)


if __name__ == "__main__":
    os.chdir("..")
    run()
    ctj.run()
