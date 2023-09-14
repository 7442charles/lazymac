import os
from pytube import YouTube
from pydub import AudioSegment
import json
from googleapiclient.discovery import build

# ANSI escape code for green color
GREEN = '\033[92m'
# ANSI escape code for red color
RED = '\033[91m'
# Reset ANSI escape code
RESET = '\033[0m'

# Set your YouTube API key here
YOUTUBE_API_KEY = 'EKA API KEY YAKO'

# Function to search for a video using the YouTube Data API
def search_video(song_title):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=song_title,
        type='video',
        part='id',
        maxResults=1
    )
    response = request.execute()

    if 'items' in response and response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return video_url
    else:
        print("No results found.")
        return None

# Function to download audio in MP3 format using pytube
def download_audio(song_title, output_folder):
    video_url = search_video(song_title)
    if not video_url:
        return None

    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=output_folder)
        return os.path.join(output_folder, audio_stream.title + ".mp4")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        return None

# Function to add song details to a JSON file
def add_song_details_to_json(song_title, thumbnail_url, song_path):
    song_details = {
        "song_name": song_title,
        "thumbnail_url": thumbnail_url,
        "song_path": song_path
    }

    json_file = "songs_details.json"

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        data.append(song_details)
    else:
        data = [song_details]

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    output_folder = "musicvideo"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    while True:
        song_title = input("Enter the song title (or type 'exit' to quit): ")
        
        if song_title.lower() == 'exit':
            break

        # Download audio in MP3 format
        audio_path = download_audio(song_title, output_folder)

        if audio_path:
            mp3_path = os.path.splitext(audio_path)[0] + ".mp3"
            os.rename(audio_path, mp3_path)
            print(f"{GREEN}Downloaded '{song_title}' audio in MP3 format.{RESET}")

            # Get the video details
            video_url = search_video(song_title)
            add_song_details_to_json(song_title, video_url, mp3_path)
            print(f"{GREEN}Added song details to songs_details.json.{RESET}")
