import os
from pathlib import Path
import pickle
import argparse
from time import sleep

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import typer
from rich import print

from googleapiclient.http import MediaFileUpload

client_secrets_file = "client_secrets.json"

def insert_captions(sub_file:Path, target_video_id, track_name="default", sub_language="en", authenticate=False):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    credential_save_path = Path("credentials_youtube_force-ssl.pickle")

    if not credential_save_path.exists() or authenticate:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        pickle.dump(credentials, credential_save_path.open("wb"))

    credentials = pickle.load(credential_save_path.open("rb"))
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.captions().insert(
        part="snippet",
        sync=False,
        body={
          "snippet": {
            "language": sub_language,
            "name": track_name,
            "videoId": target_video_id,
          }
        },
        media_body=MediaFileUpload(str(sub_file))
    )
    response = request.execute()

    print(response)

def upload_video( file:Path, title, description='', privacy_status='private', authenticate=False,):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    api_service_name = "youtube"
    api_version = "v3"
    credential_save_path = Path("credentials_youtube_upload.pickle")

    if not credential_save_path.exists() or authenticate:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        pickle.dump(credentials, credential_save_path.open("wb"))

    credentials = pickle.load(credential_save_path.open("rb"))
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
          "snippet": {
            "description": description,
            "title": title
          },
          "status": {
            "privacyStatus": privacy_status
          }
        },
        
        # TODO: For this request to work, you must replace "YOUR_FILE"
        #       with a pointer to the actual file you are uploading.
        media_body=MediaFileUpload(str(file))
    )
    response = request.execute()

    return response

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--sub-auth", action="store_true", help="Authenticate with youtube.")
    argparser.add_argument("--sub-file", type=Path, help="Subtitle file to upload.")
    argparser.add_argument("--sub-target-video-id", type=str, help="Subtitle file to upload.")
    argparser.add_argument("--sub-name", type=str, default="default", help="The name of the subtitle track.")
    argparser.add_argument("--sub-language", type=str, default="en", help="The language of the subtitle track.")

    argparser.add_argument("--upload-file", type=Path, help="Video file to upload.")
    argparser.add_argument("--upload-title", type=str, help="Video title.")
    argparser.add_argument("--upload-description", type=str, help="description of uploaded video.")
    argparser.add_argument("--upload-privacy", type=str, help="Set privace of video to youtube video. Can be: public, private, unlisted.")
    argparser.add_argument("--upload-auth", action="store_true", help="Authenticate with youtube.")
    args = argparser.parse_args()

    video_id = None

    if any([args.upload_auth, args.upload_file, args.upload_title, args.upload_description, args.upload_privacy]):
        assert args.upload_file, "You need to specify a video file to upload."
        assert args.upload_title, "You need to specify a title for the video."
        assert args.upload_description, "You need to specify a description for the video."
        assert args.upload_privacy, "You need to specify a privacy setting for the video."
        print("Uploading video...")
        r = None
        while not r or r['status'] != 403:
            try:
                r = upload_video(args.upload_file, args.upload_title, args.upload_description, args.upload_privacy, args.upload_auth)
            except googleapiclient.errors.HttpError as e:
                print(e)
                print("Sleeping for 1 hour...")
                sleep(60*60)
            video_id = r['id']

    if any([args.sub_auth, args.sub_file, args.sub_name, args.sub_language]):
        assert args.sub_file, "You need to specify a subtitle file to upload."
        assert video_id or args.sub_target_video_id, ("You need to specify a video "
            "id to upload the subtitle to, or need to upload a video at the same time.")
        
        print("Uploading subtitles...")
        r = None
        while not r or r['status'] != 403:
            try:
                insert_captions(args.sub_file, video_id, args.sub_name, args.sub_language, args.sub_auth)
            except googleapiclient.errors.HttpError as e:
                print(e)
                sleep(60*60)
                print("Sleeping for 1 hour...")