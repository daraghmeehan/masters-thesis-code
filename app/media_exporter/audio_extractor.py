import datetime
from pathlib import Path
import subprocess
import ffmpeg


class AudioExtractor:
    """
    A class for extracting audio tracks and segments from video files.

    Attributes:
        output_folder (str): Directory where extracted audio tracks will be saved.
        audio_tracks (dict): A dictionary mapping language names to the paths of extracted audio tracks.
    """

    def __init__(self, output_folder: Path) -> None:
        """
        Initializes the AudioExtractor with the specified output folder.

        Args:
            output_folder (Path): Directory where extracted audio tracks will be saved.
        """
        self.output_folder = output_folder
        self.audio_tracks = {}

    def extract_all_language_tracks(self, video_file: Path, audio_tracks: dict) -> None:
        """
        Extracts audio tracks for all specified languages from a video file.

        Args:
            video_file (Path): Path to the input video file.
            audio_tracks (dict): A dictionary mapping language names to their corresponding audio track name, e.g. {"English": "eng"}.
        """
        for language, audio_track_name in audio_tracks.items():
            if audio_track_name == "None":
                # If a given language has no corresponding audio track, e.g. if it only has a subtitle file
                continue

            audio_track = self.extract_audio_track(
                video_file, language, audio_track_name
            )
            self.audio_tracks[language] = audio_track

    # TODO: Need to normalise volume of audio tracks
    def extract_audio_track(
        self, video_file: Path, language: str, audio_track_name: str
    ) -> Path:
        """
        Extracts a specific audio track from a video file based on the provided language and track name.

        Args:
            video_file (Path): Path to the input video file.
            language (str): The language name for which the audio track should be extracted, e.g. "English".
            audio_track_name (str): The name of the audio track to extract, e.g. "eng" for English.

        Returns:
            Path: Path to the extracted audio file.

        Raises:
            ValueError: If no audio stream is found for the specified language.
        """
        # Get the index of the audio stream of the given language
        audio_stream_index = None
        streams = ffmpeg.probe(str(video_file))["streams"]
        for i, stream in enumerate(streams):
            if (
                stream["codec_type"] == "audio"
                and stream["tags"].get("language") == audio_track_name
            ):
                audio_stream_index = i - 1
                break
        if audio_stream_index is None:
            raise ValueError(f"No audio stream found for {language}")

        # Was WAV before (which works quicker with MP4)
        audio_track = self.output_folder / f"{video_file.stem}-{language}.mp3"

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i",
            str(video_file),
            "-map",
            f"0:a:{audio_stream_index}",
            "-map_metadata",
            "0",
            "-movflags",
            "use_metadata_tags",
            "-ab",
            "48k",
            str(audio_track),  # Output file path
        ]

        # Run the command using subprocess
        subprocess.run(command)

        return audio_track

    def extract_segment(
        self,
        language: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        segment_name: str,
    ) -> Path:
        """
        Extracts a segment of an audio file between the specified start and end times.

        Args:
            language (str): The language name of the audio file to extract the segment from.
            start_time (datetime.datetime): The start time of the segment.
            end_time (datetime.datetime): The end time of the segment.
            segment_name: (str): What name to save the segment with.

        Returns:
            Path: Path to the extracted audio segment file.
        """
        audio_track = self.audio_tracks[language]
        start_time_str = convert_datetime_to_ffmpeg_time(start_time)
        end_time_str = convert_datetime_to_ffmpeg_time(end_time)

        audio_segment_path = self.output_folder / f"{segment_name}.mp3"

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i",
            str(audio_track),
            "-ss",
            start_time_str,
            "-to",
            end_time_str,
            "-c",  # Before was "-acodec"
            "copy",
            str(audio_segment_path),
        ]

        # Run the command using subprocess
        subprocess.run(command)
        return audio_segment_path


def convert_datetime_to_ffmpeg_time(time: datetime.datetime) -> str:
    """
    Converts a datetime object to a string format suitable for use with ffmpeg.

    Args:
        time (datetime.datetime): The datetime object to convert.

    Returns:
        str: The converted time string in "H:MM:SS.sss" format.
    """
    return time.strftime("%H:%M:%S.%f")[:-3]
