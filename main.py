#Object Tracker

import cv2
import numpy as np

class ObjectTracker:
    #A special method of the class.
    #It is auto invoked as object of the class is created.
    #It initializes the object to first (initial) state.

    def __init__(self, src=0):
        #Capture the video source
        self.video_handle = cv2.VideoCapture(src)
        #Test the open status
        if not self.video_handle.isOpened():
            raise Exception('Cant Access : '+ src )

        #A frame to initialize from the video source and process too
        self.frame = None

        #A flag to indicate the selection state of the ROI
        self.selection_state = 0
        self.selection = []

    def on_mouse_event(self, event, x, y, flag, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selection.clear() # reset the selection
            self.selection.append(x) #x of mouse down
            self.selection.append(y) #y of mouse down
            self.selection_state = 1

        elif event == cv2.EVENT_LBUTTONUP:
            self.selection.append(x)  # x of mouse up
            self.selection.append(y)  # y of mouse up
            self.selection_state = 2

        if self.selection_state ==2:
            #x,y of mouse down and x,y of mouse up are captured
            #normalize the users rectangle forming orientation in a manner that x1,y1 are top,left and x2,y2 are bottom,right
            if self.selection[0] > self.selection[2]:
                self.selection[0], self.selection[2] = self.selection[2], self.selection[0]
            if self.selection[1] > self.selection[3]:
                self.selection[1], self.selection[3] = self.selection[3], self.selection[1]

            #correct x1 if it has become negative (selection ends outside the window)
            self.selection[0] = 0 if self.selection[0] < 0 else self.selection[0]
            # correct y1 if it has become negative (selection ends outside the window)
            self.selection[1] = 0 if self.selection[1] < 0 else self.selection[1]
            # correct x2 if it has become greater than width (selection ends outside the window)
            self.selection[2] = self.frame.shape[1] if self.selection[2] > self.frame.shape[1] else self.selection[2]
            # correct y2 if it has become greater than height (selection ends outside the window)
            self.selection[3] = self.frame.shape[0] if self.selection[3] > self.frame.shape[0] else self.selection[3]

            self.selection_state = 3

    def play_and_track(self):
        #Create named windows
        cv2.namedWindow('Object Tracker')
        #cv2.namedWindow('ROI')

        #Register with CV2 for a callback on mouse event
        cv2.setMouseCallback('Object Tracker', self.on_mouse_event )

        #know the FPS
        fps = self.video_handle.get(cv2.CAP_PROP_FPS)
        print(fps)
        #read the first frame
        flag, self.frame = self.video_handle.read() #(boolean, ndarray)
        while flag:
            print(self.selection_state)
            #As processing is to be done on HUE channel, so lets convert the frame from BGR to HSV
            hsv_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            if self.selection_state == 3:
                #cv2.rectangle(self.frame, (self.selection[0], self.selection[1]), (self.selection[2], self.selection[3]), (0,127,255), 1)
                roi = hsv_frame[self.selection[1]:self.selection[3], self.selection[0]:self.selection[2]]
                cv2.imshow('ROI', roi)
                #histogram (of HUE channel only)
                #calcHist([images], [channels], mask, [intervals], [ranges])
                hist_roi = cv2.calcHist([roi],[0], None, [180], [0,179])

                #Define initial tracker window for CAMShift
                tracker_window = [self.selection[0], self.selection[1], self.selection[2] - self.selection[0], self.selection[3] - self.selection[1]] #left(x1),top(y1),width(x2-x1),height (y2-y1)

                #Set termination criteria for CAMShift to: 10 iterations or max movement of 1 pixel
                termination_criteria = (cv2.TermCriteria_COUNT | cv2.TermCriteria_EPS, 10,1)

                self.selection_state = 4

            if self.selection_state == 4:
                #backprojection
                #calcBackProject([images], [channels], histogram, [ranges], scale)
                backprojection = cv2.calcBackProject([hsv_frame],[0], hist_roi,[0,179], 1 )

                #Here we create a mask from the source image, by dropping out the weakly pronounced colors
                mask = cv2.inRange(hsv_frame,np.array((0,60,30)), np.array((180, 255, 230)))
                backprojection = backprojection & mask

                cv2.imshow('BackProjection', backprojection)

                #CAMShift
                ellipse_params, tracker_window = cv2.CamShift(backprojection, tracker_window, termination_criteria)
                #Draw an ellipse on original image

                cv2.ellipse(self.frame, ellipse_params, color=(0,0,255), thickness=2)

            #render
            cv2.imshow('Object Tracker', self.frame)
            #delay to match the FPS
            if cv2.waitKey(int(1000/fps)) == 27: #ASCII(ESC) == 27
                break
            #next frame
            flag, self.frame = self.video_handle.read()

        #Destroy all windows
        cv2.destroyAllWindows()

    #A special method of the class
    #It gets auto invoked (by the Garbage Collector) as life of the object ends (When reference count reduces to 0 or when application ends) .
    def __del__(self):
        if self.video_handle.isOpened():
            self.video_handle.release()

ot = ObjectTracker(0)
ot.play_and_track()
