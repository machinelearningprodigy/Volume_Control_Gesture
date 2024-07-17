import cv2
import mediapipe as mp
import time
import threading

class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.hand_colors = [(0, 255, 0), (255, 0, 0)]  # Colors for different hands
        self.part_colors = [(255, 0, 255), (255, 255, 0), (0, 255, 255), (255, 165, 0), (255, 192, 203)]  # Colors for different parts

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for hand_no, handLms in enumerate(self.results.multi_hand_landmarks):
                hand_color = self.hand_colors[hand_no % len(self.hand_colors)]
                if draw:
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        part_color = self.part_colors[id % len(self.part_colors)]
                        cv2.circle(img, (cx, cy), 5, part_color, cv2.FILLED)
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,
                                               self.mpDraw.DrawingSpec(color=hand_color, thickness=2, circle_radius=2),
                                               self.mpDraw.DrawingSpec(color=hand_color, thickness=2, circle_radius=2))
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    part_color = self.part_colors[id % len(self.part_colors)]
                    cv2.circle(img, (cx, cy), 5, part_color, cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

def process_frames(cap, detector, frame_queue):
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break

        img = detector.findHands(img, draw=True)
        frame_queue.append(img)
        if len(frame_queue) > 2:
            frame_queue.pop(0)

def main():
    pTime = 0
    cap = cv2.VideoCapture(0)
    cap.set(3, 1080)
    cap.set(4, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    detector = handDetector()
    frame_queue = []
    fps_list = []

    capture_thread = threading.Thread(target=process_frames, args=(cap, detector, frame_queue))
    capture_thread.start()

    while True:
        if len(frame_queue) == 0:
            time.sleep(0.01)
            continue

        img = frame_queue[0]
        lmList = detector.findPosition(img, draw=True)
        if lmList:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Maintain a rolling average of the last 10 FPS values
        fps_list.append(fps)
        if len(fps_list) > 10:
            fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)

        cv2.putText(img, f'FPS: {int(avg_fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Introduce sleep to control FPS
        time.sleep(0.025)  # Approx 40 FPS

    capture_thread.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
