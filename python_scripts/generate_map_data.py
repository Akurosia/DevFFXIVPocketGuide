from ffxiv_aku import *
from typing import Any
from bs4 import BeautifulSoup, Tag
from ffxiv_aku import *
try:
    from .helper import getImage
except:
    from helper import getImage
from PIL.ImageFile import ImageFile
from PIL import ImageDraw, ImageFont, Image, ImageOps
import traceback
import random

def test():
    aetherytes = readJsonFile(r"P:\extras\json\xivapi_data2\Aetheryte.json")
    aetherytes_trans = loadDataTheQuickestWay("Aetheryte.json")

    counter = 0
    w, h = (2048, 2048)
    for key, aetheryte in aetherytes.items():
        if aetheryte['fields']["Map"]['value'] == 16:
            print(key)
            continue
        for level in aetheryte['fields']["Level"]:
            if level['value'] == 0:
                continue
            if level.get('sheet', None) is None:
                continue

            counter += 1
            lev = getLevel(str(level['value']), lang="de", pixel=True)
            lev["x"] = lev["x"]+w/2
            lev["y"] = -lev["y"]+h/2
            name = aetherytes_trans[key]['AethernetName']['Name_de']

            print('{ "id": "' + str(counter) + f'", "name": "{name}", "category": "ore", "position": [{lev["x"]}, {lev["y"]}], "description": "{name}" ' + '},')


            lev = getLevel(str(level['value']), lang="de")
            _map = getMaps(lev['mapid'], "de")
            print(_map)

            _sizefactor = float(_map['SizeFactor'])
            _x_offset = float(_map['OffsetX'])
            _y_offset = float(_map['OffsetY'])
            x = FromMapCoordinate(result=float(lev["x"]), sizefactor=100)
            y = FromMapCoordinate(result=float(lev["y"]), sizefactor=100)
            x2 = ToMapPixel(val=x, offset=_x_offset, sizefactor=_sizefactor)
            y2 = ToMapPixel(val=y, offset=_y_offset, sizefactor=_sizefactor)
            x = x2 + w/2
            y = y2 + h/2
            print('{ "id": "1", "name": "' + name + '", "category": "'+ fix_slug(name) +'", "position": ['+f'{x},{-y2+h/2}'+'], "description": "' + name + '" },')


quest: dict[str, dict[str, str]] = loadDataTheQuickestWay("Quest.json")
fates: dict[str, dict[str, str]] = loadDataTheQuickestWay("Fate.json", translate=False)
fates_trans: dict[str, dict[str, str]] = loadDataTheQuickestWay("Fate.json", translate=True)
ttype: dict[str, dict[str, str]] = loadDataTheQuickestWay("TerritoryType.json", translate=True)
placename: dict[str, dict[str, str]] = loadDataTheQuickestWay("PlaceName.json", translate=True)
ces: dict[str, dict[str, str]] = loadDataTheQuickestWay("DynamicEvent.json")
ces_type: dict[str, dict[str, str]] = loadDataTheQuickestWay("DynamicEventType.json")
maps: dict[str, dict[str, str]] = loadDataTheQuickestWay("Map.json")
fishingspot: dict[str, dict[str, str]] = loadDataTheQuickestWay("Fishingspot.json", translate=False)
treasurehuntrank = loadDataTheQuickestWay("TreasureHuntRank.json")
spearfishingspot: dict[str, dict[str, str]] = loadDataTheQuickestWay("SpearfishingNotebook.json", translate=False)
fatemapping = {
        'ui/icon/060000/060852.tex': 'Notorious monster',

        "ui/icon/060000/060801.tex": "Gegner Wellen",
        "ui/icon/060000/060802.tex": "Boss besiegen",
        "ui/icon/060000/060803.tex": "Sammeln",
        "ui/icon/060000/060804.tex": "Verteidigen",

        'ui/icon/000000/000000.tex': 'NoType',

        'ui/icon/060000/060501.tex': 'Kill Enemies',
        'ui/icon/060000/060502.tex': 'Kill Boss',
        'ui/icon/060000/060503.tex': 'Collect',
        'ui/icon/060000/060504.tex': 'Defense',
        'ui/icon/060000/060505.tex': 'Escort',
        'ui/icon/060000/060506.tex': 'Chase',
        'ui/icon/060000/060508.tex': 'Holiday (Limited Time)',
        'ui/icon/060000/060994.tex': 'Concerted works',

        'ui/icon/060000/060958.tex': 'Notorious monsters',
        'ui/icon/063000/063926.tex': 'Fete',

        "ui/icon/063000/063909.tex": "CE Boss besiegen",
        "ui/icon/063000/063910.tex": "CE Solo Kampf",
        "ui/icon/063000/063911.tex": "CE Gegner Wellen",

}
fatemapping2 = {v:k for k,v in fatemapping.items()}
path_of_main_script = ""

