import os
from pathlib import Path
import pickle
import argparse

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload

argparser = argparse.ArgumentParser()
argparser.add_argument("--auth", action="store_true", help="Authenticate with youtube.")
argparser.add_argument("-f", "--sub-file", type=Path, required=True, help="Subtitle file to upload.")
argparser.add_argument("-i", "--target-video-id", type=str, required=True, help="Subtitle file to upload.")
argparser.add_argument("-n", "--track-name", type=str, default="default", help="The name of the subtitle track.")
argparser.add_argument("--sub-language", type=str, default="en", help="The language of the subtitle track.")
args = argparser.parse_args()

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

credential_save_path = Path("credentials.pickle")

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"

    if not credential_save_path.exists() or args.auth:
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
            "language": args.sub_language,
            "name": args.track_name,
            "videoId": args.target_video_id,
          }
        },
        media_body=MediaFileUpload(str(args.sub_file))
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()