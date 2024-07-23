from ffxiv_aku import *
from distutils.version import StrictVersion
from natsort import natsorted

# this is to fix some of the broken json files
def clean_json(string):
    string = re.sub(r",[ \t\r\n]+}", "}", string)
    string = re.sub(r",[ \t\r\n]+\]", "]", string)
    x = None
    try:
        x = json.loads(string)
    except:
        string = re.sub(r"\s\/\/.*", "", string)
        try:
            x = json.loads(string)
        except:
            x = json.loads(string[1:])
    if isinstance(x, dict):
        x = [x]
    return x


def sanatizeURL(url):
    #return ncorreect urls early
    if url.startswith("https://github.com/"):
        return url
    #return custom urls early
    if not url.startswith("https://raw.githubusercontent.com/"):
        return url
    splitURL = url.split("/")[3:]
    splitURL.insert(2, "raw")
    newURL = "https://github.com/" + "/".join(splitURL)
    return newURL


def write(out, data):
    out.write(str(data) + "\n")


def getFinalData():
    file_location = os.path.dirname(os.path.realpath(__file__))
    result_file = os.path.join(file_location, "..", "_posts", "single_page_content", "2013-01-01--2.0--1--dalamud.md")
    dalamud_data = readJsonFile("dalamud_repos.json")
    print_color_green(f"Write result to {result_file}")
    with open(result_file, "w", encoding="utf8") as out:
        write(out, "---")
        write(out, 'wip: "True"')
        write(out, 'title: "Plugins"')
        write(out, 'layout: index')
        write(out, 'page_type: guide')
        write(out, 'categories: "dalamud"')
        write(out, 'plugins:')
        for key, value in dalamud_data.items():
            print(key)
            print(value)
            desc = value.get("description", "").replace("\n", "<br>").replace("<br><br>", "<br>").replace('"', "'")
            try:
                write(out, f' - name: "{key}"')
                write(out, f'   description: "{desc}"')
                if value.get("punchline", None):
                    pun = value["punchline"][0].replace('"', "'")
                    write(out, f'   punchline: "{pun}"')
                if value.get("DalamudApiLevel", None):
                    write(out, f'   DalamudApiLevel: {value["DalamudApiLevel"]}')
                if value.get("tags", None):
                    write(out, f'   tags:')
                    for tag in value["tags"]:
                        write(out, f'     - tag: "{tag}"')
                write(out, f'   versions:')
                #create dict as version > (author, url, repo)
                tmp = {}
                for v in value["versions"]:
                    author, url, repo, version = v
                    if not tmp.get(version, None):
                        tmp[version] = []
                    _tuple = (author, url, repo)
                    tmp[version].append(_tuple)
                #versions = [k for k in tmp].sort(key=StrictVersion)
                versions = natsorted([k for k in tmp],reverse=True)
                for version in versions:
                    #create dict as url > (author, repo)
                    tmp2 = {}
                    for u in tmp[version]:
                        author, url, repo = u
                        if not tmp2.get(url, None):
                            tmp2[url] = []
                        _tuple = (author, repo)
                        tmp2[url].append(_tuple)
                    urls = natsorted([k for k in tmp2])
                    #print_color_green(urls)
                    for url1 in urls:
                        #print_color_green(tmp2[url1][0])
                        author, repo = tmp2[url1][0]
                        write(out, f'     - author: "{author}"')
                        write(out, f'       url: "{url1}"')
                        write(out, f'       version: "{version}"')
                        write(out, f'       repo: "{repo}"')
            except Exception as e:
                print_color_red(e)

        write(out, "---")


def run():
    skip_urls = []
    completed_repos = []
    repos_with_load_errors = []
    content = readJsonFile(r"C:\Users\kamot\AppData\Roaming\XIVLauncher\dalamudConfig.json")
    result = {}#readJsonFile("dalamud_repos.json")
    # collect all urls from local dalamud file
    repo_urls = []
    for key in content["ThirdRepoList"]['$values']:
        url = key['Url']
        url = sanatizeURL(url)
        repo_urls.append(url)

    repo_urls += ["https://kamori.goats.dev/Plugin/PluginMaster"]

    print(len(repo_urls))
    print(len(list(set([x.lower() for x in repo_urls]))))

    #print_pretty_json(sorted(repo_urls))
    for url in sorted(repo_urls):
        if url == "https://plugins.carvel.li":
            url = "https://git.carvel.li/liza/plugin-repo/raw/branch/master/dist/pluginmaster.json"
        tjson = ""
        if url in skip_urls:
            ...#continue
        response = requests.get(url)
        if response:
            if response.text.strip() == "":
                repos_with_load_errors.append(url)
                continue
            tjson = clean_json(response.text)
            if tjson == []:
                repos_with_load_errors.append(url)
                continue
            for entry in tjson:
                if not result.get(entry['Name'], None):
                    result[entry['Name']] = {
                        "name": entry['Name'],
                        "description": entry.get('Description', ""),
                        "versions": [],
                        "tags": [],
                        "DalamudApiLevel": entry.get('DalamudApiLevel', 0)
                    }
                    if entry.get('Punchline', None):
                        result[entry['Name']]["punchline"] = entry['Punchline'],
                    if entry.get('Tags', None):
                        result[entry['Name']]["tags"] += entry['Tags'][0],
                    if entry.get('CategoryTags', None):
                        result[entry['Name']]["tags"] += entry['CategoryTags'][0],
                    if entry.get('ImageUrls', None):
                        result[entry['Name']]["image"] = entry['ImageUrls'][0],

                _tuple = (entry['Author'], url, entry.get('RepoUrl', None), entry.get('AssemblyVersion', 0))
                if int(result[entry['Name']].get("DalamudApiLevel", 0)) < int(entry.get('DalamudApiLevel', 0)):
                    result[entry['Name']]["DalamudApiLevel"] = int(entry["DalamudApiLevel"])
                result[entry['Name']]["versions"].append(_tuple)
        else:
            print(f"Error on: {url}")
            repos_with_load_errors.append(url)
        completed_repos.append(url)
    writeJsonFile("dalamud_repos.json", result)
    print_pretty_json(completed_repos)
    print_pretty_json(repos_with_load_errors)


if __name__ == "__main__":
    try:
        #run()
        getFinalData()
    except Exception as e:
        print(e)
    #print debug things
