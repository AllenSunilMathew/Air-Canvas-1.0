# Airnvas-1.0
🖌️ AI Sketch-to-Image Generator

An AI-powered desktop application that transforms hand-drawn sketches into high-quality realistic or stylized images using Generative AI and diffusion models.

📌 Overview

This project implements a sketch-to-image generation system using Stable Diffusion and ControlNet. Users can draw simple sketches on a canvas and generate detailed images in multiple styles (Realistic, Animated, Outline).

The system runs locally and integrates a web-based frontend with a FastAPI backend powered by deep learning models.

🚀 Features

🎨 Interactive drawing canvas

✏️ Brush and eraser tools

🎭 Multiple style modes (Realistic, Animated, Outline)

⚡ Diffusion-based image generation

🧠 Vision-based prompt generation

💻 Fully local processing (no cloud dependency)

🔁 Multiple generation cycles with reset support

🏗️ System Architecture

Flow:

User Sketch → Image Preprocessing → Prompt Generation → 
Stable Diffusion + ControlNet → Generated Image → Display Result

Components:

Frontend (HTML, CSS, JavaScript)

Backend API (FastAPI)

AI Models (Stable Diffusion, ControlNet, Vision Model)

🛠️ Technologies Used

Python

FastAPI

PyTorch

Diffusers

Transformers

OpenCV

HTML / CSS / JavaScript

💻 System Requirements

Windows 10 / 11 (64-bit)

Minimum 16 GB RAM

NVIDIA GPU with CUDA support (recommended)

Python 3.9+

Stable internet connection (for first model download)

⚙️ Installation
1️⃣ Clone the Repository
git clone <repository-url>
cd AI_Sketch_Product

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Install CUDA-enabled PyTorch (GPU systems)
pip install torch --index-url https://download.pytorch.org/whl/cu118

5️⃣ Run run.py

6️⃣ Launchs Application

Opens:

draw.html

result.html

🔄 First-Time Run

On first execution, required AI models will be downloaded automatically and cached locally. This may take several minutes.

🧪 Usage

Draw a sketch on the canvas.

Select a style (Realistic / Animated / Outline).

Click Generate.

View the generated image on the Result page.

Click Clear to reset and draw again.

📊 Performance Notes

GPU acceleration significantly improves generation speed.

Inference time depends on hardware configuration.

RTX 20xx and above GPUs are recommended.

⚠️ Limitations

Requires high hardware resources.

Limited style customization.

Single image generation per request.

🔮 Future Enhancements

High-resolution model integration

Depth-based control

Mobile application support

Real-time optimization

📄 License

This project is developed for educational and research purposes.
Ensure compliance with the licenses of Stable Diffusion and related models.

🙏 Acknowledgements

Stable Diffusion

Hugging Face

PyTorch

Open-source AI community



process

python run.py
venv\Scripts\activate
cd backend
uvicorn main:app --reload
