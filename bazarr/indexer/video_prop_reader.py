# coding=utf-8

import logging
import os
from knowit import api
import enzyme
from enzyme.exceptions import MalformedMKVError

from utils import get_binary
from database import TableEpisodes, TableMovies
from get_languages import create_languages_dict, language_from_alpha3

VIDEO_EXTENSION = [
    # Unknown
    ".webm",

    # SDTV
    ".m4v",
    ".3gp",
    ".nsv",
    ".ty",
    ".strm",
    ".rm",
    ".rmvb",
    ".m3u",
    ".ifo",
    ".mov",
    ".qt",
    ".divx",
    ".xvid",
    ".bivx",
    ".nrg",
    ".pva",
    ".wmv",
    ".asf",
    ".asx",
    ".ogm",
    ".ogv",
    ".m2v",
    ".avi",
    ".bin",
    ".dat",
    ".dvr-ms",
    ".mpg",
    ".mpeg",
    ".mp4",
    ".avc",
    ".vp3",
    ".svq3",
    ".nuv",
    ".viv",
    ".dv",
    ".fli",
    ".flv",
    ".wpl",

    # HD
    ".mkv",
    ".mk3d",
    ".ts",
    ".wtv",

    # Bluray
    ".m2ts",
]


def video_prop_reader(file):
    video_prop = {}

    if os.path.splitext(file)[1] not in VIDEO_EXTENSION:
        logging.debug(f'Unsupported file extension: {file}')
        return video_prop

    ffprobe_path = get_binary("ffprobe")

    # if we have ffprobe available
    if ffprobe_path:
        api.initialize({"provider": "ffmpeg", "ffmpeg": ffprobe_path})
        data = api.know(file)
    # if not, we use enzyme for mkv files
    elif not ffprobe_path and os.path.splitext(file)[1] == "mkv":
        if os.path.splitext(file)[1] == ".mkv":
            with open(file, "rb") as f:
                try:
                    mkv = enzyme.MKV(f)
                except MalformedMKVError:
                    logger.error(
                        "BAZARR cannot analyze this MKV with our built-in MKV parser, you should install "
                        "ffmpeg/ffprobe: " + file
                    )
                else:
                    data = mkv
    else:
        logging.debug(f"ffprobe not available and enzyme doesn't support this file extension: {file}")

    if data:
        audio_language = []
        video_format = None
        video_resolution = None
        video_codec = None
        audio_codec = None
        file_size = None

        if ffprobe_path:
            file_size = data['size']
            if 'video' in data and len(data['video']):
                video_resolution = data['video'][0]['resolution']
                if 'codec' in data['video'][0]:
                    video_codec = data['video'][0]['codec']
            if 'audio' in data and len(data['audio']):
                audio_codec = data['audio'][0]['codec']
                for audio_track in data['audio']:
                    if 'language' in audio_track:
                        audio_lang = audio_track['language'].alpha3
                        if audio_lang:
                            converted_audio_lang = language_from_alpha3(audio_track['language'].alpha3)
                            if converted_audio_lang and converted_audio_lang not in audio_language:
                                audio_language.append(converted_audio_lang)
                            elif not converted_audio_lang:
                                pass
                            else:
                                pass
        elif not ffprobe_path and os.path.splitext(file)[1] == "mkv":
            file_size = os.path.getsize(file)
            if len(data.video_tracks):
                for video_track in data.video_tracks:
                    video_resolution = str(video_track.height) + 'p'
                    video_codec = video_track.codec_id

            if len(data.audio_tracks):
                audio_codec = data.audio_tracks[0].codec_id
                for audio_track in data.audio_tracks:
                    audio_language.append(audio_track.name)

        video_prop['audio_language'] = str(audio_language)
        video_prop['format'] = video_format
        video_prop['resolution'] = video_resolution
        video_prop['video_codec'] = video_codec
        video_prop['audio_codec'] = audio_codec
        video_prop['file_size'] = file_size

    return video_prop