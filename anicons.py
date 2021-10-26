"""
Anicons.py
    Makes your folders more pleasing to look at
"""
import time
import logging
import os
import re

from pathlib import Path
from animods.misc import c
from animods.fs import (
    generate_lock_file,
    alter_attributes,
    count_filetypes)
from animods.api import (
    get_episode_names_for_anime,
    get_data_for_id,
    get_predictions_for_folder_name)
from animods.img import (
    create_config,
    create_ico,
    download_poster)

logging.basicConfig(level=logging.WARNING)
main_path = input('Set root Folder path Example ./anime :')


def cls_in(delay=0, keep=''):
    """Clears the term screen ( windows only for now )"""
    time.sleep(delay)
    os.system('cls')
    print(keep)


def merge(dict1, dict2):
    """Merges two dicts """
    res = {**dict1, **dict2}
    return res


def get_size(start_path='.'):
    """Gets size of a path """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        logging.debug(dirnames)
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # skip if it is symbolic link
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
    return total_size


def get_lock(path):
    ''' Reads a lockfile and returns data '''
    print(f'{c.bold}{c.black} READ : lockfile {c.o}')
    with open(Path.joinpath(path, 'Ξ.lock'), 'r', encoding='utf-8') as lock_file:
        lock_file_data = lock_file.read()
        lock_file.close()
        # wrap the file data in an eval()
        # to make it pythonable
        lock_file_data = eval(lock_file_data)  # pylint: disable =eval-used
        # Return data
        return lock_file_data


def sanitize(dirty=''):
    """Sanitizes filenames to avoid windows error"""
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
    print(f'{c.b_black}{c.bold} _initialize_lockfile {path}{c.o}')
    generate_lock_file(path, {})
    lock_file = get_lock(path)
    lock_file["is_skipped"] = False
    lock_file["is_verified"] = False
    lock_file["is_spliced"] = False
    lock_file["folder_rename_skip"] = False
    lock_file["episode_rename_skip"] = False
    lock_file["has_episode_data"] = False
    lock_file["has_folder_data"] = False
    lock_file["has_anime_data"] = False
    lock_file["has_file_data"] = False
    lock_file["has_prediction"] = False
    lock_file["has_icon"] = False

    generate_lock_file(path, lock_file)


def _generate_folder_data(path):
    ''' Generates the following data if has_folder_data is false
        ATTRIBUTES :
        folder_name : current folder name
        folder_size_MB : folder size in megabytes
        folder_size_GB : folder size in gigabytes
        folder_contents : enumeration of files within the folder
    '''
    print(f'{c.b_black}{c.bold} _generate_folder_data {path}{c.o}')
    lock_file = get_lock(path)
    if not lock_file['has_folder_data']:
        # Get data
        lock_file['folder_name'] = path.name
        lock_file['folder_size_MB'] = round((get_size(path)/1024)/1024, 2)
        lock_file['folder_size_GB'] = round(
            ((get_size(path)/1024)/1024)/1024, 2)
        # Count up the files and their types
        # Bundle it up into a dict and add it to the lock data
        file_enumeration = count_filetypes(path)
        folder_contents = {}
        for filetype in file_enumeration:
            folder_contents[filetype] = file_enumeration[filetype]
        lock_file['folder_contents'] = folder_contents
        # Set the has file data to true to avoid refetch
        lock_file['has_folder_data'] = True
        # cement changes
        generate_lock_file(path, lock_file)
    else:
        print(f'{c.bold}{c.b_black}Folder data already exists. {c.o}')


def _generate_predictions(path):
    ''' Generates predictions from the folder name if has_episode_data is false
    fetches 5 predictions from the jikan.moe api and
    lets the user choose the correct one
        ATTRIBUTES:
        is_verified : boolean
        predictions : list containing data
    leads to episode data generation
    '''
    print(f'{c.b_black}{c.bold} _generate_predictions {path}{c.o}')

    lock_file = get_lock(path)

    if not lock_file['has_file_data']:
        # Get data
        try:
            lock_file['predictions'] = get_predictions_for_folder_name(
                path.name)
            print(f"{c.bold}{c.red}{lock_file['predictions']}{c.o}")
            # avoid refresh
            lock_file["has_prediction"] = True
            # cement changes
            generate_lock_file(path, lock_file)
        except ConnectionResetError as error:
            print(error)


