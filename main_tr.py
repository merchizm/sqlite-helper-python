"""
SQLite3 Helper Class
===================================
 * OOP class assignment
"""

import sqlite3
import sys
import re
from os.path import exists, realpath
from os import system, name

from pyfiglet import Figlet  # for stylish print
from termcolor import colored  # for colored print
from boxing import boxing  # for successfully message


class SqliteHelper:
    def __init__(self, ui=False):
        self.cur = None
        self.conn = None
        self.table_exists = None
        self.ui = ui  # user interface setting
        if ui:
            self.menu()

    def menu(self, without=False):
        if without is False:
            f = Figlet(font='roman', width=125)
            print(colored(f.renderText('SQLite3\nDB Helper'), 'green'))
        menu_options = {
            1: 'Veritabanı oluştur veya bağlan',
            2: 'Tablo Oluştur',
            3: 'Satır Gir',
            4: 'Satır Sil',
            5: 'Satır Getir',
            6: 'Tablo Düşür',
            7: 'Çıkış',
        }
        print('{:^26s}'.format(colored("=Menu=", 'green', attrs=['bold'])))
        for key in menu_options.keys():
            text = str(key) + '--' + menu_options[key]
            print(colored(text, 'green'))
        option = int(input(colored('\n\nTercihinizi giriniz: ', 'white', attrs=['bold'])))
        if option == 7:
            exit('görüşürüz..')
        elif option == 1:  # create or connect database
            file_name = self.input(
                'Bağlanmak istediğiniz veritabanının dosyasının adını girin (:memory: geçerli)',
                'string')
            self.create_connection(file_name)

            system('cls' if name in ('nt', 'dos') else 'clear')

            print(boxing(colored('Başarıyla veritabanına bağlanıldı.', 'blue')))
        elif option == 2:  # create table
            table_name = self.input('Oluşturmak istediğiniz tablonun ismini belirtiniz', 'string')
            table_column_count = int(self.input("Tabloda kaç satır olacağını belirtiniz", "int"))
            table_columns = []
            pk_status = False
            for i in range(table_column_count):
                column_name = self.input("[%s] 1. Satırın ismini belirtiniz" % str(i), "string")
                column_type = self.type("[%s] 2. Satırın türünü belirtiniz [Veri tipinin karşısındaki sayıyı giriniz]"
                                        % str(i))
                if self.question("[%s] 3. Bu satır boş olabilir mi" % str(i)):
                    null_status = "NULL"
                else:
                    null_status = "NOT NULL"

                # We use variable outside the loop to make one column a primary key.
                primary_key = ""
                if not pk_status:
                    primary_key_status = self.question("[%s] 4. Bu satır Birincil Anahtar olsun mu" % str(i))
                    primary_key = "PRIMARY KEY" if primary_key_status is True else ""
                    pk_status = True
                #

                table_columns.append({
                    "column_name": column_name,
                    "column_type": column_type,
                    "primary_key": primary_key,
                    "null_status": null_status
                })
                sys.stdout.write(("=====" * 5) + "\r\n")

            system('cls' if name in ('nt', 'dos') else 'clear')  # clear terminal cls:win, clear:linux,unix

            print(boxing(colored('Tablonun sorgusu oluşturuluyor..', 'blue')))

            r = self.create_table(table_name, table_columns)

            system('cls' if name in ('nt', 'dos') else 'clear')

            if r:
                print(boxing(colored('Tablo oluşturuldu.', 'blue')))
            else:
                print(boxing(colored('Tablo oluşturulurken hata ile karşılaşıldı.', 'red')))
        elif option == 3:  # insert row
            table_name = self.input('Satır girmek istediğiniz tabloyu belirtiniz', 'string')
            columns_query = self.cur.execute(f"pragma table_info('{table_name}')").fetchall()
            print(colored('Tablodaki sütunlar:', attrs=["bold"]))
            for column in columns_query:
                print(colored('-' + str(column[1]) + " | type " + str(column[2]) + " | is "
                              + ('NULL' if column[3] == 0 else 'NOT NULL'), 'green'))
            if self.question("Bu tabloya satır girmek istediğinize emin misiniz?"):
                values = []
                for column in columns_query:
                    types_to_type = {
                        "TEXT": "string",
                        "INTEGER": "int",
                        "REAL": "string",
                        "BLOB": "string"
                    }
                    if column[3] == 1:
                        value = self.input('"' + column[1] + '" Satırının içeriğini giriniz [BOŞ BIRAKILAMAZ]',
                                           types_to_type[column[2]])
                    else:
                        value = self.input('"' + column[1] + '"Satırının içeriğini giriniz [boş bırakmak için '
                                                             '0 veya null yazın.]',
                                           types_to_type[column[2]])
                    if column[2] == "REAL":
                        values.append(float(value))
                    elif column[2] == "TEXT" or column[2] == "BLOB":
                        values.append(str(value))
                    else:
                        values.append(int(value))
                system('cls' if name in ('nt', 'dos') else 'clear')
                if self.insert(table_name, values):
                    print(boxing(colored('Satır başarıyla girildi.', 'blue')))
                else:
                    print(boxing(colored('Satır girilirken hata ile karşılaşıldı.', 'red')))
            else:
                system('cls' if name in ('nt', 'dos') else 'clear')
                print(boxing(colored('Satır girme işlemi iptal edildi.', 'red')))
        elif option == 4:  # delete row
            table_name = self.input('Satır silmek istediğiniz tablonun adını giriniz', 'string')
            cur = self.cur.execute("SELECT * FROM {} LIMIT 50;".format(table_name))
            column_names = list(map(lambda x: x[0], cur.description))
            system('cls' if name in ('nt', 'dos') else 'clear')
            formatted_row = "{:<10}" * len(column_names)
            sys.stdout.write(formatted_row.format(*column_names))
            sys.stdout.write("\r\n"+("==========" * len(column_names))+"\r\n")
            for row in cur.fetchall():
                row = [str(x) for x in row]
                sys.stdout.write(formatted_row.format(*row) + "\r\n")
            row_id = self.input('Silmek istediğiniz satırın id\'sini giriniz.', 'string')
            if self.delete_row(table_name, "id", row_id):
                print(boxing(colored('Satır başarıyla silindi.', 'blue')))
            else:
                print(boxing(colored('Satır silinirken bir hata meydana geldi..', 'red')))
        elif option == 5:  # get row(s)
            table_name = self.input('Satır(lar) çekmek istediğiniz tablonun adını giriniz', 'string')
            row_id = self.input('Çekmek istediğiniz satırın id\'sini giriniz', 'string')
            result = self.get_rows(table_name, "id", row_id)
            if result is not None:
                column_names = self.get_column_names(table_name)
                system('cls' if name in ('nt', 'dos') else 'clear')
                formatted_row = "{:<10}" * len(column_names)
                sys.stdout.write(formatted_row.format(*column_names))
                sys.stdout.write("\r\n" + ("==========" * len(column_names)) + "\r\n")
                for row in result:
                    row = [str(x) for x in row]
                    sys.stdout.write(formatted_row.format(*row) + "\r\n")
                sys.stdout.write("\r\n" * 5)
            else:
                print(boxing(colored('Veri getirilirken hata ile karşılaşıldı', 'red')))
        elif option == 6:  # drop table
            table_name = self.input('Düşürmek istediğiniz tablonun adını giriniz', 'string')
            if self.question("Are you sure you want to drop table \"%s\"" % table_name):
                if self.drop_table(table_name):
                    print(boxing(colored('Tablo başarıyla düşürüldü.', 'blue')))
                else:
                    print(boxing(colored('Tablo düşürülürken hata ile karşılaşıldı.', 'red')))
            else:
                system('cls' if name in ('nt', 'dos') else 'clear')
                boxing(colored('Tablo düşürülmesinden vazgeçildi.', 'blue'))
        self.menu(True)

    def create_connection(self, filename, table_name="null"):
        if exists(realpath(filename)):
            try:
                self.conn = sqlite3.connect(realpath(filename))
                self.cur = self.conn.cursor()
            except sqlite3.OperationalError as e:
                raise Exception('Bilinmeyen bir hata oluştu. Hata detayları: %s' % e)
        elif filename == ':memory:':
            try:
                self.conn = sqlite3.connect(filename)
                self.cur = self.conn.cursor()
            except sqlite3.OperationalError as e:
                raise Exception('Bilinmeyen bir hata oluştu. Hata detayları: %s' % e)
        else:
            raise Exception("Veritabanı dosyası bulunamadı. Dosya konumu : %s" % realpath(filename))

        if table_name != 'null':
            # check table count
            self.cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=(?)", table_name)

            if self.cur.fetchone()[0] == 1:
                self.table_exists = True
            else:
                raise Exception("Tablo veritabanında bulunamadı. Tablo adı: %s" % table_name)
                # if table doesn't exist run create_table function

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def get_column_names(self, table_name):
        cur = self.cur.execute("SELECT * FROM {};".format(table_name))
        return list(map(lambda x: x[0], cur.description))

    def create_table(self, table_name, columns=[]):
        if columns != {}:
            column_string = ""
            for column in columns:
                column_string = column_string + "%s   %s   %s   %s," % (column["column_name"], column["column_type"],
                                                                        column["primary_key"], column["null_status"])
            columns_string = column_string.strip(",")
            # delete the last comma because it is extra.
            query = "CREATE TABLE IF NOT EXISTS %s(%s);" % (table_name, columns_string)
            self.cur.execute(query)
            return True
        else:
            sys.stdout.write('Hata: Columns parametresi girilmemiş.')
            return False

    def drop_table(self, table_name):
        try:
            self.cur.execute("DROP TABLE {}".format(table_name))
        except Exception as e:
            sys.stdout.write("Tablo düşürülemedi: %s. Hata: {}.".format(table_name, e))
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
                sys.stdout.write("{} tablosuna veri girilirken hata oluştu. Hata: {}.".format(table_name, e))
                return False
            self.conn.commit()
            return True
        else:
            sys.stdout.write("{} tablosuna veri eklenirken hata meydana geldi."
                             "Açıklama: veriler istenilen türde verilmemiş.".format(table_name))
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
                "{} tablosundan veri getirilemedi. Sütun bilgisi: {}. Hata: {}".format(table_name, column, e))
            return None

    def get_rows(self, table_name, column, query):
        try:
            if query.isdigit():
                return self.cur.execute("SELECT * FROM {} WHERE {} = {};".format(table_name, column, query)).fetchall()
            else:
                return self.cur.execute(
                    "SELECT * FROM {} WHERE {} LIKE '{}';".format(table_name, column, query)).fetchall()
        except sqlite3.Error as e:
            sys.stdout.write(
                "{} tablosundan veri getirilemedi. Sütun bilgisi: {}. Hata: {}".format(table_name, column, e))
            return None

    def delete_row(self, table_name, column, query):
        q = ""
        try:
            if query.isdigit():
                q = "DELETE FROM {} WHERE {} = {};".format(table_name, column, query)
            else:
                q = "DELETE FROM {} WHERE {} LIKE {};".format(table_name, column, query)
            print(q)
            self.cur.execute(q)
        except sqlite3.Error as e:
            sys.stdout.write("{} tablosundan satır silinemedi. Sorgu: {}. Hata: {}".format(table_name, q, e))
            return False
        return True

    def question(self, question_paragraph):
        options = {"yes": True, "y": True, "no": False, "n": False}
        while True:
            sys.stdout.write("%s ? [Y/n]\n" % question_paragraph)
            choice = input().lower()
            if choice in options:
                return options[choice]
            else:
                sys.stdout.write(colored("lütfen 'yes' veya 'no' ile yanıt veriniz. " "(veya 'y' veya 'n').\n", "yellow"))

    def input(self, input_paragraph, data_type):
        while True:
            sys.stdout.write(
                "%s ? [Yanıt Türü:%s]\n" % (input_paragraph, "Number" if data_type == "int" else "Text"))
            response = input().lower()
            if data_type == "int" and response.isdigit():
                return response
            elif data_type == "string" and response is not None:
                return response
            else:
                sys.stdout.write(colored("Lütfen geçerli bir cevap giriniz. Boş bırakmayınız.\n", "yellow"))

    def type(self, type_paragraph="Sütunun veri türü ne olsun? [veri türünün numarasını giriniz]"):
        while True:
            data_types = {
                1: "TEXT",
                2: "NUMERIC",
                3: "INTEGER",
                4: "REAL",
                5: "BLOB"
            }
            print("Num|Type")
            for key in data_types.keys():
                print(str(key), data_types[key])
            sys.stdout.write(type_paragraph + "\n")
            number = input()
            if number.isdigit() and 1 <= int(number) <= 5:
                return data_types[int(number)]
            else:
                sys.stdout.write(colored("Lütfen geçerli bir cevap giriniz. Boş bırakmayınız.\n", "yellow"))


if __name__ == '__main__':
    helper = SqliteHelper(True)