def get_x_image(_id: str = "NoType"):
    # Load the overlay image (e.g., icon or stamp)
    _id = fatemapping2[_id]
    _id = _id.replace("ui/icon/", "").replace(".tex", "").split("/")[1]
    overlay_path = f"P:/extras/images/ui/icon/{_id[:3]}000/{_id}_hr1.png" # Replace with your overlay image path
    overlay_image = Image.open(overlay_path)

    # Resize the cropped overlay image if necessary
    x = 40
    y = 40
    overlay_size = (x, y)  # Adjust the size as needed
    overlay_image = overlay_image.resize(overlay_size)
    overlay_image = overlay_image.convert("RGBA")
    return overlay_image, int(x/2), int(y/2)


def getMapFromID(mapid):
    for key, value in maps.items():
        if value['Id'] == mapid:
            return value


def load_url_as_bs4(url: str) -> BeautifulSoup:
    page: requests.Response = requests.get(url, timeout=60)
    if page.status_code != 200:
        raise Exception()
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    return soup


def getTablesFromConsoleGamesWiki(url: str, zone: str) -> dict[str, Any]:
    soup: BeautifulSoup = load_url_as_bs4(url)
    main: Tag = soup.select(".mw-parser-output")[0] # type: ignore
    tables: list[Tag] = main.find_all("table", {"class":"location sortable table"}) # type: ignore
    result: dict[str, Any] = {}
    for table in tables:
        tbody: Tag = table.find_all("tbody")[0] # type: ignore
        entries: list[Tag] = tbody.find_all("tr") # type: ignore
        thead: Tag = entries[0]
        entries = entries[1:]

        header: list[str] = []
        cols: list[Tag] = thead.find_all("th") # type: ignore
        for col in cols:
            h: str = col.text.strip() # type: ignore
            if h == "FATE":
                h = "Fate Name"
            elif h == "Fate Location":
                h = "Location"
            header.append(h)

        for row in entries:
            tmp: dict[str, Any] = {}
            cols = row.find_all("td") # type: ignore
            for i, col in enumerate(cols):
                if i == 0 and header[i] == "":
                    continue
                if header[i] == "Location":
                    name = col.text.strip()
                    name = name.split("(X:")[1]
                    name = name.split(")")[0]
                    x, y = name.split(", Y:")
                    tmp[header[i]] = {
                        "x": x,
                        "y": y,
                    }
                else:
                    tmp[header[i]] = col.text.strip() # type: ignore
            tmp['Fate Name'] = fixFateNames(tmp['Fate Name'])
            print(tmp['Fate Name'])
            found = False
            for key, value in fates.items():
                if tmp['Fate Name'].lower() == value['fields']['Name'].lower().strip():
                    tmp["Fate ID"] = key
                    tmp["Fate Type"] = "Fate"
                    found = True
                    break
            for key, value in ces.items():
                if tmp['Fate Name'].lower() == value['Name_de'].lower().strip():
                    tmp["Fate ID"] = key
                    tmp["Fate Type"] = "CE"
                    found = True
                    break
            if not found:
                continue
            tmp = fix_fate_ids(tmp)
            result[tmp["Fate ID"]] = tmp
    return result


def fix_fate_ids(tmp: dict[str, Any]) -> dict[str, Any]:
    if tmp['Fate Name'] == "Sister Crustacean":
        tmp["Fate ID"] = "235"
    if tmp['Fate Name'] == "Tender Buttons":
        tmp["Fate ID"] = "290"
    if tmp['Fate Name'] == "Shadow Over Stilltide":
        tmp["Fate ID"] = "1465"
    if tmp['Fate Name'] == "The Wright Stuff":
        tmp["Fate ID"] = "1467"
    if tmp['Fate Name'] == "Tojil Annihilation":
        tmp["Fate ID"] = "1446"
    return tmp


