import json
import os

path_of_main_script = ""

def writeline(f, data):
    f.write(data)


def createShortURL(url):
    newURL = url
    removeHTTPS = False
    removeHTTP = False
    if "https" in newURL:
        removeHTTPS = True
        newURL = url.replace("https://", "")
    if "http" in newURL:
        removeHTTP = True
        newURL = url.replace("http://", "")
    newURL = newURL.split("/")
    if len(newURL) > 1:
        newURL = newURL[0] + "/" + newURL[1]
    else:
        newURL = newURL[0]
    if removeHTTPS:
        return "https://" + newURL
    if removeHTTP:
        return "http://" + newURL


def links():
    with open("T:/var/www/ffxiv/links.json", "r", encoding="utf-8") as f:
        links = json.load(f)
    filecontent = ""
    filecontent += '---\n'
    filecontent += 'layout: links\n'
    filecontent += 'title: Links\n'
    filecontent += 'last_modified_at: 2022-03-17\n'
    filecontent += 'permalink: /links/\n'
    filecontent += 'description: "Search through class and jobs guides on the FFXIV Pocket Guide."\n'
    filecontent += 'page_type: index\n'
    filecontent += 'page_category: links\n'
    filecontent += 'links:\n'
    for key, value in links.items():
        filecontent += f"    - category: {key}\n"
        filecontent += "      links: \n"
        for name, entry in value.items():
            if entry.get('disabled', False) or entry.get('url', "") == "":
                continue
            filecontent += f"        - name: {name}\n"
            filecontent += f"          url: {entry['url']}\n"
            filecontent += f"          shorturl: {createShortURL(entry['url'])}\n"
            filecontent += f"          favicon: {entry['favicon']}\n"
    filecontent += '---\n'

    filename = f"{path_of_main_script}/_pages/links/index.html"
    with open(filename, encoding="utf8") as f:
        doc = f.read()
    if not doc == filecontent:
        with open(filename, "w", encoding="utf8") as f:
            f.write(filecontent)


def run(main_script=r"C:\Users\kamot\Documents\GitHub\DevFFXIVPocketGuide"):
    global path_of_main_script
    path_of_main_script = main_script
    links()


if __name__ == "__main__":
    run()
