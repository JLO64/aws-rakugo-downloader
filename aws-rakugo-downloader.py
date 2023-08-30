import os
from yt_dlp import YoutubeDL
import argparse
import boto3
from datetime import datetime

now = datetime.now() # current date and time

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
        date_time = now.strftime("%Y%m%d")
        ydl_opts = {
            'outtmpl': f'~/downloaded-videos/{website_name}/%(title)s' + date_time + '.%(ext)s'
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Error downloading {url}")
            if str(e).find('Programme') != -1:
                print("Programme is likely no longer available.") 

def upload_folder_contents_to_AWS_S3(bucket_name, folder_path, bucket=None):
    #upload the contents of a folder to an AWS S3 bucket
    print(f"Uploading contents of {folder_path} to {bucket_name}")
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(subdir, file)
            object_key = full_path[len(folder_path)+1:]
            # check if object already exists in bucket
            if any(obj.key == object_key for obj in bucket.objects.all()):
                print(f"Object with key {object_key} already exists in bucket {bucket_name}. Skipping upload.")
                continue
            print(f"Uploading {full_path}")
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=object_key, Body=data)

def generate_txt_file_of_all_files_in_s3_bucket(bucket_name, bucket=None):
    #generate a text file of all the files in an S3 bucket
    #include their name, path, size, last modified date, and link
    print(f"Generating text file of all files in {bucket_name}")
    with open(os.path.expanduser(f'~/downloaded-videos/{bucket_name}.txt'), 'w') as f:
        f.write(f"# {bucket_name}\n")
        for obj in bucket.objects.all():
            object_url = f"https://{bucket_name}.s3.amazonaws.com/{obj.key}"
            #in MB
            object_size = str((obj.size/1000000).__round__(2)) + ' MB'
            object_date = str(obj.last_modified).split(' ')[0]
            f.write(f"\n## {obj.key}\n- {object_size}\n -{object_date}\n- URL:{object_url}\n")

def main(args):
    #print(read_txt_urls(args.txtfile))
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(args.s3bucket)
    download_videos(read_txt_urls(args.txtfile))
    upload_folder_contents_to_AWS_S3(args.s3bucket, os.path.expanduser('~/downloaded-videos'), bucket=bucket)
    generate_txt_file_of_all_files_in_s3_bucket(args.s3bucket, bucket=bucket)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download videos from URLs in a text file')
    parser.add_argument('--txtfile', metavar='txtfile', type=str, help='path to the text file containing URLs')
    parser.add_argument('--s3bucket', metavar='s3bucket', type=str, help='name of the S3 bucket to upload to')
    args = parser.parse_args()
    main(args)
