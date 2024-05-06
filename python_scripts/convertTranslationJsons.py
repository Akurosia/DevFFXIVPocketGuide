from ffxiv_aku import *


def run():
    os.chdir("..")
    for lang in ['en-US', 'de-DE', 'fr-FR', 'ja-JP', 'cn-CN', 'ko-KR']:
        new_data = {}
        files = glob(f"assets/translations/*/{lang}.json", recursive=True)
        for _file in files:
            #print(_file)
            new_data = dict(new_data, **readJsonFile(_file))
        writeJsonFile(f"assets/translations/{lang}.json", new_data)

if __name__ == "__main__":
    run()
