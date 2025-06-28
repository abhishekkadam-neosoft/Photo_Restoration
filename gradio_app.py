#!/usr/bin/env python3
"""
Gradio Web App for Photo Restoration
A user-friendly web interface for the Bringing Old Photos Back to Life system
"""

import gradio as gr
import os
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import time

# Import our photo restoration functions
from photo_restoration_runner import restore_photos, make_grid

def check_model_files():
    """Check if required model files and directories exist"""
    required = [
        ("Face Detection Model", "photo_restoration/Face_Detection/shape_predictor_68_face_landmarks.dat"),
        ("Face Enhancement Checkpoints", "photo_restoration/Face_Enhancement/checkpoints"),
        ("Global Checkpoints", "photo_restoration/Global/checkpoints"),
        ("Restoration Script", "photo_restoration/run.py"),
    ]
    results = []
    for name, path in required:
        if os.path.exists(path):
            if os.path.isdir(path):
                count = len(os.listdir(path))
                if count > 0:
                    results.append((name, path, True, f"Directory with {count} files"))
                else:
                    results.append((name, path, False, "Directory is empty"))
            else:
                size = os.path.getsize(path)
                results.append((name, path, True, f"File size: {size} bytes"))
        else:
            results.append((name, path, False, "Missing"))
    return results

def debug_check_setup():
    """Gradio function to check setup and return a markdown report"""
    results = check_model_files()
    report = "# 🛠️ System Check\n\n"
    all_ok = True
    for name, path, ok, info in results:
        if ok:
            report += f"- ✅ **{name}**: `{path}` ({info})\n"
        else:
            report += f"- ❌ **{name}**: `{path}` ({info})\n"
            all_ok = False
    if all_ok:
        report += "\n---\n**All required files and models are present!**\n"
    else:
        report += "\n---\n**Some files or models are missing. Please run `setup_environment.py` again.**\n"
    return report

def create_slider_comparison(original_image, restored_image):
    """
    Create a slider comparison between original and restored images
    
    Args:
        original_image: PIL Image of original
        restored_image: PIL Image of restored
    
    Returns:
        HTML string for slider comparison
    """
    if original_image is None or restored_image is None:
        return "No images to compare"
    
    # Convert images to base64 for HTML embedding
    import base64
    import io
    
    def image_to_base64(img):
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    original_b64 = image_to_base64(original_image)
    restored_b64 = image_to_base64(restored_image)
    
    # Create HTML with CSS for slider comparison
    html = f"""
    <style>
    .comparison-container {{
        position: relative;
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        overflow: hidden;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .comparison-before {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
    }}
    
    .comparison-after {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 2;
        clip-path: polygon(0 0, 50% 0, 50% 100%, 0 100%);
        transition: clip-path 0.1s ease;
    }}
    
    .comparison-slider {{
        position: absolute;
        top: 0;
        left: 50%;
        width: 4px;
        height: 100%;
        background: #fff;
        z-index: 3;
        cursor: ew-resize;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        transform: translateX(-50%);
    }}
    
    .comparison-slider::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 40px;
        height: 40px;
        background: #fff;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}
    
    .comparison-slider::after {{
        content: '◀ ▶';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 12px;
        color: #333;
        font-weight: bold;
    }}
    
    .comparison-labels {{
        position: absolute;
        bottom: 10px;
        z-index: 4;
        width: 100%;
        display: flex;
        justify-content: space-between;
        padding: 0 10px;
        color: white;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }}
    </style>
    
    <div class="comparison-container" id="comparison-container">
        <img src="data:image/png;base64,{original_b64}" class="comparison-before" alt="Before">
        <img src="data:image/png;base64,{restored_b64}" class="comparison-after" alt="After" id="after-image">
        <div class="comparison-slider" id="slider"></div>
        <div class="comparison-labels">
            <span>Before</span>
            <span>After</span>
        </div>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const container = document.getElementById('comparison-container');
        const slider = document.getElementById('slider');
        const afterImage = document.getElementById('after-image');
        
        let isDragging = false;
        
        function updateSlider(e) {{
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
            
            slider.style.left = percentage + '%';
            afterImage.style.clipPath = `polygon(0 0, ${{percentage}}% 0, ${{percentage}}% 100%, 0 100%)`;
        }}
        
        slider.addEventListener('mousedown', function() {{
            isDragging = true;
        }});
        
        document.addEventListener('mousemove', function(e) {{
            if (isDragging) {{
                updateSlider(e);
            }}
        }});
        
        document.addEventListener('mouseup', function() {{
            isDragging = false;
        }});
        
        container.addEventListener('click', function(e) {{
            updateSlider(e);
        }});
    }});
    </script>
    """
    
    return html

