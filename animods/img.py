
# pylint: disable:F0001
from PIL import Image
import os
from tempfile import SpooledTemporaryFile
import time
from requests import get
from io import BytesIO
from pathlib import Path
from animods.misc import c, print_progress_bar


def download_poster(image_url, out_dir):
    print("  [ Api ] Downloading cover art :")
    buffer = SpooledTemporaryFile(max_size=1000000000)
    r = get(image_url, stream=True)
    if r.status_code == 200:
        downloaded = 0
        filesize = int(r.headers['content-length'])
        for chunk in r.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)

            print_progress_bar(downloaded, filesize)
            time.sleep(0.007)
            # print(downloaded/filesize)
        buffer.seek(0)
        print()
        if Path.joinpath(out_dir, 'image.jpg').exists():
            os.remove(Path.joinpath(out_dir, 'image.jpg'))
        i = Image.open(BytesIO(buffer.read()))
        i.save(os.path.join(out_dir, 'image.jpg'), quality=100)
    buffer.close()


def create_ico(path):
    """Creates an an.ico file in the specified path using image.jpg

    @Params : 
        path : where the jpeg rests 
        Source : A path that points to where image.jpg is 

    """
    # current_folder = Path.cwd()
    current_folder = Path(path)
    oi_path = Path.joinpath(current_folder, 'image.jpg')

    if oi_path.exists():
        print(f'{c.purple}Generating icon from : {oi_path}{c.o}')

        tc = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
        tc_path = Path.joinpath(current_folder, 'tc.png')
        tc.save(tc_path)
        print(f'{c.b_black}Created Transparent Canvas at : {tc_path}{c.o}')

        # original image resize
        oi = Image.open(oi_path)
        roi = oi.resize((180, 256))
        roi_path = Path.joinpath(current_folder, 'roi.png')
        roi.save(roi_path, format="png")
        print(f'{c.b_black}Generated Resized PNG at :{roi_path}{c.o}')

        rio = Image.open(roi_path)
        tc.paste(rio, (38, 0))
        fp_path = Path.joinpath(current_folder, 'fp.png')
        tc.save(fp_path, format="png")
        print(f'{c.b_black}Generated Final PNG at {fp_path}{c.o}')

        fp = Image.open(fp_path)
        sizes = [(256, 256)]
        fpi_path = Path.joinpath(current_folder, 'an.ico')
        fp.save(fpi_path, format="ICO", sizes=sizes)
        print(f'{c.green}Generated Icon at {fpi_path}{c.o}')
        print(f'{c.purple}Cleaning up residual files in {fpi_path}{c.o}')
        residual_files = ['fp.png', 'tc.png', 'roi.png']
        for file in residual_files:
            residual_file_path = Path.joinpath(current_folder, file)
            print(f'{c.b_black}Info: {c.red}Removing {residual_file_path}{c.o}')
            os.remove(residual_file_path)
        print(f'{c.green}Cleaning up complete ...{c.o}')
    else:
        print(f'\n{c.red}Origin image not found {oi_path}{c.o}\n')


def create_config(path):
    print(f'{c.purple}Generating config for : {path}{c.o}')
    path = str(path)
    try:
        f = open(path+r"\desktop.in", "w")
        f.write(f'[.ShellClassInfo]\nIconResource=an.ico,0\nConfirmFileOp=0')
        f.close()
        os.rename(path+r'\desktop.in', path+r'\desktop.ini')
    except FileExistsError:
        print('[ >_< ] file already exists ... Remaking')
        os.remove(path+r'\desktop.in')
        os.remove(path+r'\desktop.ini')
        f = open(path+r"\desktop.in", "w")
        f.write(f'[.ShellClassInfo]\nIconResource=an.ico,0\nConfirmFileOp=0')
        f.close()
        os.rename(path+r'\desktop.in', path+r'\desktop.ini')
        print('[ ^_^ ] Remade icon config ')
