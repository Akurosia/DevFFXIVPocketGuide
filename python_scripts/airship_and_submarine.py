from ffxiv_aku import *
import traceback
from playwright.sync_api import Playwright, sync_playwright, expect
import time

data = None
submarineexploration = loadDataTheQuickestWay("submarineexploration.en.json", translate=False)

def iterate_locator(locator):
    return [locator.nth(x) for x in range(0, locator.count())]

key_map = {
    "Discover via": "unlocked_by",
    "EXP": "exp",
    "Alias": "alias",
    "Rank": "lvl",
    "link": "link",
    "Map": ""
}

def get_airship_information(page, data) -> None:
    try:
        page.goto("https://ffxiv.gamerescape.com/wiki/Category:Airship_Deployment_Sector")
        table = iterate_locator(page.locator("table"))[1:][0]
        tablehead = iterate_locator(table.locator("th"))
        tablerows = iterate_locator(table.locator("tbody").locator("tr"))[1:]
        for row in tablerows:
            name = ""
            location = {}
            elements = iterate_locator(row.locator("td"))
            for i, cell in enumerate(elements):
                header_name = tablehead[i].text_content().strip()
                cellvalue = cell.text_content().strip()
                if header_name == "Name":
                    location["link"] = cell.locator("a").get_attribute("href")
                    name = cellvalue
                else:
                    location[key_map[header_name]] = cellvalue
            #print(location)
            #add items if available
            if data["Sea of Clouds"].get(name, None):
                if data["Sea of Clouds"][name].get("items", None):
                    location["items"] = data["Sea of Clouds"][name]["items"]
            data["Sea of Clouds"][name] = location
    except Exception as e:
        traceback.print_exc()
    return data


def get_submarine_information(page, data) -> None:
    try:
        page.goto("https://ffxiv.gamerescape.com/wiki/Category:Subaquatic_Deployment_Sector")
        time.sleep(2)
        locations = iterate_locator(page.locator('.tabbertab'))
        for loc in locations:
            loc_name = loc.get_attribute("title").strip().replace("Lilac Sea", "The Lilac Sea")
            #if not loc_name == "South Indigo Deep (Lv. 120-)":
            #    continue
            print(loc_name)
            if not data.get(loc_name, None):
                data[loc_name] = {}
            #loc.click()

            table = iterate_locator(loc.locator("table"))[0]
            tablehead = iterate_locator(table.locator("th"))
            tablerows = iterate_locator(table.locator("tbody").locator("tr"))
            for row in tablerows:
                name = ""
                location = {}
                elements = iterate_locator(row.locator("td"))
                for i, cell in enumerate(elements):
                    header_name = tablehead[i].text_content().strip()
                    cellvalue = cell.inner_text().strip()
                    if header_name == "Name":
                        location["link"] = cell.locator("a").get_attribute("href")
                        name = cellvalue
                        continue
                    elif header_name == "Map":
                        continue
                    elif header_name == "Rank":
                        continue
                    location[key_map[header_name]] = cellvalue
                print(f"\t {location}")
                #add items if available
                if data[loc_name].get(name, None):
                    if data[loc_name][name].get("items", None):
                        location["items"] = data[loc_name][name]["items"]
                data[loc_name][name] = location
    except Exception as e:
        traceback.print_exc()
    return data


def get_items_per_location(page, url):
    page.goto(f"https://ffxiv.gamerescape.com{url}")
    table = iterate_locator(page.locator("table"))[2:][0]
    #print(table.text_content())
    tablehead = iterate_locator(table.locator("th"))
    tablerows = iterate_locator(table.locator("tbody").locator("tr"))[1:]
    items = []
    for row in tablerows:
        elements = iterate_locator(row.locator("td"))
        for i, cell in enumerate(elements):
            header_name = tablehead[i].text_content().strip()
            cellvalue = None
            counter = 0
            while cellvalue == None:
                try:
                    cellvalue = cell.inner_text().replace(" ", "").strip()
                except:
                    print("Try Again")
                    counter+=1
                    if counter > 1:
                        raise Exception
            if header_name == "Quantity":
                continue
            list_of_image = iterate_locator(cell.locator("img"))
            if len(list_of_image) > 2:
                continue
            for img in list_of_image:
                if img.get_attribute("alt") == "Airship XP Icon.png":
                    items.append(cellvalue)
    return items


def fix_submarine(data):
    for locations, location_spots in data.items():
        if locations == "Sea of Clouds":
            continue
        print(locations)
        for spot, spot_data in location_spots.items():
            for key, value in submarineexploration.items():
                if spot.lower() == value['Destination'].lower():
                    data[locations][spot]["lvl"] = value['RankReq']
                    break
    return data

def add_items(page, data):
    try:
        for locations, location_spots in data.items():
            print_color_yellow(locations)
            for spot, spot_data in location_spots.items():
                if spot == "":
                    continue
                if data[locations][spot].get("items", None) == []:
                    print_color_red("\t" + spot)
                elif not data[locations][spot].get("items", None):
                    print_color_green("\t" + f"{spot} - {spot_data.get("link", None)}")
                    items = get_items_per_location(page, spot_data['link'])
                    print_color_green("\t" + f"{items}")
                    data[locations][spot]["items"] = items
                    writeJsonFile("airship_submarine.json", data, sort_sub_keys=True)
                else:
                    print_color_red("\t" + spot)
    except Exception:
        traceback.print_exc()
        print("WROTE")
        writeJsonFile("airship_submarine.json", data, sort_sub_keys=True)
    return data

def run():
    global data
    os.chdir("../python_scripts")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        witdh, height = 1920, 1080
        context = browser.new_context(
            color_scheme='dark',
            viewport={"width": witdh, "height": height}
        )
        page = context.new_page()
        try:
            data = readJsonFile("airship_submarine.json") or { "Sea of Clouds": {} }
            #data = { "Sea of Clouds": {} }
            data = get_airship_information(page, data)
            data = get_submarine_information(page, data)
            data = fix_submarine(data)
            data = add_items(page, data)
        except Exception:
            traceback.print_exc()
        context.close()
        browser.close()
        writeJsonFile("airship_submarine.json", data, sort_sub_keys=True)
    os.chdir("../_posts")

if __name__ == "__main__":
    os.chdir("../_posts")
    run()
