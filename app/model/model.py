import re
from typing import List, Tuple, Dict, Union
from datetime import datetime, timedelta

NON_SPEAKING_SYMBOLS = ["♪", "<i>", "[", "]"]
SPECIAL_ENCODINGS = {
    "Friends": "utf-8-sig"
}  # TODO: Ability to save different encoding mappings (e.g. Spanish Friends subtitle files have '\ufeff' at start) in the application
DEFAULT_SUBTITLE_MATCHING_METHOD = "Closest Start Time"
DEFAULT_SUBTITLE_TIMING_TOLERANCE = 1.5  # Tolerance value (in seconds) for matching non-overlapping subtitles that are still close in timing and should be matched

# TODO: Allow for updating non-speaking symbols in the application.
# TODO: Allow for choosing tolerance value in the application.
# TODO: Allow for choosing subtitle matching method (most overlap or closest start time) in the application.


class Subtitle:
    """
    Represents a subtitle with start and end times and the text of the subtitle.

    Attributes:
        start_time (datetime): The start time of the subtitle.
        end_time (datetime): The end time of the subtitle.
        text (str): The subtitle text.
    """

    def __init__(self, start_time: datetime, end_time: datetime, text: str) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def __str__(self) -> str:
        """
        Return a string representation of the subtitle in the SRT format.

        Returns:
            str: A string representing the subtitle with its start and end times and text.
        """
        start_str = self.start_time.strftime("%H:%M:%S,%f")[
            :-3
        ]  # Truncate microseconds to milliseconds
        end_str = self.end_time.strftime("%H:%M:%S,%f")[
            :-3
        ]  # Truncate microseconds to milliseconds
        return f"{start_str} --> {end_str}\n{self.text}"


