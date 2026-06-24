import cv2
import numpy as np

class HSVObjectDetector:
    def __init__(self, lower=(35,40,40), upper=(85,255,255), min_area=300):
        self.lower = np.array(lower, dtype=np.uint8)
        self.upper = np.array(upper, dtype=np.uint8)
        self.min_area = float(min_area)

    def detect(self, bgr):
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, mask
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < self.min_area:
            return None, mask
        M = cv2.moments(c)
        if M['m00'] == 0:
            return None, mask
        u = int(M['m10'] / M['m00'])
        v = int(M['m01'] / M['m00'])
        x,y,w,h = cv2.boundingRect(c)
        return {'u':u,'v':v,'bbox':(x,y,w,h),'area':area,'confidence':min(1.0, area/(bgr.shape[0]*bgr.shape[1]))}, mask
