"""
SQLite3 Helper Class
===================================
 * OOP class assignment
"""

import sqlite3
import sys
from os.path import exists, realpath
from os import system

from pyfiglet import Figlet  # for stylish print
from termcolor import colored  # for colored print
from boxing import boxing # for successfully message


class SqliteHelper:
    def __init__(self, ui=False):
        self.cur = None
        self.conn = None
        self.table_exists = None
        self.ui = ui  # user interface setting
        if ui:
            self.menu()

    def menu(self):
        f = Figlet(font='roman', width=125)
        print(colored(f.renderText('SQLite3\nDB Helper'), 'green'))
        menu_options = {
            1: 'Create or Connect Database',
            2: 'Create Table',
            3: 'Insert Row',
            4: 'Delete Row',
            5: 'Fetch Row',
            6: 'Fetch Rows',
            7: 'Drop Table',
            8: 'Exit',
        }
        print('{:^26s}'.format(colored("=Menu=", 'green', attrs=['bold'])))
        for key in menu_options.keys():
            text = str(key) + '--' + menu_options[key]
            print(colored(text, 'green'))
        option = int(input(colored('\n\nEnter your choice: ', 'white', attrs=['bold'])))
        if option == 8:
            exit('bye')
        elif option == 1:  # create or connect database
            file_name = self.input(
                'What is the name of the database file you want to connect to (:memory: is valid)',
                'string')
            table_name = self.question('Do you want to link to a table')
            if table_name:
                table_name = self.input('Enter table name', 'string')
            self.create_connection(file_name, table_name)

            system("cls||clear")

            boxing(colored('Successfully connected.', 'blue'))

        elif option == 2:  # create table
            table_name = self.input('', 'string')
            table_column_count = int(self.input("How many columns will there be in your table", "int"))
            table_columns = []
            pk_status = False
            for i in range(table_column_count):
                column_name = self.input("[%s] 1. What will the column name be" % str(i), "string")
                column_type = self.type("[%s] 2. What will be the Data type of the column? [Write the number of "
                                        "the data type]" % str(i))
                null_status = "NULL" if self.question("[%s] 3. Could the column be null") else "NOT NULL"
                # We use variable outside the loop to make one column a primary key.
                primary_key_status = self.question("[%s] 4. Will this column be the primary key" % str(i)) if \
                    pk_status is not True else False
                pk_status = True if primary_key_status is True else False
                primary_key = "PRIMARY KEY" if primary_key_status is True else ""
                #
                column = "%s   %s   %s   %s" % (column_name, column_type, primary_key, null_status)
                table_columns.append({
                    "column_name": column_name,
                    "column_type": column_type,
                    "primary_key": primary_key,
                    "null_status": null_status
                })

            system("cls||clear")  # clear terminal cls:win, clear:linux,unix

            sys.stdout.write("Creating table query...")

            r = self.create_table(table_name, table_columns)

            system("cls||clear")

            if r:
                boxing(colored('Table successfully created.', 'blue'))
            else:
                boxing(colored('An error occurred while creating the table.', 'red'))
        elif option == 3:  # insert row
            pass

    def create_connection(self, filename, table_name="null"):
        if exists(realpath(filename)):
            try:
                self.conn = sqlite3.connect(realpath(filename))
                self.cur = self.conn.cursor()
            except sqlite3.OperationalError as e:
                raise Exception('Unknown error occurred. Error details: %s' % e)
        elif filename == ':memory:':
            try:
                self.conn = sqlite3.connect(filename)
                self.cur = self.conn.cursor()
            except sqlite3.OperationalError as e:
                raise Exception('Unknown error occurred. Error details: %s' % e)
        else:
            raise Exception("File doesn't exists. File location: %s" % realpath(filename))

        if table_name != 'null':
            # check table count
            self.cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=(?)", table_name)

            if self.cur.fetchone()[0] == 1:
                self.table_exists = True
            else:
                raise Exception("Table doesn't exists in the database file. Table name: %s" % table_name)
                # if table doesn't exist run create_table function

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def create_table(self, table_name, columns=[]):
        if columns != {}:
            result = []
            for column in columns:
                column_string = "%s   %s   %s   %s" % (column["column_name"], column["column_type"],
                                                       column["primary_key"], column["null_status"])
                result.append(column_string)

            columns_string = ""
            for column in result:
                columns_string += column + ","

            # delete the last comma because it is extra.
            query = "CREATE TABLE %s(%s);" % (table_name, columns_string[-len(columns_string)])
            self.cur.execute(query)
            return True
        else:
            sys.stdout.write('Exception: Missing Parameter ! Missing Parameter is; \"columns\"\nExample: [{...data}]')
            return False

    def drop_table(self, table_name):
        if self.ui:
            if self.question("Are you sure you want to drop table \"%s\""):
                try:
                    self.cur.execute("DROP TABLE {}".format(table_name))
                except Exception as e:
                    sys.stdout.write("Cannot remove table: %s. Exception: {}.".format(table_name, e))
                    return False
                self.conn.commit()
                return True
            else:
                sys.stdout.write("Table dropping was cancelled.")
        else:
            try:
                self.cur.execute("DROP TABLE {}".format(table_name))
            except Exception as e:
                sys.stdout.write("Cannot drop table: %s. Exception: {}.".format(table_name, e))
                return False
            self.conn.commit()
            return True

    def insert(self, table_name, values):
        if table_name is not None and type(values) is list:
            inserted_values = tuple(values)
            placeholder = ",".join(["(?)" for i in range(len(values))])  # (?), * len(values)
            try:
                if any(isinstance(i, tuple) for i in inserted_values):  # see if items in list are distinct queries
                    self.cur.executemany("INSERT INTO {} values({})".format(table_name, placeholder), inserted_values)
                else:
                    self.cur.execute("INSERT INTO {} values({})".format(table_name, placeholder), inserted_values)
            except sqlite3.OperationalError as e:
                sys.stdout.write("Exception: {} when inserting data into table {}. "
                                 "Possible data length mismatch, invalid table".format(e, table_name))
                return False
            self.conn.commit()
            return True
        else:
            sys.stdout.write("Trying to insert data into table {} "
                             "which is not of type list. Passed type {}".format(table_name, type(values)))
            return False

    def get_row(self, table_name, column, query):
        try:
            if (type(query)) is str:
                return self.cur.execute(
                    "SELECT * FROM {} WHERE {} LIKE '{}';".format(table_name, column, query)).fetchone()
            else:
                return self.cur.execute("SELECT * FROM {} WHERE {} = {};".format(table_name, column, query)).fetchone()
        except sqlite3.Error as e:
            sys.stdout.write(
                "Cannot query rows from {}. Requested column: {}. Exception: {}".format(table_name, column, e))
            return None

    def get_rows(self, table_name, column, query):
        try:
            if (type(query)) is str:
                return self.cur.execute(
                    "SELECT * FROM {} WHERE {} LIKE '{}';".format(table_name, column, query)).fetchall()
            else:
                return self.cur.execute("SELECT * FROM {} WHERE {} = {};".format(table_name, column, query)).fetchall()
        except sqlite3.Error as e:
            sys.stdout.write(
                "Cannot query rows from {}. Requested column: {}. Exception: {}".format(table_name, column, e))
            return None

    def delete_row(self, table_name, column, query):
        q = ""
        if self.ui:
            if self.question("Are you sure you want to delete the first record accessed with the %s:%s query in the "
                             "%s table?" % (column, query, table_name)):
                try:
                    if type(query) is str:
                        q = "DELETE FROM {} WHERE {} LIKE {};".format(table_name, column, query)
                    else:
                        q = "DELETE FROM {} WHERE {} = {};".format(table_name, column, query)
                    self.cur.execute(q)
                except sqlite3.Error as e:
                    sys.stdout.write("Cannot delete row from {}. Query: {}. Exception: {}".format(table_name, q, e))
                    return False
                return True
            else:
                sys.stdout.write("row %s:%s deleting has been cancelled." % (column, query))
        else:
            try:
                if type(query) is str:
                    q = "DELETE FROM {} WHERE {} LIKE {};".format(table_name, column, query)
                else:
                    q = "DELETE FROM {} WHERE {} = {};".format(table_name, column, query)
                self.cur.execute(q)
            except sqlite3.Error as e:
                sys.stdout.write("Cannot delete row from {}. Query: {}. Exception: {}".format(table_name, q, e))
                return False
            return True

    def question(self, question_paragraph):
        options = {"yes": True, "y": True, "no": False, "n": False}
        while True:
            sys.stdout.write("%s ? [Y/n]" % question_paragraph)
            choice = input().lower()
            if choice in options:
                return options[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

    def input(self, input_paragraph, data_type):
        while True:
            sys.stdout.write("%s ? [Response Type:%s]" % (input_paragraph, "Number" if data_type == "int" else "Text"))
            response = input().lower()
            if data_type == "int" and response.isdigit():
                return response
            elif data_type == "string" and response is not None:
                return response
            else:
                sys.stdout.write("Please give a valid response, do not leave it blank.\n")

    def type(self, type_paragraph="What will be the Data type of the column? [Write the number of the data type]"):
        while True:
            data_types = {
                1: "TEXT",
                2: "NUMERIC",
                3: "INTEGER",
                4: "REAL",
                5: "BLOB"
            }
            print("Num|Type")
            for k, v in data_types.items():
                num, d_type = v
                print(num, d_type)
            sys.stdout.write(type_paragraph)
            number = input()
            if number.isdigit() and 1 <= int(number) <= 5:
                return data_types[int(number)]
            else:
                sys.stdout.write("Please enter a valid number, do not leave it blank.\n")


if __name__ == '__main__':
    helper = SqliteHelper(True)
