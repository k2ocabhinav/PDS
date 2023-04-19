import cv2
import time
import math as m
import pyttsx3  
from flask import Flask, render_template, Response, request
import mediapipe as mp
from numpy import imag
import win32api
import pyautogui



app = Flask(__name__)
cap = cv2.VideoCapture(0)
value=0
@app.route('/',methods=['GET', 'POST'])
def index():
    return render_template('/index.html')

@app.route('/success',methods=['GET', 'POST'])
def success():
    global value
    if request.method == 'POST':
        if request.form.get('Text') == 'Text':
            value=1
            gen(value)
        elif request.form.get('Voice') == 'Voice':
            value=2
            gen(value)
        elif request.form.get('Both') == 'Both':
            value=3
            gen(value)
    return render_template('success.html')

@app.route('/choice',methods=['GET', 'POST'])
def choice():
    
    return render_template('choice.html')



def gen(value):
    # Calculate angle.
    print(value)
    def findAngle(x1, y1, x2, y2):
        theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
            (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
        degree = int(180 / m.pi) * theta
        return degree


 
    good_frames = 0
    bad_frames = 0

    # Font type.
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Colors.
    blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

 
    
    # Meta
    fps = int(cap.get(cv2.CAP_PROP_FPS)) 
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Video writer.
    # video_output = cv2.VideoWriter('output.mp4', fourcc, fps, frame_size)

    while cap.isOpened():
        # Capture frames.
        success, image = cap.read()
        if not success:
            print("Null.Frames")
            break

        fps = cap.get(cv2.CAP_PROP_FPS)

        h, w = image.shape[:2]


        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        keypoints = pose.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark


        l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
        l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
        # Right shoulder
        r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
        r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
        # Left ear.
        l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
        l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
        # Left hip.
        l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
        l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

       
        neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
        torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

       

        angle_text_string = 'Neck : ' + str(int(neck_inclination)) + '  Torso : ' + str(int(torso_inclination))

        if neck_inclination < 30 and torso_inclination < 10:
            
            bad_frames = 0
            good_frames += 1
            
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, light_green, 2)
            cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, light_green, 2)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, light_green, 2)

            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), green, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), green, 4)

            
            good_time = (1 / fps) * good_frames
            bad_time =  (1 / fps) * bad_frames

            if good_time > 0:
                time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
                cv2.putText(image, time_string_good, (10, h - 20), font, 0.9, green, 2)
            else:
                time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
                cv2.putText(image, time_string_bad, (10, h - 20), font, 0.9, red, 2)

            if good_time > 5 and value == 1:
                # pyautogui.alert('Please take a break!')
                win32api.MessageBox(0, 'Please take a break!', 'Alert', 0x00001000) 
            
 

            elif good_time > 5 and value == 2:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices') 
                engine.setProperty('voice', voice[1].id)
                text = "Please take a break!"  
                engine.say(text)  
                engine.runAndWait()

            elif good_time > 5 and value == 3:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices')
                engine.setProperty('voice', voice[1].id)
                text = "Please take a break!"  
                engine.say(text)  
                engine.runAndWait()
                # pyautogui.alert('Please take a break!')
                win32api.MessageBox(0, 'Please take a break!', 'Alert', 0x00001000) 

                

        elif neck_inclination < 30 and torso_inclination > 10:

            good_frames = 0
            bad_frames += 1
            
            #Please sit straight
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, red, 2)
            cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, red, 2)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, red, 2)
            
            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)


            good_time = (1 / fps) * good_frames
            bad_time =  (1 / fps) * bad_frames

            # Pose time.
            if good_time > 0:
                time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
                cv2.putText(image, time_string_good, (10, h - 20), font, 0.9, green, 2)
            else:
                time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
                cv2.putText(image, time_string_bad, (10, h - 20), font, 0.9, red, 2)
                

            if bad_time > 4 and value == 1:
                win32api.MessageBox(0, 'Please sit straight!', 'Alert', 0x00001000) 
            
            elif bad_time > 4 and value == 2:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices') #get the available voices
    # eng.setProperty('voice', voice[0].id) #set the voice to index 0 for male voice
                engine.setProperty('voice', voice[1].id)
                text = "Please sit straight!"  
                engine.say(text)  
                engine.runAndWait()

            elif bad_time > 4 and value == 3:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices') #get the available voices
    # eng.setProperty('voice', voice[0].id) #set the voice to index 0 for male voice
                engine.setProperty('voice', voice[1].id)
                text = "Please sit straight!"  
                engine.say(text)  
                engine.runAndWait()
                # pyautogui.alert('Please take a break!')
                win32api.MessageBox(0, 'Please sit straight!', 'Alert', 0x00001000) 

        elif neck_inclination > 30 and torso_inclination < 10:

               
            good_frames = 0
            bad_frames += 1
            #Please Raise Your Neck and Sit Straight
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, red, 2)
            cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, red, 2)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, red, 2)
            
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)

            good_time = (1 / fps) * good_frames
            bad_time =  (1 / fps) * bad_frames

            # Pose time.
           

        
        # Calculate the time of remaining in a particular posture.
            good_time = (1 / fps) * good_frames
            bad_time =  (1 / fps) * bad_frames

            # Pose time.
            if good_time > 0:
                time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
                cv2.putText(image, time_string_good, (10, h - 20), font, 0.9, green, 2)
            else:
                time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
                cv2.putText(image, time_string_bad, (10, h - 20), font, 0.9, red, 2)
        
            if bad_time > 4 and value == 1:
                win32api.MessageBox(0, 'Please Lift Your Head and Sit Straight', 'Alert', 0x00001000) 
            
            elif bad_time > 4 and value == 2:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices') #get the available voices
    # eng.setProperty('voice', voice[0].id) #set the voice to index 0 for male voice
                engine.setProperty('voice', voice[1].id)
                text = "Please Lift Your Head and Sit Straight"  
                engine.say(text)  
                engine.runAndWait()

            elif bad_time > 4 and value == 3:
                engine = pyttsx3.init()  
                engine.setProperty("rate", 100) 
                voice = engine.getProperty('voices') 
                engine.setProperty('voice', voice[1].id)
                text = "Please Lift Your Head and Sit Straight"  
                engine.say(text)  
                engine.runAndWait()
                # pyautogui.alert('Please take a break!')
                win32api.MessageBox(0, 'Please Lift Your Head and Sit Straight', 'Alert', 0x00001000) 
        
        # Display image. 
        frame = cv2.imencode('.jpg', image)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
            


@app.route('/video_feed')
def video_feed():
    return Response(gen(value),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=="__main__":
    app.run(debug=True)
