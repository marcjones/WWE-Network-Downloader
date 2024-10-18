from model.download_request import SeasonDownloadRequest, EpisodeDownloadRequest
from model.season_info import SeasonInfo
from wwe.episode_downloader import download_episode
from wwe.wwe_v2 import WWEClient


def download_season(request: SeasonDownloadRequest):
    client = WWEClient()
    season_info = client.get_season_info(request)
    episode_download_requests = build_episode_download_requests(season_info,
                                                                request)
    for episode in episode_download_requests:
        download_episode(episode, client)


def build_episode_download_requests(season_info: SeasonInfo,
    request: SeasonDownloadRequest):
    episode_download_requests = []
    start_downloading = False if request.episode_from_id else True

    print(f'Processing episodes from season "{season_info.title}"')
    print('Eligible episodes will be queued for download')

    for episode in season_info.episodes:
        if not start_downloading and episode == request.episode_from_id:
            print(
                f'Found first episode {request.episode_from_id}, will start '
                f'queueing episodes for download from here')
            start_downloading = True

        if start_downloading:
            print(f'Adding episode ID {episode} to download queue')
            episode_download_requests.append(
                EpisodeDownloadRequest(
                    episode_id=episode,
                    start_time=None,
                    end_time=None,
                    output_filename=None,
                    filename_date_prefix=request.filename_date_prefix,
                    output_dir=request.output_dir if request.output_dir else season_info.title,
                    quality=request.quality,
                    force=request.force,
                    chapters=request.chapters,
                    subtitles=request.subtitles,
                    keep_files=request.keep_files
                )
            )

        if (request.episode_to_id and episode == request.episode_to_id) or (
            0 < request.episode_count == len(episode_download_requests)):
            print(
                f'Maximum episode limit reached at episode {episode}. No '
                f'further episodes will be queued for download')
            break

    print(
        f'Queued {len(episode_download_requests)} episodes from '
        f'{season_info.title} for download.')

    return episode_download_requests
