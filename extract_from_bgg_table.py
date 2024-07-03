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
    try:
        if url.find('https://boardgamegeek.com/geeksearch.php?action=search&advsearch') == -1:
            print("the url is not for bbg advance search result web page. Please provide a valid web page")
            return 1, False

        page_request = requests.get(url)
        main_page = page_request.text
        soup = BeautifulSoup(main_page,'html.parser')
        page_numbers_bar = soup.find_all('div',{"class": "fr"})
        
        last_page = page_numbers_bar[0].find_all('a',{"title": "last page"})

        if not last_page:
            pages = page_numbers_bar[0].find_all('a') 
            if not pages:
                return 1, True
            
            page_before_next = 1
            for page in pages:
                if page["title"] != "next page":
                    page_before_next = page.text
                else:
                    return int(page_before_next), True
                
        return int(last_page[0].text[1:-1]), True
    except Exception:
        print("error occured. check the url, then try again")
        return 1,False

url = 'https://boardgamegeek.com/geeksearch.php?action=search&advsearch=1&objecttype=boardgame&q=&include%5Bdesignerid%5D=&geekitemname=&geekitemname=&include%5Bpublisherid%5D=&range%5Byearpublished%5D%5Bmin%5D=&range%5Byearpublished%5D%5Bmax%5D=&range%5Bminage%5D%5Bmax%5D=&floatrange%5Bavgrating%5D%5Bmin%5D=&floatrange%5Bavgrating%5D%5Bmax%5D=&range%5Bnumvoters%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmin%5D=&floatrange%5Bavgweight%5D%5Bmax%5D=&range%5Bnumweights%5D%5Bmin%5D=&colfiltertype=owned&searchuser=noobcitizen&range%5Bminplayers%5D%5Bmax%5D=&range%5Bmaxplayers%5D%5Bmin%5D=&playerrangetype=normal&range%5Bleastplaytime%5D%5Bmin%5D=&range%5Bplaytime%5D%5Bmax%5D=&B1=Submit'

VALID = False
page_num =1
while VALID is False:
    url = input("enter url:")
    print("url is: " + url)
    log_progress('url entered. Starting get total number of web pages')
    page_num, VALID = get_number_of_pages(url)  

log_progress('number of pages acquired')


search_result_df = pd.DataFrame(columns=['Ranking','Name', 'Geek Rating', 'Average Rating','Number of Votes'])

parameter_index = url.index("advsearch")
url_parameters = url[parameter_index:]
print(url_parameters)
for page in range(1,page_num +1):
    print(page)
    current_page = requests.get(f'https://boardgamegeek.com/search/boardgame/page/{page}?'+ url_parameters).text
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

