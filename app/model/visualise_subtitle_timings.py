from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from model import SubtitleModel

# Note: This is auxiliary code to generate graphs for visualising subtitle timings used in the thesis.
## TODO: Actually integrate this in the application possibly.


def datetime_objects_from_zero_to_time(max_time, every_x_seconds=1):
    # Start time
    start_time = datetime(1900, 1, 1)

    # Create a list of datetime.datetime objects from time 0 to max_time
    datetime_objects = [
        start_time + timedelta(seconds=i * every_x_seconds)
        for i in range(
            int((max_time - start_time).total_seconds() / every_x_seconds) + 2
        )
    ]

    return datetime_objects


def visualise_subtitle_timings(subtitles):
    # Define colors for alternating segments
    colors = ["red", "blue"]

    # Initialise subplot
    fig, ax = plt.subplots()

    # Iterate over each language
    for i, lang in enumerate(subtitles.keys()):
        timings = subtitles[lang]
        y = [i] * len(timings)  # Y-coordinate for the language line
        for j, (start, end) in enumerate(timings):
            # Plot filled rectangle for each subtitle segment
            ax.fill_betweenx(y, start, end, color=colors[j % 2], alpha=1, linewidth=5)

    # Set y-axis ticks and labels for languages
    ax.set_yticks(range(len(subtitles)))
    ax.set_yticklabels(list(subtitles.keys()))

    # Set x-axis label
    ax.set_xlabel("Time")

    # # Calculate the maximum end time in minutes
    # max_end_time = max(end for timings in subtitles.values() for _, end in timings)
    # all_seconds = datetime_objects_from_zero_to_time(max_end_time, every_x_seconds=5)
    # # Plotting vertical line every x seconds
    # for dt in all_seconds:
    #     ax.vlines(
    #         dt,
    #         ymin=0 - 0.025,
    #         ymax=len(subtitles.keys()) - 0.975,
    #         color="grey",
    #         linewidth=0.3,
    #     )

    # Show plot
    plt.show()


subtitle_files = {
    "English": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.en.srt",
    "Spanish": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.es.srt",
    "French": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.fr.srt",
    "Japanese": "C:/Stuff/Gilmore Girls/S01/Gilmore Girls_S01E01_Pilot.ja.srt",
}

subtitle_models = {
    language: SubtitleModel(language, subtitle_file)
    for language, subtitle_file in subtitle_files.items()
}

# Example subtitles data structure: { 'Language1': [(start1, end1), (start2, end2), ...], 'Language2': [(start1, end1), (start2, end2), ...], ... }
subtitles = {
    language: [(sub.start_time, sub.end_time) for sub in subtitle_model.subtitles]
    for language, subtitle_model in subtitle_models.items()
}


#####

# # Simulating padding of 1 second
# subtitles["English"][0] = (
#     subtitles["English"][0][0] - timedelta(seconds=1),
#     subtitles["English"][0][1],
# )
# subtitles["English"][4] = (
#     subtitles["English"][4][0],
#     subtitles["English"][4][1] + timedelta(seconds=1),
# )
# subtitles["English"][5] = (
#     subtitles["English"][5][0] - timedelta(seconds=1),
#     subtitles["English"][5][1],
# )
# subtitles["English"][6] = (
#     subtitles["English"][6][0],
#     subtitles["English"][6][1] + timedelta(seconds=1),
# )
# subtitles["English"][7] = (
#     subtitles["English"][7][0] - timedelta(seconds=1),
#     subtitles["English"][7][1],
# )
# subtitles["English"][8] = (
#     subtitles["English"][8][0],
#     subtitles["English"][8][1] + timedelta(seconds=1),
# )
# subtitles["English"][9] = (
#     subtitles["English"][9][0] - timedelta(seconds=1),
#     subtitles["English"][9][1],
# )

# cumulative_duration = 0
# # Iterate over the first x subtitles and print their duration
# for i, (start, end) in enumerate(subtitles["English"][:35]):
#     # Check if cumulative duration exceeds 15 seconds
#     if cumulative_duration > 15:
#         cumulative_duration = 0  # Reset cumulative to current duration

#     duration = (end - start).total_seconds()
#     cumulative_duration += duration

#     # Formatting the start time
#     formatted_start = start.strftime("%H:%M:%S.%f")[
#         :-3
#     ]  # Slice to remove last three digits of microseconds
#     # Formatting the end time
#     formatted_end = end.strftime("%H:%M:%S.%f")[:-3]

#     # Print formatted information
#     print(
#         f"Subtitle {i+1}: Start {formatted_start}, End {formatted_end}, Duration {duration:.3f} seconds, Cumulative {cumulative_duration:.3f} seconds"
#     )

# ## Creating a 1 second subtitle to visualise
# # Create the new subtitle time range
# new_start_time = datetime(1900, 1, 1, 0, 0, 45)  # 45 seconds
# new_end_time = datetime(1900, 1, 1, 0, 0, 46)  # 46 seconds

# # Add the new subtitle timing to the English subtitles
# subtitles["English"].insert(0, (new_start_time, new_end_time))

#####

# Visualise subtitle timings
visualise_subtitle_timings(subtitles)
