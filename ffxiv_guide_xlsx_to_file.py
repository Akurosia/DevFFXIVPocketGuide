#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import os
import traceback
# traceback.print_exc()
import errno
import yaml
from yaml.loader import SafeLoader
import python_scripts.generatePatch as gp
from ffxiv_aku import pretty_json, print_color_green, sys, writeJsonFile
from python_scripts.header import addHeader
from python_scripts.guide import addGuide, logdata, logdata_lower
from python_scripts.helper import uglyContentNameFix, getContentName
#from python_scripts.constants import *
from python_scripts.custom_logger import getLogger
from python_scripts.xlsx_entry_helper import get_header_from_xlsx, getEntryData, getPrevAndNextContentOrder, read_xlsx_file
import python_scripts.convert_skills_to_guide_form as csgf
import python_scripts.generateLinks as gl
import python_scripts.generateHousingMissions as ghm

logger = getLogger(50)
disable_green_print = True
disable_yellow_print = True
disable_blue_print = True
disable_red_print = True
debug_row_number = 0
print_debug = False

LANGUAGES = ["de", "en", "fr", "ja", "cn", "ko"]
LANGUAGES_MAPPING = {
    "de": "de-DE",
    "en": "en-US",
    "fr": "fr-FR",
    "ja": "ja-JP",
    "cn": "cn-CN",
    "ko": "ko-KR"
}

def get_old_content_if_file_is_found(_existing_filename):
    if os.path.exists(_existing_filename):
        with open(_existing_filename, encoding="utf8") as f:
            doc = list(yaml.load_all(f, Loader=SafeLoader))[0]
            return doc
    return {}


def try_to_create_file(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def cleanup_logdata(logdata_instance_content):
    try:
        del logdata_instance_content["combatants"]
    except Exception:
        pass
    try:
        del logdata_instance_content["zone"]
    except Exception:
        pass
    try:
        del logdata_instance_content["contentzoneid"]
    except Exception:
        pass
    music = None
    try:
        music = logdata_instance_content["music"]
        del logdata_instance_content["music"]
    except Exception:
        pass

    for _, enemy in logdata_instance_content.items():
        try:
            del enemy["tether"]
        except Exception:
            pass
        try:
            del enemy["headmarker"]
        except Exception:
            pass
    new_lic = {}
    for k, v in logdata_instance_content.items():
        new_lic[k] = v
    return new_lic, music


def getDataFromLogfile(entry):
    logdata_instance_content = None
    music = None
    contentzoneid = ""
    # get correct title capitalization to read data from logdata
    title = uglyContentNameFix(entry["title_de"].title(), entry["instanceType"], entry["difficulty"])
    # get the latest data from logdata
    if not entry["title_de"] == "" and logdata_lower.get(entry["title_de"].lower()):
        try:
            logdata_instance_content = dict(logdata[getContentName(title, lang="de")])
        except Exception:
            logdata_instance_content = dict(logdata[title])
        if logdata_instance_content.get('contentzoneid', None):
            contentzoneid = logdata_instance_content['contentzoneid']
        logdata_instance_content, music = cleanup_logdata(logdata_instance_content)
    return logdata_instance_content, music, contentzoneid


def writeFileIfNoDifferent(filename, filedata):
    try:
        with open(filename, "r", encoding="utf8") as f:
            x_data = f.read()
    except Exception:
        x_data = None

    if not filedata == x_data:
        with open(filename, "w", encoding="utf8") as fi:
            fi.write(filedata)
        print(f"Wrote new data to file {filename}")


def write_content_to_file(entry, filename, old_data, content_translations):
    logdata_instance_content, music, contentzoneid = getDataFromLogfile(entry)
    filedata = '---\n'
    filedata += addHeader(entry, old_data, music, contentzoneid, content_translations)
    filedata += addGuide(entry, old_data, logdata_instance_content, content_translations)
    filedata += '---'
    filedata += '\n'
    writeFileIfNoDifferent(filename, filedata)


expansion_list = {
    "arr": "2_arr",
    "hw": "3_hw",
    "sb": "4_sb",
    "shb": "5_shb",
    "ew": "6_ew",
    "dt": "7_dt"
}

def run(sheet, max_row, max_column, elements, orderedContent):
    global debug_row_number # used in debugger to verify entry
    global print_debug
    # for every row do:
    for i in range(2, max_row):
        try:
            #filename = ""
            debug_row_number = i
            # comment the 2 line out to filter fo a specific line, numbering starts with 1 like it is in excel
            if not True:
                #if debug_row_number > 10 :
                if debug_row_number not in [737]:
                    print_debug = True
                    continue
            entry = getEntryData(sheet, max_column, i, elements, orderedContent)
            if print_debug:
                print(entry['title'])
            logger.info(pretty_json(entry))
            # if the done collumn is not prefilled
            if entry["exclude"] == "end":
                print("END FLAG WAS FOUND!")
                break
            if not (entry["exclude"] or entry["done"]):
                content_translations = {}
                for lang in LANGUAGES:
                    content_translations[lang] = {}
                #print(f"{entry['instanceType']}: {entry['title']}")
                if entry['categories'] == "":
                    print("Skipped due to no expansion specified")
                    continue
                expansion = expansion_list[entry['categories']]
                filename = f"{expansion}_new/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                existing_filename = f"{expansion}/{entry['instanceType']}/{entry['date'].replace('.', '-')}--{entry['patchNumber']}--{entry['sortid'].zfill(5)}--{entry['slug'].replace(',', '')}.md"
                old_data = get_old_content_if_file_is_found(existing_filename)
                # if old file was found, replace filename to save
                if not old_data == {}:
                    filename = existing_filename
                    # logger.info(pretty_json(old_data))
                try_to_create_file(filename)
                write_content_to_file(entry, filename, old_data, content_translations)
                # write translation file
                filename_translation_location = f"../assets/translations/content/{entry['categories']}/{entry['instanceType']}/{entry['slug'].replace(',', '').replace('_', '-')}"
                if not os.path.exists(filename_translation_location):
                    os.makedirs(filename_translation_location)
                for lang in LANGUAGES:
                    writeJsonFile(filename_translation_location + f"/{LANGUAGES_MAPPING[lang]}.json", content_translations[lang])

            elif entry['title'] != "":
                print_color_green(f"Skip {entry['title']} as its marked as {entry['exclude']}/{entry['done']}")
        except Exception as e:
            logger.critical(f"Error when handeling '{filename}' with line id '{i}' ({e})")
            traceback.print_exception(*sys.exc_info())


def main():
    logger.critical('START')
    sheet, max_row, max_column = read_xlsx_file()
    XLSXELEMENTS = get_header_from_xlsx(sheet, max_column)
    csgf.load_global_data()
    # change into _posts dir
    os.chdir("./_posts")
    # first run to create all files
    orderedContent = getPrevAndNextContentOrder(sheet, XLSXELEMENTS, max_row)
    #logger.debug(orderedContent)
    try:
        run(sheet, max_row, max_column, XLSXELEMENTS, orderedContent)
        pass
    except Exception:
        traceback.print_exception(*sys.exc_info())

    if not print_debug:
        #csgf needs also to run from posts dir
        csgf.run()
        gl.run()
        gp.run()
        ghm.run()
    logger.critical('STOP')

if __name__ == "__main__":
    print(sys.version)
    main()
