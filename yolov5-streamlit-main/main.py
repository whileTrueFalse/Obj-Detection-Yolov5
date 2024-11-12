
The FileNotFoundError for weights/yolov5s.pt indicates that the YOLOv5 model weights file is missing from the weights directory. Here’s how to address this issue:

Solution 1: Download the Weights Manually
Download the weights file:
Go to the YOLOv5 GitHub releases page.
Download yolov5s.pt and place it in the weights directory within yolov5-streamlit-main.
Verify the Path:
Ensure the downloaded file is named exactly yolov5s.pt and resides in yolov5-streamlit-main/weights/.
Solution 2: Automate the Download in Code
Alternatively, you can add code to download the weights file programmatically if it’s missing. This way, the file will be downloaded automatically when you run the app.

Here’s how to modify the code to check for the file and download it if needed:

python
Copy code
from io import StringIO
from pathlib import Path
import streamlit as st
import time
from detect import detect
import os
import sys
import argparse
from PIL import Image
import urllib.request

def download_weights():
    weights_path = 'weights/yolov5s.pt'
    if not os.path.exists(weights_path):
        st.warning("Downloading YOLOv5 model weights...")
        os.makedirs('weights', exist_ok=True)
        url = 'https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt'
        urllib.request.urlretrieve(url, weights_path)
        st.success("YOLOv5 weights downloaded successfully.")

# Call the download function at the start
download_weights()

def get_subdirs(b='.'):
    '''
        Returns all sub-directories in a specific Path
    '''
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd):
            result.append(bd)
    return result

def get_detection_folder():
    '''
        Returns the latest folder in runs/detect
    '''
    return max(get_subdirs(os.path.join('runs', 'detect')), key=os.path.getmtime)

if __name__ == '__main__':

    st.title('YOLOv5 Streamlit App')

    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='weights/yolov5s.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str,
                        default='data/images', help='source')
    parser.add_argument('--img-size', type=int, default=640,
                        help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float,
                        default=0.35, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float,
                        default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true',
                        help='display results')
    parser.add_argument('--save-txt', action='store_true',
                        help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true',
                        help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true',
                        help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int,
                        help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true',
                        help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true',
                        help='augmented inference')
    parser.add_argument('--update', action='store_true',
                        help='update all models')
    parser.add_argument('--project', default='runs/detect',
                        help='save results to project/name')
    parser.add_argument('--name', default='exp',
                        help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true',
                        help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    print(opt)

    # Ensure directories exist
    os.makedirs("data/images", exist_ok=True)
    os.makedirs("data/videos", exist_ok=True)

    # Input options
    source = ("Image Detection", "Video Detection")
    source_index = st.sidebar.selectbox("Select Input", range(
        len(source)), format_func=lambda x: source[x])

    # Handle image upload
    if source_index == 0:
        uploaded_file = st.sidebar.file_uploader("Upload Image", type=['png', 'jpeg', 'jpg'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Loading resources...'):
                st.sidebar.image(uploaded_file)
                image_path = os.path.join("data", "images", uploaded_file.name)
                Image.open(uploaded_file).save(image_path)
                opt.source = image_path
        else:
            is_valid = False

    # Handle video upload
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Video", type=['mp4'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Loading resources...'):
                st.sidebar.video(uploaded_file)
                video_path = os.path.join("data", "videos", uploaded_file.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                opt.source = video_path
        else:
            is_valid = False

    if is_valid:
        print('File is valid, starting detection...')
        if st.button('Start Detection'):
            detect(opt)

            detection_folder = get_detection_folder()

            if source_index == 0:  # Display detected images
                with st.spinner(text='Preparing Images'):
                    for img in os.listdir(detection_folder):
                        img_path = os.path.join(detection_folder, img)
                        st.image(img_path, caption=f"Detected: {img}")
                    st.balloons()
            else:  # Display detected video
                with st.spinner(text='Preparing Video'):
                    video_files = [vid for vid in os.listdir(detection_folder) if vid.endswith('.mp4')]
                    if video_files:
                        video_path = os.path.join(detection_folder, video_files[0])
                        st.video(video_path)
                    else:
                        st.warning("No video output found.")
                    st.balloons()