def fixFateNames(name: str) -> str:
    #print_color_yellow(name)
    name = name.strip()
    name = re.sub(r"^\(Lv. \d+\) ", "", name)
    name = name.replace(" (FATE)", "")
    if name == "Sneak and Spell":
        name = "Sneak & Spell"
    if name == "The Killing of a Sacred Bombadier":
        name = "The Killing of a Sacred Bombardier"
    if name == "On the Non-existent":
        name = "On the Nonexistent"
    #print_color_blue(name)
    return name


def add_extra_data(result: dict[str, Any]) -> dict[str, Any]:
    result["Western La Noscea"]['336'] = {
            "Company Seals": "58",
            "Experience": "4,158",
            "Fate ID": "336",
            "Fate Level": "45",
            "Fate Name": "The Mandragoras",
            "Fate Type": "Fate",
            "Gil": "90",
            "Location": {
                "x": "19",
                "y": "35"
            }
        }
    result["Kholusia"]['1466'] = {
            "Experience": "48,600",
            "Fate ID": "1465",
            "Fate Name": "Shadow Over Stilltide",
            "Fate Type": "Fate",
            "Gemstones": "12",
            "Gil": "140",
            "Level": "70",
            "Location": {
                "x": "31.8",
                "y": "24.8"
            },
            "Type": "Slay enemies"
        }
    result["Kholusia"]['1468'] = {
            "Experience": "48,600",
            "Fate ID": "1467",
            "Fate Name": "The Wright Stuff",
            "Fate Type": "Fate",
            "Gemstones": "12",
            "Gil": "140",
            "Level": "70",
            "Location": {
                "x": "12.6",
                "y": "27.3"
            },
            "Type": "Slay enemies"
        }
    result["The Rak'tika Greatwood"]['1447'] = {
            "Experience": "50,220",
            "Fate ID": "1447",
            "Fate Name": "Tojil Annihilation",
            "Fate Type": "Fate",
            "Gemstones": "12",
            "Gil": "150",
            "Level": "75",
            "Location": {
                "x": "30.4",
                "y": "22.3"
            },
            "Type": "Notorious monster"
        }
    return result


def getLinksFromConsoleGamesWiki(createnew = False):
    result = {}
    soup: BeautifulSoup = load_url_as_bs4("https://ffxiv.consolegameswiki.com/wiki/List_of_FATEs")
    main: Tag = soup.select(".mw-parser-output")[0]

    try:
        if createnew:
            ERROR
        result = readJsonFile("FatesFromConsoleWiki.json")
    except:
        result = {}
    zones: list[Tag] = main.find_all("h3")
    for zone in zones:
        zonename: str = zone.text.strip().replace(" FATEs", "")
        if zonename == "The Bozjan Southern Front":
            zonename = "Bozjan Southern Front"
        if result.get(zonename, None):
            continue
        try:
            print(zonename)
            if not result.get(zonename, None):
                result[zonename] = {}
            link = zone.find("a", href=True)
            result[zonename] = getTablesFromConsoleGamesWiki(f"https://ffxiv.consolegameswiki.com{link['href']}", zonename)
        except Exception as e:
            print_color_red(f"Error for {zonename} ({e})")
            print(traceback.format_exc())
    #result = add_extra_data(result)
    return result

unique_fate_types = {
    "Map": set(),
    "Objective": set(),
    "Combined": set(),
}

