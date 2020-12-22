# pip install requests
# pip install html5lib
# pip install bs4
# pip install manganelo
# pip install fpdf

import requests
from bs4 import BeautifulSoup
import urllib.parse 
# from manganelo import SearchManga
# from manganelo import MangaInfo
from PyPDF2 import PdfFileReader
import os
from PIL import Image
import glob
import json
import re

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

def search_manga(title):

    base_url = 'https://mangafast.net/?s='

    title = title.replace(' ', '+')

    search_url = base_url + title

    r = requests.get(search_url)

    soup = BeautifulSoup(r.content, 'html5lib')

    table = soup.find('div', attrs={'class':'p mrg'})


    title_array = [] 

    '''
    [{title : bloody monday, link : https://...com}]
    '''

    for div in table.findAll('div', attrs={'class':'ls5'}):
        title_info = {}
        
        # Because title has many \t \n char 
        title = div.a.h3.text
        title = title.strip('\n')
        title = title.strip('\t')
        title_info['title'] = title
        title_info['link'] = div.a['href']
        
        title_array.append(title_info)

    for i in range(len(title_array)):
        print('[{}]  {}'.format(i, title_array[i]['title']))

    print()

    # TODO : USER INPUT
    # user_input = input('Choose the manga to download from PICK 1: ')
    user_input = '0' # CHANGE THIS IN THE END

    if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
        return title_array[int(user_input)]
    else:
        print("Incorrect Input. Quitting Session. Rerun Program.")
        quit(1)
        return 


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

def find_chapters(url):
    
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib')

    table = soup.find('table', attrs={'class':'lsch', 'id':'table'})
    
    chapter_list = []

    for tr in table.tbody.findAll('tr', attrs={'itemprop':'hasPart'}):
        chapter_info = {}

        chapter_info['chapter'] = int(tr.td.a.span.text)
        chapter_info['link'] = tr.td.a['href']

        chapter_list.append(chapter_info)
    
    
    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])

    # TODO : USER INPUT FROM SORTED LIST... ASK FOR RANGE OR comma delimeter, or ASK TO DOWNLOAD ALL
    chapter_to_download = []
    chapter_to_download.append(chapter_list[0])

    return chapter_to_download

def download_chapters(chapters):

    for i in range(len(chapters)):
        
        r = requests.get(chapters[i]['link'])

        soup = BeautifulSoup(r.content, 'html5lib')

        table = soup.find('div', attrs={'class':'chp2', 'id':'Read'})

        images = [] # list of image links WORKLS

        for img in table.findAll('img', attrs={'class':'lazy'}):

            images.append(img['data-src'])

        # DOWNLOAD ALL FILES TO DIRECTORY

        # TRANSFER TO PDF USING PIL







def main():
    # ADD USER INPUT
    # title = input("Manga to Download: ")
    # download_all = input("Download all Chapters? YES OR NO: ")
    # chapter = input("Chapter to Download: ")

    # search = SearchManga(title, threaded=True)


    title_info = search_manga("bloody Monday") # return {'title' : title, 'link' : https...}

    chapter = find_chapters(title_info['link'])

    download_chapters(chapter)

    # panel_list = get_manga_panels(manga_url_chapter) # get all images url from chapter

    # download_pdf(panel_list)

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

# https://github.com/nixonjoshua98/manganelo/blob/master/manganelo/api/downloadchapter.py
if __name__ == '__main__':
    # https://mangafast.net/bloody-monday-chapter-97/
    main()

    # im_list = []

    # im = 'https://cdn.statically.io/img/img.y7349.top/img/c/bloody-monday/chapter-97/bloody-monday-chapter-97-page-1.jpg?q=70'
    # im2 = 'https://cdn.statically.io/img/img.y7349.top/img/c/bloody-monday/chapter-97/bloody-monday-chapter-97-page-2.jpg?q=70'
    # im3 = 'https://cdn.statically.io/img/img.y7349.top/img/c/bloody-monday/chapter-97/bloody-monday-chapter-97-page-3.jpg?q=70'

    # im_list.append(im)
    # im_list.append(im2)
    # im_list.append(im3)

    # for i in im_list:
    #     parsed_url = i.split('-')
    #     num = parsed_url[7]
    #     parsed_num = num.split('.')
    #     pg_num = parsed_num[0]
    #     res = requests.get(i)
    #     f_name = pg_num + ".jpg"

    #     file = open(f_name, "wb")
    #     file.write(res.content)
    #     file.close()

    # im_paths = []

    # for file in glob.glob('./*.jpg'):
    #     im = Image.open(file)
    #     im.convert('RGB')
    #     im_paths.append(im)
    
    # im1 = im_paths[0]
    # im_paths.pop(0)

    # im1.save(r'lol.pdf', save_all=True, append_images=im_paths)

















   