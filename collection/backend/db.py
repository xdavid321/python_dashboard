import sqlite3
from sqlite3 import Error
from .query import Queries
import os
from datetime import datetime

class DataSource:
    def __init__(self, db_path = None):
        self.con = None
        self.db_path = db_path
        # self.connect()

    def connect(self):
        if(self.db_path == None):
            CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
            self.db_path = CURRENT_DIR + '/../../db.sqlite3'
        self.con = self.init_connection(db_path = self.db_path)
        self.validateDatabaseTables()

    def init_connection(self, db_path):
        try:
            con = sqlite3.connect(db_path)
            return con
            print("Connection established")
        except Error:
            print(Error)

    def validateDatabaseTables(self):
        print("Validating tables")
        cursor = self.con.cursor()
        try:
            cursor.execute(Queries["CHECK_USER_TABLE"])
            print("User table exists")
        except Error:
            print("User table not found")
            try:
                cursor.execute(Queries["CREATE_USER_TABLE"])
                cursor.execute(Queries["CREATE_SUPER_USER"])
                print("User table created")
            except Error as e:
                print("User table creation failed")
                print(type(e).__name__)
        try:
            cursor.execute(Queries["CHECK_DATA_TABLE"])
            print("Data table exists")
        except Error:
            print("Data table not found")
            try:
                cursor.execute(Queries["CREATE_DATA_TABLE"])
                print("Data table created")
            except Error as e:
                print("Data table creation failed")
                print(type(e).__name__)
        self.con.commit()

    def get_column_names(self):
        cursor = self.con.cursor()
        try:
            cursor.execute(Queries["DATA_COLUMN_NAMES"])
            rows = cursor.fetchall()
        except Error:
            print(str(Error))
            rows = []
        columns = []
        for i, row in enumerate(rows):
            if(i >= 2):
                columns.append(row[1])
        return columns

    def create_column_from_headers(self, headers):
        db_cols = self.get_column_names()
        col_tb_created = []
        for header in headers:
            found = False
            for db_col in db_cols:
                if(db_col == header):
                    found = True
            if(found == False):
                col_tb_created.append(header)
        for col in col_tb_created:
            self.add_column(col)
        print("\n")

    def add_column(self, column_name):
        cursor = self.con.cursor()
        try:
            cursor.execute(Queries["ADD_DATA_COLUMN"] % column_name)
            print("column "+column_name+" created")
        except Error as e:
            print("column "+column_name+" could not be created")
            print(type(e).__name__)
    
    def format_str(self, ip):
        return "'" + str(ip) + "'"

    def map_header_db_cols(self, headers, db_cols):
        col_map = {}
        for i, db_col in enumerate(db_cols):
            for j, header in enumerate(headers):
                if(header == db_col):
                    col_map[j] = db_col
        return col_map
    
    def insert_data_rows(self, headers = [], data = []):
        cursor = self.con.cursor()
        db_cols = self.get_column_names()
        col_map = self.map_header_db_cols(headers, db_cols)
        col_indexes = []
        print(headers)
        print(col_map)
        for i, header in enumerate(headers):
            col_indexes.append(str(col_map[i]))
        col_indexes = ",".join(col_indexes)
        count = 0
        for i, data_row in enumerate(data):
            row = ",".join(map(self.format_str, data_row))
            sql = Queries["INSERT_DATA_ROW"].format(cols = col_indexes, vals=row)
            try:
                cursor.execute(sql)
                count += 1
            except Error as e:
                print(type(e).__name__)
        try:
            self.con.commit()
            print("Total Records inserted: %s" % str(count))
            return count
        except Error as e:
            print(type(e).__name__)
    
    def fetch_user(self, user_id):
        cursor = self.con.cursor()
        sql = Queries["FETCH_USER"].format(user_id = user_id)
        cursor.execute(sql)
        user = cursor.fetchall()
        return user

    def fetch_data(self, markets = None, start = None, end = None):
        filters = []
        filter_string = ""
        if(markets != None):
            market_arr = []
            arr = markets.split(",")
            for market in arr:
                market_arr.append("'{market}'".format(market=market))
            markets = ",".join(market_arr)
            filters.append("market__market IN ({market})".format(market = markets))
        if end != None:
            filters.append("date <= '{end_date}'".format(end_date = end))
        if start != None:
            filters.append("date >= '{start_date}'".format(start_date = start))
        if len(filters) != 0:
            filter_string = "WHERE " + " AND ".join(filters)
        sql = Queries["FETCH_DATA"].format(filters = filter_string)
        cursor = self.con.cursor()
        cursor.execute(sql)    
        data = cursor.fetchall()
        for i, row in enumerate(data):
            data[i] = row[2:]
        headers = self.get_column_names()
        return headers, data
    
    def fetch_users(self, current_user_id):
        try:
            cursor = self.con.cursor()
            sql = Queries["FETCH_ALL_USERS"].format(current_user=current_user_id)
            print(sql)
            cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            print("Error occurerd while fetching users")
            print(str(e))
            return None

    def update_market(self, user_id, markets):
        try:
            cursor = self.con.cursor()
            sql = Queries['UPDATE_USER_MARKETS'].format(user_id= user_id, markets= markets)
            cursor.execute(sql)
            self.con.commit()
        except Error as e:
            print(str(e))

    def update_user_password(self, user_id, password):
        try:
            cursor = self.con.cursor()
            sql = Queries['UPDATE_USER_PASSWORD'].format(user_id= user_id, password= password)
            cursor.execute(sql)
            self.con.commit()
        except Error as e:
            print(str(e))
    
    def delete_user(self, user_id):
        try:
            cursor = self.con.cursor()
            sql = Queries['DELETE_USER'].format(user_id= user_id)
            print(sql)
            cursor.execute(sql)
            self.con.commit()
        except Error as e:
            print(str(e))
    
    def add_user(self, user_id, user_type, market, password):
        try:
            cursor = self.con.cursor()
            sql = Queries['CREATE_NEW_USER'].format(user_id= user_id, user_type=user_type, password=password, market=market)
            print(sql)
            cursor.execute(sql)
            self.con.commit()
        except Error as e:
            print(str(e))

    def update_my_password(self, user_id, password_new, password_old):
        try:
            cursor = self.con.cursor()
            sql = Queries['UPDATE_MY_PASSWORD'].format(user_id=user_id, password_old=password_old, password_new=password_new)
            print(sql)
            result = cursor.execute(sql)
            self.con.commit()
            if result.rowcount == 1:
                return True
            else:
                return False 
        except Error as e:
            print(str(e))
        
        
# dataSrc = DataSource()