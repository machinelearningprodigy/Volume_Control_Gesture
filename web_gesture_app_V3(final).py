# import cv2
# import numpy as np
# import streamlit as st
# import threading
# import time
# from hand_tracking import handDetector, process_frames
# import pulsectl
# import pygame
# from io import BytesIO

# # Initialize the volume control
# pulse = pulsectl.Pulse('volume-control')
# sinks = pulse.sink_list()
# sink = sinks[0]  # Use the first sink for volume control

# def set_volume(volume):
#     pulse.volume_set_all_chans(sink, volume)

# def get_volume_range():
#     return (0.0, 1.0)

# minVol, maxVol = get_volume_range()

# # Initialize Pygame mixer
# pygame.mixer.init()

# # Music control variables
# music_files = []
# music_titles = []
# current_track_index = 0

# def play_music():
#     if music_files:
#         pygame.mixer.music.load(music_files[current_track_index])
#         pygame.mixer.music.play()

# def pause_music():
#     if pygame.mixer.music.get_busy():
#         pygame.mixer.music.pause()

# def unpause_music():
#     if pygame.mixer.music.get_busy():
#         pygame.mixer.music.unpause()

# def next_track():
#     global current_track_index
#     if music_files:
#         current_track_index = (current_track_index + 1) % len(music_files)
#         play_music()

# def previous_track():
#     global current_track_index
#     if music_files:
#         current_track_index = (current_track_index - 1) % len(music_files)
#         play_music()

# def main():
#     st.title("Hand Gesture Music Control")

#     # Upload button
#     uploaded_files = st.file_uploader("Upload Music", type=["mp3", "wav"], accept_multiple_files=True)
#     if uploaded_files:
#         for uploaded_file in uploaded_files:
#             file_bytes = uploaded_file.read()
#             music_files.append(BytesIO(file_bytes))
#             music_titles.append(uploaded_file.name)
#         play_music()  # Start playing the first uploaded song

#     # Control buttons
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         if st.button("Previous"):
#             previous_track()
#     with col2:
#         if st.button("Play"):
#             play_music()
#     with col3:
#         if st.button("Pause"):
#             pause_music()
#     with col4:
#         if st.button("Unpause"):
#             unpause_music()
#     with col5:
#         if st.button("Next"):
#             next_track()

#     # Display uploaded music files in an album-like structure
#     st.subheader("Music Album")
#     if music_files:
#         for index, music_title in enumerate(music_titles):
#             with st.container():
#                 st.write(f"Track {index + 1}: {music_title}")

#     cap = cv2.VideoCapture(0)
#     cap.set(3, 1080)
#     cap.set(4, 720)
#     cap.set(cv2.CAP_PROP_FPS, 30)

#     detector = handDetector()
#     frame_queue = []
#     fps_list = []

#     capture_thread = threading.Thread(target=process_frames, args=(cap, detector, frame_queue))
#     capture_thread.start()

#     volBar = 400
#     volPer = 0

#     pTime = time.time()

#     while True:
#         if len(frame_queue) == 0:
#             time.sleep(0.01)
#             continue

#         img = frame_queue[0]
#         lmList = detector.findPosition(img, draw=False)

#         if len(lmList) != 0:
#             x1, y1 = lmList[4][1], lmList[4][2]
#             x2, y2 = lmList[8][1], lmList[8][2]
#             cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

#             length = np.hypot(x2 - x1, y2 - y1)

#             # Reduce hand range for more sensitivity
#             vol = np.interp(length, [20, 200], [minVol, maxVol])
#             volBar = np.interp(length, [20, 200], [400, 150])
#             volPer = np.interp(length, [20, 200], [0, 100])

#             set_volume(vol)

#             if length < 20:
#                 cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime

#         # Maintain a rolling average of the last 10 FPS values
#         fps_list.append(fps)
#         if len(fps_list) > 10:
#             fps_list.pop(0)
#         avg_fps = sum(fps_list) / len(fps_list)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         # Introduce sleep to control FPS
#         time.sleep(0.025)  # Approx 40 FPS

#     capture_thread.join()
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

import cv2
import numpy as np
import streamlit as st
import threading
import time
from hand_tracking import handDetector, process_frames
import pulsectl
import pygame
from io import BytesIO

# Initialize the volume control
pulse = pulsectl.Pulse('volume-control')
sinks = pulse.sink_list()
sink = sinks[0]  # Use the first sink for volume control

def set_volume(volume):
    pulse.volume_set_all_chans(sink, volume)

def get_volume_range():
    return (0.0, 1.0)

minVol, maxVol = get_volume_range()

# Initialize Pygame mixer
pygame.mixer.init()

# Music control variables
music_files = []
music_titles = []
current_track_index = 0

def play_music():
    if music_files:
        pygame.mixer.music.load(music_files[current_track_index])
        pygame.mixer.music.play()

def pause_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

def unpause_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.unpause()

def next_track():
    global current_track_index
    if music_files:
        current_track_index = (current_track_index + 1) % len(music_files)
        play_music()

def previous_track():
    global current_track_index
    if music_files:
        current_track_index = (current_track_index - 1) % len(music_files)
        play_music()

def main():
    st.title("Hand Gesture Music Control")

    # Upload button
    uploaded_files = st.file_uploader("Upload Music", type=["mp3", "wav"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            music_files.append(BytesIO(file_bytes))
            music_titles.append(uploaded_file.name)
        play_music()  # Start playing the first uploaded song

    # Control buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Previous"):
            previous_track()
    with col2:
        if st.button("Play"):
            play_music()
    with col3:
        if st.button("Pause"):
            pause_music()
    with col4:
        if st.button("Unpause"):
            unpause_music()
    with col5:
        if st.button("Next"):
            next_track()

    # Display uploaded music files in an album-like structure
    st.subheader("Music Album")
    if music_files:
        for index, music_title in enumerate(music_titles):
            with st.container():
                st.write(f"Track {index + 1}: {music_title}")

    cap = cv2.VideoCapture(0)
    cap.set(3, 1080)
    cap.set(4, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    detector = handDetector()
    frame_queue = []
    fps_list = []

    capture_thread = threading.Thread(target=process_frames, args=(cap, detector, frame_queue))
    capture_thread.start()

    volBar = 400
    volPer = 0

    pTime = time.time()
    gesture_start_time = None
    gesture_held = False

    while True:
        if len(frame_queue) == 0:
            time.sleep(0.01)
            continue

        img = frame_queue[0]
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            length = np.hypot(x2 - x1, y2 - y1)

            # Reduce hand range for more sensitivity
            vol = np.interp(length, [20, 200], [minVol, maxVol])
            volBar = np.interp(length, [20, 200], [400, 150])
            volPer = np.interp(length, [20, 200], [0, 100])

            if length < 20:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

            if gesture_start_time is None:
                gesture_start_time = time.time()
            elif time.time() - gesture_start_time >= 3:
                gesture_held = True
                set_volume(vol)

        else:
            gesture_start_time = None

        if gesture_held:
            set_volume(vol)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Maintain a rolling average of the last 10 FPS values
        fps_list.append(fps)
        if len(fps_list) > 10:
            fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Introduce sleep to control FPS
        time.sleep(0.025)  # Approx 40 FPS

    capture_thread.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
