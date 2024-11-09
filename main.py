import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt, QTimer, QTime


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


class WhiteDraggableSquare(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.setFixedSize(large_icon_width, large_icon_height)
        self.dragging = False

        # Layout for Widgets
        layout = QVBoxLayout()

        # Clock Widget
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_clock()
        layout.addWidget(self.clock_label)

        # Timer to update clock every second
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

        # Note Pad Widget
        self.note_pad = QTextEdit()
        self.note_pad.setPlaceholderText("Write your notes here...")
        layout.addWidget(self.note_pad)

        self.setLayout(layout)

    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss A")
        self.clock_label.setText(current_time)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = WhiteDraggableSquare()
    widget.move(300, 300)
    widget.show()
    sys.exit(app.exec())
