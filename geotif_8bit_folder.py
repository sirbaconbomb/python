import numpy as np
from datetime import datetime
from os import listdir


def main(folder):
    """
    converts arbitrary formated tif file to 8bits
    """
    try:
        import tifffile as tif
    except ImportError:
        print('[ERROR] no module named tifffile found, please install it')
        return

    for file in listdir(folder):
        image = f'{folder}\\{file}'

        # check if image if a tif
        if image[-3:] not in ('tif', 'tiff'):
            print(f"[Warning] {image} is not a tif.")
            continue

        # load and convert image
        imageArray = tif.imread(image)
        converted = np.around(imageArray).astype('int8')

        # getting the date
        date = datetime.now()
        year, month, day = date.year, date.month, date.day

        # getting the new name
        name = image[:-4]

        new_name = f'{name}_{month:02}{day:02}{year}.tif'
        tif.imwrite(new_name, converted)

        print(f"[INFO] {file}: conversion to 8bits was successful")


if __name__ == '__main__':
    # the name of the folder goes here
    main('.\\data')
