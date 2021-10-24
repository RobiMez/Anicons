import ffmpeg
import json
from animods.misc import c



def get_probe(path):
    probe = ffmpeg.probe(path)
    return probe

def save_probe_to_json(path):
    probe = ffmpeg.probe(path)
    file = open(f'{path}.json','w')
    json.dump(probe,file)
    file.close()

def get_file_data(path):
    filedata = {}

    video_streams = []
    video_quality = []
    audio_streams = []
    subtitle_streams = []
    attachment_streams = []
    try:
        fp = ffmpeg.probe(path)
        for stream in fp["streams"]:
            if stream['codec_type'] == "video":
                video_streams.append(stream)
                video_quality.append(stream['height'])
            elif stream['codec_type'] == "audio":
                audio_streams.append(stream)
            elif stream['codec_type'] == "subtitle":
                subtitle_streams.append(stream)
            elif stream['codec_type'] == "attachment":
                attachment_streams.append(stream)
            else:
                pass
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'
    
    filedata['video_streams'] = video_streams
    filedata['video_quality'] = video_quality
    filedata['audio_streams'] = audio_streams
    filedata['subtitle_streams'] = subtitle_streams
    filedata['attachment_streams'] = attachment_streams
    return filedata
    




def get_num_streams_from_filepath (fpath):
    fp = ffmpeg.probe(fpath)
    return fp["format"]["nb_streams"]

def get_streams_from_filepath (fpath):
    fp = ffmpeg.probe(fpath)
    return fp["streams"]

def get_video_qual_from_filepath (fpath):
    print(f'{c.purple}Probing {fpath}{c.o}')
    fp = None
    vstreams = []
    try:
        fp = ffmpeg.probe(fpath)
        for stream in fp["streams"]:
            if stream['codec_type'] == "video":
                vstreams.append(stream['height'])
        return vstreams
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'
def get_video_streams_from_filepath (fpath):
    print(f'{c.purple}Probing {fpath}{c.o}')
    fp = None
    vstreams = []
    try:
        fp = ffmpeg.probe(fpath)
        for stream in fp["streams"]:
            if stream['codec_type'] == "video":
                vstreams.append(stream)
        return vstreams
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'

def get_audio_streams_from_filepath (fpath):
    print(f'{c.purple}Probing {fpath}{c.o}')
    fp = None
    astreams = []
    try:
        fp = ffmpeg.probe(fpath)
        for stream in fp["streams"]:
            if stream['codec_type'] == "audio":
                astreams.append(stream)
        return astreams
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'

def get_subtitle_streams_from_filepath (fpath):
    print(f'{c.purple}Probing {fpath}{c.o}')
    fp = None
    sstreams = []
    try:
        fp = ffmpeg.probe(fpath)
        for stream in fp["streams"]:
            if stream['codec_type'] == "subtitle":
                sstreams.append(stream)
        return sstreams
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'

def get_attachment_streams_from_filepath (fpath):
    print(f'{c.purple}Probing {fpath}{c.o}')
    fp = None
    astreams = []
    try:
        fp = ffmpeg.probe(fpath)
        for stream in fp["streams"]:
            if stream['codec_type'] == "attachment":
                astreams.append(stream)
        return astreams
    except ffmpeg.Error as e:
        print(f'{c.red}{e.stderr}{c.o}')
        return 'Probe_error'
