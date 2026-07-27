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


def sort_key(value):
    return str(value).casefold()


def normalize_cell_value(value):
    return " ".join(str(value or "").replace("\xa0", " ").split())


def normalize_exp(value):
    normalized = normalize_cell_value(value).replace(",", "").replace(".", "")
    return normalized if normalized.isdigit() else ""


def merge_stable_value(existing_data, new_data, key, location_label):
    old_value = normalize_cell_value(existing_data.get(key))
    new_value = normalize_cell_value(new_data.get(key))

    if key == "exp":
        old_value = normalize_exp(old_value)
        new_value = normalize_exp(new_value)

    if not new_value:
        if old_value:
            new_data[key] = old_value
        else:
            new_data.pop(key, None)
        return

    if old_value and old_value != new_value:
        print_color_yellow(
            f"[AAS] Ignoring unstable {key} change for {location_label}: "
            f"{old_value!r} -> {new_value!r}"
        )
        new_data[key] = old_value
        return

    new_data[key] = new_value


def merge_location_data(existing_data, scraped_data, location_label):
    merged = dict(existing_data or {})
    merged.update(scraped_data)

    for stable_key in ("exp", "unlocked_by"):
        merge_stable_value(existing_data or {}, merged, stable_key, location_label)

    if existing_data and existing_data.get("items"):
        merged["items"] = existing_data["items"]

    return merged


def find_deployment_table(container):
    tables = container.locator("table")
    for table_index in range(tables.count()):
        table = tables.nth(table_index)
        headers = [
            normalize_cell_value(header.inner_text())
            for header in iterate_locator(table.locator("thead th, tr:first-child th"))
        ]
        if "Name" in headers and ("EXP" in headers or "Discover via" in headers):
            return table
    raise RuntimeError("Could not find the deployment-sector data table.")


def read_table_rows(table):
    headers = [
        normalize_cell_value(header.inner_text())
        for header in iterate_locator(table.locator("thead tr").first.locator("th"))
    ]
    if not headers:
        headers = [
            normalize_cell_value(header.inner_text())
            for header in iterate_locator(table.locator("tr").first.locator("th"))
        ]

    parsed_rows = []
    rows = table.locator("tbody tr")
    for row_index in range(rows.count()):
        row = rows.nth(row_index)
        cells = row.locator("td")
        if cells.count() != len(headers):
            continue

        row_data = {}
        for cell_index, header_name in enumerate(headers):
            cell = cells.nth(cell_index)
            row_data[header_name] = normalize_cell_value(cell.inner_text())
            if header_name == "Name":
                link = cell.locator("a").first
                row_data["link"] = link.get_attribute("href") if link.count() else None

        if row_data.get("Name"):
            parsed_rows.append(row_data)

    return parsed_rows


def normalize_airship_data(raw_data):
    normalized = {}
    for location_name in sorted(raw_data, key=sort_key):
        spots = raw_data.get(location_name) or {}
        normalized[location_name] = {}
        for spot_name in sorted(spots, key=sort_key):
            spot_data = dict(spots.get(spot_name) or {})
            if isinstance(spot_data.get("items"), list):
                spot_data["items"] = sorted(dict.fromkeys(spot_data["items"]), key=sort_key)
            normalized[location_name][spot_name] = {
                key: spot_data[key]
                for key in sorted(spot_data, key=sort_key)
            }
    return normalized


def write_airship_cache(filename, raw_data):
    writeJsonFile(str(filename), normalize_airship_data(raw_data), sort_sub_keys=True)


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
        table = find_deployment_table(page)
        for row_data in read_table_rows(table):
            name = row_data["Name"]
            scraped = {
                "link": row_data.get("link"),
                "lvl": normalize_cell_value(row_data.get("Rank")),
                "unlocked_by": normalize_cell_value(row_data.get("Discover via")),
                "exp": normalize_exp(row_data.get("EXP")),
            }
            scraped = {key: value for key, value in scraped.items() if value not in (None, "")}
            existing = data["Sea of Clouds"].get(name, {})
            data["Sea of Clouds"][name] = merge_location_data(existing, scraped, name)
    except Exception:
        traceback.print_exc()
    return data

def get_submarine_information(page, data) -> None:
    try:
        open_gamerescape_page(page, SUBMARINE_URL, ".tabbertab")
        locations = iterate_locator(page.locator(".tabbertab"))
        for location_tab in locations:
            loc_name = normalize_cell_value(location_tab.get_attribute("title")).replace("Lilac Sea", "The Lilac Sea")
            if not loc_name:
                continue

            print(loc_name)
            data.setdefault(loc_name, {})
            table = find_deployment_table(location_tab)

            for row_data in read_table_rows(table):
                name = row_data["Name"]
                scraped = {
                    "link": row_data.get("link"),
                    "unlocked_by": normalize_cell_value(row_data.get("Discover via")),
                    "exp": normalize_exp(row_data.get("EXP")),
                }
                scraped = {key: value for key, value in scraped.items() if value not in (None, "")}
                existing = data[loc_name].get(name, {})
                data[loc_name][name] = merge_location_data(existing, scraped, f"{loc_name} / {name}")
                print(f"\t {data[loc_name][name]}")
    except Exception:
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
    for locations, location_spots in sorted(data.items(), key=lambda item: sort_key(item[0])):
        if locations == "Sea of Clouds":
            continue
        print(locations)
        for spot, spot_data in sorted(location_spots.items(), key=lambda item: sort_key(item[0])):
            for key, value in sorted(submarineexploration.items(), key=lambda item: sort_key(item[0])):
                if spot.lower() == value['Destination_en'].lower():
                    data[locations][spot]["lvl"] = value['RankReq']
                    break
    return data

def add_items(page, data):
    try:
        for locations, location_spots in sorted(data.items(), key=lambda item: sort_key(item[0])):
            print_color_yellow(locations)
            for spot, spot_data in sorted(location_spots.items(), key=lambda item: sort_key(item[0])):
                if spot == "":
                    continue
                if data[locations][spot].get("items", None) == []:
                    print_color_red("\t" + spot)
                elif not data[locations][spot].get("items", None):
                    print_color_green("\t" + f"{spot} - {spot_data.get("link", None)}")
                    items = get_items_per_location(page, spot_data['link'])
                    print_color_green("\t" + f"{items}")
                    data[locations][spot]["items"] = sorted(dict.fromkeys(items), key=sort_key)
                    write_airship_cache("airship_submarine.json", data)
                else:
                    print_color_red("\t" + spot)
    except Exception:
        traceback.print_exc()
        print("WROTE")
        write_airship_cache("airship_submarine.json", data)
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
                write_airship_cache(cache_file, data)
            except CloudflareBlockedError as exc:
                print_color_yellow(f"[AAS] {exc}")
            except Exception:
                traceback.print_exc()
                write_airship_cache(cache_file, data)
            finally:
                context.close()
    finally:
        os.chdir(origin)

if __name__ == "__main__":
    os.chdir("..")
    run(os.getcwd())
