from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt, Separator
import os
from pyfiglet import Figlet #figlet import for  ascii art 
from jikanpy import Jikan # import jikan for anime poster urls 
import requests # import requests to download said urls
from pprint import pprint
from PIL import Image
import io
import tempfile
import glob


ji = Jikan()
figlet = Figlet(font='larry3d')

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 ',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

# Splash ascii render 
print('---------------------------------------------------------------------------')
print(figlet.renderText('Anicons.py'))
print('---------------------------------------------------------------------------\n')

# Main folder that houses anime 
path = 'Anime'

# folder list  
# chose list because i need the data within to allow redundancy?
anime_folders= []

# Code traverses directory structure and appends folders/subfolders to anifolders
print(f'[ LOG ] Looking at ./{path} for anime ')
for root,d_names,f_names in os.walk(path):
    # print ('in :',root,"\n directries within:", d_names,'\n files within:', f_names,'\n')

    for dir in d_names: # This code executes For every directory in the tree 

        absolute_path  = os.path.join(root,dir) 
        directory_name = dir
        redundancy = False
        anime_folder = [directory_name , absolute_path ,redundancy] 
        anime_folders.append(anime_folder)
    # folders populated but also dirty 

# pprint(anime_folders)

folder_names = []
folder_directories = []
redundant_indices = []
for folder in anime_folders:
    if folder[0] not in folder_names:
        folder_names.append(folder[0])
    else:
        redundant_indices.append(anime_folders.index(folder))
        folder[2]=True
    folder_directories.append(folder[1])
# pprint(folder_directories)
# pprint(folder_names)
# pprint(anime_folders)
# pprint(redundant_indices)

print(f'\n[ LOG ] Finished looking at ./{path} for anime \n')
print(f'Removed {len(redundant_indices)} duplicates from listing \n')

print('\n Potential Anime folders: \n')
for folder in anime_folders:
    if folder[2] == False :
        print("    ",folder[0])

for folder in anime_folders: # Crosscheck with api if anime exists 
    if folder[2]== False:
        anime = folder[0]
        print("Folder name : ",folder[0])
        print("Fetching names in the api similar to : ",folder[0])
        # fetches data from the api matching the name 
        anime_data = ji.search(search_type='anime', query=anime,parameters={'limit' :5})
        results  = anime_data['results']
        choices = [{'name':'Not an anime folder '}] #initialze choices 
        # parse results for the returned names and let use choose which is the closest 
        for result in results:
            choice = {'name':result['title']}
            choices.append(choice)
        # print(result['title']
    else:
        break
    
    questions = [
    {
        'type': 'list',
        'message': 'Select anime name:',
        'name': 'name',
        'choices': choices,
        'validate': lambda answer: 'You must choose at least one.' \
            if len(answer) == 0 else True
    }
    ]
    name_validated = prompt(questions, style=style)
    # pprint(name_validated)
    # print(choices)
    # print(choice)
    # prints which choice was chosen 
    
    choice = choices.index(name_validated) -1
    
    anime_chosen_data = results[choice]
    print( "\n", anime_chosen_data , "\n")
    anime_poster_url = anime_chosen_data['image_url']
    anime_title = anime_chosen_data['title']
    print(anime_chosen_data['image_url'])


        
    img_url = anime_chosen_data['image_url']
    print(folder[1])
    out_dir =  folder[1]


    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        downloaded = 0
        filesize = int(r.headers['content-length'])
        for chunk in r.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)
            # print(downloaded/filesize)
        buffer.seek(0)
        i = Image.open(io.BytesIO(buffer.read()))
        i.save(os.path.join(out_dir, 'image.jpg'), quality=85)
    buffer.close()

    # file downloaded and ready , start conversion 

    # Creates a transparent canvas to paste the jpg into 
    canvas = Image.new('RGBA', (256, 256), color = (0,0,0,0))
    canvas.save(folder[1]+'\canvas.png')
    # convert the jpg into a png 

    for infile in glob.glob(folder[1]+"\image.jpg"):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        imr = im.resize((180, 256))
    # necessary file conversion to png ?
        imr.save(folder[1]+"\image.png",format="png")
        print(f'Converted {ext} to PNG with size {imr.size} and \nmetadata : {imr.info}')

    # image on canvas pasting 
    image = Image.open(folder[1]+'\image.png')
    canvas.paste(image,(38,0))
    canvas.save(folder[1]+'\poster.png')

    for infile in glob.glob(folder[1]+"\poster.png"):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        sizes=[(256, 256)]
        im.save(folder[1]+'\\an.ico',format="ICO",sizes=sizes)
        print(f'Converted {ext} with size {im.size} and \nmetadata : {im.info} to ico ')
        print('Resizing ')
    try:
        f = open(folder[1]+"\desktop.ini", "x")
        f.write("[.ShellClassInfo]\nIconResource=an.ico,0 ")
        f.close()

    except(FileExistsError):
        print('file already exists ')
        
    junk_files = ["canvas.png","image.jpg","image.png","poster.png"]
    for file in junk_files:
        if os.path.exists(folder[1]+f'\{file}'):
            os.remove(folder[1]+f'\{file}')
        else:
            print("The file does not exist") 