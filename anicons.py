import time
import PIL
import os
import re
from pathlib import Path
from animods.misc import *
from animods.fs import *
from animods.api import *
from animods.img import *

main_path = input('Set root Folder path Example ./anime :')


def cls_in(delay=0, keep=''):
    time.sleep(delay)
    os.system('cls')
    print(keep)


def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def get_lock(path):
    ''' Reads a lockfile and returns data '''
    print(f'{c.bold}{c.black} READ : lockfile {c.o}')
    lock_file = open(Path.joinpath(path, 'Ξ.lock'), 'r', encoding='utf-8')
    lock_file_data = lock_file.read()
    lock_file.close()
    # wrap the file data in an eval()
    # to make it pythonable
    lock_file_data = eval(lock_file_data)
    # Return data
    return lock_file_data


def sanitize(dirty=''):
    # / \ : * ? > < |
    dirty = dirty.replace('/', '')
    dirty = dirty.replace('\\', '')
    dirty = dirty.replace(':', ' ')
    dirty = dirty.replace('*', '')
    dirty = dirty.replace('?', '')
    dirty = dirty.replace('>', '')
    dirty = dirty.replace('<', '')
    dirty = dirty.replace('|', ' ')
    clean = dirty
    return clean


# lockfile dependant methods ---------------------------

def _initialize_lockfile(path):
    print(f'{c.b_black}{c.bold} _initialize_lockfile {path}{c.o}')
    ''' initializes a lockfile and sets constructor attributes :
        ATTRIBUTES :
        is_skipped : for skipped folders 
        is_verified : for verified folders 
        is_spliced : for splicing
        folder_rename_skip : for those who dont want to rename 
        episode_rename_skip : for those who dont want to rename 
        has_episode_data : if episode data is present and non null 
        has_folder_data : if folder data generated 
        has_anime_data : if folder data generated 
        has_file_data : if file data generated for episodes
        has_prediction : boolean
    '''
    generate_lock_file(path, {})
    lfd = get_lock(path)
    lfd["is_skipped"] = False
    lfd["is_verified"] = False
    lfd["is_spliced"] = False
    lfd["folder_rename_skip"] = False
    lfd["episode_rename_skip"] = False
    lfd["has_episode_data"] = False
    lfd["has_folder_data"] = False
    lfd["has_anime_data"] = False
    lfd["has_file_data"] = False
    lfd["has_prediction"] = False
    lfd["has_icon"] = False

    generate_lock_file(path, lfd)


def _generate_folder_data(path):
    print(f'{c.b_black}{c.bold} _generate_folder_data {path}{c.o}')
    ''' Generates the following data if has_folder_data is false
        ATTRIBUTES : 
        folder_name : current folder name 
        folder_size_MB : folder size in megabytes 
        folder_size_GB : folder size in gigabytes 
        folder_contents : enumeration of files within the folder
    '''
    lfd = get_lock(path)
    if lfd['has_folder_data'] == False:
        # Get data
        lfd['folder_name'] = path.name
        lfd['folder_size_MB'] = round((get_size(path)/1024)/1024, 2)
        lfd['folder_size_GB'] = round(((get_size(path)/1024)/1024)/1024, 2)
        # Count up the files and their types
        # Bundle it up into a dict and add it to the lock data
        file_enumeration = count_filetypes(path)
        folder_contents = {}
        for filetype in file_enumeration:
            folder_contents[filetype] = file_enumeration[filetype]
        lfd['folder_contents'] = folder_contents
        # Set the has file data to true to avoid refetch
        lfd['has_folder_data'] = True
        # cement changes
        generate_lock_file(path, lfd)
    else:
        print(f'{c.bold}{c.b_black}Folder data already exists. {c.o}')


