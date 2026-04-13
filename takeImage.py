import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time

def open_camera_prefer_macos() -> "cv2.VideoCapture | None":
    """Open camera robustly, preferring AVFoundation on macOS.

    Tries indices 0..2 across backends, warms up with a few reads,
    and sets a reasonable resolution if possible.
    """
    indices_to_try = [0, 1, 2]
    backend_candidates = []
    if hasattr(cv2, "CAP_AVFOUNDATION"):
        backend_candidates.append(cv2.CAP_AVFOUNDATION)
    backend_candidates.append(None)

    for backend in backend_candidates:
        for idx in indices_to_try:
            try:
                cam = cv2.VideoCapture(idx, backend) if backend is not None else cv2.VideoCapture(idx)
            except Exception:
                continue

            if not cam or not cam.isOpened():
                if cam:
                    cam.release()
                continue

            try:
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            except Exception:
                pass

            ok_reads = 0
            for _ in range(5):
                ret, frame = cam.read()
                if ret and frame is not None:
                    ok_reads += 1
                time.sleep(0.05)

            if ok_reads >= 2:
                return cam

            cam.release()

    return None

                    
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen,text_to_speech):
    if (l1 == "") and (l2==""):
        t='Please Enter the your Enrollment Number and Name.'
        text_to_speech(t)
    elif l1=='':
        t='Please Enter the your Enrollment Number.'
        text_to_speech(t)
    elif l2 == "":
        t='Please Enter the your Name.'
        text_to_speech(t)
    else:
        try:
            base_dir = os.path.dirname(__file__)
            
            # Camera initialization (robust, multi-backend)
            cam = open_camera_prefer_macos()
            
            if cam is None or not cam.isOpened():
                error_msg = (
                    "Error: Camera failed to open. "
                    "On macOS, allow Camera in System Settings > Privacy & Security > Camera."
                )
                print(error_msg)
                text_to_speech(error_msg)
                message.configure(text=error_msg)
                return

            detector = cv2.CascadeClassifier(haarcasecade_path)
            Enrollment = int(l1) # Ensure Enrollment is an integer for storage/comparison
            Name = l2
            sampleNum = 0
            directory = str(Enrollment) + "_" + Name
            path = os.path.join(trainimage_path, directory)
            os.makedirs(path, exist_ok=True)
            
            while True:
                ret, img = cam.read()
                
                if not ret or img is None:
                    continue 

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Ensure the face region is valid before saving
                    face_roi = gray[y : y + h, x : x + w]
                    if face_roi.size != 0:
                        sampleNum = sampleNum + 1
                        filename = f"{Name}_{Enrollment}_{sampleNum}.jpg"
                        
                        cv2.imwrite(
                            os.path.join(path, filename),
                            face_roi,
                        )
                        cv2.imshow("Frame", img)
                        
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                elif sampleNum > 50:
                    break
                    
            cam.release()
            cv2.destroyAllWindows()
            
            row = [Enrollment, Name]
            student_details_dir = os.path.join(base_dir, "StudentDetails")
            os.makedirs(student_details_dir, exist_ok=True)
            student_details_csv = os.path.join(student_details_dir, "studentdetails.csv")
            
            # Check if file exists and is empty to write header
            file_exists = os.path.exists(student_details_csv)
            is_empty = not file_exists or os.path.getsize(student_details_csv) == 0

            with open(
                student_details_csv,
                "a+",
                newline='' # Important for cross-platform CSV writing
            ) as csvFile:
                writer = csv.writer(csvFile, delimiter=",")
                if is_empty:
                    writer.writerow(["Enrollment", "Name"]) # Write Header
                
                writer.writerow(row)
                
            res = "Images Saved for ER No:" + str(Enrollment) + " Name:" + Name
            message.configure(text=res)
            text_to_speech(res)
            
        except FileExistsError:
            F = "Student Data already exists"
            text_to_speech(F)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            text_to_speech(error_msg)
            message.configure(text=error_msg)