from ffxiv_aku import *

results = {}
files = glob("../*/*.html", recursive=True)
for fi in files:
    if fi.startswith("..\\_site"):
        continue
    #print(fi)

    with open(fi, "r") as f:
        data = f.readlines()

    fi = fi.replace("\\", "/").replace("../", "")
    results[fi] = []

    for line in data:
        if "{%" in line and "include" in line:
            value = (line.strip()
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

for file, file_imports in results.items():
    if not file.startswith("_layouts"):
        continue
    print(file)
    for im in file_imports:
        print(f"\t{im}")
        if results.get(im, None):
            for x in results.get(im, None):
                print(f"\t\t{x}")
                if results.get(x, None):
                    for y in results.get(x, None):
                        print(f"\t\t\t{y}")
                        if results.get(y, None):
                            for z in results.get(y, None):
                                print(f"\t\t\t\t{z}")
                                if results.get(z, None):
                                    for w in results.get(z, None):
                                        print(f"\t\t\t\t\t{w}")

