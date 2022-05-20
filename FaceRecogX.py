import cv2
import numpy as np
import face_recognition
import argparse
import imutils
import pickle
import time as t
from datetime import datetime,time,timedelta
import pprint
import requests
import json

#ap = argparse.ArgumentParser()
#ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")
#args = vars(ap.parse_args())
#input()

def Attendance(args):
    timer = t.perf_counter_ns()
    key1 = []
    val1 = []
    video_capture = cv2.VideoCapture(0)
    print("loading encodings")
    data = pickle.loads(open(args["encodings"], "rb").read())
    for key in data:
        key1.append(key)
        val1.append(data[key])

    known_face_encodings = val1[0]
    known_face_names = val1[1]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    AttDictList = []
    Attendees = []
    Times = []
    while True:
        if(t.perf_counter_ns()-timer > 0.25*(60*(10**9))):
            break
        # Grab a single frame of video

        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_ITALIC
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            Attendees.append(name)
            Attendees.append(datetime.now().time())
            Attendees.append("Break")
            Times.append(datetime.now().strftime("%H:%M:%S"))
            AttDictList.append({"Roll": name, "Time": datetime.now().strftime("%H:%M:%S"), "Date": datetime.now().strftime("%d-%m-%Y"), "ID" : "PitchWebCam01"})
            X = json.dumps({"Roll": name, "Time": datetime.now().strftime("%H:%M:%S"), "Date": datetime.now().strftime("%d-%m-%Y"), "ID" : "PitchWebCam01"})
            print(X)
        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #pprint.pprint(Attendees)

    #f = open("C:\\Users\\Pitch\\Desktop\\FaRFASA\\g.txt")
    #f.writelines(Attendees)
    #f.close
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    def convertList(a):
        dict1 = {a[i]:'a' for i in range(0,len(lst))}
        return dict1

    lst = known_face_names

    AttendanceDict = convertList(lst)

    for i in lst:
        if i in Attendees:
            AttendanceDict[i] = 'p'
    a = args["encodings"]
    a = a.replace(".pickle", "")


    def getPeriod(S=None):
        if(8*60+0 <= S < 9*60+20):
            return 1
        elif(9*60+20 <= S < 10*60+10):
            return 2
        elif (10*60+30 <= S < 11*60+20):
            return 3
        elif (11*60+20 <= S < 12*60+10):
            return 4
        elif (13*60+40 <= S < 14*60+30):
            return 5
        elif (14*60+30 <= S < 15*60+20):
            return 6
        elif (15*60+30 <= S < 16*60+20):
            return 6
        elif (16*60+20 <= S < 17*60+10):
            return 6
        else:
            return 7



    times = Times
    T = str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), times)))/len(times)))
    T1 = T.split(".")
    T = T1[0]

    def getTimeSec(T):
        h,m,s = T.split(":")
        return int(h)*60 + int(m)

    S = getTimeSec(T)

    P = getPeriod(S)
    print(P)

    AttendanceDict["Class"] = str(P)+"-"+a
    AttendanceDict["Date"] = datetime.now().strftime("%d-%m-%Y")
    AttendanceDict["ID"] = "PitchWebCam01"
    print(AttendanceDict)
    print(AttDictList)
    #SendToServer(AttendanceDict)

def SendToServer(Dict1):
    API_ENDPOINT = "111.111.111.111"
    API_KEY = "XXXXXXXXXXXXXXXXXXXXX"
    User = "Cam1"
    r = requests.post(url = API_ENDPOINT, json = Dict1, auth =(User,API_KEY))

if __name__ == "__main__":
    args = {"encodings":"0"}
    #E = input()
    E = "zg21721.pickle"
    args["encodings"] = E
    Attendance(args)
