import json
import os

PATH_DICT = "/work/dict"
DICT_FOLDER_IS_NOT_FOUND = """Can not find folder with dicts.Manually create folder 'dict' in your work folder and put there txt files with wordlists"""
WORDLISTS_IS_NOT_FOUND = """Can not find any worldlists in your '$work/dict' folder. Create txt file and put words there separated by new line"""
WORDLISTS_IS_EMPTY = """Please select wordlist to use"""
CORES_ARE_EMPTY = "Please specify number of cores to use"
INDEX_DEPTH_IS_EMPTY = "Please specify index depth"
CONFIG_FILE_PATH = "/work/config.json"

CONFIG_TEMPLATE = {
    "cores_to_use": 4,
    "indexing_depth": 10,
    "log_level_select": "INFO",
    "ignore_http_errors_in_log": True,
}


def get_init_config() -> dict:
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, encoding="utf-8") as file:
            return json.load(file)
    else:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(CONFIG_TEMPLATE, file, indent=2)
        return get_init_config()
