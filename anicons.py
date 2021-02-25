from __future__ import print_function, unicode_literals
import os
import os.path
from os import path 
import glob
import time
import io
import tempfile
import re
import asyncio

import requests # import requests to download said urls

from PyInquirer import style_from_dict, Token, prompt, Separator #inport pyinquirer for the choice list 
from pyfiglet import Figlet #figlet import for  ascii art 
from jikanpy import Jikan # import jikan for anime poster urls 
from PIL import Image # import pil for image conversions 
from pprint import pprint

ji = Jikan()
figlet = Figlet(font='larry3d')

def printProgressBar(iteration,total, prefix='Progress:', suffix='Complete ', decimals=1, length=25, fill='█', unfill='–', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *(iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + unfill * (length - filledLength)
    # bar printing is here
    print(f'\r{prefix} │{bar}│ {percent}% {suffix}', end=printEnd)

def removeSqBrackets(dirty):
    clean = ""
    clean = re.sub(r'[[]', '(', dirty)
    clean = re.sub(r'[]]', ')', clean)
    # print(clean)
    return clean

def addQuotationMarks(dirty):
    clean = ""
    clean = re.sub(r'[[]', '(', dirty)
    clean = re.sub(r'[]]', ')', clean)
    # print(clean)
    return clean

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#bb89f5',  # default
    Token.Pointer: '#18e7f2 ',
    Token.Instruction: '#11fa4c',  # default
    Token.Answer: '#18e7f2 bold',
    Token.Question: '#63b9ff',
})

def splash_ascii(txt):
    print(figlet.renderText(txt))
def clrs():
    os.system('cls')
def divider():
    print('────────────────────────────────────────────────────────────────────────────')



# traverse directory 

# code must accept a root directory as input and spit out a tree of ? dosent os .walk do that ? 

# remove duplicates 
def remove_dupes(arr,list_to_populate_redundant_indices):
    folder_names = []
    folder_directories = []
    for folder in arr:
        if folder[0] not in folder_names:
            folder_names.append(folder[0])
        else:
            list_to_populate_redundant_indices.append(arr.index(folder))
            folder[2]=True
        folder_directories.append(folder[1])
# print tree struct 
def print_dir_tree(arr,main_folder):
    for folder in arr:
        if folder[2] == False :
            if folder[3] == main_folder:
                spliced = folder[1].split('\\')
                # print(len(spliced))
                entry = ''
                for i in range(2 , len(spliced)):
                    i=i
                    entry = entry + '    '
                entry = entry + "─ " +folder[0]+'\n'
                # pprint(folder)
                print(entry)
            else:
                spliced = folder[1].split('\\')
                # print(len(spliced))
                entry = ''
                for i in range(2 , len(spliced)):
                    entry = entry + '    '
                entry = entry + "─ " +folder[0]+'\n'
                # pprint(folder)
                print(entry)

def get_names(aname,lim):
    try:
        anime_data = ji.search(search_type='anime', query=aname,parameters={'limit' :lim})
    except requests.exceptions.ConnectionError:
        anime_data = None
        print('[ >~< ] No internet connection detected ')
        print('\n Sorry but this program requires access to the internet\n in order to download the cover arts for the folders.\n')
    if anime_data != None:

        return anime_data['results']
    else :
        return None

def download_poster(image_url,out_dir):
    print("[ ^>^ ] Downloading cover art :")
    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        downloaded = 0
        filesize = int(r.headers['content-length'])
        for chunk in r.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)
            # print(printprogressBar(downloaded))
            printProgressBar(downloaded,filesize)
            time.sleep(0.007)
            # print(downloaded/filesize)
        buffer.seek(0)
        print()
        i = Image.open(io.BytesIO(buffer.read()))
        i.save(os.path.join(out_dir, 'image.jpg'), quality=100)
    buffer.close()

