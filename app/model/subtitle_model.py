import os, re
from datetime import datetime, timedelta

NON_SPEAKING_SYMBOLS = ["♪", "<i>", "[", "]"]
SPECIAL_ENCODINGS = {"Friends": "utf-8-sig"}
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
                    subtitles[-1]["text"] += text + " "

                    # Having appended the current subtitle to the last one, we must lengthen the end time if it is later
                    if end_time > subtitles[-1].end_time:
                        subtitles[-1].end_time = end_time

                    continue

                subtitles.append(Subtitle(start_time, end_time, text))

                text = ""  # Flush the text

            elif any([symbol in line for symbol in non_speaking_symbols]):
                # If line is non-speaking caption we skip it
                continue

            else:
                text += line + " "

        return subtitles

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


# class MultiSubtitleModel!!


#################


def read_subs_file(path):
    ##!! need saved encoding mappings (sig for spanish friends because '\ufeff' at start)
    with open(file=path, encoding="utf-8-sig") as f:
        file = [line.strip() for line in f.readlines()]


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


def output_text_file(subtitle_lines, output_path):
    ##!! also need encoded output
    number_of_lines = len(subtitle_lines)

    for line_number in range(number_of_lines):
        this_line = subtitle_lines[line_number]
        if line_number < number_of_lines - 1:
            next_line = subtitle_lines[line_number + 1]

        else:
            print(this_line)


if __name__ == "__main__":
    test_path = "C:\Stuff\LanguageRepo\Subs Study\Subtitles\Friends - season 1.es subtitulos\Friends - 1x01 - The One Where Monica Gets A Roommate.es.srt"
    subs_file_raw = read_subs_file(test_path)

    parsed_subs = parse_subs_file(subs_file_raw)

    output_path = "./1x01 Spanish.txt"
    output_text_file(parsed_subs, output_path)
