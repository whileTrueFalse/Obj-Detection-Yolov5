from io import StringIO
from pathlib import Path
import streamlit as st
import time
from detect import detect
import os
import sys
import argparse
from PIL import Image

# Disable file watching to avoid inotify limits
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

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

    st.title('Vehicle-Detection using Yolo')

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='yolov5-streamlit-main/weights/yolov5s.pt', help='model.pt path(s)')
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

    # Ensure the necessary directories exist
    os.makedirs("data/images", exist_ok=True)
    os.makedirs("data/videos", exist_ok=True)

    source = ("Image detection", "Video detection")
    source_index = st.sidebar.selectbox("Select input", range(
        len(source)), format_func=lambda x: source[x])

    if source_index == 0:
        uploaded_file = st.sidebar.file_uploader(
            "Upload pictures", type=['png', 'jpeg', 'jpg'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Resources loading...'):
                st.sidebar.image(uploaded_file)
                picture = Image.open(uploaded_file)
                picture.save(f'data/images/{uploaded_file.name}')
                opt.source = f'data/images/{uploaded_file.name}'
        else:
            is_valid = False
    else:
        uploaded_file = st.sidebar.file_uploader("Upload video", type=['mp4'])
        if uploaded_file is not None:
            is_valid = True
            with st.spinner(text='Resources loading...'):
                st.sidebar.video(uploaded_file)
                with open(os.path.join("data", "videos", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                opt.source = f'data/videos/{uploaded_file.name}'
        else:
            is_valid = False

    if is_valid:
        print('valid')
        if st.button('Start testing'):
            detect(opt)

            # Get the output folder only once after detection is complete
            detection_folder = get_detection_folder()

            if source_index == 0:  # Image display
                with st.spinner(text='Preparing Images'):
                    for img in os.listdir(detection_folder):
                        img_path = str(Path(detection_folder) / img)
                        st.image(img_path, caption=f"Processed: {img}")
                    st.balloons()
            else:  # Video display
                with st.spinner(text='Preparing Video'):
                    video_files = [vid for vid in os.listdir(detection_folder) if vid.endswith('.mp4')]
                    if video_files:
                        video_path = str(Path(detection_folder) / video_files[0])
                        st.video(video_path)
                    else:
                        st.warning("No video output found.")
                    st.balloons()
