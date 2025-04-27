import io
import sys

from PIL import Image
from PyQt6.QtCore import QBuffer, QIODevice, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class ImageOptimizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smol Paste")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()  # Main layout is now horizontal
        self.central_widget.setLayout(self.main_layout)

        # --- Left Column (Image Comparison) ---
        self.image_comparison_widget = QWidget()
        self.image_comparison_layout = QVBoxLayout()  # Changed to QVBoxLayout for vertical stacking
        self.image_comparison_widget.setLayout(self.image_comparison_layout)

        self.original_image_label = QLabel("Original Image")
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.original_image_label.setScaledContents(True) # Removed to prevent stretching
        self.original_image_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.image_comparison_layout.addWidget(self.original_image_label)

        self.processed_image_label = QLabel("Processed Image")
        self.processed_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.processed_image_label.setScaledContents(True) # Removed to prevent stretching
        self.processed_image_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.image_comparison_layout.addWidget(self.processed_image_label)

        # --- Right Column (Controls) ---
        self.controls_layout = QVBoxLayout()  # Vertical layout for controls
        self.controls_widget = QWidget()  # Widget to hold the controls layout
        self.controls_widget.setLayout(self.controls_layout)

        # --- Splitter ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.image_comparison_widget)  # Add comparison widget
        self.splitter.addWidget(self.controls_widget)
        self.splitter.setSizes([600, 200])  # Initial sizes
        self.main_layout.addWidget(self.splitter)

        # Status label
        self.status_label = QLabel("Ready")
        self.controls_layout.addWidget(self.status_label)

        # Size presets
        self.size_label = QLabel("Size Preset:")
        self.controls_layout.addWidget(self.size_label)
        self.size_button_group = QButtonGroup(self)
        self.size_button_layout = QHBoxLayout()
        size_presets = ["100%", "75%", "50%", "25%"]
        for i, preset in enumerate(size_presets):
            button = QPushButton(preset)
            button.setCheckable(True)
            self.size_button_group.addButton(button, i)
            self.size_button_layout.addWidget(button)
            if preset == "100%": # Default selection
                button.setChecked(True)
        self.controls_layout.addLayout(self.size_button_layout)

        # Quality presets
        self.quality_label = QLabel("Quality Preset:")
        self.controls_layout.addWidget(self.quality_label)
        self.quality_button_group = QButtonGroup(self)
        self.quality_button_layout = QHBoxLayout()
        quality_presets = {"High (95)": 95, "Medium (85)": 85, "Low (70)": 70, "Very Low (50)": 50}
        for i, (text, value) in enumerate(quality_presets.items()):
            button = QPushButton(text)
            button.setCheckable(True)
            self.quality_button_group.addButton(button, value) # Store quality value as ID
            self.quality_button_layout.addWidget(button)
            if text == "Medium (85)": # Default selection
                button.setChecked(True)
        self.controls_layout.addLayout(self.quality_button_layout)

        # Connect preset buttons to apply changes automatically
        self.size_button_group.buttonClicked.connect(self.apply_changes)
        self.quality_button_group.buttonClicked.connect(self.apply_changes)

        # Buttons
        self.load_button = QPushButton("Load from Clipboard")
        self.load_button.clicked.connect(self.load_from_clipboard)
        self.controls_layout.addWidget(self.load_button)

        # Apply button removed - changes apply automatically

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        self.controls_layout.addWidget(self.copy_button)

        self.controls_layout.addStretch(1)  # Add stretch to push controls up

        # Stats label
        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.controls_layout.addWidget(self.stats_label)

        # Image data
        self.original_image = None
        self.processed_image = None

    def load_from_clipboard(self):
        try:
            clipboard = QApplication.clipboard()
            image = clipboard.image()

            if not image.isNull():
                self.original_image = image
                self.processed_image = image  # Initially processed is same as original
                self.display_image(image, "original")
                self.display_image(image, "processed")  # Display in both labels
                self.copy_button.setEnabled(True)
                self.status_label.setText("Image loaded successfully")
                self.stats_label.setText("") # Clear stats on new load
            else:
                self.status_label.setText("No image in clipboard")
                self.clear_image_displays()
                self.original_image = None
                self.processed_image = None
                self.copy_button.setEnabled(False)
                self.stats_label.setText("") # Clear stats if no image
        except Exception as e:
            self.status_label.setText(f"Error loading image: {str(e)}")
            self.clear_image_displays()
            self.original_image = None
            self.processed_image = None
            self.copy_button.setEnabled(False)
            self.stats_label.setText("") # Clear stats on error

    def clear_image_displays(self):
        self.original_image_label.clear()
        self.original_image_label.setText("Original Image")
        self.processed_image_label.clear()
        self.processed_image_label.setText("Processed Image")
        self.stats_label.setText("") # Clear stats when displays are cleared

    def display_image(self, image, target_label):
        try:
            pixmap = QPixmap.fromImage(image)
            label = (
                self.original_image_label
                if target_label == "original"
                else self.processed_image_label
            )

            # Scale pixmap to fit label while keeping aspect ratio, but don't scale up
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            label.setPixmap(scaled_pixmap)
            label.setText("")
        except Exception as e:
            self.status_label.setText(f"Error displaying image: {str(e)}")

    def apply_changes(self):
        if not self.original_image:
            self.status_label.setText("No image to process")
            return

        try:
            # Get original dimensions and estimate size (using PNG for lossless size)
            original_width = self.original_image.width()
            original_height = self.original_image.height()
            original_buffer_png = QBuffer()
            original_buffer_png.open(QIODevice.OpenModeFlag.WriteOnly)
            self.original_image.save(original_buffer_png, "PNG")
            original_size_bytes = original_buffer_png.size()
            original_buffer_png.close()

            # Convert QImage to PIL Image using the PNG buffer
            pil_image = Image.open(io.BytesIO(original_buffer_png.data()))

            # --- Apply transformations ---

            # Apply size reduction
            selected_size_button = self.size_button_group.checkedButton()
            if selected_size_button:
                size_text = selected_size_button.text()
                size_percent = int(size_text.replace("%", "")) / 100.0
                new_size = (int(pil_image.width * size_percent), int(pil_image.height * size_percent))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            else:
                # Handle case where no size button is selected (shouldn't happen with defaults)
                self.status_label.setText("Error: No size preset selected")
                return

            # Convert to RGB if image has alpha channel
            if pil_image.mode == "RGBA":
                pil_image = pil_image.convert("RGB")

            # Get quality value
            selected_quality_button = self.quality_button_group.checkedButton()
            if selected_quality_button:
                quality_value = self.quality_button_group.id(selected_quality_button)
            else:
                # Handle case where no quality button is selected (shouldn't happen with defaults)
                self.status_label.setText("Error: No quality preset selected")
                return

            # Convert back to QImage
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=quality_value)
            qimage = QImage()
            if not qimage.loadFromData(buffer.getvalue()):
                raise ValueError("Failed to load processed image data")

            self.processed_image = qimage
            self.display_image(qimage, "processed")  # Update only the processed image label

            # Calculate stats
            processed_size_bytes = buffer.tell() # Get size from JPEG buffer
            processed_width = qimage.width()
            processed_height = qimage.height()

            size_reduction_percent = 0
            if original_size_bytes > 0:
                size_reduction_percent = (1 - (processed_size_bytes / original_size_bytes)) * 100

            original_kb = original_size_bytes / 1024
            processed_kb = processed_size_bytes / 1024
            stats_text = (
                f"Original: {original_width}x{original_height}, {original_kb:.1f} KB\n"
                f"Processed: {processed_width}x{processed_height}, {processed_kb:.1f} KB\n"
                f"Reduction: {size_reduction_percent:.1f}%"
            )
            self.stats_label.setText(stats_text)
            self.status_label.setText("Image processed successfully")

        except Exception as e:
            self.status_label.setText(f"Error processing image: {str(e)}")

    def copy_to_clipboard(self):
        try:
            if self.processed_image:
                clipboard = QApplication.clipboard()
                clipboard.setImage(self.processed_image)
                self.status_label.setText("Image copied to clipboard")
            else:
                self.status_label.setText("No image to copy")
        except Exception as e:
            self.status_label.setText(f"Error copying image: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = ImageOptimizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
