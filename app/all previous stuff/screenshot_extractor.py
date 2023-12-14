import random
from datetime import datetime
import cv2

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage


class ScreenshotExtractor:
    def __init__(
        self, video_path, default_number_of_screenshots=5, default_image_height=360
    ):
        self.video_path = video_path
        self.default_number_of_screenshots = default_number_of_screenshots
        self.default_image_height = default_image_height

    def extract_screenshots(
        self, start_time, end_time, number_of_screenshots=None, method="Equidistant"
    ):
        if number_of_screenshots == None:
            number_of_screenshots = self.default_number_of_screenshots

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

            # Resize the frame to 360p height while maintaining aspect ratio
            height = self.default_image_height
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

    def generate_timestamps(self, start_time, end_time, number_of_screenshots, method):
        if method == "Equidistant":
            timestamps = self.generate_equidistant_timestamps(
                start_time, end_time, number_of_screenshots
            )
        else:
            timestamps = self.generate_random_timestamps(
                start_time, end_time, number_of_screenshots
            )
        return timestamps

    def generate_equidistant_timestamps(
        self, start_time, end_time, number_of_screenshots
    ):
        time_delta = (end_time - start_time) / (number_of_screenshots - 1)

        screenshot_timestamps = [
            start_time + i * time_delta for i in range(number_of_screenshots)
        ]

        return screenshot_timestamps

    def generate_random_timestamps(self, start_time, end_time, number_of_screenshots):
        time_delta = (end_time - start_time) / (number_of_screenshots)

        screenshot_timestamps = [
            start_time + (i + random.random()) * time_delta
            for i in range(number_of_screenshots)
        ]

        return screenshot_timestamps


if __name__ == "__main__":
    app = QApplication([])
    from flashcard_workspace import ScreenshotViewer
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
