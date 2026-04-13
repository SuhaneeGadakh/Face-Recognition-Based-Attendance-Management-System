import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import pyttsx3
# Remove unnecessary imports here (though they weren't in your last version, keeping it clean)
                
# Ensure these modules are in the same directory and named exactly as follows:
import show_attendance
import takeImage
import trainImage
import automaticAttedance

                         
                        
                                                    
                     


def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()


# --- PATHS AND SETUP ---
base_dir = os.path.dirname(__file__)
haarcasecade_path = os.path.join(base_dir, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(base_dir, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(base_dir, "TrainingImage")

studentdetail_path = os.path.join(base_dir, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(base_dir, "Attendance")
                                   
for required_dir in [os.path.dirname(haarcasecade_path), os.path.dirname(trainimagelabel_path), trainimage_path, os.path.dirname(studentdetail_path), attendance_path]:
    if required_dir and not os.path.exists(required_dir):
        os.makedirs(required_dir, exist_ok=True)
# --- END PATHS AND SETUP ---

window = Tk()
window.title("CLASS VISION - Face Recognition Attendance System")
window.geometry("1400x800")
window.resizable(True, True)
dialog_title = "QUIT"
dialog_text = "Are you sure want to close?"
window.configure(background="#0f0f23")                          

                                    
def on_closing():
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

                          
style = {
    'bg': '#0f0f23',
    'fg': '#ffffff',
    'font_title': ('Segoe UI', 30, 'bold'),
    'font_subtitle': ('Segoe UI', 20, 'normal'),
    'font_button': ('Segoe UI', 16, 'bold'),
    'font_text': ('Segoe UI', 13, 'normal'),
    'button_bg': '#1f2937',
    'button_fg': '#ffffff',
    'button_hover': '#374151',
    'accent_color': '#2563eb',
    'success_color': '#16a34a',
    'warning_color': '#d97706',
    'error_color': '#dc2626',
    'button_bg_light': '#f9fafb',
    'button_hover_light': '#e5e7eb',
    'button_text': '#111827'
}


                   
def del_sc1():
    sc1.destroy()


                               
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry("450x150")
    sc1.title("⚠️ Input Required")
    sc1.configure(background=style['bg'])
    sc1.resizable(False, False)
    sc1.attributes('-topmost', True)
    
                       
    sc1.update_idletasks()
    x = (sc1.winfo_screenwidth() // 2) - (450 // 2)
    y = (sc1.winfo_screenheight() // 2) - (150 // 2)
    sc1.geometry(f"450x150+{x}+{y}")
    
                            
    error_frame = tk.Frame(sc1, bg=style['bg'])
    error_frame.pack(expand=True, fill='both', padx=20, pady=20)
    
    tk.Label(
        error_frame,
        text="⚠️",
        fg=style['warning_color'],
        bg=style['bg'],
        font=('Segoe UI', 24, 'bold'),
    ).pack()
    
    tk.Label(
        error_frame,
        text="Enrollment & Name Required!",
        fg=style['fg'],
        bg=style['bg'],
        font=style['font_subtitle'],
    ).pack(pady=(10, 20))
    
                   
    ok_btn = tk.Button(
        error_frame,
        text="OK",
        command=del_sc1,
        fg=style['button_fg'],
        bg=style['accent_color'],
        width=12,
        height=1,
        font=style['font_button'],
        relief='flat',
        bd=0,
        cursor='hand2'
    )
    ok_btn.pack()
    
                      
    def on_enter(e):
        ok_btn.config(bg=style['button_hover'])
    def on_leave(e):
        ok_btn.config(bg=style['accent_color'])
    
    ok_btn.bind("<Enter>", on_enter)
    ok_btn.bind("<Leave>", on_leave)

def testVal(inStr, acttyp):
    if acttyp == "1":          
        if not inStr.isdigit():
            return False
    return True


                     
header_frame = tk.Frame(window, bg=style['bg'], height=120)
header_frame.pack(fill='x', padx=20, pady=(20, 0))
header_frame.pack_propagate(False)

                
try:
    logo = Image.open("UI_Image/0001.png")
    logo = logo.resize((60, 60), Image.LANCZOS)
    logo1 = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(header_frame, image=logo1, bg=style['bg'])
    logo_label.pack(side='left', padx=(0, 20))
except:
    logo_label = tk.Label(header_frame, text="🎓", font=('Segoe UI', 40), bg=style['bg'], fg=style['accent_color'])
    logo_label.pack(side='left', padx=(0, 20))

               
title_frame = tk.Frame(header_frame, bg=style['bg'])
title_frame.pack(side='left', expand=True, fill='both')

main_title = tk.Label(
    title_frame,
    text="CLASS VISION",
    bg=style['bg'],
    fg=style['accent_color'],
    font=style['font_title']
)
main_title.pack(anchor='w')

subtitle = tk.Label(
    title_frame,
    text="Face Recognition Attendance System",
    bg=style['bg'],
    fg=style['fg'],
    font=style['font_subtitle']
)
subtitle.pack(anchor='w', pady=(5, 0))

                 
welcome_frame = tk.Frame(window, bg=style['bg'])
welcome_frame.pack(fill='x', padx=20, pady=(20, 40))

welcome_label = tk.Label(
    welcome_frame,
    text="Welcome to CLASS VISION",
    bg=style['bg'],
    fg=style['fg'],
    font=('Segoe UI', 24, 'bold')
)
welcome_label.pack()

desc_label = tk.Label(
    welcome_frame,
    text="Advanced face recognition technology for automated attendance management",
    bg=style['bg'],
    fg=style['fg'],
    font=style['font_text']
)
desc_label.pack(pady=(10, 0))


                          
content_frame = tk.Frame(window, bg=style['bg'])
content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

                               
def create_feature_card(parent, title, description, icon, command, x, y):
    card_frame = tk.Frame(
        parent,
        bg=style['button_bg'],
        relief='flat',
        bd=0,
        width=300,
        height=200
    )
    card_frame.place(x=x, y=y)
    card_frame.pack_propagate(False)
    
    def card_click(e=None):
        command()
    
                      
    def on_enter(e):
        card_frame.config(bg=style['button_hover'])
    def on_leave(e):
        card_frame.config(bg=style['button_bg'])
    
    card_frame.bind("<Enter>", on_enter)
    card_frame.bind("<Leave>", on_leave)
    
          
    icon_label = tk.Label(
        card_frame,
        text=icon,
        font=('Segoe UI', 40),
        bg=card_frame['bg'],
        fg=style['accent_color']
    )
    icon_label.pack(pady=(20, 10))
    
           
    title_label = tk.Label(
        card_frame,
        text=title,
        font=style['font_button'],
        bg=card_frame['bg'],
        fg=style['fg']
    )
    title_label.pack()
    
                 
    desc_label = tk.Label(
        card_frame,
        text=description,
        font=style['font_text'],
        bg=card_frame['bg'],
        fg=style['fg'],
        wraplength=250
    )
    desc_label.pack(pady=(5, 15))
    
            
    btn = tk.Button(
        card_frame,
        text="Open",
        command=card_click,
        font=style['font_button'],
        bg=style['button_bg_light'],
        fg=style['button_text'],
        activebackground=style['button_hover_light'],
        activeforeground=style['button_text'],
        relief='solid',
        bd=1,
        cursor='hand2',
        width=16,
        height=3
    )
    btn.pack()
    
                                    
    card_frame.bind("<Button-1>", card_click)
    icon_label.bind("<Button-1>", card_click)
    title_label.bind("<Button-1>", card_click)
    desc_label.bind("<Button-1>", card_click)
    btn.bind("<Button-1>", card_click)
    
    return card_frame

                        
def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("👤 Register New Student")
    ImageUI.geometry("900x600")
    ImageUI.configure(background=style['bg'])
    ImageUI.resizable(True, True)
    
                       
    ImageUI.update_idletasks()
    x = (ImageUI.winfo_screenwidth() // 2) - (900 // 2)
    y = (ImageUI.winfo_screenheight() // 2) - (600 // 2)
    ImageUI.geometry(f"900x600+{x}+{y}")
    
            
    header_frame = tk.Frame(ImageUI, bg=style['bg'], height=80)
    header_frame.pack(fill='x', padx=20, pady=(20, 0))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(
        header_frame,
        text="👤 Register New Student",
        bg=style['bg'],
        fg=style['accent_color'],
        font=('Segoe UI', 24, 'bold')
    )
    title_label.pack(side='left')
    
    subtitle_label = tk.Label(
        header_frame,
        text="Capture face images for student registration",
        bg=style['bg'],
        fg=style['fg'],
        font=style['font_text']
    )
    subtitle_label.pack(side='left', padx=(20, 0))

                       
    content_frame = tk.Frame(ImageUI, bg=style['bg'])
    content_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
                  
    form_frame = tk.Frame(content_frame, bg=style['button_bg'], relief='flat', bd=0)
    form_frame.pack(fill='x', pady=(0, 20))
    
    form_title = tk.Label(
        form_frame,
        text="📝 Student Information",
        bg=style['button_bg'],
        fg=style['accent_color'],
        font=('Segoe UI', 18, 'bold')
    )
    form_title.pack(pady=(20, 10))

                           
    fields_frame = tk.Frame(form_frame, bg=style['button_bg'])
    fields_frame.pack(fill='x', padx=20, pady=(0, 20))
    
                      
    enrollment_frame = tk.Frame(fields_frame, bg=style['button_bg'])
    enrollment_frame.pack(fill='x', pady=10)
    
    lbl1 = tk.Label(
        enrollment_frame,
        text="🎓 Enrollment Number",
        bg=style['button_bg'],
        fg=style['fg'],
        font=style['font_button']
    )
    lbl1.pack(anchor='w')
    
    txt1 = tk.Entry(
        enrollment_frame,
        width=30,
        bd=0,
        validate="key",
        bg=style['bg'],
        fg=style['fg'],
        relief='flat',
        font=style['font_text'],
        insertbackground=style['fg']
    )
    txt1.pack(fill='x', pady=(5, 0), ipady=8)
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")
    
                       
    border_frame1 = tk.Frame(enrollment_frame, bg=style['accent_color'], height=2)
    border_frame1.pack(fill='x', pady=(0, 10))
    
                
    name_frame = tk.Frame(fields_frame, bg=style['button_bg'])
    name_frame.pack(fill='x', pady=10)
    
    lbl2 = tk.Label(
        name_frame,
        text="👤 Student Name",
        bg=style['button_bg'],
        fg=style['fg'],
        font=style['font_button']
    )
    lbl2.pack(anchor='w')
    
    txt2 = tk.Entry(
        name_frame,
        width=30,
        bd=0,
        bg=style['bg'],
        fg=style['fg'],
        relief='flat',
        font=style['font_text'],
        insertbackground=style['fg']
    )
    txt2.pack(fill='x', pady=(5, 0), ipady=8)
    
                       
    border_frame2 = tk.Frame(name_frame, bg=style['accent_color'], height=2)
    border_frame2.pack(fill='x', pady=(0, 10))

                       
    notification_frame = tk.Frame(content_frame, bg=style['button_bg'], relief='flat', bd=0)
    notification_frame.pack(fill='x', pady=(0, 20))
    
    notification_title = tk.Label(
        notification_frame,
        text="📢 Status",
        bg=style['button_bg'],
        fg=style['accent_color'],
        font=('Segoe UI', 16, 'bold')
    )
    notification_title.pack(pady=(20, 10))
    
    message = tk.Label(
        notification_frame,
        text="Ready to capture images...",
        bg=style['button_bg'],
        fg=style['fg'],
        font=style['font_text'],
        wraplength=400,
        justify='left'
    )
    message.pack(pady=(0, 20), padx=20)

    def take_image():
        l1 = txt1.get()
        l2 = txt2.get()
        try:
            takeImage.TakeImage(
                l1,
                l2,
                haarcasecade_path,
                trainimage_path,
                message,
                err_screen,
                text_to_speech,
            )
            txt1.delete(0, "end")
            txt2.delete(0, "end")
        except Exception as e:
            error_msg = f"Error during image capture: {e}"
            message.configure(text=error_msg)
            text_to_speech("Error during image capture")

    def train_image():
        try:
            trainImage.TrainImage(
                haarcasecade_path,
                trainimage_path,
                trainimagelabel_path,
                message,
                text_to_speech,
            )
        except Exception as e:
            error_msg = f"Error during model training: {e}"
            message.configure(text=error_msg)
            text_to_speech("Error during model training")

                    
    buttons_frame = tk.Frame(content_frame, bg=style['bg'])
    buttons_frame.pack(fill='x', pady=20)
    
                       
    takeImg = tk.Button(
        buttons_frame,
        text="📸 Capture Images",
        command=take_image,
        font=style['font_button'],
        bg=style['accent_color'], 
        fg=style['button_fg'],
        activebackground=style['button_hover'],
        activeforeground=style['button_fg'],
        relief='flat', 
        bd=0,
        cursor='hand2',
        width=22,
        height=4
    )
    takeImg.pack(side='left', padx=(0, 10))

    
                        
    trainImg = tk.Button(
        buttons_frame,
        text="🧠 Train Model",
        command=train_image,
        font=style['font_button'],
        bg=style['success_color'], 
        fg=style['button_fg'],
        activebackground=style['button_hover'],
        activeforeground=style['button_fg'],
        relief='flat', 
        bd=0,
        cursor='hand2',
        width=22,
        height=4
    )
    trainImg.pack(side='left', padx=(0, 10))
    
                  
    closeBtn = tk.Button(
        buttons_frame,
        text="❌ Close",
        command=ImageUI.destroy,
        font=style['font_button'],
        bg=style['error_color'], 
        fg=style['button_fg'],
        activebackground=style['button_hover'],
        activeforeground=style['button_fg'],
        relief='flat', 
        bd=0,
        cursor='hand2',
        width=18,
        height=4
    )
    closeBtn.pack(side='right')
    
                       
    def create_hover_effect(btn, original_color):
        def on_leave_gen(e): btn.config(bg=original_color)

        if btn == takeImg:
            def on_enter_acc(e): btn.config(bg='#3b82f6')
            btn.bind("<Enter>", on_enter_acc)
            btn.bind("<Leave>", on_leave_gen)
        elif btn == trainImg:
            def on_enter_succ(e): btn.config(bg='#22c55e')
            btn.bind("<Enter>", on_enter_succ)
            btn.bind("<Leave>", on_leave_gen)
        elif btn == closeBtn:
            def on_enter_err(e): btn.config(bg='#ef4444')
            btn.bind("<Enter>", on_enter_err)
            btn.bind("<Leave>", on_leave_gen)
    
    create_hover_effect(takeImg, style['accent_color'])
    create_hover_effect(trainImg, style['success_color'])
    create_hover_effect(closeBtn, style['error_color'])

def automatic_attedance():
    automaticAttedance.subjectChoose(text_to_speech)

def view_attendance():
    try:
        show_attendance.show_attendance_window()
    except Exception as e:
        print(f"Error opening attendance viewer: {e}")

                      
register_card = create_feature_card(
    content_frame,
    "Register Student",
    "Add new students to the system by capturing their face images",
    "👤",
    TakeImageUI,
    50, 50
)

attendance_card = create_feature_card(
    content_frame,
    "Take Attendance",
    "Mark attendance using face recognition technology",
    "📸",
    automatic_attedance,
    400, 50
)

view_card = create_feature_card(
    content_frame,
    "View Attendance",
    "Check and analyze attendance records",
    "📊",
    view_attendance,
    750, 50
)


                           
action_frame = tk.Frame(window, bg=style['bg'])
action_frame.pack(fill='x', padx=20, pady=(40, 20))

                    
exit_btn = tk.Button(
    action_frame,
    text="🚪 Exit Application",
    command=window.destroy,
    font=style['font_button'],
    bg=style['error_color'], 
    fg=style['button_fg'], 
    activebackground=style['button_hover'], 
    activeforeground=style['button_fg'],
    relief='flat', 
    bd=0,
    cursor='hand2',
    width=20,
    height=4
)
exit_btn.pack(side='right')

                                  
def exit_on_enter(e):
    exit_btn.config(bg='#ef4444')
def exit_on_leave(e):
    exit_btn.config(bg=style['error_color'])

exit_btn.bind("<Enter>", exit_on_enter)
exit_btn.bind("<Leave>", exit_on_leave)


window.mainloop()