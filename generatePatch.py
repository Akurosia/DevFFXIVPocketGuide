import json
from ffxiv_aku import *
from datetime import datetime, date


def writeline(f, data):
    f.write(data)
    f.write("\n")


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
    with open(f"_pages/patches/index.html", "w", encoding="utf8") as f:
        writeline(f, '---')
        writeline(f, 'layout: patches')
        writeline(f, 'title: Patches')
        writeline(f, 'last_modified_at: 2022-03-17')
        writeline(f, 'permalink: /patches/')
        writeline(f, 'description: "Search through class and jobs guides on the FFXIV Pocket Guide."')
        writeline(f, 'page_type: index')
        writeline(f, 'page_category: patches')
        writeline(f, 'patches:')
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

            writeline(f, f"    - name: {value['name']}")
            writeline(f, f"      patchnumber: {key}")
            writeline(f, f"      date: {value['date']}")
            writeline(f, f"      dslr: {datediff.days}")
            writeline(f, f"      pname: {value['pname']}")
            if value.get('link_to_patch', None):
                writeline(f, f"      link_to_patch: {value['link_to_patch']}")
            if value.get('link_to_special_page', None):
                writeline(f, f"      link_to_special_page: {value['link_to_special_page']}")

            ma_p, mi_p = key.split(".")
            if not ma_p in major_patches:
                major_patches.append(ma_p)
            if not mi_p in minor_patches and not ma_p == "1":
                minor_patches.append(mi_p)

        writeline(f, 'major_patches:')
        for patch in sorted(major_patches):
            writeline(f, '    - ' + str(patch))

        writeline(f, 'minor_patches:')
        for patch in sorted(minor_patches):
            writeline(f, '    - ' + str(patch))
        writeline(f, '---')


def run():
    patches()


if __name__ == "__main__":
    run()
