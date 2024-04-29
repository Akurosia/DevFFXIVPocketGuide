from ffxiv_aku import *
import re
from openpyxl import load_workbook
import os
from io import BytesIO
from bs4 import BeautifulSoup
import requests

enitems = loadDataTheQuickestWay("Item.en.json")

def load_workbook_from_url(url):
    file = requests.get(url)
    return load_workbook(filename=BytesIO(file.content))


def read_xlsx_file():
    KEY = os.environ.get("GDRIVE_APIKEY")
    MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    SHEET = "11SBQWYyFnyh19Ku6T1Wr5tNAJvxdze8tvD6m4bzPGIA"
    r = f"https://www.googleapis.com/drive/v3/files/{SHEET}/export?key={KEY}&mimeType={MIME_TYPE}"
    wb = load_workbook_from_url(r)
    #wb = openpyxl.load_workbook('./guide_ffxiv.xlsx')
    sheet = wb['Tabelle1']
    max_row = sheet.max_row
    max_column = sheet.max_column
    return sheet, max_row, max_column


def get_items_per_fight(name):
    url = f"https://ffxiv.gamerescape.com/wiki/{name}"
    page = requests.get(url)
    if page.status_code == 200:
        content = page.content
    else:
        print_color_red(url)
        return []
    print(url)
    DOMdocument = BeautifulSoup(content, 'html.parser')
    items = []
    for table in DOMdocument.find_all('table'):
        #print(table)
        for a in table.find_all('a'):
            if a.find_all("img"):
                title = a.get("title")
                if title is None:
                    continue
                if "#Acquired from Duty" in title or \
                    "#Sold by Merchant" in title or \
                    "#Rewarded from Quests" in title or \
                    "#Rewarded from Treasure Map" in title or \
                    "#Potentially received from" in title or \
                    "#Acquired from Airship Voyage" in title or \
                    "#Logging" in title or \
                    "#Harvesting" in title or \
                    "#Mining" in title or \
                    "#Quarrying" in title or \
                    "#Rewarded from Levequests" in title or \
                    "#Acquired from Gardening" in title or \
                    "#Acquired from Venture" in title or \
                    "#Dropped by Monsters" in title or \
                    "#Acquired from Reduction" in title or \
                    "#Miscellaneous Acquisition" in title or \
                    "#FATE" in title or \
                    "#Recipes" in title or \
                    " (Lost Action)" in title or \
                    "#Acquired from Desynth" in title:
                    continue
                if title in ['Weather', 'NPCs', 'Quests', 'FATEs', 'Levequests', 'Hunting Log Targets', 'Monsters', 'Logging', 'Harvesting', 'Mining', 'Quarrying', 'Fishing Log Locations', "Open this page in Garland Data", "Open this page in the Eorzea Database", "Run a search in YouTube", "Tank", "Healer", "Damage Dealer", "Trust System", "Information Needed", "Add Image"]:
                    continue
                if "#Rewarded from TT Duel" in title:
                    title = title.replace("#Rewarded from TT Duel", "")
                if "#Acquired from Chest" in title:
                    title = title.replace("#Acquired from Chest", "")
                if " (Item)" in title:
                    title = title.replace(" (Item)", "")
                if "#Available during Event" in title:
                    title = title.replace("#Available during Event", "")
                if "#Received from Coffer" in title:
                    title = title.replace("#Received from Coffer", "")
                if "Torn from the Heavens-The Dark Colossus Destroys All" in title:
                    title = title.replace("Torn from the Heavens-The Dark Colossus Destroys All", "Torn from the Heavens/The Dark Colossus Destroys All")

                if title not in items:
                    for k, v in enitems.items():
                        if v['Name'].lower() == title.lower() or v['Singular'].lower() == title.lower():
                            items.append(k)
                            break
    return items


def get_data_from_xlsx(sheet, max_column, i):
    return str(sheet.cell(row=int(i), column=int(29)).value).replace("None", "").strip()


def run():
    sheet, max_row, max_column = read_xlsx_file()
    #max_row = 20
    result = ""
    f_resutl = {}
    for i in range(2, max_row):
        entry = get_data_from_xlsx(sheet, max_column, i)
        if entry == "":
            continue
        items = get_items_per_fight(entry)
        entry_value = f'\t"{entry}": {items}' + ",\n"
        if entry_value not in result:
            result += entry_value
            f_resutl[entry] = items


    print(f_resutl)
    writeJsonFile("after_item_scan.json", f_resutl)


def test():
    befor = readJsonFile("before_item_scan.json")
    after = readJsonFile("after_item_scan.json")
    delete_after = []
    for key, value in after.items():
        for item in value:
            try:
                befor[key].remove(item)
            except Exception as e:
                print(e)
    print_pretty_json(befor)

run()