def create_ico(image_location):
    # Creates a transparent canvas to paste the jpg into 
    canvas = Image.new('RGBA', (256, 256), color = (0,0,0,0))
    save_loc = os.path.join(image_location, 'canvas.png')
    canvas.save(save_loc)
    # convert the jpg into a png 
    for infile in glob.glob(image_location+r'\image.jpg'):
        ext = os.path.splitext(infile)
        im = Image.open(infile)
        imr = im.resize((180, 256))
    # necessary file conversion to png ?
        pngsave_loc = os.path.join(image_location, 'image.png')
        try:
            imr.save(pngsave_loc,format="png")
        except Exception as e :
            print(e)
        print(f'Converted {ext} to PNG with size {imr.size} and \nmetadata : {imr.info}')
    # image on canvas pasting 
    
    img_loc = os.path.join(image_location, 'image.png')
    image = Image.open(img_loc)

    canvas.paste(image,(38,0))
    canvas.save(image_location+r'\poster.png')

    for infile in glob.glob(image_location+r"\poster.png"):
        ext = os.path.splitext(infile)
        im = Image.open(infile)
        sizes=[(256, 256)]
        im.save(image_location+'\\an.ico',format="ICO",sizes=sizes)

    print(f'Converted {ext} with size {im.size} and \nmetadata : {im.info} to ico ')
    # print('Resizing ')

def clean_up(dir,files):
    print("[ ^_^ ] Cleaning up residual files :")
    for file in files:
        if os.path.exists(dir+f'\\{file}'):
            os.remove(dir+f'\\{file}')
        else:
            print("The file does not exist") 
    time.sleep(0.5)

def set_folder_readonly(main_folder_path,root):
    os.system(f'attrib +R {main_folder_path}\\"{root}"')

def generate_config(dir,root,synop,main_folder_path):
    print("[ ^-^ ] Creating icon config  :")
    try:
        f = open(dir+r"\desktop.in", "w")
        f.write(f'[.ShellClassInfo]\nIconResource=an.ico,0\nConfirmFileOp=0\nInfoTip={synop}')
        f.close()
        os.rename(dir+r'\desktop.in',dir+r'\desktop.ini')
        os.system(f"cd Anime\\{root}&&attrib +A +S +H desktop.ini")

    except(FileExistsError):
        print('[ >_< ] file already exists ... Remaking')
        os.remove(dir+r'\desktop.in')
        os.remove(dir+r'\desktop.ini')
        f = open(dir+r"\desktop.in", "w")
        f.write(f'[.ShellClassInfo]\nIconResource=an.ico,0\nConfirmFileOp=0\nInfoTip={synop}')
        f.close()
        os.rename(dir+r'\desktop.in',dir+r'\desktop.ini')
        os.system(f"cd {main_folder_path}\\{root}&&attrib +A +S +H desktop.ini")
        print('[ ^_^ ] Remade icon config ')

###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################

