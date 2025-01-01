import cv2
import tkinter
import PIL.Image
import PIL.ImageTk
import numpy as np

class VideoCap:
    def __init__(self, window=None):
        self.window = window
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source")
            
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        self.all_filters = None
        self.panelA = None
        self.panelB = None
        
        # Start the video capture thread
        self.update()
    
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return (ret, None)
        return (False, None)
    
    def update_panel(self, original_image, filtered_image):
        # convert the images to PIL format
        original_image = PIL.Image.fromarray(original_image)
        filtered_image = PIL.Image.fromarray(filtered_image)
        
        # resize the frames
        original_image = original_image.resize((400, 400), PIL.Image.LANCZOS)
        filtered_image = filtered_image.resize((400, 400), PIL.Image.LANCZOS)
        
        # convert to ImageTk format
        original_image = PIL.ImageTk.PhotoImage(original_image)
        filtered_image = PIL.ImageTk.PhotoImage(filtered_image)
        
        # if the panels are None, initialize them
        if self.panelA is None or self.panelB is None:
            self.panelA = tkinter.Label(image=original_image)
            self.panelA.image = original_image
            self.panelA.grid(row=3, column=2, sticky="nsew")
            
            self.panelB = tkinter.Label(image=filtered_image)
            self.panelB.image = filtered_image
            self.panelB.grid(row=3, column=3, sticky="nsew")
        else:
            # update the panels
            self.panelA.configure(image=original_image)
            self.panelB.configure(image=filtered_image)
            self.panelA.image = original_image
            self.panelB.image = filtered_image
    
    def update(self):
        ret, frame = self.get_frame()
        
        if ret:
            self.original_image = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.all_filters['color']:
                self.filtered_image = frame
            elif self.all_filters['gray']:
                self.filtered_image = gray
            elif self.all_filters['gauss']:
                self.filtered_image = cv2.GaussianBlur(gray, (21, 21), 0)
            elif self.all_filters['sobel']:
                self.filtered_image = cv2.Sobel(gray, -1, dx=1, dy=0, ksize=11)
            elif self.all_filters['laplace']:
                self.filtered_image = cv2.Laplacian(gray, -1, ksize=17)
            elif self.all_filters['threshold']:
                self.filtered_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
            elif self.all_filters['median']:
                self.filtered_image = cv2.medianBlur(frame, 5)
            elif self.all_filters['average']:
                self.filtered_image = cv2.blur(frame, (5, 5))
            elif self.all_filters['unsharp']:
                gaussian = cv2.GaussianBlur(frame, (0, 0), 2.0)
                self.filtered_image = cv2.addWeighted(frame, 4.0, gaussian, -3.0, 0)
            elif self.all_filters['logTransformation']:
                img = frame.astype(float) + 1.0
                c = 255 / np.log(1 + np.max(img))
                self.filtered_image = np.array(c * np.log(img), dtype=np.uint8)
            elif self.all_filters['negativeEnhancement']:
                self.filtered_image = 255 - frame
            elif self.all_filters['powerLowEnhancement']:
                lookUpTable = np.empty((1, 256), np.uint8)
                gamma = 0.8
                for i in range(256):
                    lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                self.filtered_image = cv2.LUT(frame, lookUpTable)
            elif self.all_filters['increaseContrast']:
                alpha = 1.5
                beta = 40
                self.filtered_image = cv2.addWeighted(frame, alpha,
                                                    np.zeros(frame.shape, frame.dtype), 0,
                                                    beta)
            elif self.all_filters['decreaseContrast']:
                alpha = 0.8
                beta = -50
                self.filtered_image = cv2.addWeighted(frame, alpha,
                                                    np.zeros(frame.shape, frame.dtype), 0,
                                                    beta)
            elif self.all_filters['min']:
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                self.filtered_image = cv2.erode(frame, kernel)
            elif self.all_filters['max']:
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                self.filtered_image = cv2.dilate(frame, kernel)
            elif self.all_filters['prewitt']:
                img_gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
                kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
                kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
                img_prewittx = cv2.filter2D(img_gaussian, -1, kernelx)
                img_prewitty = cv2.filter2D(img_gaussian, -1, kernely)
                self.filtered_image = img_prewittx + img_prewitty
            elif self.all_filters['histogramEqualization']:
                self.filtered_image = cv2.equalizeHist(gray)
            
            self.update_panel(self.original_image, self.filtered_image)
            
            # Schedule the next update
            self.window.after(15, self.update)
    
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
