from dataclasses import dataclass

from m3u8 import M3U8


@dataclass
class EpisodeDownloadRequest:
    episode_id: str
    start_time: int
    end_time: int
    output_filename: str
    filename_date_prefix: bool
    output_dir: str
    quality: int
    force: bool
    chapters: bool
    subtitles: bool
    keep_files: bool


@dataclass
class SeasonDownloadRequest:
    season_id: str
    episode_count: int
    episode_from_id: str
    episode_to_id: str
    filename_date_prefix: bool
    output_dir: str
    quality: int
    force: bool
    chapters: bool
    subtitles: bool
    keep_files: bool


@dataclass
class MediaDownloadRequest:
    playlist: M3U8
    base_url: str
    title: str
    start_time: int
    end_time: int
