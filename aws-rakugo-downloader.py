import os
from yt_dlp import YoutubeDL
import argparse
import boto3

boto3.setup_default_session(profile_name='default')

def read_txt_urls(file_name):
    #return a list of urls from each line of a text filec in the home directory
    with open(os.path.expanduser(file_name), 'r') as f:
        list_of_urls = f.readlines()
    for i in range(len(list_of_urls)):
        list_of_urls[i] = list_of_urls[i].strip()
    return list_of_urls

def download_videos(list_of_urls):
    for url in list_of_urls:
        website_name = url.split('/')[2].replace('www.', '').split('.')[0].lower()
        print(website_name)
        if not os.path.exists(os.path.expanduser(f'~/downloaded-videos/{website_name}')):
            os.makedirs(os.path.expanduser(f'~/downloaded-videos/{website_name}'))
        ydl_opts = {
            'outtmpl': f'~/downloaded-videos/{website_name}/%(title)s.%(ext)s'
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Error downloading {url}")
            if str(e).find('Programme') != -1:
                print("Programme is likely no longer available.") 

def upload_folder_contents_to_AWS_S3(bucket_name, folder_path):
    #upload the contents of a folder to an AWS S3 bucket
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(folder_path)+1:], Body=data)

def main(args):
    print(read_txt_urls(args.txtfile))
    download_videos(read_txt_urls(args.txtfile))
    upload_folder_contents_to_AWS_S3(args.s3bucket, os.path.expanduser('~/downloaded-videos'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download videos from URLs in a text file')
    parser.add_argument('--txtfile', metavar='txtfile', type=str, help='path to the text file containing URLs')
    parser.add_argument('--s3bucket', metavar='s3bucket', type=str, help='name of the S3 bucket to upload to')
    args = parser.parse_args()
    main(args)