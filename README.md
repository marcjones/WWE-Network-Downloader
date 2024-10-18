WWE Network 2.0 Downloader (Improved)

Fork of Freyta's WWE Network 2.0 Downloader using Python3. This was coded by me from scratch, ideas were taken from youtube-dl.

Features include the following:
- Download single episodes or whole seasons
- Downloading episodes between set start and end times (i.e. only downloading certain matches)
- Quality selection (0 being 1080p high, 6 being 288p)
- Partial downloading of seasons, limiting by number of episodes or starting / stopping at specific episodes

### Prerequisites

#### Install ffmpeg
You must have at least version 4.2 ffmpeg installed and in your PATH. You can get ffmpeg from Homebrew:

`brew install ffmpeg`

#### Install Python requirements
Using pip3 install the required modules:

`pip3 install --user -r requirements.txt`

#### Store WWE Network credentials
Make a copy of `.env.template` named `.env`

Edit the username and password variables in `.env` to include your subscription email and password.

### Usage instructions

###### Basic episode download:

`python3 main.py -e https://network.wwe.com/video/67585`

###### Basic season download:

`python3 main.py -s https://network.wwe.com/season/15076`

###### Download episode with start and end times, using custom file name:

`python3 main.py -st 00:49:04 -et 00:59:41 -of 'Chris Jericho vs Maven' -t https://network.wwe.com/video/67585`

###### Download chapterised 720p video with date-prefixed output filename:

`-dp` looks for a date in the episode title and adds it as a prefix for the output filename. e.g. `[2002-01-07] Raw - Jan. 07, 2002`. This is useful for sorting episodes chronologically. If you were downloading all Raw, SmackDown, and PPV events in 2002 for example and wanted to watch them in order - adding this date prefix, placing all files in the same directory, and sorting by name would mean all events are sorted by air date. 

`python3 main.py -c -dp -q 2 -e https://network.wwe.com/video/67585`

### Options

#### Required options

One of the following two options must be provided:
> **-e** / **--episode** - Link or ID of single episode to download.\
> **-s** / **--season** - Link or ID of season to download.

#### Episode only options
> **-st** / **--start-time** - Start time in `HH:MM:SS` format - where to start downloading.\
> **-et** / **--end-time** - End time in `HH:MM:SS` format - where you want to finish downloading.\
> **-of** / **--output-filename** - Specify custom name for output file.

#### Season only options
> **--episode-count** - Max number of episodes to download.\
> **--season-from** - Link or ID of episode to start downloading from (ignore earlier episodes).\
> **--season-to** - Link or ID of episode to stop downloading after (ignore later episodes).

#### Other options
> **-q** / **--quality** - Quality of the video you want to download. 0 is 1080p high (default) 6 is 288p (lowest).\
> **-c** / **--chapters** - Add milestone chapters to the video.\
> **-sb** / **--subtitles** - Downloads the subtitles.\
> **-k** / **--keep-files** - Keep temporary aac and ts files.\
> **-od** / **--output-dir** - Custom name for output directory (within `/output`).\
> **-dp** / **--date-prefix** - Prefix output files with episode date in `[YYYY-MM-DD]` format (useful for chronological sorting).\
> **-f** / **--force** - Force the download of the video. Overwrites previously downloaded files.



