import os
import threading
import time

import m3u8

from db import db_util
from download import download_util
from model.download_request import EpisodeDownloadRequest
from util import utils, CONSTANTS
from wwe.wwe_v2 import WWEClient


def download_episode(request: EpisodeDownloadRequest,
    client: WWEClient = WWEClient()):
    partial_download = request.start_time is not None

    video_info = client.get_video_info(request)

    print(f'Obtained video information for episode ID {request.episode_id}')
    print(f'Starting download for episode "{video_info.title}"')

    database = db_util.database()
    database.db_connect()
    previously_downloaded = database.db_query(request.episode_id,
                                              is_partial_download=partial_download)

    if previously_downloaded and not request.force:
        raise FileExistsError(
            f'Video {request.episode_id} has already been downloaded. Please '
            f'run again with `-f` or `--force` if you want to download it '
            f'again')

    download = download_util.download()
    index_m3u8 = download.get_index_m3u8(video_info.m3u8_url)
    index_m3u8_obj = m3u8.loads(index_m3u8.data.decode('utf-8'))

    # TODO: use MediaDownloadRequest
    audio_kwargs = get_audio_download_kwargs(request, video_info,
                                             index_m3u8_obj,
                                             download)

    # Create a list where we will add our threads
    download_threads = []

    # Start the audio downloading thread
    audio_thread = threading.Thread(target=download.download_playlist,
                                    kwargs=audio_kwargs)

    audio_thread.start()
    # Add the audio to our thread list
    download_threads.append(audio_thread)

    # TODO: use MediaDownloadRequest
    video_kwargs = get_video_download_kwargs(request, video_info,
                                             index_m3u8_obj, download)

    video_thread = threading.Thread(target=download.download_playlist,
                                    kwargs=video_kwargs)
    video_thread.start()

    # Add the video thread to our thread list
    download_threads.append(video_thread)

    # Wait for all threads to be finished
    for thread in download_threads:
        thread.join()

    # Download the chapter information
    client.write_metadata(request, video_info)

    output_dir = utils.clean_text(
        request.output_dir) if request.output_dir else utils.clean_text(
        video_info.title)

    # Create output folder if it doesn't exist
    if not os.path.exists(
        CONSTANTS.OUTPUT_FOLDER + "/" + output_dir):
        os.makedirs(
            CONSTANTS.OUTPUT_FOLDER + "/" + output_dir)

    if request.subtitles:
        pass
        # TODO: implement subtitles
        # account.download_subtitles(stream_url[1], utils.clean_text(title))

    # Download the thumbnail
    download.download_thumbnail(video_info.custom_title,
                                video_info.thumbnail_url)

    # Finally we want to combine our audio and video files
    download.combine_videos(title=video_info.custom_title,
                            file_folder=output_dir,
                            keep_files=request.keep_files,
                            has_subtitles=request.subtitles)

    # Insert the downloaded video into our database
    if previously_downloaded:
        database.db_upd(video_info.id, video_info.title,
                        str(video_kwargs.get('bitrate')),
                        partial_download, int(time.time()))
        print("Updated database with the new video information")
    else:
        database.db_ins(video_info.id, video_info.title,
                        str(video_kwargs.get('bitrate')),
                        partial_download, int(time.time()))
        print("Inserted the video into the database")


def get_audio_download_kwargs(request, video_info, m3u8_obj, download):
    audio_qualities = []
    for stream in m3u8_obj.media:
        # We want English audio, so any files with eng as its language is added to our list
        if "eng" in stream.language:
            audio_qualities.append(
                (int(stream.group_id.split('audio-')[1]),
                 video_info.base_url + "/" + stream.uri))

    # Sort the audio quality from high to low
    audio_qualities.sort(reverse=True)

    # Choose the playlist we want
    audio_playlist = download.get_playlist_object(audio_qualities[0][1])

    return {"playlist": audio_playlist,
            "base_url": audio_qualities[0][1].split("index.m3u8")[0],
            "title": video_info.custom_title,
            "start_from": request.start_time if request.start_time is not None else 0,
            "end_time": request.end_time if request.end_time is not None else video_info.duration_seconds
            }


def get_video_download_kwargs(request, video_info, m3u8_obj, download):
    video_selections = []

    for stream in m3u8_obj.playlists:
        video_selections.append((stream.stream_info.bandwidth,
                                 video_info.base_url + "/" + stream.uri))

    # Select the first one which has the highest bitrate
    video_selections.sort(reverse=True)

    selected_stream = video_selections[request.quality]

    # Get the playlist m3u8 we want to download
    video_playlist = download.get_playlist_object(selected_stream[1])

    return {"playlist": video_playlist,
            "base_url": selected_stream[1].split("index.m3u8")[0],
            "title": video_info.custom_title,
            "start_from": request.start_time if request.start_time is not None else 0,
            "end_time": request.end_time if request.end_time is not None else video_info.duration_seconds,
            "bitrate": selected_stream[0]
            }
