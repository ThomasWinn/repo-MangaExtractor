# pip install requests
# pip install html5lib
# pip install bs4

import requests
import urllib.parse 
import os
import glob
import re
import shutil
import stat

from PIL import Image
from bs4 import BeautifulSoup

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

    # See if the search yielded any results
    try:
        table.findAll('div', attrs={'class':'ls5'})
    except:
        print('---------------------------------------------------')
        print("There were no search results found. Check the spelling and/or use the japanese equivalent name.")
        main()

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
    print('---------------------------------------------------')
    print('Choose manga chapters to download separated by commas i.e. 1,10,20')
    print('Choose manga chapters by range? Use dash i.e. 1-14 ... WILL NOT DOWNLOAD HALF CHAPTERS')
    print('Type ALL to download all chapters')
    print()
    user_input = input('What chapters should I download for you? : ')

    # returns whole array containing all chapters
    if (user_input.upper() == 'ALL'):
        return title_array
    
    # returns array with range of chapter numbers in an array
    elif ('-' in user_input):

        user_input = user_input.replace(' ', '')
        chapter_array = []
        
        parse_user_input = user_input.split('-') # [1,14]

        for i in range(int(parse_user_input[0]), int(parse_user_input[1]), 1): # 1  -  14

            # get index in title_array at the index where chapter = what in for loop
            num_index = next((index for (index, d) in enumerate(title_array) if d["chapter"] == i), None) # O(1)

            chapter_array.append(title_array[num_index])

        return chapter_array
    
    # return array with specific chapters downloaded
    elif (',' in user_input):

        user_input = user_input.replace(' ', '')
        chapter_array = []

        parse_user_input = user_input.split(',')

        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(title_array) if d["chapter"] == int(parse_user_input[i])), None) # O(1)

            chapter_array.append(title_array[num_index])

        return chapter_array

    # # Shouldn't need to have to check for something that isn't a number.... 
    # if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
    #     return title_array[int(user_input)]
    else:
        print("Incorrect Input. Back to the start")
        main()
        

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

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

def download_chapters(chapters, dir, title):

    for i in range(len(chapters)):
        
        r = requests.get(chapters[i]['link'])

        soup = BeautifulSoup(r.content, 'html5lib')

        table = soup.find('div', attrs={'class':'chp2', 'id':'Read'})

        images = [] # list of image links WORKLS

        for img in table.findAll('img', attrs={'class':'lazy'}):

            images.append(img['data-src'])
        
        # C:\Users\tpngu\OneDrive\Desktop\CSCI\repo-MangaExtractor\Bloody Monday\Chapter_1
        image_folder_path = os.path.join(dir, 'Chapter_' + str(chapters[i]['chapter'])) # create folder for images
        os.mkdir(image_folder_path)

        for img_link in images:
            
            # get string between this for page number
            start = img_link.find('page-') + len('page-') # page-
            end = img_link.find('.jpg') # .jpg
            pg_num = img_link[start:end]

            res = requests.get(img_link)
            

            f_name = os.path.join(image_folder_path, pg_num + '.jpg')
            file = open(f_name, 'wb')
            file.write(res.content)
            file.close()
        
        im_paths = []
        print("Finished Downloading all Images of chapter {}".format(chapters[i]['chapter']))
        for file in sorted(glob.glob(image_folder_path + '/*.jpg'), key=os.path.getmtime):
            im = Image.open(file)
            im.convert('RGB')
            im_paths.append(im)

        im1 = im_paths[0]
        im_paths.pop(0)

        chapter_num = chapters[i]['chapter']
        pdf = os.path.join(dir, 'Chapter_{}.pdf'.format(chapter_num))
        im1.save(pdf, save_all=True, append_images=im_paths)

        shutil.rmtree(image_folder_path, onerror=remove_readonly)


def main():

    print('---------------------------------------------------')
    title = input("Manga to Download: ")

    title_info = search_manga(title) # return {'title' : title, 'link' : https...}

    if (' ' in title_info['title']):
        underscore_title = title_info['title'].replace(' ', '_')
    else:
        underscore_title = title_info['title']

    cwd = os.getcwd()
    title_dir = os.path.join(cwd, underscore_title) # C:\Users\tpngu\OneDrive\Desktop\CSCI\repo-MangaExtractor\Bloody_Monday
    # print(title_dir)

    # os.mkdir(title_dir)   # TRY CATCH CAN"T MAKE FILE IF EXISTS

    chapter = find_chapters(title_info['link']) # return {'chapter': int, 'link' : string}

    download_chapters(chapter, title_dir, underscore_title)

if __name__ == '__main__':
    # https://mangafast.net/

    main()



   