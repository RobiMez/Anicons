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

import requests # import requests to download urls

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
    # Progress bar printing 
    print(f'\r{prefix} │{bar}│ {percent}% {suffix}', end=printEnd)

# Global Style for the prompts
style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#bb89f5',
    Token.Pointer: '#18e7f2 ',
    Token.Instruction: '#11fa4c',
    Token.Answer: '#18e7f2 bold',
    Token.Question: '#63b9ff',
})

# ----------
# ASTHETICS
# ----------
def splash_ascii(txt):
    print(figlet.renderText(txt))
def clrs():
    os.system('cls')
def divider():
    print('────────────────────────────────────────────────────────────────────────────')

# ----------
# FUNCTIONAL
# ----------
# Remove duplicate entries ie subfolders containing the same name as their parents  
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
# Print folder tree list 
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
# Fetch names from the jikan api 
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
# Download the poster from jikan 
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
# Generate a an.ico file 
def create_ico(source):
    """Creates a an.ico file in the specified path using image.jpg 
    
    @Params : 
        Source : A path that points to where image.jpg is 

    """
    canvas = Image.new('RGBA', (256, 256), color = (0,0,0,0))
    canvas.save(os.path.join(source, 'canvas.png'))
    print("\n[ ✨ ] Created transparent canvas \n")
    im = Image.open(source+r'\image.jpg')
    print("[ ✅ ] Opened image.jpg\n")
    imr = im.resize((180, 256))
    print("[ ✨ ] Resized to fit Canvas\n")
    pngsave_loc = source+ r'\image.png'
    imr.save(pngsave_loc,format="png")
    img_loc = os.path.join(source, 'image.png')
    image = Image.open(img_loc)
    print("[ ✅ ] Opened image.png\n")
    canvas.paste(image,(38,0))
    print("[ ✨ ] Pasted image.png onto canvas.png\n")
    canvas.save(source+r'\poster.png')
    print("[ ✅ ] Saved paste as poster.png\n")
    im = Image.open(source+r"\poster.png")
    sizes = [(256, 256)]
    im.save(source+'\\an.ico',format="ICO",sizes=sizes)
    print("[ 🦾 ] Created an.ico file with 256 * 256 size \n")
# Clean up residual files generated from create_ico
def clean_up(dir,files):
    print("[ ^_^ ] Cleaning up residual files :")
    for file in files:
        if os.path.exists(dir+f'\\{file}'):
            os.remove(dir+f'\\{file}')
        else:
            print("The file does not exist") 
    time.sleep(0.5)
# Set folder attributes as read only 
def set_folder_readonly(main_folder_path,root):
    os.system(f'attrib +R {main_folder_path}\\"{root}"')
# Generate a .ini config file 
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


def main ():

    clrs() # Clear the screen 
    splash_ascii('Anicons.py') # Renders the ascii text 
    divider() # Adds a horizontal line as a divider 

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

    # Set the choice as main folder path 
    main_folder_path = ".\\" + path_choice['path']
    anime_folders = []
    anime_folder_structure = []
    print(f'\n[ 0.0 ] Looking for anime in  {main_folder_path}\n')

    # Sub-directory traversing happens here
    for root,d_names,f_names in os.walk(main_folder_path):
        anime_folder_structure.append([root,d_names,f_names])
        for dir in d_names:
            absolute_path  = os.path.join(root,dir) 
            directory_name = dir
            redundancy = False
            children = d_names
            # The schema of the data passed into the main code 
            anime_folder  = [directory_name,absolute_path,redundancy,root,children]
            anime_folders.append(anime_folder)
    redundant_indices = []
    # Code to Avoid subnested folders with the same name i guess.
    remove_dupes(anime_folders,redundant_indices)
    print(f'[ U.U ] Finished looking for anime in : {main_folder_path} \n')
    if len(anime_folders) != 0 :
        print(f'[ >~< ] Removed {len(redundant_indices)} duplicates folders from listing.')
        # Print directory listing if they exist 
        print('\n[ ^-^ ] Potential Anime folders: \n')
        print_dir_tree(anime_folders,main_folder_path)
    else:
        print('[ >~< ] No folders found')

    time.sleep(0.2)
    # Prompt the user if they want to continue 
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
    if continuebool['name'] == 'Yes' :
        # If user chooses to continue clear screen and proceed 
        print("Cool ... ")
        clrs()
        # Do an api call for every folder in the list 
        # as long as they are not redundant 
        for folder in anime_folders:
            if folder[2] == False:
                anime = folder[0]
                os.system('cls')
                print("[ O~O ] Fetching names similar to folder name : ",folder[0])
            # Fecth data with second param as the limit of results returned.
            anime_data = get_names(folder[0],7)
            if anime_data != None:
                results  = anime_data
                # Initialze choices 
                choices = [{'name': 'Not an anime folder ( Skip )'}]
                # Parses results for the returned names 
                # Then lets us choose which is the closest to the folder name .
                for anime in anime_data:
                    choice = {'name' : anime['title']}
                    choices.append(choice)
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
                # If the user didn't pick to skip.
                if name_validated != {'name': 'Not an anime folder ( Skip )'}:
                    choice = choices.index(name_validated) -1
                    anime_chosen_data = results[choice]
                    synop = anime_chosen_data['synopsis']
                    img_url = anime_chosen_data['image_url']
                    out_dir =  folder[1]
                    time.sleep(2)
                    # DEBUG: Data and image url 
                    # print( "\n", anime_chosen_data , "\n")
                    # print(anime_chosen_data['image_url'])
                    # Download the poster using the image_url
                    download_poster(img_url,out_dir)
                    # Generate an.ico
                    print("[ ^<^ ] Converting to icon :")
                    create_ico(folder[1]) 
                    # Generate a .ini config 
                    generate_config(folder[1],folder[0],synop,main_folder_path)
                    # Change folder attributes 
                    set_folder_readonly(main_folder_path,folder[0])
                    junk_files = ["canvas.png","image.jpg","image.png","poster.png"]
                    # Clean up residual files 
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