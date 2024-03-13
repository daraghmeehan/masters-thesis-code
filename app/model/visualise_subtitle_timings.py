from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from model import SubtitleModel


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
            ax.fill_betweenx(y, start, end, color=colors[j % 2], alpha=0.4)

    # Set y-axis ticks and labels for languages
    ax.set_yticks(range(len(subtitles)))
    ax.set_yticklabels(list(subtitles.keys()))

    # Set x-axis label
    ax.set_xlabel("Time")

    # Calculate the maximum end time in minutes
    max_end_time = max(end for timings in subtitles.values() for _, end in timings)
    all_seconds = datetime_objects_from_zero_to_time(max_end_time, every_x_seconds=5)
    # all_seconds = all_seconds[:45]
    for dt in all_seconds:
        ax.vlines(
            dt,
            ymin=0 - 0.025,
            ymax=len(subtitles.keys()) - 0.975,
            color="grey",
            linewidth=0.3,
        )

    # Show plot
    plt.show()


subtitle_files = {
    "English": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.en.srt",
    "Spanish": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.es.srt",
    "French": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.fr.srt",
    "Japanese": "C:/Stuff/UniversaLearn/LanguageRepo/Language Learning Material/Netflix Downloads/Las chicas Gilmore/S01/Las chicas Gilmore_S01E01_Piloto.ja.srt",
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

# Visualise subtitle timings
visualise_subtitle_timings(subtitles)
