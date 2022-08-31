import algorithm
import os
import db_parse
import wal_to_cipher
import time

def main():
    #default path is "C:\Users\whrgk\AppData\Local\Wickr, LLC\WickrMe"
    wickr_path = input("Wickr path: ")
    now = time.localtime()
    nowtime = '%04d_%02d_%02d_%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    outputPath = str(os.getcwd() + '\\result\\'+ nowtime + '\\')
    os.makedirs(outputPath)

    dir_list = os.listdir(wickr_path)
    have_wal = False

    if "skc.wic" not in dir_list:
        print("Wickr is not logged in")
        password = input("Please type wickr password: ")
        db_password = algorithm.wickr_password(password, wickr_path).main()
    else:
        print("Wickr is logged in")
        sid = input("Please type user sid: ")
        db_password = algorithm.wickr_nonpassword(sid, wickr_path).main()
        if "wickr_db.sqlite-wal" in dir_list:
            print("\nthese data have a wal file. plz check another database\n")

            wal_path = str(outputPath + "analyze_plus_wal\\")
            wal_outputPath = os.path.join(wal_path, "result\\")
            os.makedirs(wal_outputPath)

            wal_to_cipher.cls(wickr_path, wal_path).main()
            have_wal = True

    database = algorithm.Database(db_password, wickr_path, outputPath, wickr_path)
    database.decrypt_db()
    print("Database decryption complete!")

    file_output = outputPath+"attachments\\"
    os.makedirs(outputPath+"attachments\\")

    database.decrypt_col(file_output)
    print("Column decryption complete!")
    db_parse.Paring(outputPath).paring(database.data_decrypt_path)

    if have_wal:
        print("\n"+"*"*12 + "database with wal file" + "*"*12)

        database = algorithm.Database(db_password, wickr_path, wal_outputPath, wal_path)
        database.decrypt_db()
        print("Database(combined with wal) decryption complete!")

        file_output = wal_outputPath + "attachments\\"
        os.makedirs(wal_outputPath + "attachments\\")

        database.decrypt_col(file_output)
        print("Column decryption complete!")
        db_parse.Paring(wal_outputPath).paring(database.data_decrypt_path)

main()