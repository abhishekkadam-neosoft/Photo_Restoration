# 🖼️ Photo Restoration App

**Bringing Old Photos Back to Life** - A powerful AI-powered photo restoration application based on Microsoft's research.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.8+-red.svg)](https://pytorch.org)
[![Gradio](https://img.shields.io/badge/Gradio-3.0+-green.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Overview

This application uses Microsoft's advanced AI model to restore old, damaged, or low-quality photos. It can remove scratches, enhance faces, and improve overall image quality while preserving the original character of the photo.

### ✨ Features

- **🖼️ Photo Restoration**: Restore old, damaged, or low-quality photos
- **🔧 Scratch Removal**: Remove scratches and physical damage
- **👤 Face Enhancement**: Specialized face restoration and enhancement
- **⚡ GPU/CPU Support**: Works on both CPU and GPU for optimal performance
- **🌐 Web Interface**: User-friendly Gradio web app
- **📁 Batch Processing**: Process multiple images at once
- **💾 High-Quality Downloads**: Download restored images in original quality
- **🔍 Debug Tools**: Built-in system checks and face detection testing

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **Linux/Ubuntu** (tested on Ubuntu 20.04+)
- **8GB+ RAM** (16GB+ recommended)
- **GPU with CUDA** (optional, for faster processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd inpainting_and_enhancing
   ```

2. **Run the setup script**
   ```bash
   python3 setup_environment.py
   ```
   
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Clone the Microsoft photo restoration repository
   - Download required model files (~2GB)

3. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

## 🎯 Usage

### Web Interface (Recommended)

1. **Start the Gradio app**
   ```bash
   python3 gradio_app.py
   ```

2. **Open your browser**
   - Go to: `http://127.0.0.1:7860`
   - Or use the launcher: `python3 run_gradio_app.py`

3. **Upload and restore photos**
   - Upload a photo with a visible face
   - Adjust settings (GPU, scratch removal, high resolution)
   - Click "Restore Photo"
   - Download the restored image

### Command Line Interface

#### Single Image Restoration
```bash
python3 photo_restoration_runner.py \
    --input_folder path/to/input \
    --output_folder path/to/output \
    --gpu_id 0 \
    --with_scratch \
    --hr
```

#### Multiple Images
```bash
python3 run_restoration.py \
    --input_folder path/to/input \
    --output_folder path/to/output \
    --gpu_id -1 \
    --with_scratch \
    --hr
```

### Testing

Run the test script to verify everything is working:
```bash
python3 test_photo_restoration.py
```

## 🎛️ Settings & Options

### Processing Options

| Option | Description | Default |
|--------|-------------|---------|
| **Use GPU** | Enable CUDA acceleration | `False` |
| **Remove Scratches** | Enable scratch/damage removal | `True` |
| **High Resolution** | Enable high-resolution processing | `True` |

### Image Requirements

- **Format**: JPEG, PNG, BMP, TIFF
- **Face Detection**: Must contain a detectable human face
- **Size**: 100x100 to 2000x2000 pixels recommended
- **Quality**: Clear, well-lit images work best

## 📁 Project Structure

```
inpainting_and_enhancing/
├── 📄 README.md                    # This file
├── 🐍 setup_environment.py         # Environment setup script
├── 🌐 gradio_app.py               # Main Gradio web app
├── 🚀 run_gradio_app.py           # Gradio app launcher
├── 🖼️ photo_restoration_runner.py  # Single image processor
├── 📦 run_restoration.py          # Batch image processor
├── 🧪 test_photo_restoration.py   # Test script
├── 🐛 debug_restoration.py        # Debug script
├── 📁 photo_restoration/          # Microsoft's restoration code
├── 📁 downloads/                  # Restored images (auto-created)
├── 📁 test_results/              # Test outputs (auto-created)
├── 📁 venv/                      # Python virtual environment
└── 📄 .gitignore                 # Git ignore file
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **"No restored image found"**
- **Cause**: No face detected in the image
- **Solution**: Use images with clear, front-facing faces

#### 2. **"photo_restoration directory not found"**
- **Cause**: Setup script not run
- **Solution**: Run `python3 setup_environment.py`

#### 3. **"CUDA out of memory"**
- **Cause**: GPU memory insufficient
- **Solution**: Use CPU mode or smaller images

#### 4. **"Model files missing"**
- **Cause**: Incomplete download
- **Solution**: Re-run setup script

### Debug Tools

Use the **"Debug/Check Setup"** tab in the Gradio app to:
- ✅ Check if all model files are present
- 🔍 Test face detection on your images
- 📊 View system status

### Performance Tips

- **GPU Mode**: 5-10x faster than CPU
- **Image Size**: Larger images take longer to process
- **High Resolution**: Better quality but slower
- **Batch Processing**: More efficient for multiple images

## 📊 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 18.04+ / Linux
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Python**: 3.8+

### Recommended Requirements
- **OS**: Ubuntu 20.04+ / Linux
- **RAM**: 16GB+
- **GPU**: NVIDIA with 4GB+ VRAM
- **Storage**: 20GB+ free space
- **Python**: 3.9+

## 🔬 Technical Details

### Models Used
- **Face Detection**: dlib shape predictor (68 landmarks)
- **Global Restoration**: PyTorch-based CNN
- **Face Enhancement**: Specialized face restoration model

### Processing Pipeline
1. **Face Detection**: Locate and analyze faces
2. **Global Restoration**: Remove scratches and damage
3. **Face Enhancement**: Specialized face restoration
4. **Final Output**: High-quality restored image

### Dependencies
- **PyTorch**: Deep learning framework
- **OpenCV**: Image processing
- **dlib**: Face detection
- **PIL/Pillow**: Image handling
- **Gradio**: Web interface
- **NumPy**: Numerical computing

## 📚 Citation

If you use this work, please cite the original Microsoft paper:

```bibtex
@inproceedings{wan2020bringing,
  title={Bringing Old Photos Back to Life},
  author={Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={2747--2757},
  year={2020}
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft Research** for the original photo restoration model
- **Gradio** for the web interface framework
- **Open source community** for various dependencies

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Use the debug tools** in the Gradio app
3. **Review the console logs** for error messages
4. **Open an issue** with detailed information

---

**Made with ❤️ for preserving memories through AI-powered photo restoration** 