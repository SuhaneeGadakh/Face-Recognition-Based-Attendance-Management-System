# Face Recognition Attendance System

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5-green.svg)](https://opencv.org/)

A comprehensive Python-based desktop application that streamlines the attendance tracking process using computer vision. This system leverages OpenCV to capture, train, and subsequently recognize faces to mark student attendance automatically.

## Key Features

- **Profile Registration**: Automatically captures multiple samples of a student's face linked to their Unique ID and Name.
- **Model Training**: Processes localized image data to dynamically build a reliable face recognition model using Haarcascade classifiers.
- **Automated Logging**: Identifies registered students via live camera feed and logs their attendance directly to subject-specific CSV files.
- **Data Visualization**: Provides an intuitive tabular interface to view student attendance data instantly without leaving the application.

## System Architecture

The following flowchart outlines the primary operations within the application ecosystem:

```mermaid
graph TD
    A[Launch Application] --> B{Choose Action}
    B -->|Register| C[Enter ID and Name]
    C --> D[Capture 50 Face Samples]
    D --> E[Save to 'TrainingImage' Directory]
    B -->|Train| F[Process Captures]
    F --> G[Generate Trained Pattern]
    B -->|Attendance| H[Provide Subject Name]
    H --> I[Initialize Camera Feed]
    I --> J{Face Recognized?}
    J -->|True| K[Log Time & Details]
    K --> L[Save to Subject-Specific CSV]
    J -->|False| I
    B -->|View| M[Select CSV Log]
    M --> N[Display in Tabular View]
```

## Internal Workflow

This sequence diagram illustrates the interaction between the user interface, the camera module, the Machine Learning component, and data storage.

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant Camera
    participant Model
    participant CSV_Logs

    User->>Application: Enter ID & Name
    Application->>Camera: Start Capture Mode
    Camera-->>Application: Return 50 face frames
    Application-->>User: Images Saved Successfully
    
    User->>Application: Invoke 'Train Image'
    Application->>Model: Encode images to numeric format
    Model-->>Application: Training Complete
    
    User->>Application: Enter Subject & Select 'Automatic Attendance'
    Application->>Camera: Open real-time feed
    Camera->>Model: Stream frames for detection
    Model-->>Application: Match results (Confidence Score)
    Application->>CSV_Logs: Write (ID, Name, Date, Time)
    
    User->>Application: Click 'View Attendance'
    CSV_Logs-->>Application: Read parsed records
    Application-->>User: Display Attendance Grid
```

## Installation and Setup

Follow these instructions to get the project running efficiently on your local machine.

1. **Clone the Repository**
   Download or clone the project repository to your local system environment.

2. **Install Dependencies**
   Navigate to the project root directory and execute the following command to install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Directory Configuration**
   Ensure an empty folder named `TrainingImage` exists in the root directory. If not, create it manually to avoid file path errors during image capture.

4. **Environment Variables**
   Open `attendance.py` and `automaticAttendance.py`. Verify and update any system-specific absolute paths if necessary.

5. **Start the Application**
   Run the main script to launch the graphic interface:
   ```bash
   python attendance.py
   ```

## Usage Guidelines

1. **Add a New Student**: Open the application, register a valid ID and Name under the specific entry window, and click `Take Image`. Stay positioned within the camera bounds.
2. **Train the System**: Click `Train Image` after capturing. Do not use the recognition modules until you receive confirmation that the model has successfully trained.
3. **Capture Daily Attendance**: Click `Automatic Attendance`, supply the current subject name, and let the camera scan the room. Recognition logs will dynamically construct a `.csv` database inside the project structure.
4. **View Records**: Use the viewing dashboard to read the respective subject's `.csv` file.

## Screenshots

**Main Interface Module**<br/>
<img src="https://github.com/Patelrahul4884/Attendance-Management-system-using-face-recognition/blob/master/Project%20Snap/1.PNG" alt="Simple UI" width="600"/>

**Image Acquisition Phase**<br/>
<img src="https://user-images.githubusercontent.com/26384517/86820502-c7f44500-c0a6-11ea-9530-6317ec2059d9.png" alt="While taking Image" width="600"/>

**Real-time Recognition and Attendance Logging**<br/>
<img src="https://user-images.githubusercontent.com/26384517/86821090-9465ea80-c0a7-11ea-9680-777923663d0c.png" alt="While taking Attendance" width="600"/>

**Tabular Data Presentation**<br/>
<img src="https://github.com/Patelrahul4884/Attendance-Management-system-using-face-recognition/blob/master/Project%20Snap/7.PNG" alt="Attendance in tabular format" width="600"/>
