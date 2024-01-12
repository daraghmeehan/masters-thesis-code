# from app.model.subtitle_model import SubtitleHandler


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


# class SubtitleModel:
#     def __init__(self, subtitle_files, source_language, tolerance=DEFAULT_TOLERANCE):
#         self.source_language = source_language
#         if self.source_language not in subtitle_files.keys():
#             raise ValueError("Source language must have subtitles")
#         self.tolerance = tolerance

#         self.subtitles = self.read_subtitles(subtitle_files)
#         self.subtitle_mapping = self.create_subtitle_mapping()

#     def read_subtitles(self, subtitle_files):
#         subtitles = {}

#         for language, subtitle_file in subtitle_files.items():
#             if subtitle_file == "None":
#                 continue

#             subtitle_handler = SubtitleHandler(subtitle_file)
#             subtitles[language] = subtitle_handler

#         return subtitles

#     # def create_subtitle_mapping(self):
#     #     """Creates a mapping from the source languages subtitles, and the other langauges' files"""
#     #     subtitle_mapping = {}

#     #     for language, subtitle_handler in self.subtitles.items():
#     #         if language == "None":
#     #             continue

#     def create_subtitle_mapping(self):
#         """Creates a mapping between the source languages subtitles and the other languages' files"""
#         subtitle_mapping = {}

#         source_subtitles = self.subtitles[self.source_language].subtitles
#         for i, source_subtitle in enumerate(source_subtitles):
#             source_start_time = source_subtitle["start_time"]
#             source_end_time = source_subtitle["end_time"]

#             for language, subtitle_handler in self.subtitles.items():
#                 if language == self.source_language or language == "None":
#                     continue

#                 subtitles = subtitle_handler.subtitles

#                 for j, subtitle in enumerate(subtitles):
#                     start_time = subtitle["start_time"]
#                     end_time = subtitle["end_time"]

#                     time_difference = abs(
#                         (start_time - source_start_time).total_seconds()
#                     ) + abs((end_time - source_end_time).total_seconds())

#                     if time_difference <= self.tolerance:
#                         if i in subtitle_mapping:
#                             subtitle_mapping[i][language] = j
#                         else:
#                             subtitle_mapping[i] = {language: j}

#         return subtitle_mapping

#     def get_all_texts(self, languages):
#         texts = {}

#         for language in languages:
#             if language not in self.subtitles.keys():
#                 continue
#             text = self.subtitles[language].get_all_text()
#             texts[language] = text

#         return texts
