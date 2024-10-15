from model.download_request import SeasonDownloadRequest, EpisodeDownloadRequest
from model.season_info import SeasonInfo
from wwe.episode_downloader import download_episode
from wwe.wwe_v2 import WWEClient


def download_season(request: SeasonDownloadRequest):
    client = WWEClient()
    client.login()
    season_info = client.get_season_info(request)
    episode_download_requests = build_episode_download_requests(season_info,
                                                                request)
    for episode in episode_download_requests:
        download_episode(episode, client)


def build_episode_download_requests(season_info: SeasonInfo,
    request: SeasonDownloadRequest):
    episode_download_requests = []
    for episode in season_info.episodes:
        episode_download_requests.append(
            EpisodeDownloadRequest(
                episode_id=episode,
                start_time=None,
                end_time=None,
                output_filename=None,
                filename_date_prefix=request.filename_date_prefix,
                quality=request.quality,
                force=request.force,
                chapters=request.chapters,
                subtitles=request.subtitles,
                keep_files=request.keep_files
            )
        )
    return episode_download_requests
