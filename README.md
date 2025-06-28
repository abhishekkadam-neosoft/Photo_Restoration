# Bringing Old Photos Back to Life - Local Setup

This is a local setup for Microsoft's "Bringing Old Photos Back to Life" photo restoration model, converted from the original Colab notebook to work on your local PC.

## Features

- **Photo Restoration**: Restore old, damaged, or low-quality photos
- **Scratch Removal**: Remove scratches and physical damage from photos
- **Face Enhancement**: Specialized face restoration and enhancement
- **High Resolution**: Option for high-resolution output
- **CPU/GPU Support**: Works on both CPU and GPU (CUDA)

## Prerequisites

- Python 3.7 or higher
- Git
- Internet connection (for downloading models and dependencies)

## Quick Setup

1. **Run the setup script**:
   ```bash
   python3 setup_environment.py
   ```

2. **Use the helper script** (recommended):
   ```bash
   python3 activate_and_run.py
   ```
   This will give you options to test the setup or run photo restoration.

3. **Or activate manually and run**:
   ```bash
   # On Linux/Mac:
   source photo_restoration_env/bin/activate
   
   # On Windows:
   photo_restoration_env\Scripts\activate
   
   # Then run:
   python test_setup.py  # Test the setup
   python run_restoration.py  # Run photo restoration
   ```

## Usage

### Method 1: Helper Script (Recommended)
```bash
python3 activate_and_run.py
```
This will automatically activate the virtual environment and give you options to:
- Test the setup
- Run photo restoration interactively

### Method 2: Interactive Script
```bash
# Activate virtual environment first
source photo_restoration_env/bin/activate  # Linux/Mac
# or
photo_restoration_env\Scripts\activate     # Windows

# Then run
python run_restoration.py
```
This will prompt you for:
- Input folder path (containing your old photos)
- Output folder path (where results will be saved)
- GPU usage preference
- Scratch removal preference
- High resolution preference

### Method 3: Direct Function Call
```python
# Activate virtual environment first, then:
from photo_restoration_runner import process_custom_photos

# Process your photos
process_custom_photos(
    input_folder="path/to/your/photos",
    output_folder="path/to/output",
    gpu_id=-1,  # -1 for CPU, 0 for GPU
    with_scratch=True,  # Enable scratch removal
    hr=True  # Enable high resolution
)
```

### Method 4: Command Line (Advanced)
```bash
# Activate virtual environment first, then:
cd photo_restoration
python run.py --input_folder /path/to/input --output_folder /path/to/output --GPU -1 --with_scratch --HR
```

## Parameters

- `--input_folder`: Path to folder containing input images
- `--output_folder`: Path to folder where results will be saved
- `--GPU`: GPU ID (-1 for CPU, 0 for first GPU)
- `--with_scratch`: Enable scratch removal mode
- `--HR`: Enable high resolution mode

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Output Structure

The output folder will contain:
```
output/
├── final_output/          # Final restored images
├── comparison_*.jpg       # Before/after comparisons
└── intermediate_results/  # Intermediate processing steps
```

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**:
   - Use `--GPU -1` for CPU-only mode
   - Install CUDA version compatible with your PyTorch version

2. **Memory Issues**:
   - Use CPU mode for large images
   - Reduce image resolution before processing

3. **dlib Installation Issues**:
   - On Windows: Install Visual Studio Build Tools
   - On Linux: Install `build-essential` and `cmake`
   - On Mac: Install Xcode Command Line Tools

4. **Model Download Issues**:
   - Check internet connection
   - Try downloading manually from the provided URLs

5. **Path Issues**:
   - Make sure you're running scripts from the main directory (not inside photo_restoration)
   - Use absolute paths if relative paths don't work

### Performance Tips

- **GPU Mode**: Much faster processing, requires CUDA
- **CPU Mode**: Slower but works on any system
- **Batch Processing**: Process multiple images at once for efficiency
- **Image Size**: Larger images take longer to process

## Examples

### Basic Photo Restoration
```python
from photo_restoration_runner import restore_photos

restore_photos(
    input_folder="old_photos",
    output_folder="restored_photos",
    gpu_id=-1
)
```

### Advanced Restoration with Scratch Removal
```python
from photo_restoration_runner import restore_photos

restore_photos(
    input_folder="damaged_photos",
    output_folder="restored_photos",
    gpu_id=0,  # Use GPU
    with_scratch=True,  # Remove scratches
    hr=True  # High resolution
)
```

## File Structure

After setup, your directory will look like:
```
your_project/
├── setup_environment.py          # Setup script
├── activate_and_run.py           # Helper script
├── photo_restoration_runner.py   # Main runner
├── run_restoration.py            # Interactive script
├── test_setup.py                 # Test script
├── README.md                     # This file
├── photo_restoration_env/        # Virtual environment
└── photo_restoration/            # Microsoft repository
    ├── run.py
    ├── Face_Detection/
    ├── Face_Enhancement/
    └── Global/
```

## License

This project is based on the Microsoft Bringing Old Photos Back to Life model. Please refer to the original repository for licensing information.

## Citation

If you use this work, please cite the original paper:
```
@inproceedings{wan2020bringing,
  title={Bringing Old Photos Back to Life},
  author={Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={2747--2757},
  year={2020}
}
```

## Support

For issues related to:
- **Setup/Installation**: Check the troubleshooting section
- **Model Performance**: Refer to the original paper and repository
- **Code Issues**: Check the GitHub issues of the original repository 