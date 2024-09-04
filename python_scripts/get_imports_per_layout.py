from ffxiv_aku import *

results = {}
files = glob("../**/*.html", recursive=True)
for fi in files:
    if fi.startswith("..\\_site") or fi.startswith("..\\_posts") or fi.startswith("..\\_pages"):
        continue
    #print(fi)

    with open(fi, "r", encoding="utf8") as f:
        data = f.readlines()

    fi = fi.replace("\\", "/").replace("../", "")
    results[fi] = []

    for line in data:
        if "{%" in line and ("include " in line or "include_cached " in line):
            value: str = (line.strip()
                    .replace("{%- include_cached ", "")
                    .replace("{% include_cached ", "")
                    .replace("{%- include ", "")
                    .replace("{% include ", "")
                    .replace(" -%}", "")
                    .replace(" %}", "")
                    .split(".html")[0] + ".html"
                    )
            #print(f"_includes/{value}")
            if f"_includes/{value}" not in results[fi]:
                results[fi].append(f"_includes/{value}")
#print_pretty_json(results)


def get_children(results, key, tabs=1):
    if results.get(key, None):
        for x in results.get(key, None):
            print("\t"*tabs + f"{x}")
            get_children(results, x, tabs+1)


md_files = glob("../*.md") + glob("../*.html") + glob("../_pages/*/*.html")
md_files = [x.replace("..\\", "").replace("../", "").replace("\\", "/") for x in md_files if "README" not in x]
#print_pretty_json(md_files)

for file, file_imports in results.items():
    if not file.startswith("_layouts"):
        continue
    n_file = file.replace("_layouts/", "").replace(".html", "")
    n_file = "404" if n_file == "error" else n_file
    found = False
    for x in md_files:
        if n_file in x and (not x.endswith(n_file+".html") or x == n_file+".html"):
            print_color_red(x)
            found = True
            break
    if not found:
        print_color_red(f"No direct base: most likly _posts/**/*md")
    print("\t"+file)

    for im in file_imports:
        print("\t\t" + im)
        get_children(results, im, tabs=2)

