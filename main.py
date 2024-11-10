import sys
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
from io import BytesIO
from credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Function to convert twips to pixels
def twips_to_pixels(twips):
    return abs(twips) // 15

# Example registry values (replace with the values from your registry)
icon_spacing_twips = -1140
icon_vertical_spacing_twips = -1136

# Convert to pixels
icon_width = twips_to_pixels(icon_spacing_twips)
icon_height = twips_to_pixels(icon_vertical_spacing_twips)

# 3x3 Size
large_icon_width = icon_width * 3
large_icon_height = icon_height * 3

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state"
))

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(large_icon_width, large_icon_height)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-radius: 10px;")

        self.dragging = False

        # Layout
        self.layout = QVBoxLayout()

        # Album artwork
        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(200, 200)
        self.layout.addWidget(self.album_art_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Song title and artist
        self.song_title_label = QLabel("Song Title")
        self.song_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.layout.addWidget(self.song_title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.artist_label = QLabel("Artist")
        self.artist_label.setStyleSheet("font-size: 14px; color: white;")
        self.layout.addWidget(self.artist_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Playback controls in one row
        button_layout = QHBoxLayout()

        # Styled buttons with icons and green color
        self.prev_button = QPushButton()
        self.prev_button.setIcon(QIcon("icons/player-skip-back-white.png"))
        self.prev_button.setStyleSheet(
            "background-color: #1DB954; border: none; border-radius: 10px; padding: 3px; color: white;"
        )

        self.play_button = QPushButton()
        self.play_icon = QIcon("icons/player-play-white.png")
        self.pause_icon = QIcon("icons/player-pause-white.png")
        self.play_button.setIcon(self.play_icon)
        self.play_button.setStyleSheet(
            "background-color: #1DB954; border: none; border-radius: 10px; padding: 3px; color: white;"
        )

        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon("icons/player-skip-forward-white.png"))
        self.next_button.setStyleSheet(
            "background-color: #1DB954; border: none; border-radius: 10px; padding: 3px; color: white;"
        )

        self.prev_button.clicked.connect(self.previous_song)
        self.play_button.clicked.connect(self.toggle_playback)
        self.next_button.clicked.connect(self.next_song)

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.next_button)

        # Add a vertical spacer to push the buttons up
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addItem(spacer)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Update song info every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_song_info)
        self.timer.start(5000)  # 5000 ms = 5 seconds

        self.update_song_info()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = event.globalPosition().toPoint()
            diff = current_pos - self.drag_position
            self.move(self.pos() + diff)
            self.drag_position = current_pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.snap_to_grid()

    def snap_to_grid(self):
        x = round(self.x() / icon_width) * icon_width
        y = round(self.y() / icon_height) * icon_height
        self.move(x, y)

    def update_song_info(self):
        current_track = sp.current_playback()
        if current_track:
            track = current_track['item']
            self.song_title_label.setText(track['name'])
            self.artist_label.setText(", ".join([artist['name'] for artist in track['artists']]))

            # Get album art
            album_art_url = track['album']['images'][0]['url']
            response = requests.get(album_art_url)
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(response.content).read())
            self.album_art_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.IgnoreAspectRatio))

    def toggle_playback(self):
        current_track = sp.current_playback()
        if current_track and current_track['is_playing']:
            sp.pause_playback()
            self.play_button.setIcon(self.play_icon)
        else:
            sp.start_playback()
            self.play_button.setIcon(self.pause_icon)
        self.update_song_info()

    def next_song(self):
        sp.next_track()
        self.update_song_info()

    def previous_song(self):
        sp.previous_track()
        self.update_song_info()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SpotifyWidget()
    widget.move(300, 300)
    widget.show()
    sys.exit(app.exec())
