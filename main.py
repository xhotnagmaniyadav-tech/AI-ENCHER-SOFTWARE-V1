
import sys
import cv2
import numpy as np
from PIL import Image

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


class AIPhotoCleaner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI PHOTO CLEANER")
        self.setMinimumSize(1000, 650)

        self.original = None
        self.cleaned = None

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #10131d;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 15px;
            }
            QPushButton {
                background-color: #5546d8;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7165ed;
            }
        """)

        title = QLabel("AI PHOTO CLEANER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 15px;"
        )

        self.before = QLabel("Original Photo")
        self.after = QLabel("Cleaned Photo")

        for label in (self.before, self.after):
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(400, 400)
            label.setStyleSheet(
                "background:#202536; border:1px solid #444;"
            )

        images = QHBoxLayout()
        images.addWidget(self.before)
        images.addWidget(self.after)

        open_btn = QPushButton("Open Photo")
        clean_btn = QPushButton("Clean Photo")
        save_btn = QPushButton("Export Photo")

        open_btn.clicked.connect(self.open_photo)
        clean_btn.clicked.connect(self.clean_photo)
        save_btn.clicked.connect(self.save_photo)

        buttons = QHBoxLayout()
        buttons.addWidget(open_btn)
        buttons.addWidget(clean_btn)
        buttons.addWidget(save_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(images)
        layout.addLayout(buttons)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_image(self, label, image):
        height, width, channels = image.shape
        qimage = QImage(
            image.data, width, height,
            width * channels,
            QImage.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(
            pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def open_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Photo", "",
            "Images (*.jpg *.jpeg *.png)"
        )

        if path:
            try:
                self.original = np.array(
                    Image.open(path).convert("RGB")
                )
                self.cleaned = None
                self.show_image(self.before, self.original)
                self.after.setText("Cleaned Photo")
            except Exception as error:
                QMessageBox.warning(self, "Error", str(error))

    def clean_photo(self):
        if self.original is None:
            QMessageBox.information(
                self, "Notice", "Please open a photo first."
            )
            return

        image_bgr = cv2.cvtColor(
            self.original, cv2.COLOR_RGB2BGR
        )

        result = cv2.bilateralFilter(
            image_bgr, 7, 35, 35
        )

        self.cleaned = cv2.cvtColor(
            result, cv2.COLOR_BGR2RGB
        )

        self.show_image(self.after, self.cleaned)

    def save_photo(self):
        if self.cleaned is None:
            QMessageBox.information(
                self, "Notice", "Clean a photo first."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Photo", "cleaned_photo.png",
            "PNG (*.png);;JPEG (*.jpg)"
        )

        if path:
            Image.fromarray(self.cleaned).save(path)
            QMessageBox.information(
                self, "Success", "Photo exported successfully!"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIPhotoCleaner()
    window.show()
    sys.exit(app.exec())
