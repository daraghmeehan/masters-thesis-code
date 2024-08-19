import shutil  # For copying (saving) audio

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class AudioPlayer:
    """
    A simple audio player class for playing, stopping, and saving audio files using PyQt5's QMediaPlayer.

    Attributes:
        media_player (QMediaPlayer): The QMediaPlayer instance used to handle audio playback.
    """

    def __init__(self) -> None:
        """Initializes the AudioPlayer by creating a QMediaPlayer object."""
        self.media_player = QMediaPlayer()

    def reset_player(self) -> None:
        """Resets the audio player by clearing the current audio."""
        self.update_audio("")

    def update_audio(self, audio_path: str) -> None:
        """
        Updates the audio file to be played by the player.

        Args:
            audio_path (str): The file path to the audio file. If an empty string is passed, the current media is cleared.
        """
        if audio_path == "":
            self.media_player.setMedia(QMediaContent())  # Clear the media content
        else:
            media_content = QMediaContent(QUrl.fromLocalFile(audio_path))
            self.media_player.setMedia(media_content)

    def play(self) -> None:
        """Plays the current audio file."""
        self.media_player.play()

    def stop(self) -> None:
        """Stops audio playback."""
        self.media_player.stop()

    def get_audio_path(self) -> str:
        """
        Retrieves the file path of the currently loaded audio.

        Returns:
            str: The file path of the current audio or an empty string if no audio is loaded.
        """
        if self.has_audio():
            return QUrl(self.media_player.media().canonicalUrl()).toLocalFile()
        return ""

    def save_audio(self, path: str) -> None:
        """
        Saves the currently loaded audio file to the specified path.

        Args:
            path (str): The destination file path where the audio file should be copied.
        """
        if not self.has_audio():
            return  # No audio loaded

        current_audio_path = self.get_audio_path()
        try:
            shutil.copy(current_audio_path, path)
        except IOError as e:
            print(f"Unable to copy file. {e}")

    def has_audio(self) -> bool:
        """
        Checks if there is any audio currently loaded in the player.

        Returns:
            bool: True if an audio file is loaded, otherwise False.
        """
        return bool(self.media_player.media())
