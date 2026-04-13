import csv
import cv2
import os
import time
from datetime import date
from datetime import datetime
import pandas as pd
from tkinter import *
import tkinter as tk

# --- Camera helpers ---
def open_camera_prefer_macos() -> "cv2.VideoCapture | None":
    """Try to open a camera robustly across platforms.

    Strategy (especially for macOS 14+/Apple Silicon):
    1) Try AVFoundation with indices 0..2
    2) Try default backend with indices 0..2
    If a camera opens, perform a short warm-up and set a sane resolution.
    """
    indices_to_try = [0, 1, 2]
    backend_candidates = []

    # Prefer AVFoundation on macOS when available
    if hasattr(cv2, "CAP_AVFOUNDATION"):
        backend_candidates.append(cv2.CAP_AVFOUNDATION)

    # Fallback: default backend (pass no apiPreference)
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

            # Try setting a reasonable resolution; ignore failures
            try:
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            except Exception:
                pass

            # Warm-up reads
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

# Define global paths 
current_dir = os.path.dirname(__file__)
haarcasecade_path = os.path.join(current_dir, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(current_dir, "TrainingImageLabel", "Trainner.yml")
student_details_path = os.path.join(current_dir, "StudentDetails", "studentdetails.csv")
unknown_images_dir = os.path.join(current_dir, "ImagesUnknown")
attendance_save_dir = os.path.join(current_dir, "Attendance")
trainimage_path = os.path.join(current_dir, "TrainingImage") 


# Define a simplified style for the subject choose UI
style = {
    'bg': '#0f0f23',
    'fg': '#ffffff',
    'font_button': ('Segoe UI', 16, 'bold'),
    'accent_color': '#2563eb',
    'button_hover': '#374151'
}

# --- Core Attendance Logic ---
def automaticAttendance(haarcasecade_path, trainimage_path, message, message2, text_to_speech, sub, SubUI):
    """Starts the camera for face recognition and marks attendance."""
    
    # 1. CHECK HAAR CASCADE FILE
    if not os.path.exists(haarcasecade_path):
        t = f"Fatal Error: Haar Cascade file not found at: {haarcasecade_path}"
        text_to_speech(t)
        print(t)
        if message:
             message.configure(text=t, fg='red')
        return
        
    faceCascade = cv2.CascadeClassifier(haarcasecade_path)

    # 2. CHECK FACE RECOGNITION MODEL
    if not os.path.exists(trainimagelabel_path) or os.path.getsize(trainimagelabel_path) == 0:
        t = "Error: Training model (Trainner.yml) not found or is empty. Please train the images first."
        text_to_speech(t)
        print(t)
        if message: 
             message.configure(text=t, fg='red')
        return

    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainimagelabel_path)
    except Exception as e:
        t = f"Error loading model: {e}. Ensure OpenCV is correctly installed."
        text_to_speech(t)
        print(t)
        if message: 
             message.configure(text=t, fg='red')
        return

    # 3. CHECK STUDENT DETAILS FILE AND LOAD WITH ROBUST HEADERS
    if not os.path.exists(student_details_path):
        t = "Error: Student details file not found. Please register students."
        text_to_speech(t)
        print(t)
        if message: 
             message.configure(text=t, fg='red')
        return

    try:
        # Load CSV robustly
        df = pd.read_csv(student_details_path, encoding='utf-8')
        df.columns = df.columns.str.strip()
        
        # Ensure 'Enrollment' and 'Name' columns exist (rename if necessary)
        if 'Id' in df.columns:
            df = df.rename(columns={'Id': 'Enrollment'})
        if 'Enrollment' not in df.columns or 'Name' not in df.columns:
            # Fallback for legacy files without headers: read again with no header
            legacy = pd.read_csv(student_details_path, header=None, names=['Enrollment','Name'], encoding='utf-8')
            df = legacy

        # Coerce Enrollment to numeric for reliable matching to recognizer Id
        df['Enrollment'] = pd.to_numeric(df['Enrollment'], errors='coerce').astype('Int64')
        df['Name'] = df['Name'].astype(str).str.strip()

    except Exception as e:
        t = f"Error reading student details CSV: {e}. Please manually verify the file: {student_details_path}"
        text_to_speech(t)
        print(t)
        if message: 
             message.configure(text=t, fg='red')
        return


    
    # 4. CAMERA INITIALIZATION (robust, multi-backend)
    cam = open_camera_prefer_macos()

    if cam is None or not cam.isOpened():
        error_msg = (
            "Fatal Error: Camera failed to open. "
            "On macOS, ensure app has Camera permission in System Settings > Privacy & Security > Camera."
        )
        print(error_msg)
        text_to_speech(error_msg)
        
        if message: 
             message.configure(text=error_msg, fg='red')
        return 

    # Keep the subject window open so messages can be shown there
    try:
        if message:
            message.configure(text="Camera started. Press 'q' to quit.")
        if message2:
            message2.configure(text="", fg='lightgreen')
    except Exception:
        pass
        
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ["Enrollment", "Name", "Date", "Time"]
    attendance = pd.DataFrame(columns=col_names)

    # Prepare session CSV for incremental writes
    ts = time.time()
    date_attendance = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    timeStamp = datetime.fromtimestamp(ts).strftime("%H%M%S")
    if not os.path.exists(attendance_save_dir):
        os.makedirs(attendance_save_dir)
    FileName = os.path.join(attendance_save_dir, f"Attendance_{sub}_{date_attendance}_{timeStamp}.csv")
    # Write header once at start
    if not os.path.exists(FileName) or os.path.getsize(FileName) == 0:
        with open(FileName, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(col_names)

    seen_enrollments = set()
    recognized_once = False
    
    while True:
        ret, im = cam.read()
        
        if not ret or im is None:
            continue
            
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
            
            # Recognition Threshold: Adjusted to 65
            if conf < 65: 
                ts = time.time()
                date_attendance = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                
                # Ensure Id type matches coerced Enrollment
                try:
                    Id_numeric = int(Id)
                except Exception:
                    Id_numeric = None
                student_row = df.loc[df["Enrollment"] == Id_numeric]
                aa = student_row["Name"].values
                
                if len(aa) > 0:
                    tt = str(Id_numeric) + "-" + str(aa[0])
                    # Append only once per session per Enrollment
                    if Id_numeric not in seen_enrollments:
                        seen_enrollments.add(Id_numeric)
                        now_ts = datetime.now()
                        row_date = now_ts.strftime("%Y-%m-%d")
                        row_time = now_ts.strftime("%H:%M:%S")
                        # Update in-memory df (optional)
                        attendance.loc[len(attendance)] = [Id_numeric, aa[0], row_date, row_time]
                        # Incremental write to CSV so it updates live
                        try:
                            with open(FileName, 'a', newline='') as f:
                                writer = csv.writer(f)
                                writer.writerow([Id_numeric, aa[0], row_date, row_time])
                        except Exception as write_err:
                            print(f"Warning: failed to append attendance row: {write_err}")
                        # Provide immediate UI feedback
                        if message2:
                            try:
                                message2.configure(text=f"Attendance marked for {aa[0]} ({Id_numeric}).", fg='lightgreen')
                            except Exception:
                                pass
                        try:
                            text_to_speech("Attendance marked")
                        except Exception:
                            pass
                        recognized_once = True
                else:
                    tt = "Unknown"
            else:
                Id = "Unknown"
                tt = str(Id)
            
            # Save as Unknown if confidence is very low (poor match)
            if conf > 90: 
                if not os.path.exists(unknown_images_dir):
                     os.makedirs(unknown_images_dir)
                noOfFile = len(os.listdir(unknown_images_dir)) + 1
                
                if y + h <= im.shape[0] and x + w <= im.shape[1]:
                    cv2.imwrite(os.path.join(unknown_images_dir, f"Image{noOfFile}.jpg"), im[y : y + h, x : x + w])
            
            cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)
            
        attendance = attendance.drop_duplicates(subset=["Enrollment"], keep="first")
        # If we already recognized once, overlay success banner
        if recognized_once:
            try:
                cv2.putText(im, "Attendance marked", (20, 40), font, 1.0, (0, 255, 0), 2)
            except Exception:
                pass
        cv2.imshow("Attendance", im)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        # Auto-close shortly after a successful mark
        if recognized_once:
            # small delay so user sees the confirmation and bounding box
            cv2.waitKey(1500)
            break
            
    # Clean up
    cam.release()
    cv2.destroyAllWindows()

    t = "Attendance recorded successfully"
    text_to_speech(t)