class SubtitleModel:
    """
    A model for handling subtitle files, parsing them, and extracting relevant information.

    Attributes:
        language (str): The language of the subtitles.
        non_speaking_symbols (List[str]): Symbols that indicate non-speaking text in the subtitles.
        subtitles (List[Subtitle]): A list of Subtitle objects parsed from the file.
    """

    def __init__(
        self,
        language: str,
        filename: str,
        encoding: str = "utf-8",
        non_speaking_symbols: List[str] = NON_SPEAKING_SYMBOLS,
    ) -> None:
        """
        Initialise a SubtitleModel instance by reading and parsing a subtitle file.

        Args:
            language (str): The language of the subtitle file.
            filename (str): The path to the subtitle file.
            encoding (str, optional): The encoding used to read the file. Defaults to "utf-8".
            non_speaking_symbols (List[str], optional): Symbols used for non-speaking captions. Defaults to an empty list.
        """
        self.language = language
        self.non_speaking_symbols = non_speaking_symbols

        subtitle_lines = self.read_subtitle_file(filename, encoding)
        self.subtitles = self.parse_subtitle_file(subtitle_lines, non_speaking_symbols)

    def read_subtitle_file(self, filename: str, encoding: str) -> List[str]:
        """
        Reads a subtitle file and returns its lines.

        Args:
            filename (str): The path to the subtitle file.
            encoding (str): The encoding used to read the file.

        Returns:
            List[str]: A list of lines from the subtitle file.
        """
        with open(filename, "r", encoding=encoding) as f:
            lines = f.readlines()
        return lines

    def parse_subtitle_file(
        self, subtitle_lines: List[str], non_speaking_symbols: List[str]
    ) -> List[Subtitle]:
        """
        Parses lines of a subtitle file and creates a list of Subtitle objects.

        This function reads a subtitle file line by line and processes it, extracting
        the timing information and text for each subtitle. It handles overlapping
        subtitles by merging them, and ignores non-speaking subtitles based on the
        provided symbols.

        Args:
            subtitle_lines (List[str]): The lines of the subtitle file.
            non_speaking_symbols (List[str]): Symbols that indicate non-speaking captions.

        Returns:
            subtitles (List[Subtitle]): A list of Subtitle objects with start time, end time,
                                        and text for each subtitle entry in the file.

        Note:
            The function assumes the subtitle file is in SRT format.
        """

        subtitles = []

        start_time = datetime.min
        end_time = datetime.min
        text = ""

        for i in range(len(subtitle_lines)):
            line = subtitle_lines[i].strip()

            # Subtitle number not needed
            if re.fullmatch(
                r"\ufeff?[0-9]+", line
            ):  # Sometimes has a byte-order mark (BOM)
                # Making sure this is a subtitle number, not a number printed by itself as the text of a subtitle!
                if i == 0 or subtitle_lines[i - 1].strip() == "":
                    continue
                else:
                    text += " " + line

            # Timestamp for subtitle
            elif "-->" in line:
                start_time, end_time = parse_subtitle_timing(line)

            # Empty line means we have seen the full subtitle
            elif line == "":
                # If no text has been saved we skip this subtitle
                if text == "":
                    continue

                # If the current start time is the same as the previous's or is before the previous's end time, then simply append the current subtitle
                if subtitles != [] and (
                    start_time == subtitles[-1].start_time
                    or start_time < subtitles[-1].end_time
                ):
                    subtitles[-1].text += " " + text.strip()

                    # Having appended the current subtitle to the last one, we must lengthen the end time if it is later
                    if end_time > subtitles[-1].end_time:
                        subtitles[-1].end_time = end_time

                    text = ""  # Don't forget to flush the text

                    continue

                # Otherwise we add a new completed subtitle
                subtitles.append(Subtitle(start_time, end_time, text.strip()))
                text = ""  # Flush the text

            elif any([symbol in line for symbol in non_speaking_symbols]):
                # If line is non-speaking caption we skip it
                continue

            else:
                # Normally reading subtitle text to current subtitle we are building
                text += " " + line

        return subtitles

    def get_subtitle(self, subtitle_number: int) -> Subtitle:
        return self.subtitles[subtitle_number]

    def get_all_text(self) -> str:
        """Simply gets all the text of the given subtitle file."""

        text = "\n".join([subtitle.text for subtitle in self.subtitles])
        return text

    def get_all_speaking_times(
        self, subtitle_padding: float
    ) -> List[Tuple[datetime, datetime]]:
        """
        Retrieve all speaking times from the subtitles, for use in exporting practice audio files.

        Args:
            subtitle_padding (float): Subtitle padding (in seconds) to add before and after each start/end time respectively.

        Returns:
            List[Tuple[datetime, datetime]]: A list of tuples with start and end times for each speaking segment.
        """

        sub_times = [
            (subtitle.start_time, subtitle.end_time) for subtitle in self.subtitles
        ]

        if subtitle_padding == 0:
            return sub_times

        zero_time = datetime(1900, 1, 1)

        # Apply padding
        padded_sub_times = [
            (
                max(zero_time, start_time - timedelta(seconds=subtitle_padding)),
                end_time + timedelta(seconds=subtitle_padding),
            )
            for start_time, end_time in sub_times
        ]

        # Trim overlapping times
        trimmed_times = []
        for i, (start_time, end_time) in enumerate(padded_sub_times):
            if i < len(padded_sub_times) - 1:
                next_start_time, next_end_time = padded_sub_times[i + 1]

                if end_time > next_start_time:
                    # Calculate the overlap
                    overlap_duration = end_time - next_start_time

                    # Adjust both the current end time and next start time so they meet in the middle of the overlap
                    end_time -= overlap_duration / 2
                    next_start_time += overlap_duration / 2

                    # Update the next subtitle with the new start time
                    padded_sub_times[i + 1] = (next_start_time, next_end_time)

            trimmed_times.append((start_time, end_time))

        return trimmed_times

    def all_text_to_txt_file(self, filename: str) -> None:
        """
        Save all the subtitle text to a TXT file.

        Args:
            filename (str): The path to the output .txt file.
        """
        text = self.get_all_text()

        with open(filename, "w") as f:
            f.write(text)

    # Currently unused.
    # TODO: Improve/expand this and add to the application, for creating parallel texts to read outside the application :)
    def segments_to_txt(
        self, maximum_seconds_between_segments: int, filename: str
    ) -> None:
        # TODO: Docstring.
        return
        segments = self.segment_episode(
            maximum_seconds_between_segments
        )  # TODO: Currently doesn't work, as segment_episode has been moved.
        number_of_segments = len(segments)

        with open(filename, "w") as f:
            f.write(f"Number of segments = {number_of_segments}\n\n")

            for i in range(number_of_segments):
                segment = segments[i]
                # TODO: Length should perhaps be a function of a segment class.
                segment_length = int(
                    (segment["end_time"] - datetime(1900, 1, 1)).total_seconds()
                    - (segment["start_time"] - datetime(1900, 1, 1)).total_seconds()
                )
                f.write(f"Segment {i}. Length {segment_length} seconds\n")
                start_time = segment["start_time"].strftime("%H:%M:%S")
                end_time = segment["end_time"].strftime("%H:%M:%S")
                f.write(f"{start_time} - {end_time}\n\n")
                f.write(segment["text"])
                f.write("---------------\n\n")

    def number_of_subtitles(self) -> int:
        return len(self.subtitles)