def main ():
    clrs()
    splash_ascii('Anicons.py')
    divider()

    ###########################################################################
    # Traverse current directory and prompt user for which one is the root 
    paths = []
    for root,d_names,f_names in os.walk("."):
        for dir in d_names: 
            if(root == "."):
                paths.append(dir)
    choices = [
        {
            'type': 'list',
            'message': 'Select the main folder that contains anime : ',
            'name': 'path',
            'choices': paths,
            'validate': lambda answer: 'You must choose at least one.' \
                if len(answer) == 0 else True
        }
    ]
    path_choice = prompt(choices, style=style)
    ###########################################################################
    # set the choice as main folder path 

    main_folder_path = ".\\" + path_choice['path']
    anime_folders = []
    anime_folder_structure = []


    print(f'\n[ 0.0 ] Looking for anime in  {main_folder_path}\n')

    # directory traversing happens here 💪
    for root,d_names,f_names in os.walk(main_folder_path):
        anime_folder_structure.append([root,d_names,f_names])
        # print('\n',root,d_names,'\n')
        for dir in d_names:
            # The schema of the data passed into the main code 
            absolute_path  = os.path.join(root,dir) 
            directory_name = dir
            redundancy = False
            children = d_names
            anime_folder  = [directory_name,absolute_path,redundancy,root,children]
            anime_folders.append(anime_folder)

    # pprint(anime_folder_structure)

    redundant_indices = []
    
    #########################################################
    # avoids subnested folders with the same name i guess 
    remove_dupes(anime_folders,redundant_indices)
    #########################################################
    print(f'[ U.U ] Finished looking for anime in : {main_folder_path} \n')
    #########################################################
    if len(anime_folders) != 0 :
        print(f'[ >~< ] Removed {len(redundant_indices)} duplicates folders from listing.')
        print('\n[ ^-^ ] Potential Anime folders: \n')
        print_dir_tree(anime_folders,main_folder_path)
    #########################################################
    else:
        print('[ >~< ] No folders found')
    #########################################################
    time.sleep(0.2)
    #############################################################################
    # prompt the user if they want to continue 
    cont = [
        {
            'type': 'list',
            'message': 'Proceed ? : ',
            'name': 'name',
            'choices': [
                {
                    'name':'Yes'
                },
                {
                    'name':'No'
                }
                ],
            'validate': lambda answer: 'You must choose at least one.' \
                if len(answer) == 0 else True
        }
    ]
    divider()
    continuebool = prompt(cont, style=style)
    #############################################################################

    if continuebool['name'] == 'Yes' :
        print("umm")
        clrs()

    # #################################################################################
    # Api stuff happens from here on out 😎
    # #################################################################################
        for folder in anime_folders: # Crosscheck with api if anime exists 
            if folder[2]== False:
                anime = folder[0]
                os.system('cls')
                print("[ O~O ] Fetching names similar to folder name : ",folder[0])
                # fetches data from the api matching the name 
                # try:
                #     anime_data = ji.search(search_type='anime', query=anime,parameters={'limit' :7})
                # except requests.exceptions.ConnectionError:
                #     anime_data = None
                #     print('[ >~< ] No internet connection detected ')
                #     print('\n Sorry but this program requires access to the internet\n in order to download the cover arts for the folders.\n')
            anime_data = get_names(folder[0],7)
            if anime_data != None:
                results  = anime_data
                choices = [{'name': 'Not an anime folder ( Skip )'}] # Initialze choices 
                # Parses results for the returned names and lets us choose which is the closest .
                for anime in anime_data:
                    choice = {'name' : anime['title']}
                    choices.append(choice)
                # ###########################################################
                questions = [
                {
                    'type': 'list',
                    'message': 'Select correct anime name:',
                    'name': 'name',
                    'choices': choices,
                    'validate': lambda answer: 'You must choose at least one.' \
                        if len(answer) == 0 else True
                }
                ]
                name_validated = prompt(questions, style=style)
                # ###########################################################
                # DEBUG: 
                pprint(name_validated)
                print(choices)
                # prints which choice was chosen 
                if name_validated != {'name': 'Not an anime folder ( Skip )'}:
                    
                    choice = choices.index(name_validated) -1
                    anime_chosen_data = results[choice]
                    # anime_title = anime_chosen_data['title']
                    synop = anime_chosen_data['synopsis']
                    img_url = anime_chosen_data['image_url']
                    out_dir =  folder[1]

                    time.sleep(2)

                    # DEBUG:
                    print( "\n", anime_chosen_data , "\n")
                    # print(anime_chosen_data['image_url'])
                    
                    
                    
                    download_poster(img_url,out_dir)
                    
                    print(folder[1])
                    
                    folder_sliced = folder[1].split("\\")
                    print(folder_sliced)
                    print(folder_sliced[-1])
                    quoted_folder = []
                    clean_name = ''
                    if '[' in folder_sliced[-1] or ']' in folder_sliced :
                        print("messed up title ... adding quotes ")
                        dirty_name = folder_sliced[-1]
                        clean_name = "\"" + dirty_name + "\""
                        print(clean_name)
                        print(quoted_folder)
                        nice_name = folder_sliced[0:-1] 
                        print(nice_name)
                        oof_string = ''
                        for item in nice_name:
                            oof_string = oof_string + item +'\\'
                        oof_string = oof_string + clean_name
                        print(oof_string)
                        print("[ ^<^ ] Converting to icon :")
                        create_ico(oof_string)
                        # create_ico(folder[1])
                    else:
                        print("[ ^<^ ] Converting to icon :")
                        create_ico(folder[1])   
                    
                    # file downloaded and ready , start conversion 
                    
                    print("[ ^<^ ] Converting to icon :")
                    # ####################################################
                    # generates an icon 
                    # ####################################################

                    generate_config(folder[1],folder[0],synop,main_folder_path)
                    set_folder_readonly(main_folder_path,folder[0])
                    junk_files = ["canvas.png","image.jpg","image.png","poster.png"]
                    clean_up(folder[1],junk_files)

                else:
                    print("Skipping...")
                    time.sleep(0.4)
                    pass
            else:
                pass
        print('──────────────────────────────────')
        print('My job here is done ... YEET ✨')
        print('──────────────────────────────────')


    else:
        print('Death sounds ☠')
        quit(0)
        
        


if __name__ == "__main__":
    main()