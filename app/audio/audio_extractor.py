from pathlib import Path
import ffmpeg
import subprocess
import datetime


class AudioExtractor:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.audio_files = {}

    def extract_all_language_tracks(self, video_file, audio_tracks):
        for language, audio_track in audio_tracks.items():
            if audio_track == "None":
                continue

            audio_file = self.extract_audio_track(video_file, language, audio_track)
            self.audio_files[language] = audio_file

    def extract_audio_track(self, video_file, language, audio_track):
        # First get the index of the audio stream of the given language
        audio_stream_index = None
        streams = ffmpeg.probe(video_file)["streams"]
        for i, stream in enumerate(streams):
            if (
                stream["codec_type"] == "audio"
                and stream["tags"].get("language") == audio_track
            ):
                audio_stream_index = i - 1
                break
        if audio_stream_index is None:
            raise ValueError(f"No audio stream found for {language}")

        video_file_name = Path(video_file).stem
        audio_file = f"{self.output_folder}/{video_file_name}-{language}.wav"

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # overwrites by default
            "-i",
            video_file,
            "-map",
            f"0:a:{audio_stream_index}",
            "-map_metadata",
            "0",
            "-movflags",
            "use_metadata_tags",
            "-ab",
            "48k",
            audio_file,  # output
        ]

        # Run the command using subprocess
        subprocess.run(command)

        return audio_file

    def extract_segment(self, language, start_time, end_time, is_for_flashcard):
        audio_file = self.audio_files[language]

        start_time = convert_datetime_to_ffmpeg_time(start_time)
        end_time = convert_datetime_to_ffmpeg_time(end_time)

        if is_for_flashcard:
            audio_segment_path = f"{self.output_folder}/flashcard_segment.wav"
        else:
            audio_segment_path = f"{self.output_folder}/segment.wav"

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # overwrites by default
            "-i",
            f"{audio_file}",
            "-ss",
            f"{start_time}",
            "-to",
            f"{end_time}",
            "-c",  # was "-acodec"
            "copy",
            audio_segment_path,
        ]

        # Run the command using subprocess
        subprocess.run(command)

        return audio_segment_path


def convert_datetime_to_ffmpeg_time(time):
    ffmpeg_time = time.strftime("%H:%M:%S.%f")[:-3]
    return ffmpeg_time
