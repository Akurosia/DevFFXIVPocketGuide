from ffxiv_aku import *
import traceback
from pathlib import Path
from playwright.sync_api import Page, sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth

data = None
#submarineexploration = loadDataTheQuickestWay("submarineexploration.en.json", translate=False)
#submarineexploration = readJsonFile(r"C:\Users\kamot\Desktop\XIVAPI\translated\SubmarineExploration.json")
submarineexploration: dict[str, dict[str, str]] = loadDataTheQuickestWay("SubmarineExploration.json")
GAMERESCAPE_BASE_URL = "https://ffxiv.gamerescape.com"
AIRSHIP_URL = f"{GAMERESCAPE_BASE_URL}/wiki/Category:Airship_Deployment_Sector"
SUBMARINE_URL = f"{GAMERESCAPE_BASE_URL}/wiki/Category:Subaquatic_Deployment_Sector"


class CloudflareBlockedError(RuntimeError):
    pass


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


def is_cloudflare_page(page: Page) -> bool:
    title = page.title().lower()
    body = page.locator("body").inner_text(timeout=5000).lower()
    cloudflare_markers = [
        "cloudflare",
        "checking if the site connection is secure",
        "verify you are human",
        "attention required",
    ]
    return any(marker in title or marker in body for marker in cloudflare_markers)


def open_gamerescape_page(page: Page, url: str, ready_selector: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    if is_cloudflare_page(page):
        print_color_yellow(
            "[AAS] Gamer Escape showed a Cloudflare challenge. "
            "Solve it in the visible browser window; the script will continue automatically."
        )
        try:
            page.wait_for_function(
                """() => {
                    const text = document.body?.innerText?.toLowerCase() || "";
                    const title = document.title.toLowerCase();
                    return !text.includes("cloudflare")
                        && !text.includes("checking if the site connection is secure")
                        && !text.includes("verify you are human")
                        && !title.includes("attention required");
                }""",
                timeout=180000,
            )
        except PlaywrightTimeoutError as exc:
            raise CloudflareBlockedError(
                "Cloudflare challenge was not cleared. Keeping the existing airship_submarine.json cache."
            ) from exc

    try:
        page.wait_for_selector(ready_selector, timeout=60000)
    except PlaywrightTimeoutError as exc:
        if is_cloudflare_page(page):
            raise CloudflareBlockedError(
                "Gamer Escape is still blocked by Cloudflare. Keeping the existing airship_submarine.json cache."
            ) from exc
        raise


def get_airship_information(page, data) -> None:
    try:
        open_gamerescape_page(page, AIRSHIP_URL, "table")
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
        open_gamerescape_page(page, SUBMARINE_URL, ".tabbertab")
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
    open_gamerescape_page(page, f"{GAMERESCAPE_BASE_URL}{url}", "table")
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
                if spot.lower() == value['Destination_en'].lower():
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

def run(path_of_main_script):
    global data
    root = Path(path_of_main_script)
    script_dir = root / "python_scripts"
    cache_file = script_dir / "airship_submarine.json"
    browser_profile = root / "tmp" / "gamerescape_browser_profile3"
    origin = Path.cwd()
    os.chdir(script_dir)

    try:
        data = readJsonFile(str(cache_file)) or { "Sea of Clouds": {} }
    except FileNotFoundError:
        data = { "Sea of Clouds": {} }

    custom_languages = ("de-DE", "de")
    stealth = Stealth(
        navigator_languages_override=custom_languages,
        init_scripts_only=True
    )
    try:
        with sync_playwright() as playwright:
            witdh, height = 1920, 1080
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            stealth.apply_stealth_sync(context)
            page = context.pages[0] if context.pages else context.new_page()
            try:
                data = get_airship_information(page, data)
                data = get_submarine_information(page, data)
                data = fix_submarine(data)
                data = add_items(page, data)
                writeJsonFile(str(cache_file), data, sort_sub_keys=True)
            except CloudflareBlockedError as exc:
                print_color_yellow(f"[AAS] {exc}")
            except Exception:
                traceback.print_exc()
                writeJsonFile(str(cache_file), data, sort_sub_keys=True)
            finally:
                context.close()
    finally:
        os.chdir(origin)

if __name__ == "__main__":
    os.chdir("..")
    run(os.getcwd())
