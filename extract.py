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
import errno

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
    # TODO: CHANGE TRY ACCEPT TO A IF BLOCK AND SEE WHAT FINDALL RETURNS TTO WHICH IT DOENS"T RETURN ANY RESULTS
    # See if the search yielded any results probably none... TRY EXCEPT WON"T WORK
    # try:
    #     table.findAll('div', attrs={'class':'ls5'})
    # except:
    #     print('---------------------------------------------------')
    #     print("There were no search results found. Check the spelling and/or use the japanese equivalent name.")
    #     main()

    list_of_div = table.findAll('div', attrs={'class':'ls5'})
    
    if (len(list_of_div) == 0):
            print('---------------------------------------------------')
            print("There were no search results found. Check the spelling and/or use the japanese equivalent name.")
            main()

    for div in list_of_div:
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

    print('---------------------------------------------------')
    print('Input only one number')
    print()
    user_input = input('What title should I download for you? : ')

    if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
        return title_array[int(user_input)]
    else:
        print('---------------------------------------------------')
        print("Incorrect Input. Back to the start")
        main()
        return

def find_chapters(url):
    
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html5lib')

    table = soup.find('table', attrs={'class':'lsch', 'id':'table'})
    
    chapter_list = []

    # TODO : support chap number plus additional characters i.e. 82 v2
    for tr in table.tbody.findAll('tr', attrs={'itemprop':'hasPart'}):
        chapter_info = {}

        chapter_info['chapter'] = float(tr.td.a.span.text)
        chapter_info['link'] = tr.td.a['href']

        chapter_list.append(chapter_info)
    
    
    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])

    for i in range(len(chapter_list)):
        print('[{}] chapter {}'.format(chapter_list[i]['chapter'], chapter_list[i]['chapter']))

    print('---------------------------------------------------')

    chapter_to_download = []

    print('---------------------------------------------------')
    print('Choose manga chapters to download separated by commas i.e. 1,10,20')
    print('Choose manga chapters by range? Use dash i.e. 1-14 ... WILL NOT DOWNLOAD HALF CHAPTERS')
    print('Type \'ALL\' to download all chapters')
    print()
    user_input = input('What chapters should I download for you? : ')

    # returns whole array containing all chapters
    if (user_input.upper() == 'ALL'):
        return chapter_list
    
    # TODO: when i do 0 - 1, only downloads 0 not 1
    # returns array with range of chapter numbers in an array
    elif ('-' in user_input):

        user_input = user_input.replace(' ', '')
        
        parse_user_input = user_input.split('-') # [1,14]

        for i in range(int(parse_user_input[0]), int(parse_user_input[1]), 1): # 1  -  14

            # get index in title_array at the index where chapter = what in for loop
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == i), None) # O(1)

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download
    
    # return array with specific chapters downloaded
    elif (',' in user_input):

        user_input = user_input.replace(' ', '')

        parse_user_input = user_input.split(',')

        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == int(parse_user_input[i])), None) # O(1)

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download

    # # Shouldn't need to have to check for something that isn't a number.... 
    # if (user_input.isnumeric() and int(user_input) % 1 == 0 and int(user_input) >= 0 and int(user_input) <= len(title_array) - 1):
    #     return title_array[int(user_input)]
    else:
        print('---------------------------------------------------')
        print("Incorrect Input. Back to the start")
        main()
        return

    return chapter_to_download

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# TODO: DO A TERMINAL PERCENTAGE COUNT THING
'''
Image file extensions supported [.jpg, .png]
'''
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

            if (img_link.find('.jpg') != -1):
                end = img_link.find('.jpg') # .jpg
                f_ext = '.jpg'
            elif (img_link.find('png') != -1):
                end = img_link.find('.png') # .png
                f_ext = '.png'
            else:
                print('---------------------------------------------------')
                print('Image file extension not supported as of now. IMPLEMENT NOW.')

            pg_num = img_link[start:end]

            res = requests.get(img_link)
            

            f_name = os.path.join(image_folder_path, pg_num + f_ext)
            file = open(f_name, 'wb')
            file.write(res.content)
            file.close()
        
        im_paths = []
        print('---------------------------------------------------')
        print("Finished Downloading all Images of chapter {}".format(chapters[i]['chapter']))
        for file in sorted(glob.glob(image_folder_path + '/*' + f_ext), key=os.path.getmtime):
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

    try:
        os.mkdir(title_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


    chapter = find_chapters(title_info['link']) # return {'chapter': int, 'link' : string}

    download_chapters(chapter, title_dir, underscore_title)

if __name__ == '__main__':
    # https://mangafast.net/
    main()



   