# --- Subject Choose UI Wrapper ---
def subjectChoose(text_to_speech):
    """Creates the UI for selecting a subject before starting attendance."""
    
    SubUI = tk.Tk()
    SubUI.title("📚 Select Subject")
    SubUI.geometry("500x300")
    SubUI.configure(background=style['bg'])
    SubUI.resizable(False, False)
    SubUI.attributes('-topmost', True)
    
    # Center the window
    SubUI.update_idletasks()
    x = (SubUI.winfo_screenwidth() // 2) - (500 // 2)
    y = (SubUI.winfo_screenheight() // 2) - (300 // 2)
    SubUI.geometry(f"500x300+{x}+{y}")
    
    tk.Label(
        SubUI,
        text="Enter Subject Name:",
        bg=style['bg'],
        fg=style['fg'],
        font=('Segoe UI', 18, 'bold')
    ).pack(pady=20)
    
    txt = tk.Entry(
        SubUI,
        width=30,
        bd=0,
        bg=style['fg'],
        fg=style['bg'],
        font=('Segoe UI', 14),
        relief='flat',
        insertbackground=style['bg']
    )
    txt.pack(ipady=8, padx=20)
    
    message = tk.Label(SubUI, text="Status: Ready", bg=style['bg'], fg=style['fg'], font=('Segoe UI', 10))
    message.pack(pady=5)
    
    message2 = tk.Label(SubUI, text="", bg=style['bg'], fg='lightgreen', font=('Segoe UI', 10))
    message2.pack(pady=5)
    
    def on_start_attendance():
        sub = txt.get()
        if sub:
            # Pass the SubUI object so it can be destroyed ONLY on successful camera open
            automaticAttendance(haarcasecade_path, trainimage_path, message, message2, text_to_speech, sub, SubUI)
        else:
            text_to_speech("Please enter a subject name.")

    start_btn = tk.Button(
        SubUI,
        text="Start Attendance",
        command=on_start_attendance,
        font=style['font_button'],
        bg=style['accent_color'],
        fg=style['fg'],
        relief='flat',
        bd=0,
        cursor='hand2',
        width=20,
        height=2
    )
    start_btn.pack(pady=20)
    
    SubUI.mainloop()