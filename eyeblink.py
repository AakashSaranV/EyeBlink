import cv2
import dlib
import numpy as np
import time

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)

# Setup initial variables
idList = [22, 23, 24, 26, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]


ratioList = []
symbol = ""
bstate = "opened"
counter = 0
color = (255, 0, 255)
blink_start_time = None
oblink_start = None
i = 1
word = ""
sent = ""

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    if len(faces) > 0:
        face = faces[0]
        landmarks = predictor(gray, face)

        for id in idList:
            x = landmarks.part(id).x
            y = landmarks.part(id).y
            cv2.circle(img, (x, y), 5, color, cv2.FILLED)

        # Extracting eye landmarks for calculations
# Left eye
            leftUp = (landmarks.part(37).x, landmarks.part(37).y)
            leftDown = (landmarks.part(41).x, landmarks.part(41).y)
            leftLeft = (landmarks.part(36).x, landmarks.part(36).y)
            leftRight = (landmarks.part(39).x, landmarks.part(39).y)

            # Right eye
            rightUp = (landmarks.part(43).x, landmarks.part(43).y)
            rightDown = (landmarks.part(47).x, landmarks.part(47).y)
            rightLeft = (landmarks.part(42).x, landmarks.part(42).y)
            rightRight = (landmarks.part(45).x, landmarks.part(45).y)


        # Calculate distances
        def calculate_distance(p1, p2):
            return np.linalg.norm(np.array(p1) - np.array(p2))

        lLengthVer = calculate_distance(leftUp, leftDown)
        lLengthHor = calculate_distance(leftLeft, leftRight)
        rLengthVer = calculate_distance(rightUp, rightDown)
        rLengthHor = calculate_distance(rightLeft, rightRight)

        lRatio = int((lLengthVer / lLengthHor) * 100)
        rRatio = int((rLengthVer / rLengthHor) * 100)
        ratio = int((rRatio + lRatio) / 2)

        ratioList.append(ratio)
        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg <= 33 and counter == 0:
            bstate = "closed"
            if blink_start_time is None:
                blink_start_time = time.time()

            if oblink_start is not None:
                oblink_end = time.time()
                oblink_dur = oblink_end - oblink_start
                print(f"open Duration: {oblink_dur:.2f} seconds")

                if oblink_dur >= 2.0:
                    # Convert symbol to letter based on Morse code
                    morse_dict = {
                        ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F", "--.": "G",
                        "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L", "--": "M", "-.": "N",
                        "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T", "..-": "U",
                        "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y", "--..": "Z", ".----": "1", "..---": "2",
                        "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7", "---..": "8",
                        "----.": "9", "-----": "0"
                    }
                    letter = morse_dict.get(symbol, "ERROR")
                    word += letter
                    symbol = ""

                if oblink_dur >= 4.0:
                    sent += " " + word
                    word = ""

                oblink_start = None

            color = (0, 200, 0)
            counter = 1

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (255, 0, 255)

        elif ratioAvg > 33:
            bstate = "opened"
            if blink_start_time is not None:
                blink_end_time = time.time()
                blink_duration = blink_end_time - blink_start_time
                print(f"Blink Duration: {blink_duration:.2f} seconds")
                blink_start_time = None

                if blink_duration >= 1:
                    value = "-"
                else:
                    value = "." 
                symbol += value
                print(symbol)

                if oblink_start is None:
                    oblink_start = time.time()

        cv2.putText(img, f'Blink state :{bstate}', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(img, f'word :{word}', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(img, f'sentence :{sent}', (100, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        img = cv2.resize(img, (640, 360))
        cv2.imshow("Image", img)

    else:
        img = cv2.resize(img, (700, 360))
        cv2.imshow("Image", img)

    cv2.waitKey(25)