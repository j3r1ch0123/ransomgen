#!/bin/python3.9
import os
import shutil
import subprocess
import shlex
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

files = []
subdir = []

privkey = input("Enter the path to the private key file: ")

def decrypt(dataFile, privateKeyFile):

    with open(privateKeyFile, 'rb') as f:
        privateKey = f.read()
        # create private key object
        key = RSA.import_key(privateKey)

    with open(dataFile, 'rb') as f:
        # read the session key
        encryptedSessionKey, nonce, tag, ciphertext = [ f.read(x) for x in (key.size_in_bytes(), 16, 16, -1) ]

    # decrypt the session key
    cipher = PKCS1_OAEP.new(key)
    sessionKey = cipher.decrypt(encryptedSessionKey)

    # decrypt the data with the session key
    cipher = AES.new(sessionKey, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    # save the decrypted data to file
    decryptedFile = dataFile
    with open(decryptedFile, 'wb') as f:
        f.write(data)

    print('Decrypted file saved to ' + decryptedFile)

# Get a list of files to decrypt
for file in os.listdir():
    if os.path.isfile(file):
        files.append(file)

# Decrypt the files
for file in files:
    if file == "decryptor.py":
        continue
    else:
        decrypt(file, privkey)
        print("Files decrypted")

# Do the same for everything in the subdirectories
for dir in os.listdir("."):
    if os.path.isdir(dir):
        subdir.append(dir)

# Spread the decryption code
for item in subdir:
    path = "".join(item)
    shutil.copy("decryptor.py", path)
    os.chdir(path)
    cmd = "python3 decryptor.py"
    subprocess.call(shlex.split(cmd))
    os.chdir("..")
