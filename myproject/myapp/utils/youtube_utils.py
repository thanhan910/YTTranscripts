import os
from pytube import YouTube

MEDIA_ROOT = './myapp/local-media/'

def extract_video_id(url_or_id):
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        if "v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
        elif "youtu.be" in url_or_id:
            return url_or_id.split("/")[-1]
    return url_or_id

def download_audio_mp3(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt_obj = YouTube(url)
    video = yt_obj.streams.filter(only_audio=True).first()
    filename = "local-audio.mp3"
    os.remove(filename) if os.path.exists(filename) else None
    out_file = video.download(output_path=".", filename=filename)
    return out_file

def download_audio(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt_obj = YouTube(url)
    
    filename = f"{video_id}.mp3"
    output_path = os.path.join(MEDIA_ROOT, filename)  # Define the output path
    
    try:
        # Download the video to the media folder
        video = yt_obj.streams.filter(only_audio=True).first()
        video.download(output_path=MEDIA_ROOT, filename=filename)
        return output_path  # Return the path to the downloaded video
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None
