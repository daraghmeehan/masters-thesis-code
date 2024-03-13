import os, re
from datetime import datetime, timedelta

NON_SPEAKING_SYMBOLS = ["♪", "<i>", "[", "]"]
SPECIAL_ENCODINGS = {
    "Friends": "utf-8-sig"
}  ##!! need saved encoding mappings (e.g. spanish friends has '\ufeff' at start)
DEFAULT_TOLERANCE = 1.5


class Subtitle:
    def __init__(self, start_time, end_time, text):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def __str__(self):
        start_str = self.start_time.strftime("%H:%M:%S,%f")[
            :-3
        ]  # Truncate microseconds to milliseconds
        end_str = self.end_time.strftime("%H:%M:%S,%f")[
            :-3
        ]  # Truncate microseconds to milliseconds
        return f"{start_str} --> {end_str}\n{self.text}"


class SubtitleModel:
    def __init__(
        self,
        language,
        filename,
        encoding="utf-8",
        non_speaking_symbols=NON_SPEAKING_SYMBOLS,
    ):
        self.language = language
        self.filename = filename
        self.encoding = encoding
        self.non_speaking_symbols = non_speaking_symbols

        self.subtitles = self.parse_subtitle_file(
            self.filename, encoding, non_speaking_symbols
        )

    def parse_subtitle_file(self, filename, encoding, non_speaking_symbols):
        """
        Parses a subtitle file and creates a list of Subtitle objects.

        This function reads a subtitle file line by line and processes it, extracting
        the timing information and text for each subtitle. It handles overlapping
        subtitles by merging them, and ignores non-speaking parts based on the
        provided symbols.

        Args:
            filename (str): The path to the subtitle file.
            encoding (str): The encoding used for reading the file.
            non_speaking_symbols (list of str): Symbols that indicate non-speaking text
                                                in the subtitles.

        Returns:
            list of Subtitle: A list of Subtitle objects with start time, end time,
                              and text for each subtitle entry in the file.

        Note:
            The function assumes the subtitle file is in SRT format.
        """

        with open(filename, "r", encoding=encoding) as f:
            lines = f.readlines()

        subtitles = []

        start_time = datetime.min
        end_time = datetime.min
        text = ""

        for i in range(len(lines)):
            line = lines[i].strip()

            # Subtitle number not needed
            if re.fullmatch("[0-9]+", line):
                # Making sure this is a subtitle index, not a number printed by itself as the text of a subtitle!
                if i == 0 or lines[i - 1].strip() == "":
                    continue

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
                    subtitles[-1].text += text

                    # Having appended the current subtitle to the last one, we must lengthen the end time if it is later
                    if end_time > subtitles[-1].end_time:
                        subtitles[-1].end_time = end_time

                    text = ""  # Don't forget to flush the text

                    continue

                subtitles.append(Subtitle(start_time, end_time, text))

                text = ""  # Flush the text

            elif any([symbol in line for symbol in non_speaking_symbols]):
                # If line is non-speaking caption we skip it
                continue

            else:
                text += line + " "

        return subtitles

    def get_subtitle(self, subtitle_number):
        return self.subtitles[subtitle_number]

    def get_all_text(self):
        """Simply gets all the text of the given subtitle file"""

        text = "\n".join([subtitle.text for subtitle in self.subtitles])
        return text

    def get_all_speaking_times(self, buffer_len=0.7):
        """!!buffer_len in seconds"""

        all_sub_times = [
            (subtitle["start_time"], subtitle["end_time"])
            for subtitle in self.subtitles
        ]

        # adding buffer
        if buffer_len > 0:
            all_sub_times = [
                (
                    max(0, start_time - timedelta(seconds=buffer_len)),
                    end_time + timedelta(seconds=buffer_len),
                )
                for start_time, end_time in all_sub_times
            ]

        return all_sub_times

    ##!! refactor in future
    def segment_episode(self, minimum_silence_between_segments):
        """!!Minimum silence in seconds"""

        ##!! should make this a class!!
        segments = []

        current_segment = {
            ##!! missing subtitle numbers too?? or is necessary
            "start_time": self.subtitles[0]["start_time"],
            "end_time": self.subtitles[0]["end_time"],
            "text": self.subtitles[0]["text"],
        }

        for subtitle_number in range(1, self.number_of_subtitles()):
            subtitle = self.subtitles[subtitle_number]

            if subtitle_number == self.number_of_subtitles() - 1:
                ##!! perhaps this could be segment.addsubtitle... so it can be reused
                current_segment["end_time"] = subtitle["end_time"]
                current_segment["text"] += subtitle["text"]
                segments.append(current_segment)
                return segments

            current_segment_end_time = int(
                (current_segment["end_time"] - datetime(1900, 1, 1)).total_seconds()
            )
            subtitle_start_time = int(
                (subtitle["start_time"] - datetime(1900, 1, 1)).total_seconds()
            )

            time_until_next_subtitle = subtitle_start_time - current_segment_end_time

            if time_until_next_subtitle >= minimum_silence_between_segments:
                # flush segment
                segments.append(current_segment)
                current_segment = {
                    "start_time": subtitle["start_time"],
                    # "end_time": subtitle["end_time"], # redundant
                    "text": "",
                }

            current_segment["end_time"] = subtitle["end_time"]
            current_segment["text"] += f"{subtitle['text'].strip()}\n"
            ##!! this strip is key -> but better to parse the file better?

    def all_text_to_txt_file(self, filename):
        text = self.get_all_text()

        with open(filename, "w") as f:
            f.write(text)

    def segments_to_txt(self, minimum_silence_between_segments, filename):
        segments = self.segment_episode(minimum_silence_between_segments)
        number_of_segments = len(segments)

        with open(filename, "w") as f:
            f.write(f"Number of segments = {number_of_segments}\n\n")

            for i in range(number_of_segments):
                segment = segments[i]
                ##!! length should be function of segment class!!
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

    def number_of_subtitles(self):
        return len(self.subtitles)