def _generate_predictions(path):
    print(f'{c.b_black}{c.bold} _generate_predictions {path}{c.o}')
    ''' Generates predictions from the folder name if has_episode_data is false
    fetches 5 predictions from the jikan.moe api and 
    lets the user choose the correct one 
        ATTRIBUTES:
        is_verified : boolean
        predictions : list containing data 
    leads to episode data generation 
    '''

    lfd = get_lock(path)

    if lfd['has_file_data'] == False:
        # Get data
        try:
            lfd['predictions'] = get_predictions_for_folder_name(path.name)
            print(f"{c.bold}{c.red}{lfd['predictions']}{c.o}")
            # avoid refresh
            lfd["has_prediction"] = True
            # cement changes
            generate_lock_file(path, lfd)
        except ConnectionResetError as e:
            print(e)

    pass


def _prompt_verification(path):
    print(f'{c.b_black}{c.bold} _prompt_verification {path}{c.o}')
    '''Prompts user to verify the prediction 
    Uses is_verified from the initialization to
    prompt the user for verification
    '''
    # Load data
    lfd = get_lock(path)
    predictions = lfd['predictions']
    # Render prompt
    print(
        f'\n{c.b_black} ───────────────────────────────────────────────────── {c.o}')
    print(f'{c.b_purple}    Choose the correct prediction for the folder : {c.o}\n')
    print(f'{c.white} {lfd["folder_name"]} {c.o}')
    print(
        f'\n{c.b_black} ───────────────────────────────────────────────────── {c.o}\n')
    print(f'\n{c.purple} [0] : Skip{c.o}\n')
    i = 1
    for prediction in predictions:
        print(f'{c.green} [{i}] : {prediction[0]} {c.o}')
        print(f'{c.b_black} {prediction[2]} {c.o}')
        i = i + 1
    print(f'{c.b_black} ───────────────────────────────────────────────────── {c.o}\n')
    choice = input('Choice [ 0 - 5 ]:')
    # Do post-validation
    if choice.isnumeric():  # it the choice is numeric
        if int(choice) <= 5 and int(choice) >= 0:  # its between 0 and 5 incl.
            # set verified as true to avoid re verification
            lfd['is_verified'] = True
            correct_prediction = None
            # Get the correct predicion
            # Unless skipped
            if int(choice) == 0:
                lfd['is_skipped'] = True
                pass
            else:
                correct_prediction = predictions[int(choice)-1]
            # Get the correct predicion data
            lfd['correct_prediction'] = correct_prediction
            # remove the predicions as now we are sure
            lfd.pop('predictions')
            generate_lock_file(path, lfd)
    else:
        print(f'Please choose from [ 0 - 5 ]')


def _generate_anime_data(path):
    print(f'{c.b_black}{c.bold} _generate_anime_data {path}{c.o}')
    ''''''
    lfd = get_lock(path)
    # logic after lock data is available
    mal_id = lfd['correct_prediction'][1]

    print(f'{c.purple}[Gen] Fetching Anime data for {mal_id}{c.o}')

    api_data = get_data_for_id(mal_id)
    lfd['anime_data'] = api_data
    # set has anime data to true
    lfd["has_anime_data"] = True
    generate_lock_file(path, lfd)


def _generate_episode_data(path):
    print(f'{c.b_black}{c.bold} _generate_episode_data {path}{c.o}')
    ''''''
    lfd = get_lock(path)
    mal_id = lfd['correct_prediction'][1]

    print(f'{c.purple}[Gen] Fetching Episode data for {mal_id}{c.o}')

    ep_data = get_episode_names_for_anime(mal_id)
    lfd['episode_names'] = ep_data
    # set has episode data to true
    lfd["has_episode_data"] = True
    generate_lock_file(path, lfd)


