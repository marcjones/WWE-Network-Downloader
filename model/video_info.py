from dataclasses import dataclass


@dataclass
class VideoInfo:
    id: str
    title: str
    custom_title: str
    description: str
    long_description: str
    duration_seconds: int
    thumbnail_url: str
    series: str
    season: str
    season_number: int
    episode_number: int
    preview_thumbnails_url: str
    base_url: str
    m3u8_url: str
    subtitle_url: str
    chapter_titles_url: str
    chapter_thumbnails_url: str
