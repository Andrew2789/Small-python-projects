from ctypes import wintypes
from random import randint
from PIL import Image
import os, ctypes

def random_weighted(dictionary):
    '''Selects a random key from a dictionary based on their values (must be int values).'''
    rnd_value = randint(1, sum(dictionary.values()))
    lower_bound = 0
    for key in dictionary.keys():
        upper_bound = dictionary[key] + lower_bound
        if lower_bound < rnd_value <= upper_bound:
            return key
        lower_bound = upper_bound

def scale_image(image, x, y):
    '''Scale an image to fit new x and y dimensions without distortion (edges will be cropped if new dimensions are at a different aspect ratio).'''
    aspect_ratio = image.size[0] / image.size[1]
    if int(x / aspect_ratio) < y:
        return image.resize((x, int(x / aspect_ratio)), Image.ANTIALIAS)
    else:
        return image.resize((int(y * aspect_ratio), y), Image.ANTIALIAS)

def set_wallpaper(image_path):
    '''Set wallpaper on windows.'''
    SystemParametersInfo = ctypes.WinDLL('user32').SystemParametersInfoW
    SystemParametersInfo.argtypes = ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint
    SystemParametersInfo.restype = wintypes.BOOL
    SystemParametersInfo(20, 0, image_path, 3)
    
def main():
    #read wallpaper directory and screen resolutions from sysinfo.ini
    with open("sysinfo.ini","r") as f:
        wallpaper_dir = f.readline().split("|")[1].strip()
        resolutions = [[int(x) for x in f.readline().split("|")[1].split()] for i in (0,1)]

    #read saved ranks from ranks.ini
    with open("ranks.ini","r") as f:
        ranks = {}
        for rank in f.readlines():
            line = rank.split("|")
            ranks[line[0].strip()] = int(line[1])
    
    folders = [x for x in os.listdir(wallpaper_dir) if os.path.isdir(os.path.join(wallpaper_dir, x))]

    #add dict entries for new folders
    for folder in folders:
        if folder not in ranks.keys():
            ranks[folder] = 0
            
    #delete dict entries for folders that no longer exist
    for key in list(ranks.keys()):
        if key not in folders:
            del(ranks[key])

    folder = random_weighted(ranks)
    
    images = [x for x in os.listdir(os.path.join(wallpaper_dir, folder)) if os.path.isfile(os.path.join(wallpaper_dir, folder, x))]
    #selected_images = [Image.open(y) for y in [os.path.join(wallpaper_dir, folder, x) for x in map(images.pop, (randint(0, len(images)-1), randint(0, len(images)-2)))]]
    selected_images = []
    for i in (0, 1):
        selected_images.append(Image.open(os.path.join(wallpaper_dir, folder, images.pop(randint(0, len(images) - 1)) )))

    #create wallpaper image
    scaled_images = [scale_image(selected_images[x], *resolutions[x]) for x in range(2)]
    background = Image.new("RGB", (resolutions[0][0] + resolutions[1][0], max(resolutions[0][1], resolutions[1][1])))
    for i in (0, 1):
        background.paste(scaled_images[i], (i * resolutions[0][0], 0))
    background.save("background.png", "PNG", quality=100)

    set_wallpaper(os.path.join(os.getcwd(), "background.png"))

    #update ranks.ini
    with open("ranks.ini","w") as f:
        f.truncate()
        for key in ranks.keys():
            f.write("%s | %d\n" % (key, ranks[key]))

main()