def _generate_file_data(path):
    print(f'{c.b_black}{c.bold} _generate_file_data {path}{c.o}')
    '''sets media_data and predicted ep num and current filename'''
    lfd = get_lock(path)
    folder_contents = lfd['folder_contents']
    supported_media_types = ['.mp4', '.mkv', '.flv', '.webm']

    for item in folder_contents:
        if item in supported_media_types:
            i = 0
            file_data_container = []
            for item in path.rglob(f"*{item}"):
                file_data = {}
                file_data['current_filename'] = item.name
                pep_num = re.findall(r'\b\d+\b', item.name)
                file_data['predicted_ep_num'] = pep_num
                # media = get_file_data(str(Path.joinpath(Path.cwd(),item)))
                # for item in media:
                #     if item != 'video_quality':
                #         file_data[item] = len(item[0])
                #     else:
                #         file_data['video_quality'] = media[item]
                # file_data_container.append(file_data)
                i += 1

            lfd['file_data'] = file_data_container
            lfd["has_file_data"] = True
            generate_lock_file(path, lfd)
            print(f'{c.blue}{file_data}{c.o}')


def _splice_local_and_api(path):
    print(f'{c.b_black}{c.bold} _splice_local_and_api {path}{c.o}')
    '''Splices local and anime data , needs 
    has anime data and has file data to be set
    sets spliced_data'''
    lfd = get_lock(path)
    if lfd['has_file_data'] and lfd['has_episode_data']:

        api_episodes = lfd['episode_names']
        local_episodes = lfd['file_data']

        episodes = {}
        print(f'{c.blue}{api_episodes}{c.o}')
        print(f'{c.yellow}{local_episodes}{c.o}')

        def check_delta(lfd):
            data = lfd['file_data']
            delta = []
            for ep in data:
                prediction_data = []
                # if prediction failed pass the ep
                if ep['predicted_ep_num'] == []:
                    print(f'{c.red}Predicting episode names has failed {c.o}\n{c.yellow} try renaming with episode numbers with spaces around \n that is : Ep 02 , instead of ep_02 or E02 \n or remove numbers that are not episode numbers , \n that is : 2020 , 720 1080 , it confuses the app {c.o}')

                else:
                    prediction = ep['predicted_ep_num']
                # if api episodes non null
                if lfd['episode_names'] != {}:
                    try:
                        prediction_data = lfd['episode_names'][int(
                            prediction[0])]
                        prediction_data['original'] = ep
                        episodes[prediction[0]] = prediction_data
                        print(
                            f'\n{c.yellow}{prediction}{c.orange}{prediction_data}{c.o}\n')
                    except:
                        pass
                else:
                    print(
                        f'{c.red}Could not find Episode data from the internet {c.o}\n')
                    # TODO: add dupe checking
                # print(f'\n{c.red}{delta}{c.o}\n')
        check_delta(lfd)

        lfd['spliced_data'] = episodes
        lfd['is_spliced'] = True
        generate_lock_file(path, lfd)

    else:
        print(f'{c.red}{c.bold} Episode / File data not fetched{c.o}')
    time.sleep(4)

#  Features ------------------------------------


def rename_folder(path):
    lfd = get_lock(path)
    fn = lfd['folder_name']
    t = lfd['anime_data']['title_english']
    if t == None:
        t = lfd['anime_data']['title']
    t = sanitize(t)
    apath = Path.absolute(path)
    print(apath.parent)
    napath = Path.joinpath(apath.parent, t)
    print(napath)
    # do stuff
    # ask if they want to rename the folder
    if fn == t or lfd['folder_rename_skip'] == True:
        pass
    else:
        choice = input(
            f'Rename \n{c.yellow}{fn}{c.o} to \n{c.green}{t}{c.o}\n? (y/n)')
        if choice == 'y' or choice == 'Y':
            print(f'Renaming ...')
            os.rename(apath, napath)
            lfd['folder_name'] = napath.name
        else:
            lfd['folder_rename_skip'] = True
    generate_lock_file(napath, lfd)


