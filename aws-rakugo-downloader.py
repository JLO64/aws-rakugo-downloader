import os
from yt_dlp import YoutubeDL
import argparse
#import boto3

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
        if not os.path.exists(f'~/downloaded-videos/{website_name}'):
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

#def upload_folder_contents_to_AWS_S3()



def main(args):
    print(read_txt_urls(args.txtfile))
    download_videos(read_txt_urls(args.txtfile))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download videos from URLs in a text file')
    parser.add_argument('--txtfile', metavar='txtfile', type=str, help='path to the text file containing URLs')
    #parser.add_argument('--outputdir', metavar='outputdir', type=str, help='path to the output directory')
    args = parser.parse_args()
    main(args)