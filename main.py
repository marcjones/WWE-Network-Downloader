import argparse
from shutil import which

from util import utils, CONSTANTS
from model.download_request import EpisodeDownloadRequest
from model.download_request import SeasonDownloadRequest
from wwe.episode_downloader import download_episode
from wwe.season_downloader import download_season


def check_dependencies():
    if which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found. Please ensure it is installed and exists on "
            "your PATH.")
    if CONSTANTS.USERNAME == "" or CONSTANTS.PASSWORD == "":
        raise RuntimeError(
            "Missing login credentials - Please ensure a `.env` file exists "
            "with your WWE Network username and password. Check the README "
            "for instructions.")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Download videos from WWE Network.')

    content_ids = parser.add_mutually_exclusive_group(required=True)

    # Download either an episode or a season. Exactly 1 arg supported of these 2
    content_ids.add_argument('-e', '--episode', type=str,
                             help='Link or ID of episode to download. e.g. '
                                  'https://network.wwe.com/video/178225 or '
                                  '178225')
    content_ids.add_argument('-s', '--season', type=str,
                             help='Link or ID of season to download. e.g. '
                                  'https://network.wwe.com/season/15072 or '
                                  '15072')

    # Episode only args
    parser.add_argument('-st', '--start_time',
                        help='Where in the episode to start the download in '
                             'HH:MM:SS (not supported for season downloads)',
                        required=False)
    parser.add_argument('-et', '--end_time',
                        help='Where in the episode to stop the download in '
                             'HH:MM:SS (not supported for season downloads)',
                        required=False)
    parser.add_argument('-of', '--output_filename',
                        help='Custom output file name (not supported for '
                             'season downloads)',
                        required=False)

    # Season only args
    parser.add_argument('--episode-count', type=int,
                        help='Maximum number of episodes to download when '
                             'downloading a season. Defaults to no limit. Can '
                             'be used in combination with --season-from. If '
                             'used with --season-to then whichever limitation '
                             'is reached first will override the other.',
                        required=False, default=0)
    parser.add_argument('--season-from', type=str,
                        help='Link or ID of the episode to start downloading '
                             'from when downloading a season. e.g. '
                             'https://network.wwe.com/video/178225 or 178225. '
                             'When present, any episodes that appear before '
                             'the one specified in the seasons episode list '
                             'will NOT be downloaded.', required=False)
    parser.add_argument('--season-to', type=str,
                        help='Link or ID of the episode to stop downloading '
                             'at when downloading a season. e.g. '
                             'https://network.wwe.com/video/178225 or 178225. '
                             'When present, any episodes that appear after '
                             'the one specified in the seasons episode list '
                             'will NOT be downloaded.', required=False)

    # Shared args
    # TODO: fix quality selection properly
    parser.add_argument('-q', '--quality',
                        help='Quality of video to download. Value between 0 ('
                             'highest) and 6 (lowest). Defaults to 0 (1080p '
                             'HIGH)',
                        required=False, default=0)
    parser.add_argument('-c', '--chapters',
                        help='Add chapter "milestones" to the video',
                        required=False, action='store_true')
    parser.add_argument('-sb', '--subtitles',
                        help='Add subtitles to the video', required=False,
                        action='store_true')
    parser.add_argument('-k', '--keep_files',
                        help='Keep the temporary download files',
                        required=False,
                        action='store_true')
    parser.add_argument('-od', '--output_dir',
                        help='Custom output directory name (under /output)',
                        required=False)
    parser.add_argument('-dp', '--date_prefix',
                        help='Prefix the output file with episode date in '
                             'YYYY-MM-DD format',
                        required=False, action='store_true')
    parser.add_argument('-f', '--force',
                        help='Overwrite previously downloaded files',
                        required=False, action='store_true')

    return parser.parse_args()


def build_episode_download_request(args):
    start_time = utils.time_to_seconds(
        args.start_time) if args.start_time else None
    end_time = utils.time_to_seconds(args.end_time) if args.end_time else None

    return EpisodeDownloadRequest(
        episode_id=(get_media_id(args.episode)),
        start_time=start_time,
        end_time=end_time,
        output_filename=args.output_filename,
        filename_date_prefix=args.date_prefix,
        output_dir=args.output_dir,
        quality=args.quality,
        force=args.force,
        chapters=args.chapters,
        subtitles=args.subtitles,
        keep_files=args.keep_files
    )


def build_season_download_request(args):
    episode_from = get_media_id(args.season_from) if args.season_from else None
    episode_to = get_media_id(args.season_to) if args.season_to else None

    return SeasonDownloadRequest(
        season_id=get_media_id(args.season),
        episode_count=args.episode_count,
        episode_from_id=episode_from,
        episode_to_id=episode_to,
        filename_date_prefix=args.date_prefix,
        output_dir=args.output_dir,
        quality=args.quality,
        force=args.force,
        chapters=args.chapters,
        subtitles=args.subtitles,
        keep_files=args.keep_files
    )


def get_media_id(input_val):
    media_id = utils.parse_media_id(input_val)
    if not media_id:
        raise argparse.ArgumentError(
            'ERROR: Invalid media link or id - a valid episode or season URL '
            'or ID must be provided')
    return media_id


def quality_validator(value):
    quality = int(value)
    max_value = len(CONSTANTS.VIDEO_QUALITY)
    if quality < 0 or quality >= max_value:
        raise argparse.ArgumentError(
            f"Invalid value for 'quality' - must be a number between 0 and "
            f"{max_value}")
    return quality


def main():
    check_dependencies()
    args = parse_args()
    if args.episode:
        request = build_episode_download_request(args)
        download_episode(request)
    else:
        request = build_season_download_request(args)
        download_season(request)


if __name__ == "__main__":
    main()
