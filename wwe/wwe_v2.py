import html
import re
from datetime import datetime

import requests

from model.download_request import EpisodeDownloadRequest
from model.video_info import VideoInfo
from util import CONSTANTS, utils

LOGIN_URL = 'https://dce-frontoffice.imggaming.com/api/v2/login'
INFO_PATH = 'https://dce-frontoffice.imggaming.com/api/v4/vod/'


class WWEClient:
    def __init__(self):
        with requests.Session() as self._session:
            self._session.headers.update(CONSTANTS.HEADERS)

        self.user = CONSTANTS.USERNAME
        self.password = CONSTANTS.PASSWORD
        self.logged_in = False
        self.refreshToken = None

    def login(self):
        payload = {
            'id': self.user,
            'secret': self.password
        }

        token_data = self._session.post(LOGIN_URL, json=payload,
                                        headers=CONSTANTS.HEADERS).json()

        if 'code' in token_data:
            raise ConnectionError(
                'Error while logging in. Possibly invalid username/password')

        self.refreshToken = token_data['refreshToken']
        self._session.headers.update(
            {'Authorization': f'Bearer {token_data["authorisationToken"]}'})
        print('Succesfully logged in')
        self.logged_in = True

    def get_video_info(self, request: EpisodeDownloadRequest):
        video_id = request.episode_id
        response = self._session.get(
            f'{INFO_PATH}{video_id}?includePlaybackDetails=URL').json()

        try:
            if response['message']:
                raise RuntimeError(f'Video with ID {video_id} not found')
        except KeyError:
            pass

        if response['accessLevel'] == 'DENIED':
            raise ConnectionRefusedError(
                f'You don\'t have access to video with ID {video_id}')

        episode_info = response.get('episodeInformation')
        series_info = episode_info.get(
            'seriesInformation') if episode_info else None
        series = series_info.get('title') if series_info else None
        season = episode_info.get('seasonTitle') if episode_info else None
        season_number = episode_info.get(
            'seasonNumber') if episode_info else None
        episode_number = episode_info.get(
            'episodeNumber') if episode_info else None

        m3u8_url, subtitles_url, chapter_titles_url, chapter_thumbnails_url = self.get_streams(
            response['playerUrlCallback'])

        episode_title = response.get('title')

        custom_title = request.output_filename if request.output_filename else episode_title

        if request.filename_date_prefix:
            date = self.parse_date(episode_title)
            if date:
                custom_title = f'[{date}] {custom_title}'

        return VideoInfo(id=video_id,
                         title=response['title'],
                         custom_title=utils.clean_text(custom_title),
                         description=response['description'],
                         long_description=response['longDescription'],
                         duration_seconds=response['duration'],
                         thumbnail_url=response['thumbnailUrl'],
                         series=series,
                         season=season,
                         season_number=season_number,
                         episode_number=episode_number,
                         preview_thumbnails_url=response['thumbnailsPreview'],
                         base_url=m3u8_url.split('.m3u8')[0].rsplit('/', 1)[0],
                         m3u8_url=m3u8_url,
                         subtitle_url=subtitles_url,
                         chapter_titles_url=chapter_titles_url,
                         chapter_thumbnails_url=chapter_thumbnails_url)

    def get_streams(self, callback_url):
        stream = self._session.get(callback_url,
                                   headers=CONSTANTS.HEADERS).json()

        m3u8 = stream['hls'][0]['url']

        for i in stream['hls'][0]['subtitles']:
            if i['format'] == "vtt":
                subtitle_stream = i['url']
                break

        try:
            chapter_titles = stream['annotations']['titles']
            chapter_thumbnails = stream['annotations']['thumbnails']
        except TypeError:
            chapter_titles = None
            chapter_thumbnails = None

        return m3u8, subtitle_stream, chapter_titles, chapter_thumbnails

    def write_metadata(self, request: EpisodeDownloadRequest,
        video_info: VideoInfo):
        print("\nStarting to write the metadata file")
        title = utils.clean_text(video_info.title)
        meta_file = open(
            f"{CONSTANTS.TEMP_FOLDER}/{video_info.custom_title}-metafile", "w")
        # TODO: write other metadata
        meta_file.write(f";FFMETADATA1\n\
    title={title}\n")

        if request.chapters and video_info.chapter_titles_url:
            print("\nWriting chapter information")

            start_time = request.start_time if request.start_time else 0
            end_time = request.end_time if request.end_time else video_info.duration_seconds + 1

            # Get the chapter data
            chapter_data = self._session.get(
                video_info.chapter_titles_url).content.decode('utf-8')
            # Match the chapter information. Example is below
            #
            # 402712                                        <----- Ignored
            # 00:18:47.601 --> 00:31:26.334                 <----- Wanted
            # Steamboat vs Pillman: Halloween Havoc 1992    <----- Wanted

            chapters = re.findall(
                r'(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)\n\n',
                chapter_data)

            # Write the chapter information.
            # We loop through all the chapters, but only write the information which is between
            # our start and stop time.
            for chapter in chapters:
                timestamp = re.findall(r'(\d{2}:\d{2}:\d{2})', chapter[0])
                timestamp_start = utils.time_to_seconds(timestamp[0])
                timestamp_end = utils.time_to_seconds(timestamp[1])

                if (timestamp_end >= start_time and (
                    end_time == 0 or timestamp_end <= end_time)):
                    print(
                        f"{html.unescape(chapter[1])}: {timestamp_start} - {timestamp_end}")
                    meta_file.write(
                        f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={str(timestamp_start * 1000)}\nEND={str(timestamp_end * 1000)}\ntitle={html.unescape(chapter[1])}\n\n")

            print("Finished writing chapter information\n")

        print("\nStarting to write the stream title")
        meta_file.write(f"[STREAM]\ntitle={title}")
        print("Finished writing the stream title\n")

        print("Finished writing the metadata file")
        meta_file.close()

    def parse_date(self, input):
        # Regex matches the format "Month. DD, YYYY"
        date_pattern = r'([A-Za-z]+)\.\s+(\d{2}),\s+(\d{4})$'

        # Check if the input ends with a date in this format
        match = re.search(date_pattern, input)

        if match:
            # Extract the components from the matched date
            month, day, year = match.groups()

            # Parse to date object
            try:
                date_obj = datetime.strptime(f'{month} {day} {year}',
                                             '%b %d %Y')
                # Format the date as 'YYYY-MM-DD' and return it
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None

        return None