def parse_subtitle_timing(line):
    start_time, end_time = line.split(" --> ")

    # Handling having milliseconds or not, e.g. 01:30:12 vs 01:30:12,00s7
    if "," in start_time:
        start_time = datetime.strptime(start_time, "%H:%M:%S,%f")
    else:
        start_time = datetime.strptime(start_time, "%H:%M:%S")

    if "," in end_time:
        end_time = datetime.strptime(end_time, "%H:%M:%S,%f")
    else:
        end_time = datetime.strptime(end_time, "%H:%M:%S")

    return start_time, end_time


# class Subtitles:
#     def __init__(self, language):
#         self.language = language
#         self.subtitles = []
#         self.segments = {}  # Dictionary to hold segments

#     def add_subtitle(self, subtitle):
#         self.subtitles.append(subtitle)

#     def number_of_subtitles(self):
#         return len(self.subtitles)

#     def get_segment(self, segment_number):
#         return self.segments.get(segment_number, [])

#     def create_segments(
#         self, minimum_silence_between_segments
#     ):  ##?? also maximum_segment_time
#         ...


class AVIModel:
    def __init__(self, subtitle_files, tolerance=DEFAULT_TOLERANCE):
        self.subtitle_files = subtitle_files
        self.tolerance = tolerance

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

    def determine_reference_file(self):
        reference_file = self.subtitle_files.get("Reference", "None")

        if reference_file != "None":
            return reference_file

        # Assign reference file to first non-"None" file if no reference was given
        for subtitle_file in self.subtitle_files.values():
            if subtitle_file != "None":
                return subtitle_file

        raise RuntimeError("Must have a viable reference file")

    ##!! add params!
    def build_multilingual_alignment(self):
        # """Creates a mapping from the reference subtitles to all the other languages' subtitles"""
        # """Performs alignment :)"""

        #####

        # (Initialisation)
        # First initialise data structure with just reference language
        ## First 'column' is 'Reference'
        ## Add 0 to N for lines 0 to N in reference model

        self.alignment = self.Alignment(
            self.subtitle_models["Reference"].subtitles, self.languages
        )

        # (Matching)
        # Then go through each language in turn:
        ## Add current language to 'columns'
        ## Find closest matching subtitle in reference language:
        ### If match is good enough add to multilingual subtitle
        ### Else add new empty dummy subtitle in appropriate place with empty indices for reference/other languages

        for language in self.languages:
            # If current language's file is also reference file, just copy reference's values
            if self.subtitle_files[language] == self.reference_file:
                self.alignment.copy_reference_values(language=language)
            else:
                self.alignment.add_new_language(
                    language=language,
                    subtitles=self.subtitle_models[language].subtitles,
                )

        # (Reverse mapping)
        # Then go through each subtitle in multilingual structure:
        ## For each language 'column', add current index to that language's mapping into multilingual structure

        self.reverse_mappings = {}
        # for

        # (Future proofing adding new languages)
        # If at some point a new language is added:
        ## Add a 'column'
        ## Add subtitles to appropriate places
        ## If need to create a new dummy subtitle, need to add 1 to all reverse mappings higher than current index!

        #####

    #     def get_all_texts(self, languages):
    #         texts = {}

    #         for language in languages:
    #             if language not in self.subtitles.keys():
    #                 continue
    #             text = self.subtitles[language].get_all_text()
    #             texts[language] = text

    #         return texts

    # def create_segments(self, ...):
    #     pass

    def get_subtitle(self, language, subtitle_number):
        return self.subtitle_models[language].get_subtitle(subtitle_number)

    def get_alignment(self):
        return self.alignment.alignment

    def get_all_aligned_data(self):
        texts = {
            language: self.subtitle_models[language].get_all_text()
            for language in self.languages
        }
        return texts

    def get_all_subtitles(self):
        all_subtitles = [
            (language, model.subtitles)
            for language, model in self.subtitle_models.items()
        ]
        return all_subtitles

    class Alignment:
        def __init__(self, reference_subtitles, languages):
            self.languages = languages

            self.aligned_languages = ["Reference"]
            self.alignment = []

            for i, subtitle in enumerate(reference_subtitles):
                start_time, end_time = subtitle.start_time, subtitle.end_time

                # Initialize subtitle_indices as an empty list for each language key
                subtitle_indices = {
                    "Reference": [i]
                }  # Add the index for the reference language first
                subtitle_indices.update({language: [] for language in self.languages})

                self.alignment.append(
                    {
                        "timings": (start_time, end_time),
                        "subtitle_indices": subtitle_indices,
                    }
                )

        def copy_reference_values(self, language):
            for entry in self.alignment:
                # Using [:] slice to create a copy
                entry["subtitle_indices"][language] = entry["subtitle_indices"][
                    "Reference"
                ][:]

            self.aligned_languages.append(language)

        def add_new_language(self, language, subtitles):
            # Otherwise we must choose the most suitable existing entry in the alignment or create a new entry
            for subtitle_index, subtitle in enumerate(subtitles):
                start_time, end_time = subtitle.start_time, subtitle.end_time

                # Calculating every entry in alignment that overlaps with current subtitle to add
                overlapping_entries = self.calculate_overlapping_entries(
                    start_time, end_time
                )

                # If no entries overlap, we must make a new entry at the right place
                if overlapping_entries == []:
                    self.add_missing_subtitle(
                        start_time, end_time, language, subtitle_index
                    )
                    continue

                # Otherwise we find the tuple with the largest overlap value...
                max_overlap_entry = max(overlapping_entries, key=lambda x: x[1])

                # ...extract the alignment index...
                max_overlap_entry_index = max_overlap_entry[0]

                # ...and add the current subtitle index to this entry.
                self.alignment[max_overlap_entry_index]["subtitle_indices"][
                    language
                ].append(subtitle_index)

            self.aligned_languages.append(language)

        def calculate_overlapping_entries(self, start_time, end_time):
            overlapping_entries = []

            for entry_index, entry in enumerate(self.alignment):
                overlap = calculate_subtitle_overlap(
                    (start_time, end_time), entry["timings"]
                )

                if overlap > 0:
                    overlapping_entries.append((entry_index, overlap))

            return overlapping_entries

        def add_missing_subtitle(self, start_time, end_time, language, subtitle_index):
            # First create the missing subtitle entry
            subtitle_indices = {"Reference": []}
            subtitle_indices.update({language: [] for language in self.languages})
            subtitle_indices[language].append(subtitle_index)

            new_entry = {
                "timings": (start_time, end_time),
                "subtitle_indices": subtitle_indices,
            }

            # Then find where our entry should go and insert it
            for entry_index, entry in enumerate(self.alignment):
                entry_start_time, entry_end_time = entry["timings"]

                # Find the first time
                if end_time <= entry_start_time:
                    if entry_index != 0:
                        previous_entry_end_time = self.alignment[entry_index - 1][
                            "timings"
                        ][1]
                        assert previous_entry_end_time <= start_time
                    self.alignment.insert(entry_index, new_entry)
                    return

                # If come to the end, our missing subtitle must be after all the current entries
                if entry_index == len(self.alignment) - 1:
                    assert entry_end_time <= start_time
                    self.alignment.append(new_entry)
                    return

            raise RuntimeError("Trying to add a missing subtitle when it doesn't fit")


def calculate_subtitle_overlap(subtitle_1, subtitle_2):
    """
    Calculate the proportion of one subtitle that overlaps with another.

    Args:
    subtitle_1 (tuple): A tuple representing the timings of the first subtitle (start_time_1, end_time_1).
    subtitle_2 (tuple): A tuple representing the timings of the second subtitle (start_time_2, end_time_2).

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
