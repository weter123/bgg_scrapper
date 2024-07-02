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

def get_number_of_pages(url):
    main_page = requests.get(url).text
    soup = BeautifulSoup(main_page,'html.parser')
    page_numbers_bar = soup.find_all('div',{"class": "fr"})
    
    last_page = page_numbers_bar[0].find_all('a',{"title": "last page"})

    if not last_page:
        pages = page_numbers_bar[0].find_all('a') 
        if not pages:
            return 1
        
        page_before_next = 1
        for page in pages:
            if page["title"] != "next page":
                page_before_next = page.text
            else:
                return int(page_before_next)
            
    return int(last_page[0].text[1:-1])

url = 'https://boardgamegeek.com/geeksearch.php?action=search&advsearch=1&objecttype=boardgame&q=&include%5Bdesignerid%5D=&geekitemname=&geekitemname=&include%5Bpublisherid%5D=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&range%5Bnumweights%5D%5Bmin%5D=&colfiltertype=owned&searchuser=noobcitizen&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&playerrangetype=normal&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&B1=Submit'

page_num = get_number_of_pages(url)

search_result_df = pd.DataFrame(columns=['Ranking','Name', 'Geek Rating', 'Average Rating','Number of Votes'])

log_progress("Requesting Data from website")
for page in range(1,page_num +1):
    current_page = requests.get(f'https://boardgamegeek.com/search/boardgame/page/{page}?advsearch=1&q=&include%5Bdesignerid%5D=&include%5Bpublisherid%5D=&geekitemname=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=&range%5Bnumweights%5D%5Bmin%5D=&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&colfiltertype=owned&searchuser=noobcitizen&playerrangetype=normal&B1=Submit').text

    soup = BeautifulSoup(current_page,'html.parser')
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



timestamp_format = '%Y-%h-%d-%H%M%S'
now = datetime.now()
timestamp = now.strftime(timestamp_format)
with pd.ExcelWriter(f'search_result_{timestamp}.xlsx') as writer:
    search_result_df.to_excel(writer,sheet_name='Search_Result')

