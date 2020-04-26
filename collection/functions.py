from .backend import db
from .backend import xlsx_handler
from datetime import datetime, timedelta
import time
import re
import os

ds = db.DataSource()

xlsx_handle = xlsx_handler.XLSX()

# def split_headers(headers):


def getDateRangeFromWeek(week):
    match = re.match(r'(.*)-W(.*)', week)
    p_year = match.group(1)
    p_week = match.group(2)
    firstdayofweek = datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + timedelta(days=6.9) + timedelta(1)
    return firstdayofweek, lastdayofweek

def split_headers(headers):
    final_headers = []
    for header in headers:
        arr = header.split('__')
        for x in range(0,len(arr)):
            try:
                final_headers[x]
            except:
                final_headers.append([])
        for i, elem in enumerate(arr):
            final_headers[i].append(elem)
    return final_headers

def fetch_users(current_user_id):
    ds.connect()
    print("Fetching users except ", current_user_id)
    users = ds.fetch_users(current_user_id=current_user_id)
    user_data = []
    for user_row in users:
        lst = list(user_row)
        if lst[2] == '':
            lst[2] = 'All'
        user_data.append(lst)
    return user_data

def update_user_markets(user_id, markets):
    ds.connect()
    ds.update_market(user_id, markets)

def update_user_password(user_id, password):
    ds.connect()
    ds.update_user_password(user_id=user_id, password=password)

def handle_delete_user(user_id):
    ds.connect()
    ds.delete_user(user_id=user_id)

def handle_add_user(user_id, user_type, market, password):
    ds.connect()
    ds.add_user(user_id=user_id, user_type=user_type, password=password, market=market)

def handle_my_password_update(user_id, password_old, password_new):
    ds.connect()
    return ds.update_my_password(user_id=user_id, password_new=password_new,password_old=password_old)

def fetch_data(markets = None, week = None):
    ds.connect()
    week_start = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d')
    week_end  = datetime.strftime(datetime.now() + timedelta(1), '%Y-%m-%d')
    if week != None:
        week_start, week_end = getDateRangeFromWeek(week)
    headers, data =ds.fetch_data(markets, week_start, week_end)
    final_headers = split_headers(headers)
    return final_headers, data

def handle_user_auth(user_id, password):
    ds.connect()
    user = ds.fetch_user(user_id)
    if len(user) == 0:
        response = {
            'status': False,
            'message': "NOT_FOUND"
        }
    else:
        if user[0][2] == password :
            response = {
                'status': True,
                'message': "SUCCESS",
                'user_type': user[0][3],
                'market': user[0][4]
            }
        else:
            response = {
                'status': False,
                'message': "WRONG_PASSWORD"
            }
    return response

def handle_uploaded_file(f, headerCols):
    file_path = 'collection/datasheets/'+f.name
    raw_headers = []
    data = []
    insert_count = 0
    with open(file_path, 'wb+') as destination:  
        for chunk in f.chunks():
            destination.write(chunk)  
        ds.connect()
        data = xlsx_handle.readSheet(file_location = file_path)
        raw_headers, headers, data = xlsx_handle.process_data(data, headerCols)
        ds.create_column_from_headers(headers)
        insert_count = ds.insert_data_rows(headers= headers, data= data)

    if os.path.isfile(file_path):
        os.remove(file_path)
    return {
        'headers': raw_headers,
        'data': data,
        'insert_count': insert_count
    }

    