# pip install requests
# pip install html5lib
# pip install bs4
# pip install google 
# pip install manganelo

import requests
from bs4 import BeautifulSoup
# import google 
from manganelo import SearchManga
from manganelo import MangaInfo
import csv


if __name__ == '__main__':
    print("hello")

    search = SearchManga("Grand Blue", threaded=True)

    # .results() returns a generator - We create a list from the generator here
    results = list(search.results())

    print(results)

    best_result = results[0]

    manga_info = MangaInfo(best_result.url, threaded=True)

    manga_page = manga_info.results()

    print()
    print(manga_page.chapters)


    # results = [MangaSearchResult(title=?, url=?), MangaSearchResult(title=?, url=?)]












    # # prints all the html elements CHOPPY UGLY
    # URL = "https://www.geeksforgeeks.org/data-structures/"
    # r = requests.get(URL)
    # print(r.content)


    # GETS ALL HTML TAGS BUT PRETTY
    # URL = "http://www.values.com/inspirational-quotes"
    # r = requests.get(URL) 
    
    # soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
    # print(soup.prettify()) 

    # EXPORT TO CSV
    # URL = "http://www.values.com/inspirational-quotes"
    # r = requests.get(URL) 
    
    # soup = BeautifulSoup(r.content, 'html5lib') 
    # print(soup.prettify()) 
    
    # quotes=[]  # a list to store quotes 
    
    # table = soup.find('div', attrs = {'id':'all_quotes'})  
    
    # for row in table.findAll('div', 
    #                         attrs = {'class':'col-6 col-lg-3 text-center margin-30px-bottom sm-margin-30px-top'}): 
    #     quote = {} 
    #     quote['theme'] = row.h5.text 
    #     quote['url'] = row.a['href'] 
    #     quote['img'] = row.img['src'] 
    #     quote['lines'] = row.img['alt'].split(" #")[0] 
    #     quote['author'] = row.img['alt'].split(" #")[1] 
    #     quotes.append(quote) 
    
    # filename = 'inspirational_quotes.csv'
    # with open(filename, 'w', newline='') as f: 
    #     w = csv.DictWriter(f,['theme','url','img','lines','author']) 
    #     w.writeheader() 
    #     for quote in quotes: 
    #         w.writerow(quote)