# TODO: Handle different subtitle file types :)
def parse_subtitle_timing(line: str) -> Tuple[datetime, datetime]:
    """
    A useful helper function to parse a subtitle timing line and return the start and end times as datetime objects.

    Args:
        line (str): A line from a subtitle file that contains the timing information,
                    e.g. "HH:MM:SS,fff --> HH:MM:SS,fff" for SRT files.

    Returns:
        Tuple[datetime, datetime]: A tuple containing the start time and end time as datetime objects.
    """
    start_time, end_time = line.split(" --> ")

    # Handling having milliseconds or not, e.g. 01:30:12 vs 01:30:12,007
    if "," in start_time:
        start_time = datetime.strptime(start_time, "%H:%M:%S,%f")
    elif "." in start_time:
        start_time = datetime.strptime(start_time, "%H:%M:%S.%f")
    else:
        start_time = datetime.strptime(start_time, "%H:%M:%S")

    if "," in end_time:
        end_time = datetime.strptime(end_time, "%H:%M:%S,%f")
    elif "." in end_time:
        end_time = datetime.strptime(end_time, "%H:%M:%S.%f")
    else:
        end_time = datetime.strptime(end_time, "%H:%M:%S")

    return start_time, end_time


class AVIModel:
    """
    The central Model class of the application which handles multilingual subtitle alignment based on a reference subtitle file.

    Attributes:
        subtitle_files (Dict[str, str]): A dictionary where keys are languages and values are paths
                                         to the corresponding subtitle files. The key 'Reference'
                                         points to the reference subtitle file used for alignment.
        subtitle_matching_method (str): The method to use to decide which overlapping subtitle best matches the current subtitle being added.
        subtitle_timing_tolerance (float): The timing tolerance in seconds for aligning subtitles that don't overlap but have similar timings.
                                           Defaults to DEFAULT_SUBTITLE_TIMING_TOLERANCE.
        reference_file (str): The file path of the reference subtitle file used for alignment.
        subtitle_models (Dict[str, SubtitleModel]): A dictionary containing SubtitleModel instances for the
                                                    reference and other languages' subtitles.
        languages (List[str]): A list of languages (excluding 'Reference') for which subtitles are provided.
        alignment (Alignment): An instance of the nested Alignment class that holds the aligned subtitle data.
        reverse_mappings (Dict[str, Dict[int, int]]): A dictionary for mapping subtitle indices from
                                                      each language into to the aligned multilingual structure.
    """

    def __init__(
        self,
        subtitle_files: Dict[str, str],
        subtitle_matching_method: str = DEFAULT_SUBTITLE_MATCHING_METHOD,
        subtitle_timing_tolerance: float = DEFAULT_SUBTITLE_TIMING_TOLERANCE,
    ) -> None:
        """
        Initializes the AVIModel with the provided subtitle files and timing tolerance.

        The reference subtitle file is determined, a SubtitleModel is created for the reference and for each language,
        and the models across multiple languages are aligned.

        Args:
        subtitle_files (Dict[str, str]): A dictionary with languages as keys and paths to subtitle files as values.
        subtitle_matching_method (str): The method to use to decide which overlapping subtitle best matches the current subtitle being added.
        subtitle_timing_tolerance (float, optional): The timing tolerance in seconds for aligning subtitles that don't overlap but have similar timings.
                                                     Defaults to DEFAULT_SUBTITLE_TIMING_TOLERANCE.
        """
        self.subtitle_files = subtitle_files
        self.subtitle_matching_method = subtitle_matching_method
        self.subtitle_timing_tolerance = subtitle_timing_tolerance

        self.reference_file = self.determine_reference_file()
        self.subtitle_models = {
            "Reference": SubtitleModel("Reference", self.reference_file)
        }

        self.languages = [
            language
            for language in self.subtitle_files.keys()
            if language != "Reference" and self.subtitle_files[language] != "None"
        ]

        for language in self.languages:
            subtitle_file = self.subtitle_files[language]
            self.subtitle_models[language] = SubtitleModel(language, subtitle_file)

        self.build_multilingual_alignment()

    def determine_reference_file(self) -> str:
        """
        Determines the reference subtitle file.

        Returns:
            str: The path to the reference subtitle file.

        Raises:
            RuntimeError: If no viable reference file is found.
        """
        reference_file = self.subtitle_files.get("Reference", "None")

        if reference_file != "None":
            return reference_file

        # Assign reference file to first non-"None" file if no reference was given
        for subtitle_file in self.subtitle_files.values():
            if subtitle_file != "None":
                return subtitle_file

        raise RuntimeError("Must have a viable reference file!")

    # TODO: Add parameters - which decision method to choose (most overlap or closest start time), and tolerance value
    def build_multilingual_alignment(self) -> None:
        """
        Builds the alignment structure across multiple languages based on the reference subtitles.

        The method initializes the alignment with the reference subtitles, then aligns each additional language's subtitles one-by-one.
        """

        # INITIALISATION
        # First initialise data structure with just reference subtitles

        # TODO: Actually use tolerance value!
        self.alignment = self.Alignment(
            self.languages, self.subtitle_models["Reference"].subtitles
        )

        # MATCHING
        # Go through each language in turn:
        ## For each subtitle:
        ### Find closest matching subtitle in reference language:
        #### If match is good enough, add to multilingual subtitle
        #### Else, add new empty dummy subtitle in appropriate place with empty indices for reference/other languages

        for language in self.languages:
            # If current language's file is also reference file, just copy reference's values
            if self.subtitle_files[language] == self.reference_file:
                self.alignment.copy_reference_values(language=language)
            else:
                self.alignment.add_new_language(
                    language=language,
                    subtitles=self.subtitle_models[language].subtitles,
                    subtitle_matching_method=self.subtitle_matching_method,
                )

        # REVERSE MAPPING
        # Go through each subtitle in the multilingual structure:
        ## For each language, add current alignment index to that language's mapping into multilingual structure

        # TODO: Actually implement and use reverse mappings.
        self.reverse_mappings = {}

        # ADDING NEW LANGUAGES (Future proofing)
        # If at some point a new language is added:
        ## Add subtitles to appropriate places
        ## If need to create a new dummy subtitle, need to add 1 to all reverse mappings higher than current index!

    # TODO: Allow for different segmenting algorithms, e.g. by making segments of e.g. 15 seconds long.
    # TODO: Maybe choose a default maximum seconds value.
    def create_segments(self, maximum_seconds_between_segments: float) -> None:
        """
        Segments the subtitle entries of the alignment based on maximum allowed silence duration between segments.

        This method assigns a segment number to each entry in the aligned subtitles. If the
        time gap between consecutive subtitles exceeds the specified maximum duration, a
        new segment is started.

        Args:
            maximum_seconds_between_segments (float): The maximum duration (in seconds) of
                                                      silence allowed between subtitles
                                                      before starting a new segment.
        """

        # Don't need to track previous entry's start time as only compare current subtitle's start time to end time of previous subtitle
        end_time = self.alignment.alignment[0]["timings"][1]
        # Don't need to assign first entry's segment to 1 as it's always 1
        segment = 1

        for entry in self.alignment.alignment[1:]:
            current_start_time, current_end_time = entry["timings"]

            if (
                current_start_time - end_time
            ).total_seconds() > maximum_seconds_between_segments:
                segment += 1

            # Assign the segment to the entry
            entry["segment"] = segment

            # Update current values for the next loop
            end_time = current_end_time

    def get_subtitle(self, language: str, subtitle_number: int) -> Subtitle:
        return self.subtitle_models[language].get_subtitle(subtitle_number)

    def get_alignment(
        self,
    ) -> List[Dict[str, Union[Tuple[datetime, datetime], Dict[str, List[int]], int]]]:
        return self.alignment.alignment

    def get_all_subtitles(self) -> List[Tuple[str, List[Subtitle]]]:
        all_subtitles = [
            (language, model.subtitles)
            for language, model in self.subtitle_models.items()
        ]
        return all_subtitles

    # TODO: Actually retrieve aligned texts!

    def get_all_texts(self, languages: List[str]) -> Dict[str, str]:
        """
        Retrieves all subtitle text data for the specified languages.

        Args:
            languages (List[str]): A list of languages for which to retrieve subtitle text.

        Returns:
            Dict[str, str]: A dictionary where each key is a language and the corresponding
                            value is the subtitle text for that language.
        """
        texts = {}

        for language in languages:
            if language not in self.subtitles.keys():
                continue
            text = self.subtitles[language].get_all_text()
            texts[language] = text

        return texts

    class Alignment:
        """
        Manages the alignment of subtitles across multiple languages based on a reference subtitle file.

        Attributes:
            languages (List[str]): List of language for the subtitles.
            aligned_languages (List[str]): List of languages that have been aligned.
            alignment (List[Dict[str, any]]): List of alignment entries containing timings, subtitle indices, and assigned segments.
        """

        def __init__(
            self, languages: List[str], reference_subtitles: List[Subtitle]
        ) -> None:
            """
            Initializes the alignment structure with reference subtitles and languages.

            Args:
                reference_subtitles (List[Subtitle]): A list of Subtitle objects for the reference language.
                languages (List[str]): A list of language codes for which subtitles need to be aligned.
            """
            self.languages = languages
            self.aligned_languages = []  # TODO: Perhaps delete as not really used.
            self.alignment = []

            for i, subtitle in enumerate(reference_subtitles):
                start_time, end_time = subtitle.start_time, subtitle.end_time

                # Initialise subtitle_indices as an empty list for each language key
                subtitle_indices = {
                    "Reference": [i]
                }  # Add the index for the reference language first

                # TODO: Perhaps only do this when adding a new language instead of beforehand.
                # Add placeholders for all languages
                subtitle_indices.update({language: [] for language in self.languages})

                self.alignment.append(
                    {
                        "timings": (start_time, end_time),
                        "subtitle_indices": subtitle_indices,
                        "segment": 1,  # No segmenting applied at initialisation TODO: Perhaps update this later...
                    }
                )

            self.aligned_languages.append("Reference")

        def copy_reference_values(self, language: str) -> None:
            """
            Copies the reference subtitle indices to the specified language, in case the reference file is also one of the chosen languages.

            Args:
                language (str): The language to which reference values should be copied.
            """
            for entry in self.alignment:
                # Using [:] slice to create a copy
                entry["subtitle_indices"][language] = entry["subtitle_indices"][
                    "Reference"
                ][:]

            self.aligned_languages.append(language)

        def add_new_language(
            self,
            language: str,
            subtitles: List[Subtitle],
            subtitle_matching_method: str,
        ) -> None:
            """
            Adds subtitles of a new language to the alignment structure.
            For each subtitle, we must choose the most suitable existing entry in the alignment or create a new entry.
            The most suitable existing entry is determined by the chosen method.

            Args:
                language (str): The language of the subtitles being added.
                subtitles (List[Subtitle]): A list of Subtitle objects for the new language.
                subtitle_matching_method (str): The method, either closest start time or highest overlap, to decide which overlapping entry is the best match for the current subtitle being added to the alignment.
            """
            for subtitle_index, subtitle in enumerate(subtitles):
                start_time, end_time = subtitle.start_time, subtitle.end_time

                # Calculating every entry in alignment that overlaps with current subtitle to add
                overlapping_entries = self.calculate_overlapping_entries(
                    start_time, end_time
                )

                # TODO: Use timing tolerance value here and match with closest start time, else find overlapping entries and choose highest overlap :)

                # If no entries overlap, we must make a new entry at the right place
                if overlapping_entries == []:
                    self.add_missing_subtitle(
                        language, subtitle_index, start_time, end_time
                    )
                    continue

                # If we have overlapping entries, we choose the best entry with the desired method
                if subtitle_matching_method == "Closest Start Time":
                    # Find the entry with closest start time
                    best_entry = min(
                        overlapping_entries,
                        key=lambda x: abs(
                            self.alignment[x[0]]["timings"][0] - start_time
                        ),
                    )
                elif subtitle_matching_method == "Highest Overlap":
                    # Find the entry with the highest overlap
                    best_entry = max(overlapping_entries, key=lambda x: x[1])
                else:
                    raise ValueError(
                        "Invalid subtitle matching method specified. Use 'Closest Start Time' or 'Highest Overlap'."
                    )

                # Extract the alignment index
                best_entry_index = best_entry[0]

                # Add the current subtitle index to this entry.
                self.alignment[best_entry_index]["subtitle_indices"][language].append(
                    subtitle_index
                )

            self.aligned_languages.append(language)

        def calculate_overlapping_entries(
            self, start_time: datetime, end_time: datetime
        ) -> List[Tuple[int, float]]:
            """
            Calculates the overlapping entries in the alignment for a given subtitle.

            Args:
                start_time (datetime): The start time of the subtitle.
                end_time (datetime): The end time of the subtitle.

            Returns:
                List[Tuple[int, float]]: A list of tuples, each containing the index of the overlapping entry
                                        and the overlap duration.
            """
            overlapping_entries = []

            for entry_index, entry in enumerate(self.alignment):
                overlap = calculate_subtitle_overlap(
                    (start_time, end_time), entry["timings"]
                )

                if overlap > 0:
                    overlapping_entries.append((entry_index, overlap))

            return overlapping_entries

        # TODO: Ideally the missing entry would be added without searching through the entire alignment again and instead would work dynamically inside `add_new_language`
        def add_missing_subtitle(
            self,
            language: str,
            subtitle_index: int,
            start_time: datetime,
            end_time: datetime,
        ) -> None:
            """
            Adds a missing subtitle entry to the alignment.

            Args:
                language (str): The language of the new subtitle.
                subtitle_index (int): The index of the subtitle in the given language's subtitles.
                start_time (datetime): The start time of the subtitle.
                end_time (datetime): The end time of the subtitle.
            """
            # First create the missing subtitle entry
            subtitle_indices = {"Reference": []}
            subtitle_indices.update({language: [] for language in self.languages})
            subtitle_indices[language].append(subtitle_index)

            new_entry = {
                "timings": (start_time, end_time),
                "subtitle_indices": subtitle_indices,
                "segment": 1,  # TODO: Perhaps allow for adding to already created segments dynamically :)
            }

            # Then find where the entry should go and insert it
            for entry_index, entry in enumerate(self.alignment):
                entry_start_time, entry_end_time = entry["timings"]

                # Find the first time a query entry's start time is after the end time of the entry to add
                if end_time <= entry_start_time:
                    if entry_index != 0:
                        # Making sure the previous entry's end time is before the new entry's start time
                        previous_entry_end_time = self.alignment[entry_index - 1][
                            "timings"
                        ][1]
                        assert previous_entry_end_time <= start_time
                    self.alignment.insert(entry_index, new_entry)
                    return

                # If come to the end, our missing subtitle must be after all the current entries
                if entry_index == len(self.alignment) - 1:
                    assert (
                        entry_end_time <= start_time
                    )  # Confirming the start time of the entry to add comes after the query entry's end time
                    self.alignment.append(new_entry)
                    return

            raise RuntimeError("Trying to add a missing subtitle when it doesn't fit")