def rename_episodes(path):
    lfd = get_lock(path)

    for item in lfd['spliced_data']:
        original_name = lfd['spliced_data'][item]['original']['current_filename']
        recomended_name = lfd['spliced_data'][item]['title']

        on_path = Path.joinpath(path, original_name)
        ext = on_path.suffix
        new_filename = f'EP {item} - {recomended_name}{ext}'
        new_filename = sanitize(new_filename)
        rn_path = Path.joinpath(path, new_filename)

        print(on_path)
        print(rn_path)
        print(not rn_path.exists())
        if not rn_path.exists() and not lfd['episode_rename_skip']:
            choice = input(
                f"{c.blue}Rename Episode ? : {c.yellow}{original_name} -> {c.green}EP {item} - {recomended_name} {ext}{c.o} [y/n]")
            if choice == 'y' or choice == 'Y':

                print(f'Renaming ... ')
                os.rename(on_path, rn_path)

                lfd['episodes_renamed'] = True
            else:
                lfd['episode_rename_skip'] = True
    generate_lock_file(path, lfd)

    pass


def iconify(path):
    lfd = get_lock(path)
    cover = lfd['anime_data']['image_url']
    if lfd['has_icon'] == False:

        download_poster(cover, path)
        create_ico(path, path)
        create_config(path)
        alter_attributes(Path.joinpath(path, 'desktop.ini'), '+H')
        alter_attributes(Path.joinpath(path, 'image.jpg'), '+H')
        alter_attributes(path, '+R')
        lfd['has_icon'] = True
    else:
        print('skipping icon creation because already exists')


def main():
    for node in Path(main_path).rglob('*'):
        print(f'{c.b_black} Going through : {main_path}{c.o}')
        print(f'{c.b_black} Currently on  : {node}{c.o}')
        if node.is_dir():
            if Path.joinpath(node, 'Ξ.lock').exists():
                # We have a folder with a lock file
                print(f'{c.green} Found a lockfile {c.o}')

                l_file = open(Path.joinpath(node, 'Ξ.lock'),
                              'r', encoding='utf-8')
                data = l_file.read()
                l_file.close()
                data = eval(data)

                if data['has_folder_data'] == False:
                    _generate_folder_data(node)
                else:
                    print(
                        f'{c.green}[Lock file] folder data already fetched. {c.o}\n')

                # must have folder data to be predictable
                if data['has_prediction'] == False:
                    _generate_predictions(node)
                else:
                    print(
                        f'{c.green}[Lock file] predictions already fetched. {c.o}\n')

                # must have predictions to be verifiable
                if data['is_verified'] == False:
                    _prompt_verification(node)
                else:
                    print(f'{c.green}[Lock file]  already Verified . {c.o}\n')

                if data['has_episode_data'] == False:
                    _generate_episode_data(node)
                else:
                    print(
                        f'{c.green}[Lock file] episode data already fetched. {c.o}\n')

                if data['has_anime_data'] == False:
                    _generate_anime_data(node)
                else:
                    print(
                        f'{c.green}[Lock file] anime data already fetched. {c.o}\n')

                if data['has_file_data'] == False:
                    _generate_file_data(node)
                else:
                    print(
                        f'{c.green}[Lock file]  file data already fetched. {c.o}\n')

                if data['is_spliced'] == False:
                    _splice_local_and_api(node)
                else:
                    print(f'{c.green}[Lock file]  already spliced. {c.o}\n')

                rename_episodes(node)
                iconify(node)
                rename_folder(node)
            else:
                _initialize_lockfile(node)
                _generate_folder_data(node)
                _generate_predictions(node)
                _prompt_verification(node)
                _generate_anime_data(node)
                _generate_episode_data(node)
                _generate_file_data(node)
                _splice_local_and_api(node)

                rename_episodes(node)
                iconify(node)
                rename_folder(node)

    print(f"\n{c.purple}Finished ... Exiting in 10{c.o}")
    time.sleep(10)


if __name__ == '__main__':
    main()


