from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout, \
    QSizePolicy, QComboBox, QSplitter
from PyQt6.QtGui import QImage, QPixmap, QClipboard
from PyQt6.QtCore import Qt, QBuffer, QIODevice
import sys
from PIL import Image
import io

class ImageOptimizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Optimizer")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()  # Main layout is now horizontal
        self.central_widget.setLayout(self.main_layout)

        # --- Left Column (Image Comparison) ---
        self.image_comparison_widget = QWidget()
        self.image_comparison_layout = QVBoxLayout() # Changed to QVBoxLayout for vertical stacking
        self.image_comparison_widget.setLayout(self.image_comparison_layout)

        self.original_image_label = QLabel("Original Image")
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.original_image_label.setScaledContents(True) # Removed to prevent stretching
        self.original_image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_comparison_layout.addWidget(self.original_image_label)

        self.processed_image_label = QLabel("Processed Image")
        self.processed_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.processed_image_label.setScaledContents(True) # Removed to prevent stretching
        self.processed_image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_comparison_layout.addWidget(self.processed_image_label)

        # --- Right Column (Controls) ---
        self.controls_layout = QVBoxLayout()  # Vertical layout for controls
        self.controls_widget = QWidget()      # Widget to hold the controls layout
        self.controls_widget.setLayout(self.controls_layout)

        # --- Splitter --- 
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.image_comparison_widget) # Add comparison widget
        self.splitter.addWidget(self.controls_widget)
        self.splitter.setSizes([600, 200]) # Initial sizes
        self.main_layout.addWidget(self.splitter)

        # Status label
        self.status_label = QLabel("Ready")
        self.controls_layout.addWidget(self.status_label)

        # Size presets
        self.size_label = QLabel("Size Preset:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["100%", "75%", "50%", "25%"])
        self.controls_layout.addWidget(self.size_label)
        self.controls_layout.addWidget(self.size_combo)

        # Quality presets
        self.quality_label = QLabel("Quality Preset:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High (95)", "Medium (85)", "Low (70)", "Very Low (50)"])
        self.quality_combo.setCurrentIndex(1) # Default to Medium
        self.controls_layout.addWidget(self.quality_label)
        self.controls_layout.addWidget(self.quality_combo)

        # Buttons
        self.load_button = QPushButton("Load from Clipboard")
        self.load_button.clicked.connect(self.load_from_clipboard)
        self.controls_layout.addWidget(self.load_button)

        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setEnabled(False)
        self.controls_layout.addWidget(self.apply_button)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        self.controls_layout.addWidget(self.copy_button)

        self.controls_layout.addStretch(1) # Add stretch to push controls up

        # Image data
        self.original_image = None
        self.processed_image = None

    def load_from_clipboard(self):
        try:
            clipboard = QApplication.clipboard()
            image = clipboard.image()

            if not image.isNull():
                self.original_image = image
                self.processed_image = image # Initially processed is same as original
                self.display_image(image, 'original')
                self.display_image(image, 'processed') # Display in both labels
                self.apply_button.setEnabled(True)
                self.copy_button.setEnabled(True)
                self.status_label.setText("Image loaded successfully")
            else:
                self.status_label.setText("No image in clipboard")
                self.clear_image_displays()
                self.original_image = None
                self.processed_image = None
                self.apply_button.setEnabled(False)
                self.copy_button.setEnabled(False)
        except Exception as e:
            self.status_label.setText(f"Error loading image: {str(e)}")
            self.clear_image_displays()
            self.original_image = None
            self.processed_image = None
            self.apply_button.setEnabled(False)
            self.copy_button.setEnabled(False)

    def clear_image_displays(self):
        self.original_image_label.setText("Original Image")
        self.original_image_label.clear()
        self.processed_image_label.setText("Processed Image")
        self.processed_image_label.clear()

    def display_image(self, image, target_label):
        try:
            pixmap = QPixmap.fromImage(image)
            label = self.original_image_label if target_label == 'original' else self.processed_image_label
            
            # Scale pixmap to fit label while keeping aspect ratio, but don't scale up
            scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            label.setPixmap(scaled_pixmap)
            label.setText("")
        except Exception as e:
            self.status_label.setText(f"Error displaying image: {str(e)}")

    def apply_changes(self):
        if not self.original_image:
            self.status_label.setText("No image to process")
            return

        try:
            # Convert QImage to PIL Image
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            self.original_image.save(buffer, "PNG")
            pil_image = Image.open(io.BytesIO(buffer.data()))
            buffer.close()

            # Apply size reduction
            size_text = self.size_combo.currentText()
            size_percent = int(size_text.replace('%', '')) / 100.0
            new_size = (int(pil_image.width * size_percent),
                        int(pil_image.height * size_percent))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to RGB if image has alpha channel
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')

            # Get quality value
            quality_text = self.quality_combo.currentText()
            quality_value = int(quality_text[quality_text.find('(')+1:quality_text.find(')')])

            # Convert back to QImage
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=quality_value)
            qimage = QImage()
            if not qimage.loadFromData(buffer.getvalue()):
                raise ValueError("Failed to load processed image data")

            self.processed_image = qimage
            self.display_image(qimage, 'processed') # Update only the processed image label
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