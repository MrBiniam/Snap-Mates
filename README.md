# Filtrawy - Advanced Image Processing Application

A modern and powerful image processing application built with Python, featuring a user-friendly GUI and extensive filter collection. Created by Cherinet ([Chereanbot](https://github.com/Chereanbot/Filtrawy)).

## Features

* Modern and intuitive graphical user interface
* Real-time filter preview with side-by-side comparison
* Extensive collection of image processing filters
* Live camera feed support
* Batch processing capabilities
* Keyboard shortcuts for common operations
* Undo/Redo functionality
* Zoom and fit-to-window options

### Available Filters:

* Basic Filters:
  * Color/RGB
  * Grayscale
  * Threshold

* Enhancement Filters:
  * Increase/Decrease Contrast
  * Log Transformation
  * Temperature Adjustment
  * Saturation Control

* Blur Filters:
  * Gaussian Blur
  * Median Blur
  * Average Blur

* Edge Detection:
  * Sobel Filter
  * Laplacian Filter
  * Prewitt Filter

* Effects:
  * Sepia
  * Vintage
  * Vignette
  * Unsharp Mask
  * Histogram Equalization

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository:
```bash
git clone https://github.com/Chereanbot/Filtrawy.git
cd Filtrawy
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Interface Overview:
   * Top Menu: File operations, edit functions, and view controls
   * Left Panel: Filter selection buttons
   * Center: Original and filtered image display
   * Control Panel: Slider controls for filter parameters

3. Basic Operations:
   * Open Image: File > Open Image or Ctrl+O
   * Save Image: File > Save or Ctrl+S
   * Undo/Redo: Edit menu or Ctrl+Z/Ctrl+Y
   * Reset Image: Edit > Reset Image or Ctrl+R
   * Zoom: View menu or Ctrl+Plus/Minus

4. Applying Filters:
   * Select a filter from the left panel
   * Adjust parameters using the sliders
   * See real-time preview of changes
   * Use undo/redo to navigate through changes

5. Batch Processing:
   * Select File > Batch Process
   * Choose input and output folders
   * Select filter to apply
   * Process multiple images automatically

## Keyboard Shortcuts

* File Operations:
  * Ctrl+O: Open Image
  * Ctrl+S: Save
  * Ctrl+Shift+S: Save As

* Edit Operations:
  * Ctrl+Z: Undo
  * Ctrl+Y: Redo
  * Ctrl+R: Reset Image

* View Operations:
  * Ctrl++: Zoom In
  * Ctrl+-: Zoom Out
  * Ctrl+0: Fit to Window

## Requirements

* Python 3.8+
* OpenCV (cv2)
* NumPy
* Pillow (PIL)
* tkinter (usually comes with Python)

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* Created by Cherinet ([Chereanbot](https://github.com/Chereanbot/Filtrawy))
* Built using OpenCV, NumPy, and tkinter
* Special thanks to the Python imaging community

## Contact

For questions or suggestions, please open an issue on the [GitHub repository](https://github.com/Chereanbot/Filtrawy).