def _prompt_verification(path):
    '''Prompts user to verify the prediction
    Uses is_verified from the initialization to
    prompt the user for verification
    '''
    print(f'{c.b_black}{c.bold} _prompt_verification {path}{c.o}')
    # Load data
    lock_file = get_lock(path)
    predictions = lock_file['predictions']
    # Render prompt
    print(
        f'\n{c.b_black} ───────────────────────────────────────────────────── {c.o}')
    print(f'{c.b_purple}    Choose the correct prediction for the folder : {c.o}\n')
    print(f'{c.white} {lock_file["folder_name"]} {c.o}')
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
            lock_file['is_verified'] = True
            correct_prediction = None
            # Get the correct predicion
            # Unless skipped
            if int(choice) == 0:
                lock_file['is_skipped'] = True
            else:
                correct_prediction = predictions[int(choice)-1]
            # Get the correct predicion data
            lock_file['correct_prediction'] = correct_prediction
            # remove the predicions as now we are sure
            lock_file.pop('predictions')
            generate_lock_file(path, lock_file)
    else:
        print('Please choose from [ 0 - 5 ]')


def _generate_anime_data(path):
    """Generates anime data"""
    print(f'{c.b_black}{c.bold} _generate_anime_data {path}{c.o}')

    lock_file = get_lock(path)
    # logic after lock data is available
    mal_id = lock_file['correct_prediction'][1]

    print(f'{c.purple}[Gen] Fetching Anime data for {mal_id}{c.o}')

    api_data = get_data_for_id(mal_id)
    lock_file['anime_data'] = api_data
    # set has anime data to true
    lock_file["has_anime_data"] = True
    generate_lock_file(path, lock_file)


def _generate_episode_data(path):
    """Generates episode data"""
    print(f'{c.b_black}{c.bold} _generate_episode_data {path}{c.o}')

    lock_file = get_lock(path)
    mal_id = lock_file['correct_prediction'][1]

    print(f'{c.purple}[Gen] Fetching Episode data for {mal_id}{c.o}')

    ep_data = get_episode_names_for_anime(mal_id)
    lock_file['episode_names'] = ep_data
    # set has episode data to true
    lock_file["has_episode_data"] = True
    generate_lock_file(path, lock_file)


def _generate_file_data(path):
    '''Sets media_data and predicted ep num and current filename'''
    print(f'{c.b_black}{c.bold} _generate_file_data {path}{c.o}')
    lock_file = get_lock(path)
    folder_contents = lock_file['folder_contents']
    supported_media_types = ['.mp4', '.mkv', '.flv', '.webm']

    for item in folder_contents:
        if item in supported_media_types:
            i = 0
            file_data_container = []
            # globbs for each filetype
            for fileglob in path.rglob(f"*{item}"):
                file_data = {}
                file_data['current_filename'] = fileglob.name
                pep_num = re.findall(r'\b\d+\b', fileglob.name)
                file_data['predicted_ep_num'] = pep_num
                # media = get_file_data(str(Path.joinpath(Path.cwd(),item)))
                # for item in media:
                #     if item != 'video_quality':
                #         file_data[item] = len(item[0])
                #     else:
                #         file_data['video_quality'] = media[item]
                # file_data_container.append(file_data)
                i += 1

            lock_file['file_data'] = file_data_container
            lock_file["has_file_data"] = True
            generate_lock_file(path, lock_file)
            print(f'{c.blue}{file_data}{c.o}')


def _splice_local_and_api(path):
    '''Splices local and anime data , needs
    has anime data and has file data to be set
    sets spliced_data'''
    print(f'{c.b_black}{c.bold} _splice_local_and_api {path}{c.o}')
    lock_file = get_lock(path)
    if lock_file['has_file_data'] and lock_file['has_episode_data']:

        api_episodes = lock_file['episode_names']
        local_episodes = lock_file['file_data']

        episodes = {}
        print(f'{c.blue}{api_episodes}{c.o}')
        print(f'{c.yellow}{local_episodes}{c.o}')

        def check_delta(lock_file):
            data = lock_file['file_data']

            for episode in data:
                prediction_data = []
                # if prediction failed pass the ep
                if episode['predicted_ep_num'] == []:
                    print(
                        f'{c.red}Predicting episode names has failed {c.o}\n{c.yellow} \n'
                        'try renaming with episode numbers with spaces around \n'
                        ' that is : Ep 02 , instead of ep_02 or E02 \n'
                        ' or remove numbers that are not episode numbers , \n'
                        f' that is : 2020 , 720 1080 , it confuses the app. {c.o}')

                else:
                    prediction = episode['predicted_ep_num']
                # if api episodes non null
                if lock_file['episode_names'] != {}:
                    try:
                        prediction_data = lock_file['episode_names'][int(
                            prediction[0])]
                        prediction_data['original'] = episode
                        episodes[prediction[0]] = prediction_data
                        print(
                            f'\n{c.yellow}{prediction}{c.orange}{prediction_data}{c.o}\n')
                    except Exception:  # pylint: disable=broad-except
                        pass
                else:
                    print(
                        f'{c.red}Could not find Episode data from the internet {c.o}\n')
        check_delta(lock_file)
        lock_file['spliced_data'] = episodes
        lock_file['is_spliced'] = True
        generate_lock_file(path, lock_file)

    else:
        print(f'{c.red}{c.bold} Episode / File data not fetched{c.o}')
    time.sleep(4)

