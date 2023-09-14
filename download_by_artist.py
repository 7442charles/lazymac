import os
from pytube import YouTube
from googleapiclient.discovery import build
from pydub import AudioSegment

# Set your YouTube API key here
YOUTUBE_API_KEY = 'AIzaSyAyQheAF7Tr0RcGHTG2Xmaioa9qvu3qBiM'

# Function to search for a YouTube channel based on the artist's name
def search_channel(artist_name):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=artist_name,
        type='channel',
        part='id',
        maxResults=1
    )
    response = request.execute()

    if 'items' in response and response['items']:
        channel_id = response['items'][0]['id']['channelId']
        return channel_id
    else:
        print(f"No YouTube channel found for {artist_name}.")
        return None

# Function to retrieve all video IDs from a channel
def get_channel_video_ids(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    video_ids = []

    # Retrieve the first page of videos
    request = youtube.search().list(
        channelId=channel_id,
        type='video',
        part='id',
        maxResults=50  # You can adjust the number of results per page
    )
    response = request.execute()

    while response.get('items'):
        for item in response['items']:
            video_ids.append(item['id']['videoId'])

        # Check if there are more pages of results
        if 'nextPageToken' in response:
            request = youtube.search().list(
                channelId=channel_id,
                type='video',
                part='id',
                maxResults=50,
                pageToken=response['nextPageToken']
            )
            response = request.execute()
        else:
            break

    return video_ids

# Function to download audio in MP3 format from a video URL
def download_audio(artist_name, video_url, output_folder):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_path = os.path.join(output_folder, artist_name, audio_stream.title + ".mp3")

        # Download audio stream as MP3
        audio_stream.download(output_path=output_folder, filename=audio_stream.title + ".mp3")
        
        return audio_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

if __name__ == "__main__":
    artist_name = input("Enter the artist's name: ")
    channel_id = search_channel(artist_name)
    output_folder = "artist_audios"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if channel_id:
        artist_folder = os.path.join(output_folder, artist_name)
        
        if not os.path.exists(artist_folder):
            os.makedirs(artist_folder)
        
        print(f"Found YouTube channel for {artist_name}.")
        video_ids = get_channel_video_ids(channel_id)

        if video_ids:
            print(f"Found {len(video_ids)} videos in the channel.")

            for video_id in video_ids:
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                audio_path = download_audio(artist_name, video_url, artist_folder)

                if audio_path:
                    print(f"Downloaded audio from video {video_id} as MP3.")