def calculate_subtitle_overlap(
    subtitle_1: Tuple[datetime, datetime], subtitle_2: Tuple[datetime, datetime]
) -> float:
    """
    Calculate the proportion of a subtitle that overlaps with another.
    Note: This calculates the overlap proportion of the first subtitle.

    Args:
        subtitle_1 (Tuple[datetime, datetime]): A tuple representing the timings of the first subtitle
                                                (start_time_1, end_time_1).
        subtitle_2 (Tuple[datetime, datetime]): A tuple representing the timings of the second subtitle
                                                (start_time_2, end_time_2).

    Returns:
        float: The proportion of the first subtitle that overlaps with the second subtitle.
    """
    start_time_1, end_time_1 = subtitle_1
    start_time_2, end_time_2 = subtitle_2

    # Calculate the overlap duration
    overlap_start = max(start_time_1, start_time_2)
    overlap_end = min(end_time_1, end_time_2)
    overlap_duration = max(
        overlap_end - overlap_start, timedelta()
    )  # timedelta gives 0 seconds in case overlap is negative

    # Calculate the duration of the first subtitle
    subtitle_1_duration = end_time_1 - start_time_1

    # Calculate the overlap percentage
    overlap = overlap_duration.total_seconds() / subtitle_1_duration.total_seconds()

    return overlap