def process_single_image(image, use_gpu, with_scratch, high_resolution):
    """
    Process a single uploaded image
    
    Args:
        image: PIL Image object from Gradio
        use_gpu: Boolean for GPU usage
        with_scratch: Boolean for scratch removal
        high_resolution: Boolean for high resolution mode
    
    Returns:
        tuple: (original_image, restored_image, download_path)
    """
    if image is None:
        return None, None, None
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save uploaded image with original quality
        input_path = os.path.join(input_dir, "uploaded_image.jpg")
        image.save(input_path, quality=100)  # Maximum quality
        
        print(f"Saved input image to: {input_path}")
        print(f"Input directory contents: {os.listdir(input_dir)}")
        print(f"Image size: {image.size}, Mode: {image.mode}")
        
        # Set GPU ID
        gpu_id = 0 if use_gpu else -1
        
        # Process the image
        print(f"Processing image with GPU: {use_gpu}, Scratch removal: {with_scratch}, High res: {high_resolution}")
        
        success = restore_photos(
            input_folder=input_dir,
            output_folder=output_dir,
            gpu_id=gpu_id,
            with_scratch=with_scratch,
            hr=high_resolution
        )
        
        print(f"Restoration success: {success}")
        print(f"Output directory contents: {os.listdir(output_dir) if os.path.exists(output_dir) else 'Output dir not found'}")
        
        if not success:
            print("Restoration failed, returning None")
            return None, None, None
        
        # Check each stage for debugging
        stage_dirs = ["stage_1_restore_output", "stage_2_detection_output", "stage_3_face_output", "final_output"]
        for stage in stage_dirs:
            stage_path = os.path.join(output_dir, stage)
            if os.path.exists(stage_path):
                contents = os.listdir(stage_path)
                print(f"Stage {stage}: {len(contents)} items")
                if contents:
                    print(f"  Contents: {contents}")
                    # Check subdirectories
                    for item in contents:
                        item_path = os.path.join(stage_path, item)
                        if os.path.isdir(item_path):
                            sub_contents = os.listdir(item_path)
                            print(f"    {item}/: {sub_contents}")
        
        # Load results - check multiple possible output locations
        possible_output_dirs = [
            os.path.join(output_dir, "final_output"),
            output_dir,
            os.path.join(output_dir, "restored_image"),
            os.path.join(output_dir, "stage_1_restore_output", "restored_image"),
            os.path.join(output_dir, "stage_1_restore_output", "origin"),
            os.path.join(output_dir, "stage_3_face_output", "each_img")
        ]
        
        restored_image = None
        restored_path = None
        for output_subdir in possible_output_dirs:
            print(f"Checking for results in: {output_subdir}")
            if os.path.exists(output_subdir):
                print(f"Found output directory: {output_subdir}")
                contents = os.listdir(output_subdir)
                print(f"Contents: {contents}")
                
                # Look for restored image
                test_path = os.path.join(output_subdir, "uploaded_image.jpg")
                if os.path.exists(test_path):
                    print(f"Found restored image at: {test_path}")
                    restored_image = Image.open(test_path)
                    restored_path = test_path
                    break
                else:
                    # Check for any image files
                    for file in contents:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            test_path = os.path.join(output_subdir, file)
                            print(f"Found image file: {test_path}")
                            restored_image = Image.open(test_path)
                            restored_path = test_path
                            break
                    if restored_image:
                        break
        
        if restored_image:
            print("Creating high-quality download file")
            
            # Create a permanent download directory
            download_dir = "downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # Generate unique filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"restored_photo_{timestamp}.jpg"
            download_path = os.path.join(download_dir, download_filename)
            
            # Save restored image with maximum quality
            restored_image.save(download_path, quality=100, optimize=False)
            print(f"Saved high-quality restored image to: {download_path}")
            
            print("Returning original and restored images for comparison")
            return image, restored_image, download_path
        else:
            print("No restored image found")
            print("Possible reasons:")
            print("1. No face detected in the image")
            print("2. Image quality too poor for processing")
            print("3. Image size or format not supported")
            print("4. Face detection failed")
            return None, None, None

