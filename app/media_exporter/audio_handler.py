from datetime import datetime, timedelta
import subprocess  # To get the audio track names

from pydub import AudioSegment
from subtitle_handler import SubtitleHandler


def extract_speaking_audio(video_filename, subtitle_handler, ep_number):
    # load the video file
    # video = AudioSegment.from_file(video_filename, format="mp4")

    # extract the audio tracks
    # audio_tracks = video.get_channels()
    # audio_tracks = [
    #     AudioSegment.from_file(audio_filename, format="mp3")
    #     for audio_filename in [
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 1.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 2.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 3.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 4.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 5.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 6.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 7.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 8.mp3",
    #         "./Netflix Downloads/Las chicas Gilmore/S01/gg 9.mp3",
    #     ]
    # ]
    # track_order = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # track_order = [1]

    audio_tracks = [
        AudioSegment.from_file(audio_filename, format="mp3")
        for audio_filename in [
            f"./Clannad_[1-24]/Clannad - {ep_number} [BD 1280x720 x264 AACx3](jp).mp3",
            # f"./Clannad_[1-24]/Clannad - {ep_number} [BD 1280x720 x264 AACx3](en).mp3",
            # f"./Clannad_[1-24]/Clannad - {ep_number} [BD 1280x720 x264 AACx3](jp).mp3"
        ]
    ]
    # track_order = [1, 2, 3]
    track_order = [1]

    # track_names = list_audio_tracks(video_filename)

    # # list the audio tracks
    # print("Audio Tracks:")
    # for i, track in enumerate(track_names):
    #     print(i + 1, "-", "Track Name: ", track)

    # # prompt the user to choose the order for the audio tracks
    # while True:
    #     track_order = input("Enter the order of the audio tracks (e.g. 1,2,3): ")
    #     try:
    #         track_order = [int(x) for x in track_order.split(",")]
    #         # if all(0 < i <= len(audio_tracks) for i in track_order) and len(
    #         #     track_order
    #         # ) != len(set(track_order)):
    #         if all(0 < i <= len(audio_tracks) for i in track_order):
    #             break
    #         else:
    #             print(
    #                 "Invalid input. Please enter integers between 1 and ",
    #                 len(audio_tracks),
    #             )
    #     except ValueError:
    #         print(
    #             "Invalid input. Please enter integers between 1 and ", len(audio_tracks)
    #         )

    individual_audio_segments = [AudioSegment.empty() for _ in track_order]
    complete_track = AudioSegment.empty()

    speaking_times = subtitle_handler.get_all_speaking_times()

    for i, subtitle_times in enumerate(speaking_times):
        subtitle_start_time = subtitle_times[0]
        subtitle_end_time = subtitle_times[1]

        # In the middle
        if i > 0 and i < len(speaking_times) - 1:
            audio_segment_start_time = subtitle_start_time
            # ensuring we do not overlap the end time with the start time of the next subtitle, especially when using a buffer
            audio_segment_end_time = min(subtitle_end_time, speaking_times[i + 1][0])

        # First subtitle
        elif i == 0:
            zero_time = datetime(1900, 1, 1)
            audio_segment_start_time = max(
                subtitle_start_time, zero_time
            )  # in case the buffer puts the first subtitle before the start of the audio
            audio_segment_end_time = min(subtitle_end_time, speaking_times[i + 1][0])

        # Last subtitle
        else:
            video_duration = audio_tracks[
                0
            ].duration_seconds  # duration of the video in seconds
            # Convert the duration in seconds to datetime object
            video_end = datetime(1900, 1, 1) + timedelta(seconds=video_duration)
            audio_segment_start_time = subtitle_start_time
            audio_segment_end_time = min(subtitle_end_time, video_end)

        # turning our times into milliseconds
        start_ms = int(
            (audio_segment_start_time - datetime(1900, 1, 1)).total_seconds() * 1000
        )
        end_ms = int(
            (audio_segment_end_time - datetime(1900, 1, 1)).total_seconds() * 1000
        )

        if (
            individual_audio_segments[0].duration_seconds > 12
            or i == len(speaking_times) - 1
        ):
            # fade out last subtitle and flush individual segments into complete track
            for track in track_order:
                individual_audio_segments[track - 1] = individual_audio_segments[
                    track - 1
                ].append(
                    audio_tracks[track - 1][start_ms : end_ms + 3000].fade_out(3000),
                    crossfade=0,
                )
                ##!! fade out time (+2000) could go over end of audio!!

                complete_track = complete_track.append(
                    individual_audio_segments[track - 1], crossfade=0
                )
                individual_audio_segments[track - 1] = AudioSegment.empty()

        else:
            for track in track_order:
                individual_audio_segments[track - 1] = individual_audio_segments[
                    track - 1
                ].append(audio_tracks[track - 1][start_ms:end_ms], crossfade=0)

    # # Concatenate all audio segments
    # result = audio_segments[0]
    # for audio_segment in audio_segments[1:]:
    #     result = result.append(audio_segment, crossfade=0)

    # Export the result
    print(f"Exporting episode {ep_number}")
    complete_track.export(f"result_{ep_number}.mp3", format="mp3")
    print("Finished\n")


def list_audio_tracks(filepath):
    cmd = "ffprobe -v error -select_streams a -show_entries stream_tags=language -of default=nw=1:nk=1 {}".format(
        filepath
    )
    result = subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout = result.stdout.decode("utf-8").strip()
    print(stdout)
    return stdout
