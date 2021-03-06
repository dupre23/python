import cx_Oracle, logging
from UserOptions.UserOptions import UserOptions

class SqlClass():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        #implement logging

    def __enter__(self):
        self.connectToDb()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnectFromDb()

    def connectToDb(self):
        try:
            self.db_conn = cx_Oracle.connect("{0}/{1}@//localhost:1521/xe".format(self.username, self.password))
            self.db_cursor = self.db_conn.cursor()
        except cx_Oracle.DatabaseError as e:
            print("Connection could not be completed: ", e)
        else:
            print("Connected successfully to database!")

    def disconnectFromDb(self):
        try:
            self.db_cursor.close()
            self.db_conn.close()
            print("Disconnected from database!")
        except AttributeError:
            print ("Connection could not be closed!")
        except cx_Oracle.DatabaseError as e:
            print ("Connection could not be closed!", e)

    def performAction(self, option):
        if option == "1":
            if not self.addUser():
                print("Could not add user to database!")
        if option == "2":
            if not self.deleteUser():
                print("Could not delete user from database!")
        if option == "3":
            if not self.listUsers():
                print("Could not list users from database!")

    def addUser(self):
        if not self.getAvailableUserId():
            print("Could not obtain next available user_id!")
            return False
        user_info = UserOptions().getAddUserFields()
        values = "({0}, '{1}', '{2}', '{3}', '{4}')".format(self.user_id, user_info[0], user_info[1], user_info[2], user_info[3])
        try:
            self.db_cursor.execute("INSERT INTO users VALUES {}".format(values))
            self.db_cursor.execute("commit")
        except (cx_Oracle.DatabaseError, cx_Oracle.IntegrityError) as e:
            print("Could not add user in database: "+e)
            return False
        else:
            print("{} user was added to the database".format(values))
            return True

    def deleteUser(self):
        '''
        Deletes a user by: A - user_id; B - username

        Try/except statemets are not needed because the input was validated in getDeleteUserFields method
        '''
        delete_type, delete_field = UserOptions().getDeleteUserFields()
        if delete_type == "a":
            self.db_cursor.execute("SELECT user_id FROM users WHERE user_id={}".format(int(delete_field)))
        if delete_type == "b":
            self.db_cursor.execute("SELECT user_id FROM users WHERE username='{}'".format(delete_field))
        res = self.db_cursor.fetchall()
        if len(res) == 0:
            print("Indicated user was not found in the database!")
            return False
        delete_id = res[0][0]
        if delete_type == "a":
            self.db_cursor.execute("DELETE FROM users WHERE user_id={}".format(delete_id))
            self.db_cursor.execute("commit")
        if delete_type == "b":
            self.db_cursor.execute("DELETE FROM users WHERE user_id={}".format(delete_id))
            self.db_cursor.execute("commit")
        print("User was deleted")
        return True

    def listUsers(self):
        self.db_cursor.execute("SELECT * FROM users")
        res = self.db_cursor.fetchall()
        if len(res) == 0:
            print("The database is empty, there is nothing to display")
            return True
        print("\n{:<15} {:^15} {:^15} {:^15} {:>15}".format("User_id", "First_name", "Last_name", "Email", "Username"))
        for item in res:
            print("{:<15} {:^15} {:^15} {:^15} {:>15}".format(item[0], item[1], item[2], item[3], item[4]))
        print("\n")
        return True


    def getAvailableUserId(self):
        '''
        Assures that the user_id field is unique in the database and no gaps are present (e.g id's 1,2,3 NOT 1,3)

        id_list_from_db - list of id's obtained from the database
        id_normal_sequence - list of id's that are natural, arithmetical progression incremented by 1 (e.g. 1,2,3...)
        Compares the two list mentioned above and sets self.user_id to a value so that no gaps appear for user_id attribute in the database
        '''
        try:
            self.db_cursor.execute("SELECT user_id FROM USERS")
            result = self.db_cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            print("Exception when executing get users query:", e)
            return False
        if len(result) == 0:
            self.user_id = 1
        else:
            id_list_from_db = []
            for item in result:
                id_list_from_db.append(item[0])
            id_normal_sequence = list(range(1, len(id_list_from_db)+1))
            if id_list_from_db == id_normal_sequence:
                self.user_id = max(id_list_from_db) + 1
            else:
                for seq, id in zip(id_normal_sequence, id_list_from_db):
                    if seq != id:
                        self.user_id = seq
        return True