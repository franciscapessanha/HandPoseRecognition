import cv2 as cv
import sys
import numpy as np
import math
from calculate_mask import get_mask
from display import *
from calculate_fingers import get_fingers
from helpers import is_int

title = 'Hand Labeling v0.1'
state = 'start'
sample = None
threshold = None
frame_rate = 1
video_frame_rate = 1

def get_frame_rate(video_capture_source, video_capture):
  global video_frame_rate, frame_rate
  if not type(video_capture_source) == int:
    video_frame_rate = int(video_capture.get(cv.CAP_PROP_FPS))
    frame_rate = video_frame_rate

def format_frame(frame, video_capture_source):
  if type(video_capture_source) == int: # Video Capture Device is a web camera
    frame = cv.flip(frame, 1)
  new_size = get_new_size(frame)
  frame = cv.resize(frame, (new_size[1],new_size[0])) #this way every video will have the similar dimensions - and so the kernels will be right!
  return frame

def format_image(image):
  new_size = get_resize(image)
  return cv.resize(image, (new_size[1],new_size[0])) #this way every video will have the similar dimensions - and so the kernels will be right!

def get_new_size(image):
  size = image.shape
  size = list(size)
  if size[0] >= size[1]:
    size[1] = int(size[1] * (640/size[0]))
    size[0] = 640
  
  elif size[0] < size[1]:
    size[0] = int(size[0] * (640/size[1]))
    size[1] = 640
  return size

def enter_pressed(frame):
  global state, threshold, sample
  if state == 'start':
    cv.destroyWindow(title + ' - Press ENTER to sample')
    sample, threshold = open_selector_window(frame)
    state = 'labeling'
  elif state == 'calibrating':
    cv.destroyWindow(calibrate_window_title)
    state = 'labeling'

def s_key_pressed(frame):
  global state, threshold, sample
  if state == 'labeling':
    cv.destroyWindow(title)
    sample, threshold = open_selector_window(frame)

def c_key_pressed():
  global state
  if state == 'labeling':
    cv.destroyWindow(title)
    create_calibration_window()
    state = 'calibrating'

def space_pressed():
  global state, frame_rate
  if state == 'labeling':
    frame_rate = 0
    state = 'paused'
  elif state == 'paused':
    frame_rate = video_frame_rate
    state = 'labeling'

def handle_key(key, frame):
  global frame_rate
  if key == 27: # Esc key pressed
    return False
  elif key == 32: # Space key pressed
    space_pressed()
  elif key == 13: # Enter key pressed
    enter_pressed(frame)
  elif key == 99: # C key pressed
    c_key_pressed()
  elif key == 115: # S key pressed
    s_key_pressed(frame)

  return True

def handle_display(frame):
  global state
  if state == 'start':
    cv.imshow(title + ' - Press ENTER to sample', frame)
  elif state == 'labeling':
    mask = get_mask(frame,threshold)
    frame_copy, count_fingers  = get_fingers(mask,frame)
    add_string_frame(frame_copy, str(count_fingers))
    cv.imshow(title, frame_copy)
  elif state == 'calibrating':
    open_calibration_window(frame, sample)

def label_video(video_capture_source):
  cap = cv.VideoCapture(video_capture_source)
  get_frame_rate(video_capture_source, cap)

  while(True):
    # Capture frame-by-frame
    _, frame = cap.read()
    if frame is None:
      print('Video ended. Closing...')
      break

    frame = format_frame(frame, video_capture_source)
    if not handle_key(cv.waitKey(frame_rate), frame):
      break
 

    frame = format_frame(frame, video_capture_source)

    if not handle_key(cv.waitKey(frame_rate), frame): 
      break
    handle_display(frame)

  # When everything done, release the capture
  cap.release()
  cv.destroyAllWindows()

def label_image(image_source):
  global state
  while(True):
    image = cv.imread(image_source)
    image = format_image(image)

    if state == 'calibrating':
      running = 1
    else:
      running = 0

    if not handle_key(cv.waitKey(running), image): 
      break

    handle_display(image)

def handle_arguments():
  if len(sys.argv) == 1:
    label_video(0)
  elif len(sys.argv) == 2:
    if is_int(sys.argv[1]):
      label_video(int(sys.argv[1]))
    else:
      if sys.argv[1].endswith('.mp4'):
        label_video(sys.argv[1])
      elif sys.argv[1].endswith('.jpg') or sys.argv[1].endswith('.png'):
        label_image(sys.argv[1])

if __name__ == "__main__":
  handle_arguments()