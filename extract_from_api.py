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
    temp_df = pd.DataFrame(columns=['Id','Name', 'Rating'])
    page = requests.get(f'https://boardgamegeek.com/xmlapi/collection/{name}')
    root = ET.fromstring(page.text)
    if root.tag == 'errors':
        print("collection for the provided username not found."
              + "check spelling or try a different username"
        )
        return temp_df, False
    if page.status_code != 200:
        print("Unexpected issue came up. please try again")
        return temp_df, False
    for child in root:
        rating = 0.0
        if child[4][0].attrib['value'] == 'N/A':
            rating = -1.0
        else:
            rating = float(child[4][0].attrib['value'])
           
        game_dict = {
            'Id': int(child.attrib['objectid']),
            'Name' : child[0].text,
            'Rating': rating
        }
        single_mechanic_df = pd.DataFrame(game_dict, index=[0])
        temp_df = pd.concat([temp_df,single_mechanic_df],ignore_index=True)
    return temp_df, True

def extract_game_data(this_game_id,mechanics_df, designer_df):
    """extract game mechanics and designers for a specific boardgame from BBG XML API"""
    page = requests.get(f'https://api.geekdo.com/xmlapi/boardgame/{this_game_id}',timeout=10).text
    root = ET.fromstring(page)
    for child in root:
        for sub in child:
            if sub.tag == 'boardgamemechanic':
                game_dict = {'Game Id': int(this_game_id) ,'Game Mechanic': sub.text}
                new_mechanics_df = pd.DataFrame(game_dict, index = [0])
                mechanics_df = pd.concat([mechanics_df, new_mechanics_df], ignore_index=True)
            elif sub.tag == 'boardgamedesigner':
                game_dict = {'Game Id': int(this_game_id) ,'Game Designer': sub.text}
                new_designer_df = pd.DataFrame(game_dict, index = [0])
                designer_df= pd.concat([designer_df,new_designer_df], ignore_index=True)
    return mechanics_df, designer_df

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

log_progress('Collection extraction complete')

conn = sqlite3.connect(f'{username}.db')
mechanics_df = pd.DataFrame(columns = ['Game Id','Game Mechanic'])
designer_df = pd.DataFrame(columns = ['Game Id','Game Designer'])


if if_table_not_exists(conn, "BOARDGAMES"):
    pd.DataFrame(columns=['Id','Name', 'Rating']).to_sql(
        "BOARDGAMES",conn,if_exists='fail',index=False, dtype= { 'Id':'INTEGER','Name': 'TEXT','Rating': 'REAL'})

if if_table_not_exists(conn, "MECHANICS"):
    mechanics_df.to_sql(
        "MECHANICS",conn,if_exists='fail',index=False, dtype= { 'Game Id':'INTEGER', 'Game Mechanic': 'TEXT'})
else:
    mechanics_df = pd.read_sql("SELECT * FROM MECHANICS", conn)

if if_table_not_exists(conn, "DESIGNERS"):
    designer_df.to_sql(
        "DESIGNERS",conn,if_exists='fail',index=False, dtype= { 'Game Id':'INTEGER', 'Game Designer': 'TEXT'})
else:
    designer_df = pd.read_sql("SELECT * FROM DESIGNERS", conn)

log_progress('Connecting to Database complete')

extracted_id_list = collection_df['Id'].to_list()
query_statment = ("SELECT Id FROM BOARDGAMES")
sql_boardgame_df = pd.read_sql(query_statment,conn)

sql_id_list = sql_boardgame_df['Id'].to_list()

new_game_list = list(set(extracted_id_list) - set(sql_id_list))

i = 1
for game_id in new_game_list:
    print(f"extracting game mechanics from {collection_df.loc[collection_df['Id'] == game_id, 'Name'].iloc[0]} ({i}/{len(new_game_list)})")
    mechanics_df, designer_df = extract_game_data(game_id,mechanics_df, designer_df)
    i = i+1

log_progress('Game Mechanics extraction complete')

collection_df['Id'] = collection_df['Id'].astype(int)

mechanics_df.to_sql("MECHANICS", conn, if_exists='replace',index=False)
designer_df.to_sql("DESIGNERS", conn, if_exists='replace',index=False)
collection_df.to_sql("BOARDGAMES",conn,if_exists='replace',index=False)

with pd.ExcelWriter(f'{username}.xlsx') as writer:
    collection_df.to_excel(writer,sheet_name='Collection')
    mechanics_df.to_excel(writer, sheet_name='Game_Mechanics')
    designer_df.to_excel(writer, sheet_name='Game_Designers') 

log_progress('Load Data to Database complete')


query_statment = ("SELECT `Game Mechanic`, count(*) as 'Count' "
                  + "from MECHANICS "
                  + "group by `Game Mechanic` "
                  + "order by Count desc "
                  + "LIMIT 10")
top_mechanics_df = pd.read_sql(query_statment,conn)
print(top_mechanics_df.to_string())

query_statment = ("SELECT * FROM Boardgames "
                  + "ORDER BY Rating DESC "
                  + "LIMIT 10")
top_mechanics_df = pd.read_sql(query_statment,conn)
print(top_mechanics_df.to_string())

query_statment = ("SELECT `Game Designer`, count(*) as 'Count' "
                  + "from DESIGNERS "
                  + "group by `Game Designer` "
                  + "order by Count desc "
                  + "LIMIT 10")
top_mechanics_df = pd.read_sql(query_statment,conn)
print(top_mechanics_df.to_string())


conn.close()