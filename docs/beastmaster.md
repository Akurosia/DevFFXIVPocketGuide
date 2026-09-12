# Beastmaster capture list

The Bestienbändiger job page renders `_data/beastmaster.json`. Regenerate it with:

```powershell
python python_scripts/convert_skills_to_guide_form_helper/beastmaster.py
```

The regular job generator also regenerates this data. Only Beastmaster uses
`load_beastmaster_data`: it reads sheets from `tmp/Bestienbändiger_Files` when
present, otherwise calls `loadDataTheQuickestWay("NAME.json", translate=False)`.
It loads XBMPet, Pet, PlaceName, ContentFinderCondition, and ActionTransient. Local malformed or
blank exports do not silently switch to a different server version. Remove a
local export when the server should become authoritative.

The capture roster and location hints come from XBMPet. Pet supplies beast
names; PlaceName and ContentFinderCondition resolve field and duty hints.
German enemy names are matched on word boundaries within the hinted location
in `get_any_Logdata()`. Pet IDs are not enemy IDs. These matches are displayed
as log sightings, not confirmed captures; differently named species can remain
unmatched. No coordinates are inferred. Cu Sith currently has no location hint.

The current export supplies German beast text. Search covers number, beast,
location, attacks, and matched enemies. Capture progress is stored locally
in the browser, independently of Blue Mage.

For an offline rebuild, pass `--support-dir PATH` containing saved `Pet.json`,
`PlaceName.json`, `ContentFinderCondition.json`, `ActionTransient.json`, and `logdata_de_minified.json`.
XBMPet still uses the Beastmaster local/server wrapper.

Run the data tests with:

```powershell
python -m unittest python_scripts.tests.test_beastmaster
```
