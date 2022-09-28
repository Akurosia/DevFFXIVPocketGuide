import json
from ffxiv_aku import *
from datetime import datetime, date


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


def patches():
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

        filecontent += f"    - name: {value['name']}\n"
        filecontent += f"      patchnumber: {key}\n"
        filecontent += f"      date: {value['date']}\n"
        filecontent += f"      dslr: {datediff.days}\n"
        filecontent += f"      pname: {value['pname']}\n"
        if value.get('link_to_patch', None):
            filecontent += f"      link_to_patch: {value['link_to_patch']}\n"
        if value.get('link_to_special_page', None):
            filecontent += f"      link_to_special_page: {value['link_to_special_page']}\n"

        ma_p, mi_p = key.split(".")
        if not ma_p in major_patches:
            major_patches.append(ma_p)
        if not mi_p in minor_patches and not ma_p == "1":
            minor_patches.append(mi_p)

    filecontent += 'major_patches:\n'
    for patch in sorted(major_patches):
        filecontent += '    - ' + str(patch) + "\n"

    filecontent += 'minor_patches:\n'
    for patch in sorted(minor_patches):
        filecontent += '    - ' + str(patch) + "\n"
    filecontent += '---\n'

    filename = f"_pages/patches/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)


def run():
    patches()


if __name__ == "__main__":
    run()
