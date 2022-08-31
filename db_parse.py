import sqlite3
import os
import datetime

class Paring:
    def __init__(self, output):
        self.output = output

    def paring(self, path):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        analyzed_database = New_database(self.output)

        new_database = analyzed_database.create_tab()
        new_database_conn = analyzed_database.conn
        new_database_cursor = new_database_conn.cursor()

        user_profile = self.myprofile(cursor)
        analyzed_database.insert_user_profile(new_database_cursor,user_profile)
        new_database_conn.commit()

        friends_list = self.friend_list(cursor)
        analyzed_database.insert_friends_list(new_database_cursor, friends_list)
        new_database_conn.commit()

        messages = self.message_list(cursor)
        analyzed_database.insert_messages(new_database_cursor, messages)
        new_database_conn.commit()

    def myprofile(self, cursor):
        sql = "SELECT username, appID, networkName from Wickr_Account"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def friend_list(self, cursor):
        sql = "SELECT Wickr_User.userAlias, Wickr_App.appIDSec from Wickr_User join Wickr_App on Wickr_User.userIDHash = Wickr_App.user"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def message_list(self, cursor):
        sql = "Select Wickr_User.userAlias, Wickr_ConvoUser.convo from Wickr_ConvoUser join Wickr_User on Wickr_ConvoUser.user = Wickr_User._id"
        cursor.execute(sql)
        result = cursor.fetchall()
        chatroom_member = {}
        for i in result:
            if i[1] in chatroom_member.keys():
                chatroom_member[i[1]].append(i[0])
            else:
                chatroom_member[i[1]] = [i[0]]

        sql = "select Wickr_Message.convo, Wickr_User.userAlias, Wickr_Message.timestamp, Wickr_Message.readTimestamp, Wickr_Message.destructTime, Wickr_Message.type, Wickr_Message.bodyText, Wickr_Message.msgFileName " \
              "from Wickr_Message join Wickr_User on Wickr_Message.senderUserID = Wickr_User.userIDHash"
        cursor.execute(sql)
        result = cursor.fetchall()
        message = []
        for i in result:
            i = list(i)
            if i[0] in chatroom_member.keys():
                #chatroom_member
                i[0] = chatroom_member[i[0]]

                #timestamp convert
                i[2] = datetime.datetime.fromtimestamp(int(i[2])).strftime('%Y-%m-%d %H:%M:%S')
                i[3] = datetime.datetime.fromtimestamp(int(i[3])).strftime('%Y-%m-%d %H:%M:%S')
                i[4] = datetime.datetime.fromtimestamp(int(i[4])).strftime('%Y-%m-%d %H:%M:%S')
                #message type
                type = int(i[5])
                if type == 6000:
                    i[5] = "attachment"
                elif type == 1000:
                    i[5] = "message"
                else:
                    i[5] = "system message"

                message.append(i)

        return message

class New_database:
    def __init__(self, output):
        self.output = output + "analyzed_wickr_data.db"
        self.cursor = None

    def create_tab(self):
        self.conn = sqlite3.connect(self.output)
        cursor = self.conn.cursor()

        cursor.execute('''
                    CREATE table if not exists user_profile
                    (
                        username TEXT,
                        appID INTEGER,
                        networkName TEXT
                    )
        ''')
        cursor.execute('''
                            CREATE table if not exists friend_list
                            (
                                username TEXT,
                                AppID INTEGER
                            )
        ''')
        cursor.execute('''
                            CREATE table if not exists messages
                            (
                                chat_room_member TEXT,
                                send_user TEXT,
                                timestamp text,
                                read_time text,
                                destruct_time text,
                                message_type text,
                                body_text text,
                                attachment_name text
                            )
        ''')

        self.conn.commit()

        return cursor

    def insert_user_profile(self, cursor,user_profile):
        for i in user_profile:
            cursor.execute("Insert into user_profile VALUES (?,?,?);", (i[0],i[1],i[2]))

    def insert_friends_list(self, cursor, friend_list):
        for i in friend_list:
            cursor.execute("Insert into friend_list VALUES (?,?);", (i[0], i[1]))

    def insert_messages(self, cursor, messages):
        for i in messages:
            cursor.execute("Insert into messages VALUES (?,?,?,?,?,?,?,?);", (str(i[0]), i[1], i[2], i[3], i[4], i[5], i[6], i[7]))


