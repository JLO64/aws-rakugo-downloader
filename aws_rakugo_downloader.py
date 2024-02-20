from yt_dlp import YoutubeDL
import argparse, os, pytz
from datetime import datetime, timezone, timedelta

# current date and time in tokyo timezone
# timezone_offset = 9 # JST
# tzinfo = timezone(timedelta(hours=timezone_offset))
# now = datetime.now(tzinfo)

global selectedTimezone
global txt_log_filepath

def read_txt_urls(file_name):
    #return a list of urls from each line of a text filec in the home directory
    with open(os.path.expanduser(file_name), 'r') as f:
        list_of_urls = f.readlines()
    for i in range(len(list_of_urls)):
        list_of_urls[i] = list_of_urls[i].strip()
    return list_of_urls

def download_videos(list_of_urls):
    if not os.path.exists("./yt-dlp-downloads"):
        os.makedirs("./yt-dlp-downloads")
    for url in list_of_urls:
        website_name = url.split('/')[2].replace('www.', '').split('.')[0].lower()
        print(website_name)
        if not os.path.exists(f'./yt-dlp-downloads/{website_name}'):
            os.makedirs(f'./yt-dlp-downloads/{website_name}')
        ydl_opts = {
            'n_threads': 4,
            'outtmpl': f'./yt-dlp-downloads/{website_name}/%(title)s' + datetime.now(pytz.timezone(selectedTimezone)).strftime("%Y%m%d") + '.%(ext)s'
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                write_str_to_txt_file(txt_log_filepath, f"Success in downloading {url}")
        except Exception as e:
            print(f"Error downloading {url}")
            if str(e).find('Programme') != -1:
                print("Programme is likely no longer available.") 
                write_str_to_txt_file(txt_log_filepath, f"Error downloading {url}, programme is likely no longer available.")
            else:
                write_str_to_txt_file(txt_log_filepath, f"Error downloading {url}")

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

def write_str_to_txt_file(filepath, string):
    with open(os.path.expanduser(filepath), 'a') as f:
        f.write( '(' + datetime.now(pytz.timezone(selectedTimezone)).strftime("%H:%M:%S") + '): ' + string + '\n')
        

def main(txtfile, logfilepath, selectedtz):
    args = argparse.Namespace(txtfile=txtfile, logfilepath=logfilepath, selectedtz=selectedtz)
    global txt_log_filepath
    global selectedTimezone
    selectedTimezone = args.selectedtz
    txt_log_filepath = args.logfilepath
    write_str_to_txt_file(txt_log_filepath, "Downloads initiated at: " + datetime.now(pytz.timezone(selectedTimezone)).strftime("%Y-%m-%d"))
    download_videos(read_txt_urls(args.txtfile))
    write_str_to_txt_file(txt_log_filepath, "Finished downloading videos")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download videos from URLs in a text file')
    parser.add_argument('--txtfile', metavar='txtfile', type=str, help='path to the text file containing URLs')
    parser.add_argument('--logfilepath', metavar='logfilepath', type=str, help='path to the log file')
    parser.add_argument('--selectedtz', metavar='selectedtz', type=str, help='timezone to use for the log file')
    args = parser.parse_args()
    main(args.txtfile, args.logfilepath, args.selectedtz)
