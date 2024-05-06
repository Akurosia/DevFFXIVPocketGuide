from ffxiv_aku import *


for lang in ['en-US', 'de-DE', 'fr-FR', 'ja-JP', 'cn-CN', 'ko-KR']:
    new_data = {}
    files = glob(f"*/{lang}.json", recursive=True)
    for _file in files:
        #print(_file)
        new_data = dict(new_data, **readJsonFile(_file))

    writeJsonFile(f"{lang}.json", new_data)