#  Features ------------------------------------


def rename_folder(path):
    """Renames a folder"""
    lock_file = get_lock(path)
    folder_name = lock_file['folder_name']
    title = lock_file['anime_data']['title_english']
    if title is None:
        title = lock_file['anime_data']['title']
    title = sanitize(title)
    abs_path = Path.absolute(path)
    print(abs_path.parent)
    napath = Path.joinpath(abs_path.parent, title)
    print(napath)
    # ask if they want to rename the folder
    if folder_name == title or lock_file['folder_rename_skip']:
        pass
    else:
        choice = input(
            f'Rename \n{c.yellow}{folder_name}{c.o} to \n{c.green}{title}{c.o}\n? (y/n)')
        if choice in ("y", "Y"):
            print('Renaming ...')
            os.rename(abs_path, napath)
            lock_file['folder_name'] = napath.name
        else:
            lock_file['folder_rename_skip'] = True
    generate_lock_file(napath, lock_file)


def rename_episodes(path):
    """Renames episodes"""
    lock_file = get_lock(path)

    for item in lock_file['spliced_data']:
        original_name = lock_file['spliced_data'][item]['original']['current_filename']
        recomended_name = lock_file['spliced_data'][item]['title']

        on_path = Path.joinpath(path, original_name)
        ext = on_path.suffix
        new_filename = f'EP {item} - {recomended_name}{ext}'
        new_filename = sanitize(new_filename)
        rn_path = Path.joinpath(path, new_filename)

        print(on_path)
        print(rn_path)
        print(not rn_path.exists())
        if not rn_path.exists() and not lock_file['episode_rename_skip']:
            choice = input(
                f"{c.blue}Rename Episode ? : \n"
                f"{c.yellow}{original_name} -> {c.green}EP {item} - {recomended_name} {ext}\n"
                f" [y/n]{c.o}")
            if choice in ("y", "Y"):

                print('Renaming ... ')
                os.rename(on_path, rn_path)

                lock_file['episodes_renamed'] = True
            else:
                lock_file['episode_rename_skip'] = True
    generate_lock_file(path, lock_file)


def iconify(path):
    """Creates icons """
    lock_file = get_lock(path)
    cover = lock_file['anime_data']['image_url']
    if not lock_file['has_icon']:

        download_poster(cover, path)
        create_ico(path, path)
        create_config(path)
        alter_attributes(Path.joinpath(path, 'desktop.ini'), '+H')
        alter_attributes(Path.joinpath(path, 'image.jpg'), '+H')
        alter_attributes(path, '+R')
        lock_file['has_icon'] = True
    else:
        print('skipping icon creation because already exists')


def main():
    """Main Execution"""
    for node in Path(main_path).rglob('*'):
        print(f'{c.b_black} Going through : {main_path}{c.o}')
        print(f'{c.b_black} Currently on  : {node}{c.o}')
        if node.is_dir():
            if Path.joinpath(node, 'Ξ.lock').exists():
                # We have a folder with a lock file
                print(f'{c.green} Found a lockfile {c.o}')
                data = None
                with open(
                    Path.joinpath(node, 'Ξ.lock'),
                    'r',
                        encoding='utf-8') as l_file:
                    data = l_file.read()
                    l_file.close()
                    data = eval(data)  # pylint: disable=eval-used

                if not data['has_folder_data']:
                    _generate_folder_data(node)
                # must have folder data to be predictable
                if not data['has_prediction']:
                    _generate_predictions(node)
                # must have predictions to be verifiable
                if not data['is_verified']:
                    _prompt_verification(node)

                if not data['has_episode_data']:
                    _generate_episode_data(node)

                if not data['has_anime_data']:
                    _generate_anime_data(node)

                if not data['has_file_data']:
                    _generate_file_data(node)

                if not data['is_spliced']:
                    _splice_local_and_api(node)

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
