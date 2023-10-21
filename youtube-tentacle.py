# TODO add functionality to check if a youtube video has been deleted
# TODO add functionality to upload youtube videos
import os
import sys
import pickle
from pathlib import Path
import tempfile

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from oauth2client.client import flow_from_clientsecrets

home = os.getenv("HOME")
project_dir = Path(__file__).parent
client_secrets_file = project_dir/"client_secret_939544863452-t9npirab3oq40raqok1kbnj4dfksv8ng.apps.googleusercontent.com.json"
#f"{home}/KEYS/client_secret_939544863452-t9npirab3oq40raqok1kbnj4dfksv8ng.apps.googleusercontent.com.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   client_secrets_file))


flow = flow_from_clientsecrets(client_secrets_file,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

exit(0)

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
credentials_path = Path()/".youtube-tentacle-credentials"

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"


    # Get credentials and create an API client
    dir = tempfile.gettempdir()
    credentials_path = Path(dir)/".youtube-tentacle-credentials"
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
