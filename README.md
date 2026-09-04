# FFXIV Pocket Guide - Development Sandbox

## 📌 Original Repository:  [FFXIVPocketGuide/FFXIVPocketGuide](https://github.com/FFXIVPocketGuide/FFXIVPocketGuide)
## 📌 Original Dev Repository:  [FFXIVPocketGuide/DevFFXIVPocketGuide](https://github.com/FFXIVPocketGuide/DevFFXIVPocketGuide) (deforked, as Git search wasn't working for me)

This repository is used by the developers of FFXIV Pocket Guides for updating the site.

## Enemy image coverage

Install the script dependencies once:

```powershell
python -m pip install -r scripts/requirements-enemy-images.txt
```

Create a coverage report from the sibling Meddle WebP output:

```powershell
python scripts/enemy_image_coverage.py
```

Create/update `_data/enemy_images.json` with URLs retaining the original WebP folder and filenames:

```powershell
python scripts/enemy_image_coverage.py --manifest
```

The detailed coverage report is written to `tmp/enemy-image-coverage.json`. Running
with `--manifest` also updates the browser-friendly report data at
`assets/data/enemy-image-coverage.json`; the generated site exposes it at
`/enemy-image-coverage/`. Run the manifest command before
`ffxiv_guide_xlsx_to_file.py`: the guide generator reads `_data/enemy_images.json`
and writes the matching hosted image URLs into each enemy entry's front matter.
The images remain in the Meddle WebP directory and are not copied or renamed.
