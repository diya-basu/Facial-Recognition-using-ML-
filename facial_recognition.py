import facial_recognition
import numpy as np
import cv2
import os
import glob

#get ref to webcam using this module 
video_cap=cv2.VideoCapture(0)

#creating a directory to known faces and people 
known_face_encodings=[]
known_face_names=[]
dirname=os.path.dirname(__file__)
path=os.path.join(dirname,'known_people/')

#create array of saved jpg file path 
list_of_files = [f for f in glob.glob(path+'*.jpg')]
#find number of known faces
number_files = len(list_of_files)

names=list_of_files.copy()

for i in range(number_files):
    globals()['image_{}'.format(i)] = facial_recognition.load_image_file(list_of_files[i])
    globals()['image_encoding_{}'.format(i)] = facial_recognition.face_encodings(globals()['image_{}'.format(i)])[0]
    known_face_encodings.append(globals()['image_encoding_{}'.format(i)])

    # Create array of known names
    names[i] = names[i].replace("known_people/", "")  
    known_face_names.append(names[i])

#variables to detect the faces and encode them using webcam 
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True: 
    #take a single video frame 
    ret,frame=video_cap.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = facial_recognition.face_locations(rgb_small_frame)
        face_encodings = facial_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = facial_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

         # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                 first_match_index = matches.index(True)
                 name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = facial_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

#results display 
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
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

#Release handle to webcam 
video_cap.release()
cv2.destroyAllWindows()