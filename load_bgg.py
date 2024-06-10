"""
python script that extract data from BBG XML API and display a table
"""
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import requests
import sqlite3

def log_progress(message):
    """ logs progress"""
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now() # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open("./bgg_log.txt","a") as line:
        line.write(timestamp + ' : ' + message + '\n')

def extract_from_xml(name):
    """extract collection data from BGG XML API"""
    temp_df = pd.DataFrame(columns=['Id','Name'])
    page = requests.get(f'https://boardgamegeek.com/xmlapi/collection/{name}')
    root = ET.fromstring(page.text)
    if root.tag == 'errors':
        return temp_df, False
    for child in root:
        attr_dict= child.attrib
        game_dict = {
            'Id': attr_dict['objectid'],
            'Name' : child[0].text
        }
        single_mechanic_df = pd.DataFrame(game_dict, index=[0])
        temp_df = pd.concat([temp_df,single_mechanic_df],ignore_index=True)
    return temp_df, True

def extract_game_mechanics(this_game_id,mechanics_df):
    """extract game mechanics for a specific boardgame from BBG XML API"""
    page = requests.get(f'https://api.geekdo.com/xmlapi/boardgame/{this_game_id}').text
    root = ET.fromstring(page)
    for child in root:
        for sub in child:
            if sub.tag == 'boardgamemechanic':
                if mechanics_df[mechanics_df['Game Mechanics'].str.contains(sub.text)].empty:
                    game_dict = {'Game Mechanics': sub.text, 'Count': 1}
                    mechanics_count_df = pd.DataFrame(game_dict, index = [0])
                    mechanics_df = pd.concat([mechanics_df,mechanics_count_df], ignore_index=True)
                else:
                    mechanics_df.loc[mechanics_df['Game Mechanics'] == sub.text ,'Count'] = (
                        mechanics_df.loc[mechanics_df['Game Mechanics'] == sub.text ,'Count'] +1
                    )
    return mechanics_df

def if_table_not_exists(conn, table_name):
    query_statment = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    table_exists_df = pd.read_sql(query_statment,conn)
    if table_exists_df.empty:
        return True
    return False

collection_df = pd.DataFrame()
VALID = False

while VALID is False:
    username = input("Enter username:")
    print("Username is: " + username)
    log_progress('Username entered. Starting collection extraction')
    collection_df, VALID = extract_from_xml(username)
    if VALID is False:
        print("collection for the provided username not found."
              + "check spelling or try a different username"
        )

log_progress('Collection extraction complete')

conn = sqlite3.connect(f'{username}.db')
mechanics_count_df = pd.DataFrame(columns = ['Game Mechanics', 'Count'])

if if_table_not_exists(conn, "BOARDGAME"):
    pd.DataFrame(columns=['Id','Name']).to_sql("BOARDGAME",conn,if_exists='fail',index=False)
if if_table_not_exists(conn, "MECHANICS"):
    mechanics_count_df.to_sql("MECHANICS",conn,if_exists='fail',index=False)

log_progress('Connecting to Database complete')

"""
query_statment = 'SELECT * FROM BOARDGAME'
output = pd.read_sql(query_statment,conn)
print (output)
"""
id_list = collection_df['Id'].to_list()



i = 1
for game_id in id_list:
    print(f"extracting game mechanics from {collection_df.loc[collection_df['Id'] == game_id, "Name"].iloc[0]} ({i}/{len(id_list)})")
    mechanics_count_df = extract_game_mechanics(game_id,mechanics_count_df)
    i = i+1

log_progress('Game Mechanics extraction complete')

mechanics_count_df.to_sql("MECHANICS", conn, if_exists='replace',index=False)
collection_df.to_sql("BOARDGAME",conn,if_exists='replace',index=False)

log_progress('Load Data to Database complete')

query_statment = ("SELECT * FROM MECHANICS "
                  + "ORDER BY COUNT DESC "
                  + "LIMIT 10")
top_mechanics_df = pd.read_sql(query_statment,conn)
print(top_mechanics_df)

conn.close()