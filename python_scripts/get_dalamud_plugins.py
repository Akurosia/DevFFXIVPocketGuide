from ffxiv_aku import *

content = readJsonFile(r"C:\Users\kamot\AppData\Roaming\XIVLauncher\dalamudConfig.json")


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


skip_urls = []
completed_repos = []
repos_with_load_errors = []
result = readJsonFile("dalamud_repos.json")
def run():
    global result
    global completed_repos
    # collect all urls from local dalamud file
    repo_urls = []
    for key in content["ThirdRepoList"]['$values']:
        url = key['Url']
        url = sanatizeURL(url)
        repo_urls.append(url)

    repo_urls = ["https://kamori.goats.dev/Plugin/PluginMaster"]

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
                        "versions": []
                    }
                    if entry.get('Punchline', None):
                        result[entry['Name']]["punchline"] = entry['Punchline'],
                    if entry.get('Tags', None):
                        result[entry['Name']]["tags"] = entry['Tags'],
                    if entry.get('ImageUrls', None):
                        result[entry['Name']]["image"] = entry['ImageUrls'][0],

                _tuple = (entry['Author'], url, entry.get('AssemblyVersion', 0))
                result[entry['Name']]["versions"].append(_tuple)
        else:
            print(f"Error on: {url}")
            repos_with_load_errors.append(url)
        completed_repos.append(url)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(e)
    print_pretty_json(completed_repos)
    print_pretty_json(repos_with_load_errors)
    writeJsonFile("dalamud_repos.json", result)
