#!/usr/bin/env python
# =======================================================================
'''
coded by Maurice Cokes II

purpose of code is to do a geotiff conversion to 8bit resolution
The code is AWS compatible
At the end of the code there is a clean up so that the speed of the code is a bit faster

I am maintaining the input and output name so it leaves it the same
'''
# =======================================================================
from datetime import datetime
import rasterio
import os
import json
from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles
import boto3


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    print(event)
    #get the event from S3 and parse it to get bucket and key
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    if not "geotiffs/8bit/" in key:
        print("process is going to start")
        print(bucket)
        print(key)

        #extract filename from the key
        tmp_key = key.split('/')
        tif_file = tmp_key[len(tmp_key) - 1]

        print(tif_file)

        if tif_file.lower().endswith(('.tif', '.tiff')):
            #download the tif, tif file in local storage /tmp/
            filepath = '/tmp/' + tif_file
            s3.download_file(bucket, key,filepath)

            with rasterio.open(filepath) as src:

                # reading source
                g = src.read()

                # saving the metadata
                profile = src.profile

                # converting to 8bit and adding lzw compression
                # for up to 90% compression ratio
                profile.update(dtype=rasterio.uint8, count=1, compress='lzw')

            # getting the date
            date = datetime.now()
            year, month, day = date.year, date.month, date.day

            # getting the new name
            filename = os.path.splitext(tif_file)[0]
            new_name = f'{filename}_{month:02}{day:02}{year}.tif'
            #new_name = filename + '_' + month + day + year + '.tif'

            # saving the file
            with rasterio.open('/tmp/' + new_name, 'w', **profile) as dst:
                dst.write(g.astype(rasterio.uint8))

            print("[INFO] conversion to 8bits was successful")

            output = '/tmp/' + new_name

            # Check if your input file is optimized
            is_cog = cog_validate('/tmp/' + new_name)
            print("is_cog")
            print(is_cog)
            web_profile = cog_profiles.get("deflate")
            cog_translate('/tmp/' + new_name, output, web_profile)
            
            # Check if your output file was optimized
            is_cog = cog_validate(output)
            if is_cog:
                print("is_cog")
                print(is_cog)
                #finally upload the video file on S3 video folder
                s3.upload_file('/tmp/' + new_name, bucket, 'geotiffs/8bit/' + new_name)
                with rasterio.open(filepath) as src:
                    print(src.profile)

                with rasterio.open('/tmp/' + new_name) as src:
                    print(src.profile)
                
                os.system('ls')
                os.system('rm /tmp/' + new_name)
                os.system('rm /tmp/' + tif_file)
                os.system('ls')
                print("output file is placed at" + 'geotiffs/8bit/' + new_name)
                return {
                    'statusCode': 200,
                    'body': json.dumps('Successful')
                }
            else:
                os.system('ls')
                os.system('rm /tmp/' + new_name)
                os.system('rm /tmp/' + tif_file)
                os.system('ls')
                print("validation failed")
                return {
                    'statusCode': 200,
                    'body': json.dumps('Not Success')
                }
        else:
            print(event)
            print("wrong path case")
            return {
                'statusCode': 200,
                'body': json.dumps('Invalid extension')
            }
    else:
        print("process will not start as it is the output file event")
        return {
            'statusCode': 200,
            'body': json.dumps('Invalid folder')
            }