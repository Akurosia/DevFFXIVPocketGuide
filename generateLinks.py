import json


def writeline(f, data):
    f.write(data)
    f.write("\n")


def links():
    with open(f"T:/var/www/ffxiv/links.json", "r", encoding="utf-8") as f:
        links = json.load(f)
    with open(f"_pages/links/index.html", "w", encoding="utf8") as f:
        writeline(f, '---')
        writeline(f, 'layout: links')
        writeline(f, 'title: Links')
        writeline(f, 'last_modified_at: 2022-02-25')
        writeline(f, 'permalink: /links/')
        writeline(f, 'description: "Search through class and jobs guides on the FFXIV Pocket Guide."')
        writeline(f, 'page_type: index')
        writeline(f, 'page_category: links')
        writeline(f, 'links:')
        for key, value in links.items():
            writeline(f, f"    - category: {key}")
            writeline(f, "      links: ")
            for name, entry in value.items():
                if entry.get('disable', False) or entry.get('url', "") == "":
                    continue
                writeline(f, f"        - name: {name}")
                writeline(f, f"          url: {entry['url']}")

        writeline(f, '---')


if __name__ == "__main__":
    links()
