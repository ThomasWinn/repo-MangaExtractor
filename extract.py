# pip install requests
# pip install html5lib
# pip install bs4
from __future__ import print_function

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

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from apiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def search_manga(title):

    base_url = 'https://mangafast.net/?s='

    title = title.replace(' ', '+')

    search_url = base_url + title

    r = requests.get(search_url)

    soup = BeautifulSoup(r.content, 'html5lib')

    # MangaFast.net changed their website ... CHANGED
    table = soup.find('div', attrs={'class':'list-content d-inline-block'})
    # table = soup.find('div', attrs={'class':'p mrg'})


    title_array = [] 

    '''
    [{title : bloody monday, link : https://...com}]
    '''

    # list_of_div = table.findAll('div', attrs={'class':'ls5'})
    list_of_div = soup.findAll('div', attrs={'class':'ls4j'}) # CHANGED
    
    if (len(list_of_div) == 0):
            print('---------------------------------------------------')
            print("There were no search results found. Check the spelling and/or use the japanese equivalent name.")
            main()


    # CHANGED
    for div in list_of_div:
        title_info = {}

        title = div.h3.a.text
        title_info['title'] = title

        title_info['link'] = div.h3.a['href']
        
        # Because title has many \t \n char 
        # title = div.a.h3.text
        # title = title.strip('\n')
        # title = title.strip('\t')
        # title = title.replace('\t', '')
        # title = title.strip()
        # title_info['title'] = title
        # title_info['link'] = div.a['href']
        
        title_array.append(title_info)

    if (len(title_array) == 1):
        print('---------------------------------------------------')
        print('Found {}'.format(title_array[0]['title']))
        return title_array[0]
    else:
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
    
    # again , we are going to make a request to the internet through python using the url provided from title_info
    # from title_info's link key which contains the url
    r = requests.get(url)

    # instantiate beautiful soup to return the html of the webpage in the soup variable
    soup = BeautifulSoup(r.content, 'html5lib')

    # from the html, we want to find all 'a' elements with class chapter-link
    chapter_l = soup.findAll('a', attrs={'class':'chapter-link'}) # CHANGED
    # table = soup.find('table', attrs={'class':'lsch', 'id':'table'}) 
    
    # create a list which will contain all the chapters available from mangafast.net
    chapter_list = []

    for a in chapter_l: # CHANGED

        # create a chapter_info dictionary containing chapter and the link
        # if we expand the drop down of tr, we see many of the elements of this html tag we want
        # including the chapter number and link to that chapter
        chapter_info = {}

        try:
            # we notice the chapter number is actually hiding inside the a tag that has a drop down
            # let's expand that. There we see the chapter number.


            chapter_number = a.div.span.text # CHANGED 0,
            # print(chapter_number)
            num = re.findall(r"[-+]?\d*\.\d+|\d+", chapter_number) # CHANGED
            
            # sometime there will be a chapter (blank) THIS IS SOMETHING NEW
            try:
                chapter_info['chapter'] = float(num[0]) # CHANGED
                chapter_info['link'] = a['href'] # CHANGED

                chapter_list.append(chapter_info)
            except IndexError:
                continue
            

        # IF IT SEES ADDITIONAL CHAR INFRONT OF THE CHAPTER NAME, 
        # IGNORE LATER VERSIONS AND ONLY ADD BASE VERSION TO CHAPTER LIST
        # WILL NOT SUPPORT CHAPTERS i.e. '82 V2' WILL ONLY USE 82
        # we do not see this case in tokyo ghoul. YOu may see this in other mangas you search
        except ValueError:
            continue

    # Now we want to sort the chapter_list dictionary in ascending order based on the chapter number
    # If we look closely at the for loop we just made, we are adding the chapters in 
    # from the latest chapter    
    chapter_list = sorted(chapter_list, key=lambda i: i['chapter'])

    # We will now print out the list of available chapters to the user
    for i in range(len(chapter_list)):
        # print('[{}] chapter {}'.format(chapter_list[i]['chapter'], chapter_list[i]['chapter']))
        print('Chapter {}'.format(chapter_list[i]['chapter']))

    # divide our work
    print('---------------------------------------------------')

    # create a new list to hold the chapters to download the user wants
    chapter_to_download = []

    # give users notes. Make sure to use floating point numbers in the input like 1.0, 2.0 ,etc.
    print('Please use decimals as there are half chapters as well!')
    print('Choose manga chapters to download separated by commas i.e. 1.0,10.0,20.0')
    print('Choose manga chapters by range? Use dash i.e. 1.0-14.0 ... WILL NOT DOWNLOAD HALF CHAPTERS')
    print('Type \'ALL\' to download all chapters')
    print()
    user_input = input('What chapters should I download for you? : ')

    # returns whole array containing all chapters
    if (user_input.upper() == 'ALL'):
        return chapter_list

    # returns array with range of chapter numbers in an array 
    # returns all half chapters in that range as well
    elif ('-' in user_input):

        # take out spaces within this range... e.g '14.0 - 15.0' -> '14.0-15.0' 
        # it just makes parsing the string more easier
        user_input = user_input.replace(' ', '')
        
        # split the two numbers into a list using minus sign as the separator
        parse_user_input = user_input.split('-') # [1,14]

        # starting from the first number the user inputted and go until the end point + 0.1 because
        # if you do it from 1.0 - 2.0 it will just do 1.0 and not do 2.0 at all. 
        # we also want to step through every 0.1 because there are 0.5 volumes on mangafast
        # for some reason. 
        for i in np.arange(float(parse_user_input[0]), float(parse_user_input[1]) + 0.1, 0.1): # 1.0  -  14.0

            # get index in title_array where chapter = the i'th  value we are currently at
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == round(i,1)), None) # O(1)

            # we also need to chck that if that chapter doesn't exist, we do nothing
            if (num_index == None):
                continue
            
            # add that chapter to the chapter_to_download list
            chapter_to_download.append(chapter_list[num_index])

        return chapter_to_download
    
    # return array with specific chapters downloaded
    # with a comma specific chapters to download the logic is the same essentially as above
    elif (',' in user_input):

        # replace the spaces so there is none
        user_input = user_input.replace(' ', '')

        # parse the comma list, so you get [1.0,2.0]
        parse_user_input = user_input.split(',')

        # for all the things inside that parse_user_input, we find the index in our chapter_list
        # dictionary that cooresponds to the specific chapter we want to download 
        for i in range(len(parse_user_input)):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == float(parse_user_input[i])), None) # O(1)

            chapter_to_download.append(chapter_list[num_index]) # add to list

        return chapter_to_download

    # single chapter download
    else:
        # we want to check if the user...
        # typed in a valid number, it is within the range of the chapters available
        # then add that chapter to the list to download
        if (int(float(user_input)) % 1 == 0 and int(float(user_input)) >= int(chapter_list[0]['chapter']) and int(float(user_input)) <= len(chapter_list) - 1):
            num_index = next((index for (index, d) in enumerate(chapter_list) if d["chapter"] == round(float(user_input),1)), None)
            chapter_to_download.append(chapter_list[num_index])
            return chapter_to_download
        
        # if it doesn't satisfy the condition above, return back to main and restart the program
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
# Give user status on progress of manga downloading
# Found this off of Stack Overflow
# sepcify a start in first parameter and end in second parameter. Then incrmeemnt first parameter as we go
# soooooo start with 0 / 10
# 1/10 ... 10/10
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

    # for all the chapters to download...
    for i in range(len(chapters)):
        
        # print out what chapter we are downloading
        print('Beginning to download chapter {}'.format(chapters[i]['chapter']))

        # go to the link using request and beautiful soup
        r = requests.get(chapters[i]['link'])

        soup = BeautifulSoup(r.content, 'html5lib')

        # find the parent holding all the images and in this case it's that div tag
        div = soup.find('div', attrs={'class':'content-comic py-4'})

        images = [] # list of image links 

        for img in div.findAll('img',attrs={'loading':'lazy'}): # find all the img tags and append the image links from src attribute

            images.append(img['src']) 
        
        # now we are going to make a folder containing the chapter to download
        # this folder will contain all the images from that chapter
        image_folder_path = os.path.join(dir, 'Chapter_' + str(chapters[i]['chapter'])) # create folder for images
        os.mkdir(image_folder_path)

        # NEED TO CHECK IF CHAPTER IS EMPTY
        if (len(images) == 0):
            print('Chapter {} is empty'.format(str(chapters[i]['chapter'])))
            print('---------------------------------------------------')
            continue
        
        # DO THIS LATER
        printProgressBar(0, len(images), prefix='Progress:', suffix= 'Complete')

        # Now for all the chapter's image links
        # we will write the image links to a file. THe file name will be the chapter number
        for j in range(len(images)):

            # links will be https://blahblah.com/tokyo-ghoul-page-1.jpg

            
            # get string between this for page number
            start = images[j].find('page-') + len('page-') # page-
            
            # get index of page- and the number should come right after it.

            # get the file extension and the index of the .jpg or file extension
            if (images[j].find('.jpg') != -1):
                end = images[j].find('.jpg') # .jpg
                f_ext = '.jpg'
            elif (images[j].find('png') != -1):
                end = images[j].find('.png') # .png
                f_ext = '.png'
            else:
                print('---------------------------------------------------')
                print('Image file extension not supported as of now. IMPLEMENT NOW.')


            # the page number will be the things in between page- and the file extension or . whatever
            pg_num = images[j][start:end]

            # get the image from the internet from that specific link...
            res = requests.get(images[j])
            
            # create the folder name which will contain all the chapter images
            f_name = os.path.join(image_folder_path, pg_num + f_ext) # 1.jpg
            file = open(f_name, 'wb') # we will open up a file with write binary capabilities to write images to a file
            file.write(res.content)
            file.close() # then close it

            time.sleep(0.1) # we need to write a little delay or the progress bar won't work
            
            # add progress to the bar
            printProgressBar(j+1, len(images), prefix='Progress:', suffix= 'Complete')
        

        # NOW WE WANT TO PUT ALL IMAGES INTO 1 PDF

        # define a place to store all the images
        im_paths = []
        
        # We will sort the file directory basically by numerical order starting from page 1 ... page N. 
        # THe code Sorts by time of upload 
        for file in sorted(glob.glob(image_folder_path + '/*' + f_ext), key=os.path.getmtime):

            # open the image file if possible using PIL
            # conver the image to rgb color then add it to the image paths array
            try:
                im = Image.open(file)
                im.convert('RGB')
                im_paths.append(im)

            # some image files are actually sotred on the cloud on mangafast.net and you'll see some manga chapter's
            #images just won't open even on the browser. A good exmaple is if we search naruto -> full color. 
            # no images show up, but the image files from the website will still be able to download to our computer.
            # if we try to open them, it'll throw us an error, so we accomodate through this try/except statement
            except:
                print('Image did not load on site properly. Website fault.')
                continue
        
        # Checks to see if there are no elements in list to make pdf out of
        # Save the pdf file inside the manga title's folder and then append the rest of the images onto that pdf.
        # remove the folder containing all the individual images of a certain chapter.
        try:
            im1 = im_paths[0]
            im_paths.pop(0)

            chapter_num = chapters[i]['chapter']
            pdf = os.path.join(dir, 'Chapter_{}.pdf'.format(chapter_num))
            im1.save(pdf, save_all=True, append_images=im_paths)

            # recursively remove everything from a path
            shutil.rmtree(image_folder_path, onerror=remove_readonly)
            print('---------------------------------------------------')
        except:
            continue

