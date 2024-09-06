import subprocess
from pathlib import Path
from datetime import datetime
import ffmpeg
from typing import Dict, List, Optional, Union, Tuple

from model.model import SubtitleModel

BITRATE = "48k"


class MediaExporter:
    """
    A class responsible for processing media exports based on user-defined options.

    This class manages the export of media by handling tasks such as segmenting, interleaving,
    and combining audio files.

    Attributes:
        temporary_audio_folder (Path): The path to the folder where temporary audio files will be stored.
        avi_practice_audio_folder (Path): The path to the folder where final AVI practice audio files will be stored.
    """

    def __init__(
        self, temporary_audio_folder: Path, avi_practice_audio_folder: Path
    ) -> None:
        """
        Initializes the MediaExporter with specified folders for temporary and final audio storage.

        Args:
            temporary_audio_folder (Path): The folder to store temporary audio files.
            avi_practice_audio_folder (Path): The folder to store final AVI practice audio files.
        """
        self.temporary_audio_folder = temporary_audio_folder
        self.avi_practice_audio_folder = avi_practice_audio_folder

    def export_media(self, options: dict) -> None:
        """
        Processes the media export based on provided options.

        Args:
            options (dict): A dictionary containing all the export options. The dictionary keys are expected to be:
                - "video_file" (Path): The path to the video file.
                - "reference_subtitle_file" (Path): The path to the reference subtitle file.
                - "subtitle_padding" (int): Padding for subtitles.
                - "segmenting" (Dict): Options for segmenting, with keys:
                    - "enabled" (bool): Whether segmenting is enabled.
                    - "segment_length" (Optional[int]): Length of segments if segmenting is enabled, otherwise None.
                - "interleaving" (Dict): Options for interleaving, with keys:
                    - "enabled" (bool): Whether interleaving is enabled.
                    - "combine_interleaved_segments" (bool): Whether to combine interleaved segments, only applicable if interleaving is enabled.
                - "file_combination" (str): File combination option, either "combine_everything" or "separate_files".
                - "language_options" (List[Dict[str, Union[str, float]]]): List of dictionaries, each containing:
                    - "audio_track" (str): The audio track for the language.
                    - "speed" (float): Playback speed for the audio track.
        """
        video_file = options["video_file"]
        reference_subtitle_file = options["reference_subtitle_file"]
        # TODO: Include padding in file names
        subtitle_padding = options["subtitle_padding"]
        segmenting = options["segmenting"]
        interleaving = options["interleaving"]
        # TODO: Make file combination one of five options: all_single_lines, segments (if segmenting), combined_interleaved_segments (if segmenting+interleaving), complete_files_per_language_track, all_combined
        file_combination = options["file_combination"]
        language_options = options["language_options"]

        if not video_file.exists():
            print("Need a video.")
            return

        if not reference_subtitle_file.exists():
            print("Need a reference subtitle file.")
            return

        if not language_options:
            print("Need at least one audio track.")
            return

        final_files = self.process_files(
            video_file,
            reference_subtitle_file,
            subtitle_padding,
            segmenting,
            interleaving,
            file_combination,
            language_options,
        )

        # Need to copy the final file(s) to ensure consistency! Otherwise files can be unstable, e.g. with unstable total duration/end time.
        print("Saving files.")

        # TODO: Create a folder if creating lots of separate files :)
        # create_folder = file_combination == "separate_files"
        # folder_name = self.create_folder_name()
        # self.save_files(files=final_files, output_folder=self.avi_practice_audio_folder, create_folder=create_folder)

        self.save_files(files=final_files, output_folder=self.avi_practice_audio_folder)
        print("Successfully saved files.")

        # TODO: Perhaps should clean temp files here instead of at end of exporting all files.

    def process_files(
        self,
        video_file: Path,
        reference_subtitle_file: Path,
        subtitle_padding: int,
        segmenting: Dict,
        interleaving: Dict,
        file_combination: str,
        language_options: List[Dict[str, Union[str, float]]],
    ) -> List[Path]:
        """ """

        # TODO: Implement the actual file processing logic.
        print("\nChosen options:")
        print(f"Video file: {video_file}")
        print(f"Using subtitle: {reference_subtitle_file}")
        print(f"Subtitle padding: {subtitle_padding}")
        print(f"Segmenting: {segmenting}")
        print(f"Interleaving: {interleaving}")
        print(f"File combination: {file_combination}")
        print(f"Language options: {language_options}\n")

        ### STEPS (for single condensed file) ###

        # TODO: Need to refactor this/AudioExtractor in future as code is repeated in slightly different ways.

        ## 1. Extract audio tracks from video
        # TODO: Perhaps refactor this into `extract_all_audio_tracks`
        # Extracting unique audio tracks with set comprehension
        audio_tracks = list({option["audio_track"] for option in language_options})
        audio_track_paths = {}

        for audio_track in audio_tracks:
            print(f"Extracting {audio_track} audio track.")
            # TODO: Try simply using the audio tracks inside the video file.
            audio_track_path = self.extract_audio_track(
                video_file=video_file, audio_track=audio_track
            )
            audio_track_paths[audio_track] = audio_track_path
            print("Finished extracting audio track.")

        ## 2. Read reference subtitle file & build timings with padding
        subtitle_model = SubtitleModel(
            language="Reference", filename=reference_subtitle_file
        )
        subtitle_timings = subtitle_model.get_all_speaking_times(
            subtitle_padding=subtitle_padding
        )

        ## 3. Extract all lines of dialogue to temp files
        # TODO: Use ffmpeg's filter_complex to process multiple segments at once
        for language_option in language_options:
            audio_track = language_option["audio_track"]
            speed = language_option["speed"]

            print(
                f"Extracting all lines of dialogue of {audio_track} audio track at {speed}x speed."
            )

            for line_number, subtitle_timing in enumerate(subtitle_timings):
                segment_name = (
                    f"{video_file.stem}-{audio_track}-{speed}x_line{line_number}"
                )
                self.extract_segment(
                    audio_file=audio_track_paths[audio_track],
                    start_time=subtitle_timing[0],
                    end_time=subtitle_timing[1],
                    speed=speed,
                    segment_name=segment_name,
                )

            print("Finishing extracting lines of dialogue.")

        # For naming audio tracks alphabetically with appropriate amount of digits, e.g. lang_1, ..., lang_3
        num_audio_tracks = len(language_options)
        num_audio_track_digits = len(str(num_audio_tracks))

        # TODO: Major refactoring required to make this all easier to read/manage :)

        ## 4a. Combining lines to create simple condensed files
        if (
            not segmenting["enabled"]
            or (
                not interleaving["enabled"] and file_combination == "combine_everything"
            )
            or len(language_options) == 1
        ):
            if file_combination == "combine_everything" or len(language_options) == 1:
                # Creating one file of all language 1's dialogue, then language 2, etc.
                print("Creating a simple condensed file with all language tracks.")
                files_to_combine = [
                    self.temporary_audio_folder
                    / f"{video_file.stem}-{option['audio_track']}-{option['speed']}x_line{line_number}.mp3"
                    for option in language_options
                    for line_number in range(len(subtitle_timings))
                ]
                # TODO: Definitely refactor this first, as used 6 times.
                language_and_speed_str = "-".join(
                    [
                        f"{option['audio_track']}{option['speed']}x"
                        for option in language_options
                    ]
                )
                # E.g. video_name-eng1.2x-dut1.0x-ita0.8x.mp3
                everything_combined_file = (
                    self.temporary_audio_folder
                    / f"{video_file.stem}-{language_and_speed_str}.mp3"
                )
                self.combine_audio_files(
                    files_to_combine=files_to_combine,
                    output_file=everything_combined_file,
                )
                print("Created a simple condensed file with all language tracks.")
                return [everything_combined_file]
            else:
                # Creating separate files of all language 1's dialogue, language 2's dialogue, etc.
                print("Creating simple condensed files for each language track.")
                final_files = []
                for audio_track_number, option in enumerate(language_options):
                    audio_track, speed = option["audio_track"], option["speed"]
                    files_to_combine = [
                        self.temporary_audio_folder
                        / f"{video_file.stem}-{audio_track}-{speed}x_line{line_number}.mp3"
                        for line_number in range(len(subtitle_timings))
                    ]
                    # E.g. video_name-lang1-eng-1.0x.mp3
                    combined_file_name = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x.mp3"
                    )
                    self.combine_audio_files(
                        files_to_combine=files_to_combine,
                        output_file=combined_file_name,
                    )
                    final_files.append(combined_file_name)
                print("Created simple condensed files for each language track.")
                return final_files

        ## 4b. If using segmenting, create segments, then combine lines of dialogue to create segments for every audio track
        # TODO: Make this part of SubtitleModel probably.
        segment_indices = self.segment_subtitle_timings(
            subtitle_timings=subtitle_timings,
            segment_length=segmenting["segment_length"],
        )

        # For naming segments alphabetically with appropriate amount of digits, e.g. segment_01, ..., segment_25
        num_segments = len(segment_indices)
        num_segments_digits = len(str(num_segments))

        print("Combining lines of dialogue together.")
        # TODO: File with í in its name couldn't be copied with ffmpeg.

        for audio_track_number, language_option in enumerate(language_options):
            audio_track = language_option["audio_track"]
            speed = language_option["speed"]
            for segment_number, segment in enumerate(segment_indices):
                files_to_combine = [
                    self.temporary_audio_folder
                    / f"{video_file.stem}-{audio_track}-{speed}x_line{line_number}.mp3"
                    for line_number in segment
                ]
                segment_file = (
                    self.temporary_audio_folder
                    / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x-segment{segment_number:0{num_segments_digits}}.mp3"
                )
                self.combine_audio_files(
                    files_to_combine=files_to_combine, output_file=segment_file
                )

        print("Finishing combining lines of dialogue together.")

        if not interleaving["enabled"]:
            print("Saving separate segments for each language.")
            # TODO: Already checked that combine all was off for this, but instead should run e.g. self.create_simple_condensed_audio_file() here instead if interleaving disabled and combine everything chosen
            final_files = []
            for audio_track_number, language_option in enumerate(language_options):
                audio_track = language_option["audio_track"]
                speed = language_option["speed"]
                for segment_number in range(len(segment_indices)):
                    # Ordered by language track then segment number E.g. video_name-lang2-eng-1.5x-segment05.mp3
                    segment_file = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x-segment{segment_number:0{num_segments_digits}}.mp3"
                    )
                    final_files.append(segment_file)
            print("Saved separate segments for each language.")
            return final_files

        # Otherwise, interleaving enabled
        if file_combination == "combine_everything":
            print("Saving interleaved file with everything combined.")
            language_and_speed_str = "-".join(
                [
                    f"{option['audio_track']}{option['speed']}x"
                    for option in language_options
                ]
            )
            # E.g. video_name-interleaved_15s_segments-eng1.2x_dut1.0x_ita0.8x.mp3
            everything_combined_file = (
                self.temporary_audio_folder
                / f"{video_file.stem}-interleaved_{segmenting['segment_length']}s_segments-{language_and_speed_str}.mp3"
            )

            files_to_combine = []
            for segment_number in range(len(segment_indices)):
                for audio_track_number, language_option in enumerate(language_options):
                    audio_track = language_option["audio_track"]
                    speed = language_option["speed"]
                    segment_file = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x-segment{segment_number:0{num_segments_digits}}.mp3"
                    )
                    files_to_combine.append(segment_file)

            self.combine_audio_files(
                files_to_combine=files_to_combine,
                output_file=everything_combined_file,
            )
            print("Saved interleaved file with everything combined.")
            return [everything_combined_file]

        # Know separate files chosen
        if interleaving["combine_interleaved_segments"]:
            print(
                "Saving interleaved files with same segments in each language combined."
            )
            final_files = []
            for segment_number in range(len(segment_indices)):
                language_and_speed_str = "-".join(
                    [
                        f"{option['audio_track']}{option['speed']}x"
                        for option in language_options
                    ]
                )
                # E.g. video_name-interleaved_15s_segments-segment05-eng1.2x_dut1.0x_ita0.8x.mp3
                everything_combined_file = (
                    self.temporary_audio_folder
                    / f"{video_file.stem}-interleaved_{segmenting['segment_length']}s_segments-segment{segment_number:0{num_segments_digits}}-{language_and_speed_str}.mp3"
                )

                files_to_combine = []
                for audio_track_number, language_option in enumerate(language_options):
                    audio_track = language_option["audio_track"]
                    speed = language_option["speed"]
                    segment_file = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x-segment{segment_number:0{num_segments_digits}}.mp3"
                    )
                    files_to_combine.append(segment_file)

                self.combine_audio_files(
                    files_to_combine=files_to_combine,
                    output_file=everything_combined_file,
                )
                final_files.append(everything_combined_file)

            print(
                "Saved interleaved files with same segments in each language combined."
            )
            return final_files

        if not interleaving["combine_interleaved_segments"]:
            print("Saving interleaved files with all segments separate.")
            final_files = []
            for audio_track_number, language_option in enumerate(language_options):
                audio_track = language_option["audio_track"]
                speed = language_option["speed"]
                for segment_number in range(len(segment_indices)):
                    segment_file = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x-segment{segment_number:0{num_segments_digits}}.mp3"
                    )
                    # Ordered by segment number then language track E.g. video_name-segment05-lang2-eng-1.5x.mp3
                    renamed_file_for_interleaving = (
                        self.temporary_audio_folder
                        / f"{video_file.stem}-segment{segment_number:0{num_segments_digits}}-lang{audio_track_number:0{num_audio_track_digits}}-{audio_track}-{speed}x.mp3"
                    )
                    # TODO: Need to handle if that name already exists (which shouldn't be a problem if tidy up all temp files, but should leave extracted audio tracks at least :))
                    segment_file.rename(renamed_file_for_interleaving)
                    final_files.append(renamed_file_for_interleaving)
            print("Renamed interleaved files with all segments separate.")
            return final_files

    # TODO: Refactor repeated code with media_exporter.audio_extractor.AudioExtractor
    def extract_audio_track(self, video_file: Path, audio_track: str) -> Path:
        """
        Extracts a specific audio track from a video file based on the provided language and track name.

        Args:
            video_file (Path): Path to the input video file.
            audio_track (str): The name of the audio track to extract, e.g. "eng" for English.

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
                and stream["tags"].get("language") == audio_track
            ):
                audio_stream_index = i - 1
                break
        if audio_stream_index is None:
            raise ValueError(f"No audio stream found for audio track {audio_track}")

        audio_track = (
            self.temporary_audio_folder / f"{video_file.stem}-{audio_track}.mp3"
        )

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-loglevel",
            "error",  # Only show errors
            "-i",
            str(video_file),
            "-map",
            f"0:a:{audio_stream_index}",
            "-map_metadata",
            "0",
            "-movflags",
            "use_metadata_tags",
            "-filter:a",  # Apply the audio filter
            "loudnorm=I=-18:LRA=6:TP=-1",  # The loudnorm filter for volume normalization
            "-ab",
            BITRATE,  # Audio bitrate
            str(audio_track),  # Output file path
        ]

        # Run the command using subprocess
        subprocess.run(command)

        return audio_track

    def extract_segment(
        self,
        audio_file: Path,
        start_time: datetime,
        end_time: datetime,
        speed: float,
        segment_name: str,
    ) -> Path:
        """
        Extracts a segment of an audio file between the specified start and end times.

        Args:
            audio_file (Path): The audio file to extract the segment from.
            start_time (datetime): The start time of the segment.
            end_time (datetime): The end time of the segment.
            speed (float): The speed multiplier of the segment.
            segment_name: (str): What name to save the segment with.

        Returns:
            Path: Path to the extracted audio segment file.
        """
        start_time_str = convert_datetime_to_ffmpeg_time(start_time)
        end_time_str = convert_datetime_to_ffmpeg_time(end_time)

        audio_segment_path = self.temporary_audio_folder / f"{segment_name}.mp3"

        # Define the ffmpeg command as a list of strings
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-loglevel",
            "error",  # Only show errors
            "-ss",  # Seeking comes before input file. Otherwise, the speed is first applied then the segment is extracted which extracts the wrong part
            start_time_str,
            "-to",
            end_time_str,
            "-i",
            str(audio_file),
        ]

        if speed != 1.0:
            # Apply speed change and re-encode with libmp3lame, maintaining the same bitrate
            command += [
                "-af",
                f"atempo={speed}",
                "-c:a",
                "libmp3lame",  # Re-encode with libmp3lame
                "-b:a",
                BITRATE,
            ]
        else:
            # Simply copy audio if speed is 1.0
            command += [
                "-c:a",
                "copy",
            ]

        command.append(str(audio_segment_path)),

        # Run the command using subprocess
        subprocess.run(command)
        return audio_segment_path

    def segment_subtitle_timings(
        self, subtitle_timings: List[Tuple[datetime, datetime]], segment_length: int
    ) -> List[List[int]]:
        """
        Segments subtitle timings into groups based on a maximum segment length.

        Args:
            subtitle_timings (List[Tuple[datetime, datetime]]): Each tuple contains the start and end time of a subtitle.
            segment_length (int): The maximum length (in seconds) for each segment.

        Returns:
            List[List[int]]: A list where each element is a list of subtitle indices corresponding to a segment of subtitles.
        """
        segments = []
        current_segment = []
        cumulative_length = 0

        for i, (start_time, end_time) in enumerate(subtitle_timings):
            duration = (end_time - start_time).total_seconds()

            if cumulative_length > segment_length:
                # Start a new segment if the current segment exceeds the segment length
                segments.append(current_segment)
                current_segment = []
                cumulative_length = 0

            current_segment.append(i)
            cumulative_length += duration

        # Add the last segment if it exists
        if current_segment:
            segments.append(current_segment)

        return segments

    def combine_audio_files(
        self, files_to_combine: List[Path], output_file: Path
    ) -> None:
        """
        Combines audio files into a single file using ffmpeg.

        Args:
            files_to_combine (List[Path]): List of paths to the audio files to combine.
            output_file (Path): Path to the output file where the combined audio will be saved.
        """
        # Create a temporary file to list all segments
        list_file_path = Path(self.temporary_audio_folder) / "segments.txt"
        with list_file_path.open("w") as f:
            for file in files_to_combine:
                f.write(f"file '{file}'\n")

        # Define the ffmpeg command for concatenating segments
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-loglevel",
            "error",  # Only show errors
            "-f",
            "concat",  # Use concat demuxer
            "-safe",
            "0",  # Allow unsafe file names
            "-i",
            str(list_file_path),  # Input file list
            "-c",
            "copy",  # Copy audio codec (no re-encoding)
            str(output_file),  # Output file
        ]

        try:
            # Run the command using subprocess
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error combining audio segments: {e}")
        finally:
            # Clean up temporary file
            list_file_path.unlink()

    def save_files(self, files: List[Path], output_folder: Path):
        """
        Copies a list of audio files and save them to the output folder.
        This function rebuilds the file headers which makes the end time stable, otherwise different players are unsure of the correct duration of the file.

        Args:
            files (List[Path]): List of Paths to the audio files to be copied.
            output_folder (Path): Path to the folder where the copied files will be saved.
        """
        # Iterate through each file and re-encode it
        for file in files:
            output_file = output_folder / file.name  # Preserve the original filename
            command = [
                "ffmpeg",
                "-y",  # Overwrite the output file if it exists
                "-loglevel",
                "error",  # Only show errors
                "-i",
                str(file),  # Input file
                "-c",
                "copy",
                "-write_xing",
                "0",  # Prevent writing the Xing header, which rebuilds the file headers
                str(output_file),  # Output file path
            ]

            # Run the command
            subprocess.run(command, check=True)


def convert_datetime_to_ffmpeg_time(time: datetime) -> str:
    """
    Converts a datetime object to a string format suitable for use with ffmpeg.

    Args:
        time (datetime): The datetime object to convert.

    Returns:
        str: The converted time string in "H:MM:SS.sss" format.
    """
    return time.strftime("%H:%M:%S.%f")[:-3]
