# pylint: disable:F0001
import json
import time
import requests
from pprint import pprint
from jikanpy import Jikan
ji = Jikan()
from animods.misc import *
import tempfile

def anime_fetch_to_json(anime, limit):
    data = ji.search(search_type='anime', query=anime,
                     parameters={'limit': limit})
    print(data)
    file = open(f'{anime}.json', 'w')
    json.dump(data, file)
    file.close()



def get_episode_names_for_anime(mal_id):
    print(f'{c.purple}  [Api] Fetch Episode names for : {mal_id}{c.o}')
    response_body = requests.get(
        f'https://api.jikan.moe/v3/anime/{mal_id}/episodes')
    response_body = response_body.content.decode('utf-8')
    # pprint(type(response_body))
    # pprint(response_body)
    evald = json.loads(response_body)
    episodes = evald['episodes']
    ep_names = {}
    for ep in episodes:
        ep_num = ep['episode_id']
        ep_data = {}
        ep_data['title'] = ep['title']
        ep_data['title_rom'] = ep['title_romanji']
        ep_data['filler'] = ep['filler']
        ep_data['recap'] = ep['recap']
        
        ep_names[ep_num] = ep_data
        # ep_names.append(ep['title'])
    return ep_names

def get_data_for_id(mal_id):
    print(f'{c.purple}  [Api] Fetch Anime Data for : {mal_id}{c.o}')
    endpoint_string = f'https://api.jikan.moe/v3/anime/{str(mal_id)}'
    response_body = requests.get(endpoint_string)
    # print(endpoint_string)
    # print(response_body.status_code)
    if response_body.status_code != 200:
        print(f'{c.red} Server returned a : {response_body.status_code}{c.o}')
        return False
    else : 
        response_body = response_body.content.decode('utf-8')

        # pprint(type(response_body))
        # pprint(response_body)

        result = json.loads(response_body)
        data = {}
        # pprint(result)
        
        data['title'] = result['title']
        data['mal_id'] = result['mal_id']
        data['episodes'] = result['episodes']
        data['status'] = result['status']
        data['airing'] = result['airing']
        data['title_english'] = result['title_english']
        data['title_japanese'] = result['title_japanese']
        data['aired'] = result['aired']['string']
        data['rating'] = result['rating']
        data['premiered'] = result['premiered']
        data['favorites'] = result['favorites']
        data['score'] = result['score']
        data['scored_by'] = result['scored_by']
        data['type'] = result['type']
        data['image_url'] = result['image_url']
        
        genre_list = []
        for genre in result['genres']:
            genre_list.append(genre['name'])
        data['genres'] = genre_list
        
        licensors_list = []
        for licensor in result['licensors']:
            licensors_list.append(licensor['name'])
        data['licensors'] = licensors_list
            
        producers_list = []
        for producer in result['producers']:
            producers_list.append(producer['name'])
        data['producers'] = producers_list
        
        studios_list = []
        for studio in result['studios']:
            studios_list.append(studio['name'])
        data['studios'] = studios_list
        

        # pprint(data)
        return data

def get_predictions_for_folder_name(folder_name):
    # Todo: handle 404 pages 
    resp = ji.search('anime', folder_name, parameters={'limit': 5})
    results_list = []
    for result in resp['results']:
        results_list.append((result['title'],result['mal_id'],result['synopsis']))
    return results_list
    
