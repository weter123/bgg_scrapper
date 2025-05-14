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
    with open("./bgg_log.txt","a", encoding="utf-8") as line:
        line.write(timestamp + ' : ' + message + '\n')

def extract_from_xml(name):
    """extract boardgamegeek user's collection data from BGG XML API"""
    temp_df = pd.DataFrame(columns=['Id','Name', 'Rating'])
    try:
        page = requests.get(f'https://boardgamegeek.com/xmlapi/collection/{name}', timeout=10)
        if page.status_code != 200:
            log_progress("Unexpected issue came up. please try again")
            return temp_df, False
        root = ET.fromstring(page.text)
        if root.tag == 'errors':
            log_progress("collection for the provided username not found."
                + "check spelling or try a different username"
            )
            return temp_df, False
        games_data = []
        for child in root:
            rating = 0.0
            try:
                if child[4][0].attrib['value'] == 'N/A':
                    rating = 0.0
                else:
                    rating = float(child[4][0].attrib['value'])
            except (IndexError, KeyError):
                log_progress("Unexpected XML structure. Skipping this game.")
                continue
            games_data.append({
                'Id': int(child.attrib['objectid']),
                'Name': child[0].text,
                'Rating': rating 
            })
        temp_df =pd.DataFrame(games_data)    
    except requests.exceptions.RequestException as e:
        log_progress(f"Network error: {e}")
        return temp_df, False
    except ET.ParseError:
        log_progress("Error parsing XML response. Please try again.")
        return temp_df, False
    return temp_df, True

def extract_game_data(this_game_id,mechanics_df, designer_df):
    """extract game mechanics and designers for a specific boardgame from BBG XML API"""
    try:
        page = requests.get(f'https://api.geekdo.com/xmlapi/boardgame/{this_game_id}', timeout=10)
        root = ET.fromstring(page.text)
    except requests.exceptions.RequestException as e:
        log_progress(f"Network error while fetching game data for ID {this_game_id}: {e}")
        return mechanics_df, designer_df
    except ET.ParseError:
        log_progress(f"Error parsing XML for game ID {this_game_id}. Skipping.")
        return mechanics_df, designer_df
    mechanics_data = []
    designers_data = []
    for child in root:
        for sub in child:
            if sub.tag == 'boardgamemechanic' and sub.text:
                mechanics_data.append({'Game Id': int(this_game_id), 'Game Mechanic': sub.text})
            elif sub.tag == 'boardgamedesigner' and sub.text:
                 designers_data.append({'Game Id': int(this_game_id), 'Game Designer': sub.text})
    mechanics_df = pd.concat([mechanics_df, pd.DataFrame(mechanics_data)], ignore_index=True)
    designer_df = pd.concat([designer_df, pd.DataFrame(designers_data)], ignore_index=True)
    log_progress(f"extracted game mechanics and designers from {collection_df.loc[collection_df['Id'] == game_id, 'Name'].iloc[0]} ({i}/{len(new_game_list)})")
    return mechanics_df, designer_df

def if_table_not_exists(conn, table_name):
    query_statment = f"SELECT name FROM sqlite_master WHERE type=? AND name=?"
    table_exists_df = pd.read_sql(query_statment,conn, params=('table', table_name))
    if table_exists_df.empty:
        return True
    return False

collection_df = pd.DataFrame()
VALID = False

""" prompt user for username input and run extract_from_xml function"""
while VALID is False:
    username = input("Enter username:")
    if not username.strip():
        print("Username cannot be empty. Please try again.")
        continue
    print("Username is: " + username)
    log_progress('Username entered. Starting collection extraction')
    collection_df, VALID = extract_from_xml(username)  

log_progress('Collection extraction complete')

""" connect to database and create Tables and DataFrames for Boardgames, Mechanics and Designers data"""
try:
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

    """extract list of game IDs of newly added game IDs"""



    query_statment = ("SELECT Id FROM BOARDGAMES")
    sql_boardgame_df = pd.read_sql(query_statment,conn)
    collection_df = collection_df.merge(sql_boardgame_df, on='Id', how='left', indicator=True)
    collection_df = collection_df[collection_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    new_game_list = collection_df['Id'].to_list()
    """


    sql_id_list = sql_boardgame_df['Id'].to_list()

    new_game_list = list(set(extracted_id_list) - set(sql_id_list))
    """

    """ extract data of newly added games """
    i = 1
    for game_id in new_game_list:
        mechanics_df, designer_df = extract_game_data(game_id,mechanics_df, designer_df)
        i = i+1
    log_progress('Game Mechanics extraction complete')

    """ populate database with game data """
    collection_df['Id'] = collection_df['Id'].astype(int)

    mechanics_df.to_sql("MECHANICS", conn, if_exists='append',index=False)
    designer_df.to_sql("DESIGNERS", conn, if_exists='append',index=False)
    collection_df.to_sql("BOARDGAMES",conn,if_exists='append',index=False)

    query_statment = ("SELECT * FROM BOARDGAMES")
    sql_boardgame_df = pd.read_sql(query_statment,conn)

    query_statment = ("SELECT * FROM MECHANICS")
    sql_mechanics_df = pd.read_sql(query_statment,conn)

    query_statment = ("SELECT * FROM DESIGNERS")
    sql_designer_df = pd.read_sql(query_statment,conn)

    """ create and populate excel file with game data """
    with pd.ExcelWriter(f'{username}.xlsx') as writer:
        sql_boardgame_df.to_excel(writer,sheet_name='Collection')
        sql_mechanics_df.to_excel(writer, sheet_name='Game_Mechanics')
        sql_designer_df.to_excel(writer, sheet_name='Game_Designers')
        
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

finally:
    conn.close()