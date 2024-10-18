import re


def clean_text(text):
    # Thanks to https://stackoverflow.com/a/27647173
    return re.sub(r'[\\\\\\\'/*?:"<>|]', "", text)


def time_to_seconds(time):
    time_in_seconds = 0
    time_matches = re.match("\\b(\d{2}):\\b(\d{2}):\\b(\d{2})", time)

    if time_matches:
        # 1 Hour
        seconds = 3600
        for i in range(1, 4):
            # Multiply the hours/minutes by the corrosponding seconds
            t = int(time_matches.group(i)) * seconds
            time_in_seconds += t
            # Divide the seconds by 60 so we get 60 seconds per minute,
            # and then 1 for every second
            seconds = int(seconds / 60)
    else:
        print("Invalid time format. Please use HH:MM:SS.")
        exit()
    return time_in_seconds


def parse_media_id(input_val):
    if input_val.isdigit():
        return input_val

    match = re.search(r'/(\d+)(?:\?|$)', input_val)
    if match:
        return match.group(1)

    return None
