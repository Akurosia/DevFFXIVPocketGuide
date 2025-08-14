from typing import Any
from ffxiv_aku import *
from collections import deque
try:
    from .fileimports import *
    from .helper import *
except:
    from fileimports import *
    from helper import *

#quests = loadDataTheQuickestWay("Quest.de.json")
#journalgenre = loadDataTheQuickestWay("JournalGenre.de.json")
#quests_raw = loadDataTheQuickestWay("Quest.de.json", exd = "raw-exd-all")

result = {}
nextQuest = {}

def printQuest(data: dict[str, Any]) -> None:
    del data['AcceptBool']
    del data['ActorDespawnSeq']
    del data['ActorSpawnSeq']
    del data['AnnounceBool']
    del data['Behavior']
    del data['BehaviorBool']
    del data['CanTargetBool']
    del data['ConditionBool']
    del data['ItemBool']
    del data['Listener']
    del data['QualifiedBool']
    del data['VisibleBool']
    del data['CountableNum']
    del data['ConditionValue']
    del data['ConditionType']
    del data['ConditionOperator']
    del data['QuestUInt8A']
    del data['QuestUInt8B']
    del data['Script']
    del data['ToDoCompleteSeq']
    del data['ToDoLocation']
    del data['ToDoQty']
    #print(data)
    return data

def fix_icons(icon: str) -> str:
    return {
        "ui/icon/061000/061411_hr1.webp": "ui/icon/071000/071221_hr1.webp",
        "ui/icon/061000/061412_hr1.webp": "ui/icon/071000/071201_hr1.webp",
        "ui/icon/061000/061413_hr1.webp": "ui/icon/071000/071222_hr1.webp",
        "ui/icon/061000/061414_hr1.webp": "ui/icon/071000/071281_hr1.webp",
        "ui/icon/061000/061415_hr1.webp": "ui/icon/060000/060552_hr1.webp",
        "ui/icon/061000/061416_hr1.webp": "ui/icon/061000/061436_hr1.webp",
        "ui/icon/061000/061401_hr1.webp": "ui/icon/062000/062951_hr1.webp",
        "ui/icon/061000/061402_hr1.webp": "ui/icon/062000/062952_hr1.webp",
        "ui/icon/061000/061403_hr1.webp": "ui/icon/062000/062953_hr1.webp"
    }.get(icon, icon)

def addReward(data: dict[str, Any]) -> list[Any]:
    result = []
    for i, k in enumerate(data['ItemCountReward']):
        if k == 0:
            continue
        if data['Reward'][i]['sheet'] != "Item":
            continue
        result.append({
            "Item": data['Reward'][i]['Name_de'],
            "Amount": str(k)
        })
    return result

def addOptionalReward(data: dict[str, Any]) -> list[Any]:
    result = []
    for i, k in enumerate(data['OptionalItemCountReward']):
        if k == 0:
            continue
        result.append({
            "Item": data['OptionalItemReward'][i]['Name_de'],
            "Amount": str(k),
            "IsHQ": str(data['OptionalItemIsHQReward'][i]).capitalize(),
            "Stain": data['OptionalItemStainReward'][i]['Name_de']
        })
    return result

