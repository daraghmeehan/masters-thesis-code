import shutil  # For copying audio

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class AudioPlayer:
    def __init__(self):
        # create the QMediaPlayer object
        self.media_player = QMediaPlayer()

    def reset_player(self):
        self.update_audio("")

    def update_audio(self, audio_path):
        if audio_path == "":
            self.media_player.setMedia(QMediaContent())  # Clear the media content

        media_content = QMediaContent(QUrl.fromLocalFile(audio_path))
        self.media_player.setMedia(media_content)

    def play(self):
        self.media_player.play()

    def stop(self):
        self.media_player.stop()

    def get_audio_path(self):
        if self.media_player.media():
            return QUrl(self.media_player.media().canonicalUrl()).toLocalFile()
        else:
            return ""

    def save_audio(self, path):
        current_audio_path = self.get_audio_path()

        if current_audio_path == "":
            return  # No audio loaded, or an error occurred

        try:
            shutil.copy(current_audio_path, path)
        except IOError as e:
            print(f"Unable to copy file. {e}")

    def has_audio(self):
        return bool(self.get_audio_path())