# def splice_ep_namepredicions_with_data(path):
#     lock_file = open(Path.joinpath(path,'ani.lock'), 'r',encoding='utf-8')
#     lock_file_data = lock_file.read()
#     lock_file.close()
#     # wrap the file data in an eval()
#     #  to make it pythonable
#     lock_file_data = eval(lock_file_data)
#     # logic after lock data is available

#     generate_lock_file(path,new_data)

#     pass


# class anicons:
#     def __init__ (self) :
#         os.system('cls')
#         print('-------------------------------------#')
#         self.cwd = Path.cwd()
#         self.home = Path.home()
#         print('CWD:',self.cwd)
#         print('HOME:',self.home)

#     def gen_struct(self):
#         for p in Path(self.cwd).rglob('*'):
#             if p.is_dir() :
#                 print(f"[D] {p}")
#                 # time.sleep(0.1)
#             elif p.is_file():
#                 # print(f"[F]{p.suffix}]\t{p.parent}\{p.name}")
#                 # print(f"[F][{p}")
#                 # time.sleep(0.1)
#                 if p.suffix == '.mkv' or p.suffix == '.mp4':
#                     try:
#                         probe_data = get_probe(str(p))
#                         # save_probe(str(p))
#                         # pprint(probe_data['streams'])
#                         os.system('cls')
#                     #
#                         print(f'\n{c.green}-------  File Data  ----------------------------{c.o}')
#                     #
#                         print(f"{c.b_black}Name : {c.o}",p.name)
#                         print(f'{c.purple}Duration :{c.o}',round(float(probe_data['format']['duration'])/60,2),'Minute(s)')
#                         print(f"{c.purple}Filesize :{c.o}",round(float(probe_data['format']['size'])/1024/1024,2),"Mb")
#                         print(f"{c.purple}Creation time :{c.o}",probe_data['format']['tags']['creation_time'].split('T')[0])

#                     #
#                         print(f'\n{c.green}-------  Streams ( {probe_data["format"]["nb_streams"]} ) --------------{c.o}')
#                     #

#                         for stream in probe_data['streams']:

#                             codec_type = stream['codec_type'].capitalize()
#                             # codec_name = stream['codec_name']
#                             codec_long_name = stream['codec_long_name']
#                             print(f'{c.b_purple}{codec_type} | {c.blue}{codec_long_name}{c.o}')
#                             #
#                             if codec_type == 'Video':
#                                 print(f"{c.green} Quality :{c.o}",stream['height'],'P')
#                                 print(f"{c.b_black} Aspect Ratio :{c.o}",stream['display_aspect_ratio'])
#                                 print(f"{c.b_black} Dimensions :{c.o}",stream['width'],'x',stream['height'])
#                             if codec_type == 'Audio':

#                                 print(f"{c.green} Language :{c.o}",stream['tags']['language'].capitalize())
#                                 print(f"{c.b_black} Channels :{c.o}",stream['channels'])
#                                 print(f"{c.b_black} Layout :{c.o}",stream['channel_layout'])

#                             if codec_type == 'Subtitle':

#                                 print(f"{c.green} Language :{c.o}",stream['tags']['language'].capitalize(),stream['tags']['title'])
#                                 print(f"{c.b_black} Size :{c.o}",round(float(stream['tags']['NUMBER_OF_BYTES'])/1024),'Kbs')


#                     except KeyError as e :
#                         print(f"{c.red} {e} {c.o}")
#                         if e != 'title':
#                             pass
#                         elif e != 'NUMBER_OF_BYTES':
#                             pass
#                         else :
#                             print(f"{c.b_black} {stream} {c.o}")
#                             time.sleep(20)
#                     time.sleep(0.03)

# ani = anicons()
# for node in get_structure('./'):
#     print(f'{c.green}{check_if_path_is_dir(node)}{c.o}')
#     print(f'{c.blue}{check_if_path_is_file(node)}{c.o}')
#     print(f'{c.b_black}{node}{c.o}')
