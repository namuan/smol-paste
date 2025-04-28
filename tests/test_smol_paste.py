import os

from PIL import Image
from PIL import Image as PILImage
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication
from smol_paste.smol_paste import ImageOptimizer


def test_image_load_and_properties():
    img_path = os.path.join(os.path.dirname(__file__), "test.png")
    assert os.path.exists(img_path), f"Test image not found: {img_path}"
    img = Image.open(img_path)
    assert img.format == "PNG"
    assert img.width > 0 and img.height > 0
    assert img.mode in ("RGB", "RGBA", "L")


def test_image_resize_and_quality():
    img_path = os.path.join(os.path.dirname(__file__), "test.png")
    img = Image.open(img_path)
    # Resize to 50%
    new_size = (img.width // 2, img.height // 2)
    resized = img.resize(new_size, Image.Resampling.LANCZOS)
    assert resized.size == new_size
    # Save as JPEG with different quality
    for quality in [95, 85, 70, 50]:
        from io import BytesIO
        buf = BytesIO()
        rgb_img = resized.convert("RGB") if resized.mode != "RGB" else resized
        rgb_img.save(buf, format="JPEG", quality=quality)
        size = buf.tell()
        assert size > 0
        buf.seek(0)
        loaded = Image.open(buf)
        assert loaded.size == new_size
        assert loaded.format == "JPEG"


def test_ui(qtbot):
    window = ImageOptimizer()
    qtbot.addWidget(window)
    window.show()

    # Load test image using PIL, convert to QImage, and set as clipboard image
    img_path = os.path.join(os.path.dirname(__file__), "test.png")
    assert os.path.exists(img_path)
    pil_img = PILImage.open(img_path)
    data = pil_img.tobytes("raw", "RGBA") if pil_img.mode == "RGBA" else pil_img.tobytes()
    fmt = QImage.Format.Format_RGBA8888 if pil_img.mode == "RGBA" else QImage.Format.Format_RGB888
    qimg = QImage(data, pil_img.width, pil_img.height, fmt)
    QApplication.clipboard().setImage(qimg)

    # Simulate clicking 'Load from Clipboard'
    qtbot.mouseClick(window.load_button, Qt.MouseButton.LeftButton)
    assert window.status_label.text() == "Image processed successfully"
    assert window.original_image is not None
    assert window.processed_image is not None
    assert window.copy_button.isEnabled()

    # Simulate clicking size and quality preset buttons
    for size_btn in window.size_button_group.buttons():
        qtbot.mouseClick(size_btn, Qt.MouseButton.LeftButton)
        assert size_btn.isChecked()
        # After clicking, processed image should update
        assert window.processed_image is not None
        assert window.status_label.text() == "Image processed successfully"
        assert window.stats_label.text().startswith("Original:")

    for quality_btn in window.quality_button_group.buttons():
        qtbot.mouseClick(quality_btn, Qt.MouseButton.LeftButton)
        assert quality_btn.isChecked()
        assert window.processed_image is not None
        assert window.status_label.text() == "Image processed successfully"
        assert window.stats_label.text().startswith("Original:")

    # Simulate clicking 'Copy to Clipboard'
    qtbot.mouseClick(window.copy_button, Qt.MouseButton.LeftButton)
    assert window.status_label.text() == "Image copied to clipboard"

    # Clear displays and check
    window.clear_image_displays()
    assert window.original_image_label.text() == "Original Image"
    assert window.processed_image_label.text() == "Processed Image"
    assert window.stats_label.text() == ""