def get_data_from_teamcraft():
    global unique_fate_types
    result = {}
    data = readJsonFile("https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/refs/heads/staging/libs/data/src/lib/json/fates.json")
    for key, value in data.items():
        if not value.get("position", {}).get('zoneid', None) and not value['location'] == 0:
            #print_color_red(f"Missing ZONE: key: {key} value: {value['name']['en']}")
            if key == "1626":
                value['position'] = { "zoneid": 3534, "map": 606, "x": "14.3", "y": "18.2" }
        if value.get("position", {}).get('zoneid', None):
            del value['description']
            place = placename[str(value["position"]["zoneid"])]['Name_en']
            if not result.get(place, None):
                result[place] = {}
            icon = value['icon'].replace("/i/", "ui/icon/").replace(".png", ".tex") if value.get('icon', None) and not value.get('icon', None) == "" else fatemapping.get(fates[key]['fields']['ObjectiveIcon'][0]['Icon']['path_hr1'], "")
            if icon == "":
                icon = "ui/icon/000000/000000.tex"
            result[place][key] = {
                "Location": {
                    "x": value["position"]["x"],
                    "y": value["position"]["y"],
                },
                "Company Seals": "",
                "Experience": "",
                "Fate ID": f"{key}",
                "Fate Level": fates[key]['fields']['ClassJobLevel'],
                "Fate Level Sync": fates[key]['fields']['ClassJobLevelMax'],
                "Fate Name": fates[key]['fields']['Name'],
                "Fate Type": "Fate",
                "Type": fatemapping[icon],
                #"Icon Map": fates[key]['fields']['Icon']['Map'],
                "Icon Objective": icon,
                "Gil": ""
            }
            unique_fate_types['Map'].add(fates[key]['fields']['MapIcon']['path_hr1'])
            unique_fate_types['Objective'].add(fates[key]['fields']['ObjectiveIcon'][0]['Icon']['path_hr1'])
            unique_fate_types['Combined'].add(fates[key]['fields']['MapIcon']['path_hr1'] + " + " + fates[key]['fields']['ObjectiveIcon'][0]['Icon']['path_hr1'])
    #for key, value in unique_fate_types.items():
    #    print(key, sorted(value))
    return result


def merge_fate_data(tc_fates: dict, gw_fates: dict):
    for zonename, fates_per_zone in tc_fates.items():
        if not gw_fates.get(zonename, None):
            gw_fates[zonename] = fates_per_zone
            #print_color_red(f"MISSING ZONENAME: {zonename}")
            if zonename == "The Firmament":
                for fate_id, fate_data in fates_per_zone.items():
                    gw_fates[zonename][fate_id]["Fate Type"] = "Fêtes"

        for fate_id, fate_data in fates_per_zone.items():
            if not gw_fates[zonename].get(fate_id, None):
                gw_fates[zonename][fate_id] = fate_data
                #print_color_blue(f"MISSING FATE: {fate_data["Fate Name"]}")

            gw_fates[zonename][fate_id]['Location'] = fate_data['Location']
            gw_fates[zonename][fate_id]['Fate ID'] = fate_data['Fate ID']
            gw_fates[zonename][fate_id]['Fate Level'] = fate_data['Fate Level']
            gw_fates[zonename][fate_id]['Fate Level Sync'] = fate_data['Fate Level Sync']
            gw_fates[zonename][fate_id]['Type'] = fate_data['Type']
            gw_fates[zonename][fate_id]["Icon Objective"] = fate_data["Icon Objective"]

        #print(key, value)
    return gw_fates


def get_baseimage_by_location(location):
    _id = None
    for key, value in ttype.items():
        if value['PlaceName']['Name_en'] == location:
            if len(value['Name']) < 5:
                _id = value['Name']
    if not _id:
        ERROR
    folder: str = _id[:3]
    name: str = _id.split("/")[0]
    posible_maps: list[str] = []
    for x in glob(f"P:/extras/images/ui/map/{folder}/{name}*.png"):
        if not len(x.split(" - ")) == 2: continue
        if "_event" in x: continue
        if "Altes Bootshaus.png" in x: continue
        if "Dom der Einkehr.png" in x: continue
        if "Nabaath-Mine.png" in x: continue
        if "Ruinen von Ronka.png" in x: continue
        if "Die _Emphasis_Dalriada__Emphasis_.png" in x: continue
        if "Castrum Lacus Litore.png" in x: continue
        if "_" in x: continue
        posible_maps.append(x)
    if len(posible_maps) > 1:
        print(posible_maps)
    return posible_maps[0]


