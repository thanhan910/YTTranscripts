from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from youtube_transcript_api import YouTubeTranscriptApi
import logging
import json
import os

# from youtube_transcript_api.formatters import TextFormatter
# import whisper
# from pytube import YouTube
# import re

from .utils.youtube_utils import extract_video_id, download_audio
from .utils.whisper_utils import model as whisper_model

logging.basicConfig(level=logging.INFO)
# model = whisper.load_model("base")


def extract_video_id(url_or_id):
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # Extract the video ID from the URL
        if "v=" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
        elif "youtu.be" in url_or_id:
            return url_or_id.split("/")[-1]
    return url_or_id


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def get_languages(request):
    if request.method == "POST":
        print([method for method in dir(request) if not method.startswith("_")])
        # Implement the logic similar to Flask's get_languages function
        data = json.loads(request.body)
        video_id = data["video_id"]
        video_id = extract_video_id(video_id)
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            languages = [
                {"code": transcript.language_code, "name": transcript.language}
                for transcript in transcript_list
            ]
            return JsonResponse({ 'languages' : languages })
        except Exception as e:
            return JsonResponse({'error' : str(e), 'status' : 500})
        

@csrf_exempt
def get_transcript(request):
    """
    Use OpenAI Whisper to transcribe the audio of a YouTube video.

    Credit: https://huggingface.co/spaces/SteveDigital/free-fast-youtube-url-video-to-text-using-openai-whisper
    """
    if request.method == "POST":
        data = json.loads(request.body)
        video_id = data["video_id"]
        video_id = extract_video_id(video_id)
        language = data["language"]
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return JsonResponse({'transcript' : transcript})
        except Exception as e:
            return JsonResponse({'error' : str(e), 'status' : 500})


@csrf_exempt
def get_video_text_whisper(request):
    if request.method == "POST":
        data = json.loads(request.body)
        video_id = data["video_id"]
        video_id = extract_video_id(video_id)
        if video_id == "":
            return JsonResponse({'error': "Invalid video ID"}, status=400)
        
        out_file = download_audio(video_id)
        if out_file is None:
            return JsonResponse({'error': "Failed to download audio file"}, status=400)
        
        try:
            file_stats = os.stat(out_file)
            if file_stats.st_size <= 30_000_000:
                base, ext = os.path.splitext(out_file)
                new_file = base + ".mp3"
                os.rename(out_file, new_file)
                result = whisper_model.transcribe(new_file)
                os.remove(new_file)
                return JsonResponse({'transcript': result["text"].strip()})
            else:
                logging.error("File size is too large")
                os.remove(out_file)
                return JsonResponse({'error': "File size is too large"}, status=400)
        except Exception as e:
            logging.error(f"Error processing audio file: {str(e)}")
            return JsonResponse({'error': "Error processing audio file"}, status=500)