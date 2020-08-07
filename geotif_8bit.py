import numpy as np
from datetime import datetime


def main(image):
    """
    converts arbitrary formated tif file to 8bits
    """
    try:
        import tifffile as tif
    except ImportError:
        print('[ERROR] no module named tifffile found, please install it')
        return

    # check if image if a tif
    if image[-3:] not in ('tif', 'tiff'):
        print(f"[ERROR] {image} is not a tif.")
        return

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

    print("[INFO] conversion to 8bits was successful")


if __name__ == '__main__':
    # name of the file goes here
    main('monthly_2mt_anom_201910.tif')