def add_text_to_image(modified_image, x, y, x_off, y_off, fate_id, _type):
    global fates_trans
    global ces
    y_fate_offset_no_overlap = 0
    if _type == "CE":
        fate_name = ces[fate_id]['Name_de']
        index = 0
    else:
        try:
            fate_name = fates_trans[str(int(fate_id, 16))]['Name_de']
        except:
            fate_name = fates_trans[fate_id]['Name_de']
        index = 1
    if fate_name == "Kampf um Leben und Schweiß":
        y_fate_offset_no_overlap = -20
    #draw modifies the image in memory
    draw = ImageDraw.Draw(modified_image)
    # Choose a random position offset: above, below, or right of the icon
    offset_options = [
        ("", 0, -20),   # slightly above
        ("", 0, 100),    # slightly below
        #("", 100, 30),   # to the right
    ]
    arrow, x_offset_text, y_offset_text = offset_options[index]
    x_offset_lentext = 0
    if len(fate_name) > 6:
        x_offset_lentext = (len(fate_name)-6)*5

    try:
        font = ImageFont.truetype("arialbd.ttf", 25)
    except IOError:
        font = ImageFont.load_default()
    text = arrow + fate_name
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    padding = 8

    # Initial position
    text_x = int(x) - x_off + x_offset_text - x_offset_lentext
    text_y = int(y) - y_off + y_offset_text + y_fate_offset_no_overlap

    # Clamp position to keep everything within image bounds
    img_width, img_height = modified_image.size
    rect_width = text_width + 2 * padding
    rect_height = text_height + 2 * padding

    # Adjust x if needed
    if text_x < 0:
        text_x = 0
    elif text_x + rect_width > img_width:
        text_x = img_width - rect_width

    # Adjust y if needed
    if text_y < 0:
        text_y = 0
    elif text_y + rect_height > img_height:
        text_y = img_height - rect_height

    # Background box
    rect_coords = [
        (text_x - padding, text_y - padding),
        (text_x + text_width + padding, text_y + text_height + padding)
    ]

    draw.rounded_rectangle(rect_coords, radius=10, fill=(255, 255, 255, 180))
    draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    return text