def process_multiple_images(files, use_gpu, with_scratch, high_resolution):
    """
    Process multiple uploaded images
    
    Args:
        files: List of file paths from Gradio
        use_gpu: Boolean for GPU usage
        with_scratch: Boolean for scratch removal
        high_resolution: Boolean for high resolution mode
    
    Returns:
        list: List of (original, restored, comparison) tuples
    """
    if not files:
        return []
    
    results = []
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy uploaded files
        for i, file_path in enumerate(files):
            if file_path is not None:
                ext = Path(file_path).suffix
                new_name = f"image_{i}{ext}"
                new_path = os.path.join(input_dir, new_name)
                shutil.copy2(file_path, new_path)
        
        # Set GPU ID
        gpu_id = 0 if use_gpu else -1
        
        # Process all images
        print(f"Processing {len(files)} images with GPU: {use_gpu}, Scratch removal: {with_scratch}, High res: {high_resolution}")
        
        success = restore_photos(
            input_folder=input_dir,
            output_folder=output_dir,
            gpu_id=gpu_id,
            with_scratch=with_scratch,
            hr=high_resolution
        )
        
        if not success:
            return [(None, None, None)] * len(files)
        
        # Load results
        final_output_dir = os.path.join(output_dir, "final_output")
        if os.path.exists(final_output_dir):
            for i, file_path in enumerate(files):
                if file_path is not None:
                    original_image = Image.open(file_path)
                    ext = Path(file_path).suffix
                    restored_name = f"image_{i}{ext}"
                    restored_path = os.path.join(final_output_dir, restored_name)
                    
                    if os.path.exists(restored_path):
                        restored_image = Image.open(restored_path)
                        comparison = make_grid(original_image, restored_image)
                        results.append((original_image, restored_image, comparison))
                    else:
                        results.append((original_image, None, None))
                else:
                    results.append((None, None, None))
        
        return results

