"""
python script that extract data from advanced search result in BBG Website. 
"""
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import requests

def log_progress(message):
    """ logs progress"""
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now() # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open("./bgg_log.txt","a") as line:
        line.write(timestamp + ' : ' + message + '\n')


search_result_df = pd.DataFrame(columns=['Ranking','Name', 'Geek Rating', 'Average Rating','Number of Votes'])
page_num = 1
log_progress("Requesting Data from website")
page = requests.get(f'https://boardgamegeek.com/search/boardgame/page/{page_num}?advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&colfiltertype=rated&searchuser=noobcitizen&playerrangetype=normal&B1=Submit').text

soup = BeautifulSoup(page,'html.parser')
tables = soup.find_all('table')
rows = tables[0].find_all('tr')

for row in rows:
    columns = row.find_all('td')
    if len(columns) > 3:
      

        game_dict = {
            'Ranking' :columns[0].text.strip(),
            'Name' : columns[2].a.text, 
            'Geek Rating': columns[3].text.strip(), 
            'Average Rating': columns[4].text.strip(),
            'Number of Votes':columns[5].text.strip()
        }
        single_entry_df = pd.DataFrame(game_dict, index=[0])
        search_result_df = pd.concat([search_result_df,single_entry_df],ignore_index=True)

print(search_result_df)

timestamp_format = '%Y-%h-%d-%H%M%S'
now = datetime.now()
timestamp = now.strftime(timestamp_format)
with pd.ExcelWriter(f'search_result_{timestamp}.xlsx') as writer:
    search_result_df.to_excel(writer,sheet_name='Search_Result')