def gd_init():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    return service

def gd_create_folder(service, manga_name):
    file_metadata = {
        'name': manga_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = service.files().create(body=file_metadata, fields='id').execute()
    print('---------------------------------------------------')
    print('Finished Creating Folders Now Uploading')
    return file.get('id')

# upload all pdf's in specified folder.... even the ones you've already uploaded to Gdrive
def gd_upload_chapter(service, id, dir):
    pdf_location = glob.glob(os.path.join(dir, "*.{}".format('pdf')))

    os.chdir(dir)
    pdf_list = glob.glob('*.pdf')

    for i in range(len(pdf_list)):
        
        file_metadata = {
            'name': pdf_list[i],
            'parents': [id]
        }
        media = MediaFileUpload(pdf_location[i],
                                mimetype='application/pdf',
                                resumable=True)
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print('Uploaded {} / {} to GDrive'.format(i+1, len(pdf_list)))

    print('---------------------------------------------------')
    print('Finished Uploading')

def main():

    print('---------------------------------------------------')
    title = input("Manga to Download: ")

    title_info = search_manga(title) # return {'title' : title, 'link' : https...}

    if (' ' in title_info['title'] or '\\' in title_info['title'] or '/' in title_info['title'] or ':' in title_info['title'] 
    or '*' in title_info['title'] or '?' in title_info['title'] or '"' in title_info['title'] or '<' in title_info['title']
    or '>' in title_info['title'] or '|' in title_info['title']):
        edited_title = title_info['title'].replace(' ', '_').replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

    else:
        edited_title = title_info['title']

    # C:\Users\tpngu\OneDrive\Desktop\CSCI\repo-MangaExtractor
    cwd = os.getcwd() # get string of current working directory 

    # creating the address path of the new folder we want to create... os.getcwd() + tokyo_ghoul
    title_dir = os.path.join(cwd, edited_title)

    # create the directory or folder of the address we just made...
    # Now lets say we are running this program and it's not the first time we created a tokyo ghoul folder
    # we want to make an exception for if the folder exists, don't error out if the folder exists 
    # and stops this program
    try:
        os.mkdir(title_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    '''
    Hey guys welcome back to the second episode of our let's code series where we are developing a manga extractor.
    In this episode we will be setting up our file system and
    returning the list of chapters of the searched manga to the user using the dictionary
    we returned from the search_manga function we created last episode. 

    Before we start, the code may look different because I added some print statements from last time. I added
    the dash divider to divide up our work, so it's easier to follow. Show demo.

    Sweet, Let's code now!

    Firstly we are going to create a folder for the manga series that we ended up searching.

    Again, remember that title_info is returning back a dictionary containing the title of the manga and the link associated
    to that series. * comment this in code * 

    Because file's can't be created with spaces and a bunch of certain characters, we need to replace all those with an _

    
    '''
    
    # Now we are creating the find_chapter function. returns 
    # what chapters to download, to do so, we need to pass in the link of the manga to this function
    # remember that title_info = {'title' : title, 'link' : https...}
    chapter = find_chapters(title_info['link']) # return {'chapter': float, 'link' : string}, ...

    '''
    Hey what's going on guys? Welcome to the official third episode of this lets code series. Back in episode 2.5, 
    we accomodated the changes for the new interface of mangafast.net
    so if your code literally doesn't work after watching episodes 1 and 2, I highly recommend you watching that short episode. 
    Above I'll link the video for you so you don't have to search it.

    In this episode we will go over the main downloading aspect of our manga chapters.

    Before we do that, I'm going to run over the overview of what's goign to end up happening inside this episode.

    Recall that in episodes 1 and 2, We create a folder of the manga you want to download in the directory where your current
    python script runs. 

    We will create a folder for each chapter we want to download inside the folder of the manga we want to download.

    Inside these chapter folders will contain jpg images of the pages of that specific chapter. There will be 1 to N amount of 
    images inside each chapter folder.

    After we get that done, We will use all the images to create a pdf named the chapter number for example, chapter_1.pdf.
    This will reside in the manga title's folder and outside of the chapter's folder. Then we will simply delete the chapter
    folder and all images inside it using the shutil library.

    We then rince and repeat with each chapter until we have only pdf's of each chapter inside the manga title's folder we 
    specified to download from.
    '''

    # DO THIS AT THE END.
    # Check file for each pdf name of each, if found, skip that chapter to donwload by taking out of chapter list.
    pdf_array = os.listdir(title_dir) # Lists all pdf in the searched title's folder
    
    # search through all pdf in the title's folder
    # if the chapters attempting to download is existent in the folder already, remove it from the list to download
    
    # FOr example, chapter 2 in title's folder. If the user wants to downlaod a range from chapter 2 - 8, it will remove 2 from the 'to download' list and download only 3-8
    for i in pdf_array:
        for j in chapter:
            if (i.find(str(j['chapter'])) != -1):
                chapter.remove(j)
                break

    # if there are no chapters to download, just print out a message            
    if (len(chapter) == 0):
        print('There are no additional files to be downloaded')
        return
    # so since there are chapters to be download, let's download them
    # Create a new function to download them. 
    # it will take in the chapter list to download, the directory that we made, and the edited title's name
    elif (len(chapter) > 0):
        download_chapters(chapter, title_dir, edited_title)
    else:
        print('ERROR OCCURED')

    # Upload to google drive

    print('---------------------------------------------------')
    print('Uploading to google drive')

    service = gd_init()

    f_id = gd_create_folder(service, title_info['title'])

    gd_upload_chapter(service, f_id, title_dir)

if __name__ == '__main__':
    # https://mangafast.net/

    # i = 'helpafsd-page-1.jpg'

    # start =i.find('page-') + len('page-')
    # print(start)
    main()



'''
Basically the functionality of the manga extractor is basically completed as of now. 
The next big things to add are more functionality to the user experience such as adding a progress bar 
while downloading the manga chapter. We will also connect to google drive, so that once we download our manga chapters,
we will also download a copy to google drive for that on the go experience.

All of this will be featured on part 4 so stay tune ;)
Alright guys, thats a wrap for part 3. Thank you for watching and I'll see you in the next episode. Peace guys.
'''