def generate_images():
    data = readJsonFile("FatesFromConsoleWiki.json")
    fate_by_type = {}
    for location, fates_per_zone in data.items():
        fate_by_type[location] = {}
        for fate_id, fate_data in fates_per_zone.items():
            if not fate_by_type[location].get(fate_data.get('Type', "NoType"), None):
                fate_by_type[location][fate_data.get('Type', "NoType")] = []
            fate_by_type[location][fate_data.get('Type', "NoType")].append(fate_id)

    for location, fate_type in fate_by_type.items():
        #if not location in ["Lower La Noscea"]:
        #    continue
        _map_id = None
        for x, value in ttype.items():
            if value['PlaceName']['Name_en'] == location:
                # check if the territory name e.g. o6b1 has less then 5 chars to avoid o6b1/01_event things
                if len(value['Name']) < 5:
                    _map_id = value['Map']['Id']
                    _map = getMapFromID(_map_id)
                    _sizefactor = float(_map['SizeFactor'])

                    _x_offset = float(_map['OffsetX'])
                    _y_offset = float(_map['OffsetY'])

                    #print_color_green(location)
                    if location in ["Eureka Hydatos", "Bozjan Southern Front"]:
                        _x_offset = 0
                        _y_offset = 0
                    elif location in ["Ul'dah - Steps of Nald", "Old Gridania"]:
                        _x_offset = 520
                        _y_offset = 520
                    elif location in ["The Sea of Clouds", "Azys Lla", "Coerthas Western Highlands", "The Churning Mists", "The Dravanian Forelands", "The Dravanian Hinterlands"]:
                        _x_offset = -50
                        _y_offset = -50

        if not _map_id:
            print_color_yellow(location)
            continue
        baseimage = get_baseimage_by_location(location)
        baseimg2 = baseimage.replace("P:/extras/images", "").replace("\\", "/")
        flug = fix_slug(location).replace("_", "-")
        json_as_dict = {
            "id": f"{flug}",
            "name": f"{location}",
            "imageUrl": f"https://ff14.akurosiakamo.de/extras/images/{baseimg2}",
            "size": [
                2048,
                2048
            ],
            "defaultZoom": -1.2,
            "minZoom": -1.2,
            "maxZoom": 1.7,
            "categories": [
                {"id": "ore", "name": "Ore Node", "color": "#f59e0b"},
                {"id": "herb", "name": "Herb Node", "color": "#22c55e"},
                {"id": "notorious_monster", "name": "Notorious monster", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060852_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Gegner Wellen", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060801_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Boss besiegen", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060802_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Sammeln", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060803_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Verteidigen", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060804_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "NoType", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/000000/000000_hr1.webp", "size": [30,30]},
                {"id": "kill_enemies", "name": "Kill Enemies", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060501_hr1.webp", "size": [30,30]},
                {"id": "kill_boss", "name": "Kill Boss", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060502_hr1.webp", "size": [30,30]},
                {"id": "collect", "name": "Collect", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060503_hr1.webp", "size": [30,30]},
                {"id": "defense", "name": "Defense", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060504_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Escort", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060505_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Chase", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060506_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Holiday (Limited Time", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060508_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Concerted works", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060994_hr1.webp", "size": [30,30]},
                {"id": "notorious_monsters", "name": "Notorious monsters", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/060000/060958_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "Fete", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/063000/063926_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "CE Boss besiegen", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/063000/063909_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "CE Solo Kampf", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/063000/063910_hr1.webp", "size": [30,30]},
                {"id": "fates", "name": "CE Gegner Wellen", "group": "Fates", "groupName": "FATEs", "iconUrl": "/assets/img/game_assets/063000/063911_hr1.webp", "size": [30,30]},

                {"id": "quest_side", "name": "Quest - side", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/071000/071221_hr1.webp", "size": [40,40]},
                {"id": "quest_main", "name": "Quest - main", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/071000/071201_hr1.webp", "size": [40,40]},
                {"id": "quest_side_small", "name": "Quest - side_small", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/071000/071222_hr1.webp", "size": [40,40]},
                {"id": "quest_blue", "name": "Quest - blue", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/071000/071341_hr1.webp", "size": [40,40]},
                {"id": "quest_blue2", "name": "Quest - blu2e", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/071000/071341_hr1.webp", "size": [40,40]},
                {"id": "quest_alt_sharliyan", "name": "Quest - alt_sharliyan", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/062000/062521_hr1.webp", "size": [40,40]},
                {"id": "quest_tuliyollal", "name": "Quest - Tuliyollal", "group": "quest", "groupName": "Quest", "iconUrl": "/assets/img/game_assets/062000/062523_hr1.webp", "size": [40,40]},

                {"id": "fishing_angel", "name": "Fishing - Angel", "group": "fishing", "groupName": "Fishing"},
                {"id": "fishing_spear", "name": "Fishing - Speer", "group": "fishing", "groupName": "Fishing"},

                {"id": "gathering-zone", "name": "Gathering Zone", "color": "#FFc55e", "group": "Zones", "groupName": "Zones"}
            ],
            "markers": [],
            "areas": []
        }

        #print_color_red(baseimage)
        #print_color_red((fix_slug(location), _map_id, _map['OffsetX'], _map['OffsetY'], _map['SizeFactor']))
        #print()
        original_image: ImageFile = Image.open(baseimage)
        #print_pretty_json(fate_type)
        for _type, f_type in fate_type.items():
            w, h = original_image.size
            for fate_id in f_type:
                # without the 100 here and the filter above we get wrong result when calculating pixels

                if data[location][fate_id]['Location']['x'] == "":
                    data[location][fate_id]['Location']['x'] = 0
                if data[location][fate_id]['Location']['y'] == "":
                    data[location][fate_id]['Location']['y'] = 0
                x = FromMapCoordinate(result=float(data[location][fate_id]['Location']['x']), sizefactor=100)
                y = FromMapCoordinate(result=float(data[location][fate_id]['Location']['y']), sizefactor=100)
                x2 = ToMapPixel(val=x, offset=_x_offset, sizefactor=_sizefactor)
                y2 = ToMapPixel(val=y, offset=_y_offset, sizefactor=_sizefactor)
                x = x2 + w/2
                y = y2 + h/2

                text = add_text_to_image(original_image, x, y, 0, 0,data[location][fate_id].get('Fate ID', 'Unknown'), data[location][fate_id].get('Fate Type', 'Unknown'))

                if text:
                    json_as_dict['markers'].append({ "id": "1", "name": text, "category": fix_slug(_type), "position": [x,-y2+h/2], "description": "" })

        #json_as_dict['markers'].append({ "id": "zone-1", "name": "Central Field", "category": "gathering-zone", "description": "Level 10–15 gathering area", "points": [ [ 700, 400 ], [ 900, 420 ], [ 920, 650 ], [ 580, 640 ] ] })
        tmaps, maptypes = get_treasuremaps(_map_id, w, h)
        for tmap in tmaps:
            json_as_dict['markers'].append(tmap)
        for tmap in maptypes:
            json_as_dict['categories'].append(tmap)

        tmaps = get_fishingspot(_map_id, w, h)
        for tmap in tmaps:
            json_as_dict['markers'].append(tmap)
        tmaps = get_spearfishingspot(_map_id, w, h)
        for tmap in tmaps:
            json_as_dict['markers'].append(tmap)
        tmaps = get_quest(_map_id, w, h)
        for tmap in tmaps:
            json_as_dict['markers'].append(tmap)

        new_failename = f"{path_of_main_script}/assets/leaflet/maps/" + flug + ".json"
        writeJsonFile(new_failename, json_as_dict)

try:
    from treasurespot import get_coords_later
except:
    from .treasurespot import get_coords_later
coords = {}
def get_treasuremaps(mapid, w, h):
    maps = []
    maptypes = []
    global coords
    if coords == {}:
        coords = get_coords_later({})
    for treasuremapid, treasuremapdata in coords.items():
        #if not treasuremapid == "1":
        #    continue
        item = treasurehuntrank[treasuremapid]['ItemName']['Name_de']
        maptypes.append({ "id": f"treasuremap_{fix_slug(item)}", "name": f"{item}", "group": "treasuremap", "groupName": "Schatzkarten", "color": "#22c55e" })
        for treasuremapdata_mappid, treasuremapdata_data in treasuremapdata.items():
            if mapid in treasuremapdata_mappid:
                for tmap in treasuremapdata_data:
                    tx = (tmap[0]) + w/2
                    ty = -(tmap[1]) + h/2
                    maps.append({  "type": f"treasuremap_{fix_slug(item)}",  "imageUrl": f"/assets/img/TreasureMaps/{item}/empty_map.webp",  "size": [220, 200],  "position": [tx, ty]})
    return maps, maptypes

def fix_special(merged_fates):
    for zone in ['Zadnor', 'Bozjan Southern Front']:
        for fate_id, fate_data in merged_fates[zone].items():
            if not fate_data.get('Icon Objective', None):
                icon = ces[fate_id]["EventType"]["IconObjective1"]['path']
                merged_fates[zone][fate_id]['Type'] = fatemapping[icon]
    return merged_fates

fishdata = {}
def get_fishingspot(mapid, w, h):
    maps = []
    global fishdata
    if fishdata == {}:
        for key, value in fishingspot.items():
            try:
                value['fields']['TerritoryType']['fields']['Map']['fields']['Id']
            except:
                continue
            _map_id = value['fields']['TerritoryType']['fields']['Map']['fields']['Id']
            placename_name = value['fields']['PlaceName']['fields']['Name']
            radius = value['fields']['Radius']
            if not fishdata.get(_map_id, None):
                fishdata[_map_id] = {}
            if not fishdata[_map_id].get(key, None):
                fishdata[_map_id][key] = []
            fishdata[_map_id][key].append((( value['fields']['X']), ( value['fields']['Z']), placename_name, round(radius/3, 1)))
    if not fishdata.get(mapid, None):
        return maps
    for key, value in fishdata[mapid].items():
        x, y, name, radius = value[0]
        maps.append({  "type": "fishing_angel", "name": f"{name}", "imageUrl": "/assets/img/content/map/angel.webp", "size": [radius, radius],  "position": [x, h-y]})
    return maps

spearfishdata = {}
def get_spearfishingspot(mapid, w, h):
    maps = []
    global spearfishdata
    if spearfishdata == {}:
        for key, value in spearfishingspot.items():
            try:
                value['fields']['TerritoryType']['fields']['Map']['fields']['Id']
            except:
                continue
            _map_id = value['fields']['TerritoryType']['fields']['Map']['fields']['Id']
            placename_name = value['fields']['PlaceName']['fields']['Name']
            radius = value['fields']['Radius']
            if not spearfishdata.get(_map_id, None):
                spearfishdata[_map_id] = {}
            if not spearfishdata[_map_id].get(key, None):
                spearfishdata[_map_id][key] = []
            spearfishdata[_map_id][key].append((( value['fields']['X']), ( value['fields']['Y']), placename_name, round(radius/3, 1)))
    if not spearfishdata.get(mapid, None):
        return maps
    for key, value in spearfishdata[mapid].items():
        x, y, name, radius = value[0]
        maps.append({  "type": "fishing_spear", "name": f"{name}", "imageUrl": "/assets/img/content/map/speer.webp", "size": [radius, radius],  "position": [x, h-y]})
    return maps

questdata = {}
questtypes = {
    "1":  ("side", "071000/071221_hr1.webp"),
    "3":  ("main", "071000/071201_hr1.webp"),
    "4":  ("side_small", "071000/071222_hr1.webp"),
    "8":  ("blue", "071000/071341_hr1.webp"),
    "10": ("blue2", "071000/071341_hr1.webp"),
    "33": ("alt_sharliyan", "062000/062521_hr1.webp"),
    "34": ("tuliyollal", "062000/062523_hr1.webp"),
}
def get_quest(mapid, w, h):
    maps = []
    global questdata
    if questdata == {}:
        for key, value in quest.items():
            try:
                value['IssuerLocation']['Map']['Id']
            except:
                continue
            _map_id = value['IssuerLocation']['Map']['Id']
            placename_name = value['Name_de']
            if not questdata.get(_map_id, None):
                questdata[_map_id] = {}
            if not questdata[_map_id].get(key, None):
                questdata[_map_id][key] = []
            questtype = questtypes[value['EventIconType']['value']]
            getImage(questtype[1])
            questdata[_map_id][key].append((( value['IssuerLocation']['X']), ( value['IssuerLocation']['Z']), placename_name, questtype))
    if not questdata.get(mapid, None):
        return maps
    for key, value in questdata[mapid].items():
        x, y, name, questtype = value[0]

        maps.append({  "type": f"quest_{questtype[0]}", "name": f"{name}", "position": [x+w/2, h/2-y]})
    return maps

def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    global path_of_main_script
    path_of_main_script = main_script
    try:
        tc_fates = get_data_from_teamcraft()
        #print_color_blue(tc_fates)
        gw_fates = getLinksFromConsoleGamesWiki(0)
        merged_fates = merge_fate_data(tc_fates, gw_fates)
        merged_fates = fix_special(merged_fates)
        #print_pretty_json(merged_fates['Bozjan Southern Front'])

        writeJsonFile(f"{path_of_main_script}/python_scripts/FatesFromConsoleWiki.json", merged_fates)
        #writeJsonFile(f"{path_of_main_script}/python_scripts/FatesFromConsoleWiki.json", merged_fates)
        #writeJsonFile(r"C:\Users\Akurosia\Documents\GitHub\DevFFXIVPocketGuide\python_scripts\FatesFromConsoleWiki.json", merged_fates)

        print("[GAFD] Completed getting new Fates")
    except Exception as e:
        traceback.print_exc()
    generate_images()

def get_base_images():
    lst = ["061000/061879_hr1","061000/061880_hr1","061000/061878_hr1","061000/061877_hr1","061000/061876_hr1","061000/061875_hr1","061000/061533_hr1","000000/000046_hr1","000000/000115_hr1","056000/056935_hr1","057000/057357_hr1","060000/060453_hr1","061000/061432_hr1","061000/061723_hr1","061000/061757_hr1","061000/061759_hr1","061000/061767_hr1","061000/061821_hr1","061000/061822_hr1","061000/061828_hr1","061000/061834_hr1","061000/061835_hr1"]
    for img in lst:
        getImage(img)

if __name__ == "__main__":
    run()
    #get_base_images()
