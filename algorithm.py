from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Cipher import AES
import hashlib
from pysqlsimplecipher import decrypt
import os
import sqlite3
import pandas as pd

class wickr_password:
    def __init__(self, password, path):
        self.password = bytearray(password.encode('utf-8'))
        self.path = path

    def main(self):
        with open(os.path.join(self.path, "wickr_db.sqlite.wic"), 'rb') as f:
            data = f.read()
            kdf_salt = data[0x1:0x11]
            gcm_Nonce = data[0x12:0x1E]
            gcm_Tag = data[0x1E:0x2E]
            ciphertext = data[0x2E:]

        # salt = bytes.fromhex('0B B8 17 FB 31 B8 58 36 B9 50 06 41 FE FD 9F AB')
        key = scrypt(self.password, kdf_salt, 32, 131072, r=8, p=1)

        cipher = AES.new(key, AES.MODE_GCM, gcm_Nonce)
        decrypt = cipher.decrypt_and_verify(ciphertext, gcm_Tag)
        return bytearray(decrypt[4:37]).hex()

class wickr_nonpassword:
    def __init__(self, sid, path):
        self.sid = bytearray(sid.encode('utf-8'))
        self.path = path

    def main(self):
        key = hashlib.sha256(self.sid).digest()

        with open(os.path.join(self.path, "skd.wic"), 'rb') as f:
            data = f.read()
            gcm_Nonce = data[0x1:0x0D]
            gcm_Tag = data[0x0D:0x1D]
            ciphertext = data[0x1D:]

        cipher = AES.new(key, AES.MODE_GCM, gcm_Nonce)
        decrypt1 = cipher.decrypt_and_verify(ciphertext, gcm_Tag)

        gcm_Nonce = decrypt1[0x1:0x0D]
        gcm_Tag = decrypt1[0x0D:0x1D]
        ciphertext = decrypt1[0x1D:]

        with open(os.path.join(self.path, "skc.wic"), 'rb') as f:
            data = f.read()
            key = data[1:]

        cipher = AES.new(key, AES.MODE_GCM, gcm_Nonce)
        decrypt2 = cipher.decrypt_and_verify(ciphertext, gcm_Tag)
        return bytearray(decrypt2[4:37]).hex()

class Database:
    def __init__(self, password, wickr_path, output, path):
        self.password = password
        self.path = path
        self.output = os.path.join(output, "wickr_db_decrypted.db")
        self.data_decrypt_path = os.path.join(output, "wickr_db_with_decrypted_column.db")
        self.wickr_path = wickr_path

    def decrypt_db(self):
        database_cipher = os.path.join(self.path, "wickr_db.sqlite")
        database_out = self.output
        password = 'x\'' + self.password + '\''

        database = decrypt.Decrypt(database_cipher, password, database_out)
        database.main()

    def decrypt_col(self, file_output):
        conn = sqlite3.connect(self.output)
        result_conn = sqlite3.connect(self.data_decrypt_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        for row in cursor:
            table = row[0]
            query = "SELECT * FROM "+table
            df = pd.read_sql(query,conn, index_col=None)
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    data = df.iloc[i,j]
                    if type(data) == bytes:
                        #text decrypt
                        df.iloc[i, j] = self.decrypt_data(data)

                        #decrypt attachment file
                        if df.columns[j] == 'bodyData' and df.iloc[i, j-9] == '6000':
                            self.decrypt_attach(data, file_output)
            df.to_sql(table, result_conn)

    def decrypt_data(self, data):
        key = bytes.fromhex(self.password)[1:]
        gcm_Nonce = data[0x01:0x0D]
        gcm_Tag = data[0x0D:0x1D]
        ciphertext = data[0x1D:]

        cipher = AES.new(key, AES.MODE_GCM, gcm_Nonce)
        try:
            decrypt = cipher.decrypt_and_verify(ciphertext, gcm_Tag)
        except ValueError as e:
            #these data are already plaintexts or informations that we do not analyze
            return data
        return decrypt

    def decrypt_attach(self, data, file_output):
        seek = 1

        structLength = [2, 8, 2, 6, 2]

        # get multimedia Key
        userlength = data[seek]
        user = data[seek + 1:seek + userlength + 1].decode('utf-8')
        seek = userlength + seek + structLength[1]

        typeLength = data[seek]
        type = data[seek + 1:seek + typeLength + 1].decode('utf-8')
        seek = typeLength + seek + structLength[2]

        fileNameLength = data[seek]
        fileName = data[seek + 1:seek + fileNameLength + 1].decode('utf-8')
        seek = fileNameLength + seek + structLength[3]

        guidLength = data[seek]
        guid = data[seek + 1:seek + guidLength + 1].decode('utf-8')
        seek = guidLength + seek + structLength[4]

        keyLength = data[seek]
        key = data[seek + 1:seek + keyLength + 1]

        multimedia_file = os.path.join(self.wickr_path, "temp\\attachments\\", guid)
        with open(multimedia_file, "rb") as p:
            file = p.read()
            gcm_Nonce = file[0x01:0x0D]
            gcm_Tag = file[0x0D:0x1D]
            ciphertext = file[0x1D:]

            cipher = AES.new(key[1:], AES.MODE_GCM, gcm_Nonce)
            decrypt = cipher.decrypt_and_verify(ciphertext, gcm_Tag)

            # decrypted file save to result folder
            new_file = open(str(file_output + fileName), "wb")
            new_file.write(decrypt)