# pip install requests
# pip install html5lib
# pip install bs4
# pip install manganelo
# pip install fpdf

import requests
from bs4 import BeautifulSoup
import urllib.parse 
from manganelo import SearchManga
from manganelo import MangaInfo
from PyPDF2 import PdfFileReader
import os
from PIL import Image

def get_manga_panels(url):
    # get manga panels
    panels = []

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')

    div_imgs = soup.find('div', attrs={'class':'container-chapter-reader'})

    for i in div_imgs.findAll('img'):
        panels.append(i['src'])

    return panels

def extract_manga_chapter_url(url, chapter):
    parsed_url = url.split('/')

    # get chapter url
    url_part = list(urllib.parse.urlparse(url))
    url_part[2] = '/chapter/{}/chapter_{}'.format(parsed_url[4], chapter)
    manga_url_chapter = urllib.parse.urlunparse(url_part)

    return manga_url_chapter

def main():
    # ADD USER INPUT
    # title = input("Manga to Download: ")
    # download_all = input("Download all Chapters? YES OR NO: ")
    # chapter = input("Chapter to Download: ")

    # search = SearchManga(title, threaded=True)

    # COMMENT WHEN DONE FOR TESTING ONLY
    search = SearchManga("boruto", threaded=True)
    chapter = 1

    # .results() returns a generator - We create a list from the generator here
    results = list(search.results())

    best_result = results[0] # grand blue

    manga_title = best_result.title
    manga_url_homepage = best_result.url

    manga_url_chapter = extract_manga_chapter_url(manga_url_homepage, chapter)


    panel_list = get_manga_panels(manga_url_chapter) # get all images from chapter

    PIL_list = []
    for i in panel_list:
        img = Image.open(i)
        PIL_list.append(img)

    pdf_fname = 'chapter_{}.pdf'.format(chapter)

    PIL_list[0].save(pdf_fname, "PDF", resolution=100.0, save_all=True, append_images=PIL_list)
    # Download Manga images to pdf


    '''
    Check cwd for 'Manga' folder -> if none, make one else do nothing

    Make folder for title of manga to download -> if none, make one else do nothing

    def download
        create folder chapter_NUM
        open pdf
        add jpg images on to it
        center preferred
    '''


if __name__ == '__main__':

    main()


    # # EXPORT TO CSV
    # URL = "http://www.values.com/inspirational-quotes"
    # r = requests.get(URL) 
    
    # soup = BeautifulSoup(r.content, 'html5lib') 

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