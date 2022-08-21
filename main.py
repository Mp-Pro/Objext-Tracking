#Motion Detection using Frame Differencing

import cv2

class MotionTacker:
    #__init__ is a special method of the class
    #It is auto invoked as object of the class is created.
    #Its purpose is to initialize the object to first state.
    def __init__(self, src=0):
        #Open/Access video source (file/camera)
        self.vh = cv2.VideoCapture(src)
        #Test the status
        if not self.vh.isOpened():
            raise Exception('Video Source Not Accessible')

        #define 3 frames
        self.prev_frame = None
        self.curr_frame = None
        self.next_frame = None

    #motion detection
    def frame_difference(self):
        #d1 = abs(f1-f2)
        d1 = cv2.absdiff(self.prev_frame, self.curr_frame)
        #d2 = abs(f2-f3)
        d2 = cv2.absdiff(self.curr_frame, self.next_frame)
        #diff = d1 & d2
        diff = cv2.bitwise_and(d1, d2)
        return diff

    def track(self):
        #create 2 windows
        cv2.namedWindow('Video Player')
        cv2.namedWindow('Motion')

        #know the FPS
        fps = self.vh.get(cv2.CAP_PROP_FPS)

        # read a video frame
        # and fetch a tuple (boolean, ndarray)
        # boolean indicates: read success or failure
        # ndarray: is a frame

        #initialize 3 frames
        _, self.prev_frame = self.vh.read()
        _, self.curr_frame = self.vh.read()
        flag, self.next_frame = self.vh.read()

        while flag:
            #render the frame
            cv2.imshow('Video Player', self.curr_frame)
            #render the motion
            cv2.imshow('Motion', self.frame_difference())

            #delay + read key pressed; if ESC then stop the loop
            if cv2.waitKey(int(1/fps*1000)) == 27:
                break

            #reinitialization
            self.prev_frame = self.curr_frame
            self.curr_frame = self.next_frame
            flag, self.next_frame = self.vh.read()


    #__del__ is a special method of the class
    #It is auto invoked as object of the class is about to be deallocated.
    #Its purpose is to free the resources used by the object.
    def __del__(self):
        print('in del')
        cv2.destroyAllWindows()
        if self.vh.isOpened():
            self.vh.release()


mt = MotionTacker('D:/python/ObjectTracking/birds.mp4')
mt.track()