def generate_new_quest_data() -> None:
    newQuest = {}
    for quest_id in quests:
    #for quest_id in ["70295"]:
        quest = quests[quest_id]
        data = quests[quest_id]#['66282']

        try:
            quest_ident = quest_id
            newQuest[quest_ident] = {
                "Name": data['Name_de'],
                "PreviousQuest": { i:str(v['row_id']) for i, v in enumerate(data['PreviousQuest']) if not v.get('row_id', "") == ""},
                "NextQuest": [],
                "Icon": {
                    "Banner": fix_icons(str(data['Icon']['path']).replace('.tex', "_hr1.webp")),
                    "Special": fix_icons(str(data['IconSpecial']['path']).replace('.tex', "_hr1.webp"))
                },
                "JournalGenre": {
                    "Icon": fix_icons(str(journalgenre[str(data['JournalGenre']['row_id'])]['Icon']['path']).replace('.tex', "_hr1.webp")),
                    "JournalCategory": journalgenre[str(data['JournalGenre']['row_id'])]['JournalCategory']['Name_de'],
                    "Name": journalgenre[str(data['JournalGenre']['row_id'])]['Name_de']
                },
                "ActionReward": data['ActionReward']['Name_de'],
                "Expansion": data['Expansion']['Name_de'],
                "GilReward": str(data['GilReward']),
                "PlaceName": data['PlaceName']['Name_de'],
                "Issuer": {
                    "Location": None,
                    "NPC": data['IssuerStart'].get('Singular_de', "")
                },
                "ItemRewardType": str(data['ItemRewardType']),
                "Other_Reward.Name":data['OtherReward']['Name_de'],
                "Reward": addReward(data),
                "OptionalReward": addOptionalReward(data)
            }
            if not data['IssuerLocation'].get("row_id", 0) == 0:
                newQuest[quest_ident]["Issuer"]["Location"] = getCoordsFromLocationLevel(data['IssuerLocation'])
        except Exception as e:
            #print(data)
            print(traceback.format_exc())
            ...
            asdf

    #printQuest(data)
    for quest_name, quest in newQuest.items():
        for k, v in quest['PreviousQuest'].items():
            if v == 0:
                continue
            if not quest_name in newQuest[str(v)]['NextQuest']:
                newQuest[str(v)]['NextQuest'].append(quest_name)

    # fix first quest icon fpr js script later on
    newQuest['65575']['JournalGenre']['Icon'] = "ui/icon/071000/071201_hr1.webp"

    writeJsonFile("../assets/quests_aku.json", newQuest)

### sort quests like in JS

def load_quests():
    try:
        with open("../assets/quests_aku.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            quests: dict[Any, Any] = {k: v for k, v in data.items() if v.get("JournalGenre", {}).get("Icon") == "ui/icon/071000/071201_hr1.webp"}
            return sort_quests(quests)
    except Exception as e:
        print(f'Fehler beim Laden der Quest-Daten: {e}')

def sort_quests(quests):
    ordered_quests = []
    quest_map = {k: v for k, v in quests.items()}  # Dictionary bleibt erhalten
    start_quest_id = "65575"
    start_quest = quest_map.get(start_quest_id)

    if not start_quest:
        print('Start-Quest nicht gefunden.')
        return

    visited = set()
    existing_names = set()
    queue = deque([start_quest_id])

    while queue:
        current_id = queue.popleft()
        current_quest = quest_map.get(current_id)
        if not current_quest or current_id in visited:
            continue

        quest_name = current_quest.get("Name")  # Annahme: Die Quest hat ein "Name"-Feld

        if quest_name in existing_names:
            print(f'Doppelte Quest erkannt: {quest_name} (ID: {current_id})')
            continue  # Quest nicht hinzufügen

        visited.add(current_id)
        existing_names.add(quest_name)
        ordered_quests.append(current_quest)  # Füge das komplette Dictionary hinzu

        if "NextQuest" in current_quest:
            queue.extend([qid for qid in current_quest["NextQuest"] if qid in quest_map])

    return ordered_quests  # Gibt die sortierte Liste zurück

def search_quest(quests, query):
    query = query.strip()
    if not query:
        print("Bitte eine Quest-ID oder einen Namen eingeben.")
        return

    quest_index = next((i for i, q in enumerate(quests) if q["Name"] == query), -1)
    if quest_index == -1:
        print("Quest nicht gefunden.")
        return

    completed_quests = quest_index + 1
    remaining_quests = len(quests) - completed_quests
    progress_percentage = max(0, min(100, (completed_quests / len(quests)) * 100))

    print(f"Abgeschlossene Quests: {completed_quests}")
    print(f"Verbleibende Quests: {remaining_quests}")
    print(f"Fortschritt: {progress_percentage:.2f}%")


def run() -> None:
    print("[MQF] Start MainQuestFinderr")
    print(os.getcwd())
    generate_new_quest_data()

    sorted_quests = load_quests()
    writeJsonFile("../assets/sorted_quests_aku.json", sorted_quests)

if __name__ == "__main__":
    run()
    getExecutionTime()
    #search_quest(sorted_quests, "Ydas Trauer")
