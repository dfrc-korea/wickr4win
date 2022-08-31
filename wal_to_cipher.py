import os.path
import shutil

class cls:
    def __init__(self, path, wal_outputPath):
        self.page_siz = 0x400
        self.header_siz = 0x20
        self.page_index_size = 0x08
        self.page_header_size = 0x10
        self.path = path
        self.wal_outputPath = wal_outputPath

    def data_corruption(self,number, data, page):
        data.seek(number)
        data.write(page)

    def main(self):
        cipher_DB_copy_path = str(self.wal_outputPath + "wickr_db.sqlite")

        shutil.copyfile(os.path.join(self.path, "wickr_db.sqlite"),cipher_DB_copy_path)
        data = open(cipher_DB_copy_path, 'r+b')
        wal = open(os.path.join(self.path, "wickr_db.sqlite-wal"),'rb')

        wal_header = wal.read(self.header_siz)
        walSalt = wal_header[0x10:0x18]
        while True:
            index = wal.read(self.page_index_size)
            if len(index) != self.page_index_size:
                break
            wal_page_header = wal.read(self.page_header_size)

            #already accepted page on sqlite
            if wal_page_header[:0x08] != walSalt:
                break

            page_loc = (int.from_bytes(index[:4], byteorder='big') -1) * self.page_siz
            page = wal.read(self.page_siz)
            self.data_corruption(page_loc, data, page)


if __name__ == "__main__":
	wal_cipher = cls()
	wal_cipher.main()