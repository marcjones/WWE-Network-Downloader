from dataclasses import dataclass


@dataclass
class EpisodeDownloadRequest:
    episode_id: str
    start_time: int
    end_time: int
    output_filename: str
    filename_date_prefix: bool
    quality: int
    force: bool
    chapters: bool
    subtitles: bool
    keep_files: bool


@dataclass
class SeasonDownloadRequest:
    season_id: str
    filename_date_prefix: bool
    quality: int
    force: bool
    chapters: bool
    subtitles: bool
    keep_files: bool