def create_gradio_interface():
    """Create the Gradio interface"""
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .output-image {
        border: 2px solid #ddd;
        border-radius: 8px;
        margin: 10px;
    }
    .comparison-image {
        border: 3px solid #007bff;
        border-radius: 8px;
        margin: 10px;
    }
    """
    
    with gr.Blocks(css=css, title="Photo Restoration App") as app:
        gr.Markdown(
            """
            # 🖼️ Photo Restoration App
            **Bringing Old Photos Back to Life**
            
            This app uses Microsoft's advanced AI model to restore old, damaged, or low-quality photos.
            Upload your photos and see the magic happen!
            """
        )
        
        with gr.Tab("Single Image"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Upload Settings")
                    
                    # Options
                    use_gpu = gr.Checkbox(
                        label="Use GPU (faster, requires CUDA)",
                        value=False,
                        info="Check if you have a CUDA-compatible GPU"
                    )
                    
                    with_scratch = gr.Checkbox(
                        label="Remove Scratches",
                        value=True,
                        info="Enable scratch and damage removal"
                    )
                    
                    gr.Markdown("### Resolution Settings")
                    
                    high_resolution = gr.Checkbox(
                        label="High Resolution Processing",
                        value=True,
                        info="Enable high-resolution processing (better quality, slower)"
                    )
                    
                    process_btn = gr.Button(
                        "🔄 Restore Photo",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("### Upload Your Photo")
                    input_image = gr.Image(
                        label="Upload Image",
                        type="pil",
                        height=400
                    )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Original")
                    original_output = gr.Image(label="Original Image", height=300)
                
                with gr.Column():
                    gr.Markdown("### Restored")
                    restored_output = gr.Image(label="Restored Image", height=300)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Download Restored Image")
                    download_file = gr.File(
                        label="Download",
                        visible=False,
                        interactive=False
                    )
                    download_status = gr.Markdown("Process an image to enable download")
            
            # Connect the process button
            process_btn.click(
                fn=process_single_image,
                inputs=[input_image, use_gpu, with_scratch, high_resolution],
                outputs=[original_output, restored_output, download_file]
            )
            
            # Update download status when file is available
            def update_download_status(download_path):
                if download_path and os.path.exists(download_path):
                    return f"✅ **Download Ready!**\n\nClick the file above to download your restored image.\n\nFile: `{os.path.basename(download_path)}`"
                else:
                    return "❌ **No restored image available**\n\nPlease process an image first."
            
            download_file.change(
                fn=update_download_status,
                inputs=[download_file],
                outputs=[download_status]
            )
        
        with gr.Tab("Multiple Images"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Upload Settings")
                    
                    # Options for multiple images
                    use_gpu_multi = gr.Checkbox(
                        label="Use GPU (faster, requires CUDA)",
                        value=False,
                        info="Check if you have a CUDA-compatible GPU"
                    )
                    
                    with_scratch_multi = gr.Checkbox(
                        label="Remove Scratches",
                        value=True,
                        info="Enable scratch and damage removal"
                    )
                    
                    gr.Markdown("### Resolution Settings")
                    
                    high_resolution_multi = gr.Checkbox(
                        label="High Resolution Processing",
                        value=True,
                        info="Enable high-resolution processing (better quality, slower)"
                    )
                    
                    process_multi_btn = gr.Button(
                        "🔄 Restore All Photos",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("### Upload Multiple Photos")
                    input_files = gr.File(
                        label="Upload Images",
                        file_count="multiple",
                        file_types=["image"]
                    )
            
            # Gallery for results
            gr.Markdown("### Results")
            gallery_output = gr.Gallery(
                label="Restored Images",
                show_label=True,
                elem_id="gallery",
                columns=3,
                rows=2,
                height="auto"
            )
            
            # Connect the process button for multiple images
            process_multi_btn.click(
                fn=process_multiple_images,
                inputs=[input_files, use_gpu_multi, with_scratch_multi, high_resolution_multi],
                outputs=gallery_output
            )
        
        with gr.Tab("Debug/Check Setup"):
            gr.Markdown("## 🛠️ System Check\nClick the button below to verify all required models and files are present.")
            check_btn = gr.Button("🔍 Run System Check", variant="primary")
            check_output = gr.Markdown()
            check_btn.click(fn=debug_check_setup, inputs=[], outputs=check_output)
            
            gr.Markdown("## 👤 Face Detection Test\nUpload an image to test if it's suitable for face detection.")
            test_image = gr.Image(label="Upload Image for Face Detection Test", type="pil")
            test_btn = gr.Button("🔍 Test Face Detection", variant="secondary")
            test_output = gr.Markdown()
            test_btn.click(fn=test_face_detection, inputs=[test_image], outputs=test_output)
        
        with gr.Tab("About"):
            gr.Markdown(
                """
                ## About This App
                
                This photo restoration app is based on Microsoft's **"Bringing Old Photos Back to Life"** research project.
                
                ### Features:
                - **Photo Restoration**: Restore old, damaged, or low-quality photos
                - **Scratch Removal**: Remove scratches and physical damage
                - **Face Enhancement**: Specialized face restoration and enhancement
                - **High Resolution**: Option for high-resolution output
                - **GPU/CPU Support**: Works on both CPU and GPU
                
                ### How to Use:
                1. **Single Image**: Upload one photo and see the restoration
                2. **Multiple Images**: Upload several photos for batch processing
                3. **Settings**: Choose GPU/CPU, scratch removal, and resolution options
                
                ### Technical Details:
                - Uses PyTorch-based deep learning models
                - Supports various image formats (JPEG, PNG, BMP, TIFF)
                - Processing time depends on image size and hardware
                
                ### Tips:
                - Use GPU mode for faster processing (if available)
                - Enable scratch removal for damaged photos
                - High resolution mode produces better results but takes longer
                - Larger images take more time to process
                
                ### Citation:
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
                """
            )
        
        # Footer
        gr.Markdown(
            """
            ---
            **Note**: Processing time depends on image size and your hardware. GPU mode is much faster than CPU mode.
            """
        )
    
    return app

def main():
    """Main function to run the Gradio app"""
    print("Starting Photo Restoration Gradio App...")
    
    # Check if photo_restoration directory exists
    if not os.path.exists("photo_restoration"):
        print("Error: photo_restoration directory not found!")
        print("Please run setup_environment.py first to set up the environment.")
        return
    
    # Create and launch the app
    app = create_gradio_interface()
    
    # Launch with appropriate settings
    app.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,       # Default Gradio port
        share=False,            # Set to True if you want a public link
        debug=True,
        show_error=True
    )

def test_face_detection(image):
    """Test if face detection works on the uploaded image"""
    if image is None:
        return "No image uploaded"
    
    try:
        # Try to import face detection
        import sys
        sys.path.append("photo_restoration/Face_Detection")
        
        # This is a simplified test - in practice, the actual face detection
        # happens inside the restoration pipeline
        report = f"## Face Detection Test\n\n"
        report += f"**Image Info:**\n"
        report += f"- Size: {image.size}\n"
        report += f"- Mode: {image.mode}\n"
        report += f"- Format: {image.format}\n\n"
        
        # Basic image quality checks
        width, height = image.size
        if width < 100 or height < 100:
            report += "⚠️ **Warning:** Image is very small. Face detection may fail.\n\n"
        
        if width > 2000 or height > 2000:
            report += "⚠️ **Warning:** Image is very large. Processing may be slow.\n\n"
        
        # Check if image has reasonable contrast
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            # Color image
            gray = np.mean(img_array, axis=2)
        else:
            # Grayscale
            gray = img_array
        
        contrast = np.std(gray)
        if contrast < 20:
            report += "⚠️ **Warning:** Image has low contrast. Face detection may fail.\n\n"
        
        report += "**Recommendations:**\n"
        report += "- Ensure the image contains a clear, front-facing face\n"
        report += "- Face should be reasonably sized (not too small)\n"
        report += "- Image should have good lighting and contrast\n"
        report += "- Avoid extreme angles or heavily obscured faces\n\n"
        
        report += "**Note:** This is a basic check. The actual face detection happens during restoration.\n"
        
        return report
        
    except Exception as e:
        return f"Error testing face detection: {str(e)}"

def compare_images(original, restored, slider_value):
    """
    Function to show either original or restored image based on slider
    """
    if original is None or restored is None:
        return None
    
    # Convert slider value (0-100) to choose between original and restored
    if slider_value < 50:
        return original
    else:
        return restored

if __name__ == "__main__":
    main() 