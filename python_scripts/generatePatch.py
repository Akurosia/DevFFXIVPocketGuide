from ffxiv_aku import *
from datetime import datetime, date
try:
    from python_scripts.fileimports import *
except Exception:
    from fileimports import *


LANGUAGES = ["de", "en", "fr", "ja"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP"
}
path_of_main_script = ""
klass_translations = None


def get_class_translation_data():
    global klass_translations
    klass_translations = {}
    for lang in LANGUAGES:
        klass_translations[lang] = readJsonFile(f'{path_of_main_script}/assets/translations/patches/{LANGUAGES_MAPPING[lang]}.json')
        #klass_translations[lang] = {}


def write_class_translation_data(data):
    for lang in LANGUAGES:
        klass_translations[lang] = writeJsonFile(f'{path_of_main_script}/assets/translations/patches/{LANGUAGES_MAPPING[lang]}.json', data[lang])


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

    filename = f"{path_of_main_script}/_pages/patches/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)


def single_patch_file():
    logos= {
        "ff14": "title_logoonline_hr1.tex.webp",
        "arr": "title_logo_hr1.tex.webp",
        "hw": "title_logo300_hr1.tex.webp",
        "sb": "title_logo400_hr1.tex.webp",
        "shb": "title_logo500_hr1.tex.webp",
        "ew": "title_logo600_hr1.tex.webp",
        "dt": "title_logo700_hr1.tex.webp"
    }
    versions = get_any_Versiondata()
    for key, value in exversion.items():
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

        filename = f'{path_of_main_script}/_posts/patch_details/{n_version["date"].replace(".", "-")}--{str(int(key)+2)+".0"}--{key}-{value["Name_de"].lower().replace(" ", "_")}.html'
        try:
            with open(filename, encoding="utf8") as f:
                doc = f.read()
        except:
            doc = ""
        if not doc == filecontent:
            with open(filename, "w", encoding="utf8") as f:
                f.write(filecontent)
        #print(filecontent)


def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    global path_of_main_script
    path_of_main_script = main_script
    get_class_translation_data()
    patches_overview()
    single_patch_file()
    write_class_translation_data(klass_translations)


if __name__ == "__main__":
    run()
