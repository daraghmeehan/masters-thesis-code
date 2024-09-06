import random
from datetime import datetime
from typing import List

import cv2
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage


DEFAULT_NUMBER_OF_SCREENSHOTS = 5
# DEFAULT_IMAGE_HEIGHT = 360
DEFAULT_IMAGE_HEIGHT = 150
DEFAULT_IMAGE_UI_HEIGHT = 80


class ScreenshotExtractor:
    """
    A class for extracting screenshots from a video file at specific timestamps.

    Attributes:
        video_path (str): The file path to the video from which screenshots are extracted.
    """

    def __init__(self, video_path):
        """
        Initializes the ScreenshotExtractor with the path to the video file.

        Args:
            video_path (str): The file path to the video from which screenshots will be extracted.
        """
        self.video_path = video_path

    def extract_screenshots(
        self,
        start_time: datetime,
        end_time: datetime,
        number_of_screenshots: int = DEFAULT_NUMBER_OF_SCREENSHOTS,
        method: str = "Equidistant",
        image_height: int = DEFAULT_IMAGE_HEIGHT,
        image_ui_height: int = DEFAULT_IMAGE_UI_HEIGHT,
    ) -> List[QPixmap]:
        """
        Extracts screenshots from the video at specific timestamps.

        Args:
            start_time (datetime): The start time for screenshot extraction.
            end_time (datetime): The end time for screenshot extraction.
            number_of_screenshots (int, optional): Number of screenshots to extract. Defaults to 5.
            method (str, optional): The method for timestamp generation ("Equidistant" or "Random"). Defaults to "Equidistant".
            image_height (int, optional): Height of the screenshots. Defaults to 150.
            image_ui_height (int, optional): Height of the screenshots for UI purposes. Defaults to 80.

        Returns:
            List[QPixmap]: A list of QPixmap objects representing the extracted screenshots.
        """

        if method not in ["Equidistant", "Random"]:
            print(f"Incorrect screenshot extraction method chosen: {method}")

        # Get the timestamps for the screenshots
        timestamps = self.generate_timestamps(
            start_time, end_time, number_of_screenshots, method
        )

        # Load video with a video capture object
        cap = cv2.VideoCapture(self.video_path)

        screenshots = []

        for timestamp in timestamps:
            # Convert datetime timestamp to milliseconds
            timestamp_ms = int(
                (timestamp - datetime(1900, 1, 1)).total_seconds() * 1000
            )

            # Set the video capture position to the specified timestamp
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)

            # Read a frame from the video
            ret, frame = cap.read()

            if not ret:
                continue  # Skip if frame reading fails

            # Resize the frame while maintaining the aspect ratio
            height = image_height
            width = int(frame.shape[1] / frame.shape[0] * height)
            frame = cv2.resize(frame, (width, height))

            # Convert the frame to a QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()

            screenshot = QPixmap.fromImage(q_image)
            screenshots.append(screenshot)

        # Release the video capture object
        cap.release()

        return screenshots

    def generate_timestamps(
        self,
        start_time: datetime,
        end_time: datetime,
        number_of_screenshots: int,
        method: str,
    ) -> List[datetime]:
        """
        Generates timestamps for screenshots based on the chosen method.

        Args:
            start_time (datetime): The start time for timestamp generation.
            end_time (datetime): The end time for timestamp generation.
            number_of_screenshots (int): Number of timestamps to generate.
            method (str): The method for timestamp generation ("Equidistant" or "Random").

        Returns:
            List[datetime]: A list of datetime objects representing the timestamps for screenshots.
        """
        if method == "Equidistant":
            return self.generate_equidistant_timestamps(
                start_time, end_time, number_of_screenshots
            )
        else:
            return self.generate_random_timestamps(
                start_time, end_time, number_of_screenshots
            )

    def generate_equidistant_timestamps(
        self, start_time: datetime, end_time: datetime, number_of_screenshots: int
    ) -> List[datetime]:
        """
        Generates timestamps at equal intervals between the start and end times.

        Args:
            start_time (datetime): The start time for timestamp generation.
            end_time (datetime): The end time for timestamp generation.
            number_of_screenshots (int): Number of equidistant timestamps to generate.

        Returns:
            List[datetime]: A list of datetime objects representing equidistant timestamps.
        """
        time_delta = (end_time - start_time) / (number_of_screenshots - 1)
        return [start_time + i * time_delta for i in range(number_of_screenshots)]

    def generate_random_timestamps(
        self, start_time: datetime, end_time: datetime, number_of_screenshots: int
    ) -> List[datetime]:
        """
        Generates random timestamps between the start and end times.
        The timestamps are randomly sampled from intervals between the start and end times, with the number of intervals equal to number_of_screenshots.

        Args:
            start_time (datetime): The start time for timestamp generation.
            end_time (datetime): The end time for timestamp generation.
            number_of_screenshots (int): Number of random timestamps to generate.

        Returns:
            List[datetime]: A list of datetime objects representing random timestamps.
        """
        time_delta = (end_time - start_time) / (number_of_screenshots)

        return [
            start_time + (i + random.random()) * time_delta
            for i in range(number_of_screenshots)
        ]


if __name__ == "__main__":
    app = QApplication([])
    from app.ui.flashcard_workspace import ScreenshotViewer
    from datetime import datetime

    start_time = datetime.strptime("00:00:10,000", "%H:%M:%S,%f")
    end_time = datetime.strptime("00:00:15,000", "%H:%M:%S,%f")

    video_path = "C:\LCT\RUG\THESIS\Experiment\Materials\Daddy loses his glasses\[English] Daddy loses his glasses.mp4"
    screenshot_extractor = ScreenshotExtractor(video_path)

    print(screenshot_extractor.generate_equidistant_timestamps(start_time, end_time, 5))
    print("-----")
    print(screenshot_extractor.generate_random_timestamps(start_time, end_time, 5))

    screenshots = screenshot_extractor.extract_screenshots(start_time, end_time)

    screenshot_viewer = ScreenshotViewer()
    screenshot_viewer.update_screenshots(screenshots)
    screenshot_viewer.show()
    app.exec_()
