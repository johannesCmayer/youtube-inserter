# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import sys
import pickle

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

home = os.getenv("HOME")
client_secrets_file = f"{home}/KEYS/client_secret_939544863452-t9npirab3oq40raqok1kbnj4dfksv8ng.apps.googleusercontent.com.json"

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
credentials_path = f"{home}/KEYS/google_credentials.pickle"

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    if sys.argv[1] == "--auth":
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        with open(credentials_path, 'wb') as f:
            pickle.dump(credentials, f)
        exit(0)
    else:
        with open(credentials_path, 'rb') as f:
            credentials = pickle.load(f)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    playlist_id = sys.argv[1]
    playlist_id_ref = "PLarKqD2Ythc4u-nAHVRnmC6YH36rMm-qw"
    assert len(playlist_id) == len(playlist_id_ref), f"playlist_id has not correct length\n{playlist_id}\n{playlist_id_ref}"

    video_id = sys.argv[2]
    video_id_ref ="5LbAVK7ksEk" 
    assert len(video_id) == len(video_id_ref), "video_id has not corret length"

    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
              "videoId": video_id,
              "kind": "youtube#video"
            }
          }
        }
    )
    response = request.execute()

if __name__ == "__main__":
    main()
