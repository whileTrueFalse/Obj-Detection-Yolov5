from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from pathlib import Path
import os
import argparse
from PIL import Image
from detect import detect

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGES'] = 'data/images'
app.config['UPLOAD_FOLDER_VIDEOS'] = 'data/videos'
app.config['RESULT_FOLDER'] = 'runs/detect'
app.secret_key = "supersecretkey"  # necessary for flashing messages

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER_IMAGES'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_VIDEOS'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

def get_detection_folder():
    """
    Returns the latest folder in runs/detect
    """
    detection_path = Path(app.config['RESULT_FOLDER'])
    return max([f for f in detection_path.iterdir() if f.is_dir()], key=os.path.getmtime)

@app.route('/')
def index():
    return render_template('index.html')  # Simple form for uploading files

@app.route('/upload', methods=['POST'])
def upload_file():
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='weights/yolov5s.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='data/images', help='source')
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.35, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    opt = parser.parse_args(args=[])

    # Check if the request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Determine if it's an image or video
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        save_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], file.filename)
        file.save(save_path)
        opt.source = save_path
        is_image = True
    elif file and file.filename.lower().endswith('.mp4'):
        save_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], file.filename)
        file.save(save_path)
        opt.source = save_path
        is_image = False
    else:
        flash('Unsupported file format')
        return redirect(request.url)
    
    # Run detection
    detect(opt)
    detection_folder = get_detection_folder()

    # Redirect to the result page with the folder path
    return redirect(url_for('show_results', detection_folder=detection_folder.name, is_image=is_image))

@app.route('/results/<detection_folder>')
def show_results(detection_folder):
    folder_path = os.path.join(app.config['RESULT_FOLDER'], detection_folder)
    is_image = request.args.get('is_image', default="True") == "True"
    
    # Show image or video results
    if is_image:
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return render_template('results.html', files=image_files, folder=detection_folder, is_image=True)
    else:
        video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
        return render_template('results.html', files=video_files, folder=detection_folder, is_image=False)

@app.route('/download/<detection_folder>/<filename>')
def download_file(detection_folder, filename):
    folder_path = os.path.join(app.config['RESULT_FOLDER'], detection_folder)
    return send_from_directory(folder_path, filename)

# Flask Templates
# `templates/index.html` for file upload form
# `templates/results.html` for displaying the output images or video

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
