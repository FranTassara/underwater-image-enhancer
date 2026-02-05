# Underwater Image Enhancer

A web application that enhances underwater scuba diving photos using AI and traditional image processing techniques. It corrects the blue/green color cast, improves clarity, and restores contrast — common issues in underwater photography.

## Features

- **WaterNet (AI)** — Deep learning model specialized in underwater image enhancement. Runs on CPU (~2-5s per image).
- **OpenCV pipeline** — Fast traditional processing: white balance, CLAHE, gamma correction, and sharpening. Instant results.
- **Before/After slider** — Compare the original and enhanced images side by side.
- **Drag & drop upload** — Simple interface, no sign-up required.

## Tech Stack

- **Backend:** Python, Flask
- **AI Model:** [WaterNet](https://github.com/tnwei/waternet) via PyTorch Hub
- **Image Processing:** OpenCV, NumPy, Pillow
- **Frontend:** HTML, CSS, JavaScript (no framework)

## Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/underwater-image-enhancer.git
cd underwater-image-enhancer

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install flask opencv-python numpy pillow
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

## How It Works

1. Upload an underwater photo (JPG, PNG, BMP, TIFF, or WebP)
2. Choose a method: **WaterNet** (AI, better quality) or **OpenCV** (faster)
3. Click "Enhance" and wait a few seconds
4. Compare the result using the before/after slider
5. Download the enhanced image

## Project Structure

```
├── app.py              # Flask server
├── enhance.py          # Image enhancement logic (WaterNet + OpenCV)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main page
└── static/
    ├── css/style.css   # Styling
    ├── js/app.js       # Frontend logic
    └── uploads/        # Processed images (gitignored)
```

## Notes

- The first time you use WaterNet, it will automatically download the model weights (~50 MB).
- Large images are resized to max 1920px width before processing to avoid memory issues.
- GPU is not required — all processing runs on CPU.
