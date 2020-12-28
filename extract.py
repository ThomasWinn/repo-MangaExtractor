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
import numpy as np
import time

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

    # IF IT SEES ADDITIONAL CHAR INFRONT OF THE CHAPTER NAME, IGNORE LATER VERSIONS AND ONLY ADD BASE VERSION TO CHAPTER LIST
    # WILL NOT SUPPORT CHAPTERS i.e. '82 V2' WILL ONLY USE 82
    for tr in table.tbody.findAll('tr', attrs={'itemprop':'hasPart'}):
        chapter_info = {}

        try:
            chapter_number = float(tr.td.a.span.text)
            chapter_info['chapter'] = chapter_number
            chapter_info['link'] = tr.td.a['href']

            chapter_list.append(chapter_info)
        except ValueError:
            continue

        
    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])

    for i in range(len(chapter_list)):
        # print('[{}] chapter {}'.format(chapter_list[i]['chapter'], chapter_list[i]['chapter']))
        print('Chapter {}'.format(chapter_list[i]['chapter']))

    print('---------------------------------------------------')

    chapter_to_download = []

    print('Please use decimals as there are half chapters as well!')
    print('Choose manga chapters to download separated by commas i.e. 1.0,10.0,20.0')
    print('Choose manga chapters by range? Use dash i.e. 1.0-14.0 ... WILL NOT DOWNLOAD HALF CHAPTERS')
    print('Type \'ALL\' to download all chapters')
    print()
    user_input = input('What chapters should I download for you? : ')

    # returns whole array containing all chapters
    if (user_input.upper() == 'ALL'):
        return chapter_list
    
    # TODO: when I DO 2-3, it only populates 2... not 2 and 3
    # I believe you should only look at first decimal instead of whole float. Truncating must be done. 2.3000000000000003 output sample...

    # returns array with range of chapter numbers in an array 
    # returns all half chapters in that range as well
    elif ('-' in user_input):

        user_input = user_input.replace(' ', '')
        
        parse_user_input = user_input.split('-') # [1,14]
        print(parse_user_input)
        
        for i in np.arange(float(parse_user_input[0]), float(parse_user_input[1]) + 0.1, 0.1): # 1.0  -  14.0

            # get index in title_array at the index where chapter = what in for loop
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == i), None) # O(1)

            if (num_index == None):
                print(i)
                continue

            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download
    
    # return array with specific chapters downloaded
    elif (',' in user_input):

        user_input = user_input.replace(' ', '')

        parse_user_input = user_input.split(',')

        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == float(parse_user_input[i])), None) # O(1)

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

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

'''
Image file extensions supported [.jpg, .png]
'''
def download_chapters(chapters, dir, title):

    for i in range(len(chapters)):
        
        print('Beginning to download chapter {}'.format(chapters[i]['chapter']))

        r = requests.get(chapters[i]['link'])

        soup = BeautifulSoup(r.content, 'html5lib')

        table = soup.find('div', attrs={'class':'chp2', 'id':'Read'})

        images = [] # list of image links WORKLS

        for img in table.findAll('img', attrs={'class':'lazy'}):

            images.append(img['data-src'])
        
        image_folder_path = os.path.join(dir, 'Chapter_' + str(chapters[i]['chapter'])) # create folder for images
        os.mkdir(image_folder_path)

        printProgressBar(0, len(images), prefix='Progress:', suffix= 'Complete')

        for j in range(len(images)):
            
            # get string between this for page number
            start = images[j].find('page-') + len('page-') # page-

            if (images[j].find('.jpg') != -1):
                end = images[j].find('.jpg') # .jpg
                f_ext = '.jpg'
            elif (images[j].find('png') != -1):
                end = images[j].find('.png') # .png
                f_ext = '.png'
            else:
                print('---------------------------------------------------')
                print('Image file extension not supported as of now. IMPLEMENT NOW.')

            pg_num = images[j][start:end]

            res = requests.get(images[j])
            

            f_name = os.path.join(image_folder_path, pg_num + f_ext)
            file = open(f_name, 'wb')
            file.write(res.content)
            file.close()

            time.sleep(0.1)

            printProgressBar(j+1, len(images), prefix='Progress:', suffix= 'Complete')
        
        im_paths = []
        
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
        print('---------------------------------------------------')

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


    chapter = find_chapters(title_info['link']) # return {'chapter': float, 'link' : string}

    print(chapter)
    print(len(chapter))

    # Check file for each pdf name of each, if found, skip that chapter to donwload by taking out of chapter list.
    for i in chapter:
        num = str(i['chapter'])
        if (os.path.exists(os.path.join(title_dir, 'Chapter_' + num + '.pdf'))):
            num_index = next((index for (index, d) in enumerate(chapter) if d["chapter"] == float(num)), None) # O(1)
            chapter.pop(num_index)
        else:
            continue

    if (len(chapter) == 0):
        print('There are no additional files to be downloaded')
    elif (len(chapter) > 0):
        download_chapters(chapter, title_dir, underscore_title)
    else:
        print('ERROR OCCURED')

if __name__ == '__main__':
    # https://mangafast.net/
    main()



   