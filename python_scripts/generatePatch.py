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
TRAILER_FIELDS = [
    "link_to_trailer",
    "link_to_teaser_trailer",
    "link_to_full_trailer",
    "link_to_extended_teaser_trailer",
    "link_to_special_song_trailer",
    "link_to_additional_trailer",
    "link_to_benchmark_trailer",
]


def yaml_quote(value):
    value = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def append_patch_yaml(lines, patch, indent="    "):
    lines.append(f"{indent}- name: {yaml_quote(patch['name'])}\n")
    lines.append(f"{indent}  patchnumber: {yaml_quote(patch['patchnumber'])}\n")
    lines.append(f"{indent}  date: {yaml_quote(patch['date'])}\n")
    lines.append(f"{indent}  dslr: {patch['dslr']}\n")
    lines.append(f"{indent}  pname: {yaml_quote(patch['pname'])}\n")

    if patch.get("link_to_patch", None):
        lines.append(f"{indent}  link_to_patch: {yaml_quote(patch['link_to_patch'])}\n")
    if patch.get("link_to_special_page", None):
        lines.append(f"{indent}  link_to_special_page: {yaml_quote(patch['link_to_special_page'])}\n")

    for field_name in TRAILER_FIELDS:
        if patch.get(field_name, None):
            lines.append(f"{indent}  {field_name}: {yaml_quote(patch[field_name])}\n")


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
    lines = [
        '---\n',
        'layout: patches\n',
        'title: Patches\n',
        'last_modified_at: 2022-03-17\n',
        'permalink: /patches/\n',
        'description: "Search through class and jobs guides on the FFXIV Pocket Guide."\n',
        'page_type: index\n',
        'page_category: patches\n',
        'patches:\n',
    ]
    old_date = ""
    major_patches = set()
    minor_patches = set()
    processed_patches = []
    expansion_patches = {}
    patch_lookup = {}
    for key, value in versions.items():
        if value.get('disabled', False) == "true" and not nextRelease(value):
            continue

        new_date = datetime.strptime(value['date'].replace(".", "/"), '%Y/%m/%d')
        if old_date == "":
            old_date = new_date
        datediff = new_date - old_date
        old_date = new_date
        if key.endswith("0"):
            key = key[:-1]

        patch = {
            "name": value['name'],
            "patchnumber": key,
            "date": value['date'],
            "dslr": datediff.days,
            "pname": value['pname'],
        }
        if value.get('link_to_patch', None):
            patch["link_to_patch"] = value['link_to_patch']
        if value.get('link_to_special_page', None):
            patch["link_to_special_page"] = value['link_to_special_page']
        for field_name in TRAILER_FIELDS:
            if value.get(field_name, None):
                patch[field_name] = value[field_name]

        processed_patches.append(patch)
        expansion_patches.setdefault(patch["pname"], []).append(patch)
        patch_lookup[patch["patchnumber"]] = patch
        append_patch_yaml(lines, patch)

        ma_p, mi_p = key.split(".")
        if ma_p != "1":
            major_patches.add(ma_p)
            minor_patches.add(mi_p)

    sorted_major_patches = sorted(major_patches)
    sorted_minor_patches = sorted(minor_patches)

    lines.append('expansion_patches:\n')
    for expansion_name, expansion_patch_list in expansion_patches.items():
        lines.append(f'  {expansion_name}:\n')
        for patch in expansion_patch_list:
            append_patch_yaml(lines, patch, indent="    ")

    lines.append('major_patches:\n')
    for patch in sorted_major_patches:
        lines.append(f'    - "{patch}"\n')

    lines.append('minor_patches:\n')
    for patch in sorted_minor_patches:
        lines.append(f'    - "{patch}"\n')

    lines.append('patch_matrix_rows:\n')
    for minor in sorted_minor_patches:
        lines.append(f'    - minor: "{minor}"\n')
        lines.append('      values:\n')
        for major in sorted_major_patches:
            version = f"{major}.{minor}"
            patch_data = patch_lookup.get(version, None)
            dslr = patch_data["dslr"] if patch_data else ""
            patch_date = patch_data["date"] if patch_data else ""
            lines.append(f'        - major: "{major}"\n')
            lines.append(f'          dslr: {yaml_quote(dslr) if dslr == "" else dslr}\n')
            lines.append(f'          date: {yaml_quote(patch_date)}\n')

    lines.append('---\n')
    filecontent = "".join(lines)

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
        "dt": "title_logo700_hr1.tex.webp",
        "ec": "title_logo800_hr1.tex.webp"
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
