import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

from media_exporter.audio_extractor import AudioExtractor
from model.model import SubtitleModel


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
        subtitle_padding = options["subtitle_padding"]
        segmenting = options["segmenting"]
        interleaving = options["interleaving"]
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

        self.process_files(
            video_file,
            reference_subtitle_file,
            subtitle_padding,
            segmenting,
            interleaving,
            file_combination,
            language_options,
        )

    def process_files(
        self,
        video_file: Path,
        reference_subtitle_file: Path,
        subtitle_padding: int,
        segmenting: Dict,
        interleaving: Dict,
        file_combination: str,
        language_options: List[Dict[str, Union[str, float]]],
    ) -> None:

        # TODO: Implement the actual file processing logic.
        print(f"Video file: {video_file}")
        print(f"Using subtitle: {reference_subtitle_file}")
        print(f"Subtitle padding: {subtitle_padding}")
        print(f"Segmenting: {segmenting}")
        print(f"Interleaving: {interleaving}")
        print(f"File combination: {file_combination}")
        print(f"Language options: {language_options}")

        ### STEPS (for single condensed file) ###

        # TODO: Need to refactor AudioExtractor in future.

        ## 1. Extract audio tracks from video
        audio_tracks = {
            option["audio_track"]: option["audio_track"] for option in language_options
        }  # Simply get the unique audio track names
        audio_extractor = AudioExtractor(output_folder=self.temporary_audio_folder)
        audio_extractor.extract_all_language_tracks(
            video_file=video_file, audio_tracks=audio_tracks
        )  # AudioExtractor expects audio_tracks to be a dictionary matching language names to audio track names

        ## 2. Read reference subtitle file
        subtitle_model = SubtitleModel(
            language="Reference", filename=reference_subtitle_file
        )

        ## 3. Retrieve subtitle timings with padding
        subtitle_timings = subtitle_model.get_all_speaking_times(
            subtitle_padding=subtitle_padding
        )

        ## 4. Extract all lines of dialogue to temp files
        segment_paths = []

        for line_number, subtitle_timing in enumerate(subtitle_timings):
            segment_name = f"seg_{line_number}"
            segment_path = audio_extractor.extract_segment(
                language=language_options[0]["audio_track"],
                start_time=subtitle_timing[0],
                end_time=subtitle_timing[1],
                segment_name=segment_name,
            )
            segment_paths.append(segment_path)

        ## 5. Combine all temp files to a single condensed file
        output_file = self.avi_practice_audio_folder / "condensed_audio.mp3"
        self.combine_audio_segments(segment_paths, output_file)

    def combine_audio_segments(
        self, segment_paths: List[Path], output_file: Path
    ) -> None:
        """
        Combines audio segments into a single file using ffmpeg.

        Args:
            segment_paths (List[Path]): List of paths to the audio segments to combine.
            output_file (Path): Path to the output file where combined audio will be saved.
        """
        # Create a temporary file to list all segments
        list_file_path = Path(self.temporary_audio_folder) / "segments.txt"
        with list_file_path.open("w") as f:
            for segment_path in segment_paths:
                f.write(f"file '{segment_path}'\n")

        # Define the ffmpeg command for concatenating segments
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
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
