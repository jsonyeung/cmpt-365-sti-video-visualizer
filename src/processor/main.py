from helpers import *
from tkinter import *
from tkinter import filedialog
import cv2
import math

import eel
eel.init('dist')

# Request File using File Explorer
@eel.expose
def requestVideoFile():
  root = Tk()
  root.withdraw()
  root.wm_attributes('-topmost', 1)
  folder = filedialog.askopenfilename(
    initialdir = './',
    title = 'Select a video file',
    filetypes = (
      ('Mp4 Files','*.mp4'),
      ('Avi Files', '*.avi'),
      ('Flv Files', '*.flv'),
      ('Wmv Files', '*.wmv'),
      ('Mov Files', '*.mov'),
      ('WebM Files', '*.webm')
    )
  )
  return folder or None

# Get STI
@eel.expose
def getSTI(vid_path, options):
  vid = cv2.VideoCapture(vid_path)
  if (not vid.isOpened()): return None

  print('GET_STI: Processing video...')
  type = options['type'] # Type of STI (raw or hist)
  dir = options['dir'] # Direction of axis (cols or rows)

  res = None
  if (type == 'raw'): res = imgBase64(getPixels(vid, dir))
  if (type == 'hist'): res = imgBase64(getHistInt(vid, dir))
  print('GET_STI: Finished processing')

  vid.release()
  return res

# Get Frame Count of video
@eel.expose
def getFrameCount(vid_path):
  vid = cv2.VideoCapture(vid_path)
  if (not vid.isOpened()): return 0

  frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
  vid.release()
  return frames

# Returns the cols/rows of a video in raw-pixel form
def getPixels(vid, dir):
  sti_raw = []
  while (True):
    ret, data = vid.read()
    if (not ret): break

    # get column or row depending on type
    axis = lambda i: data[i, :] if (dir == 'rows') else data[:, i]
    vid_len = len(data) if (dir == 'rows') else len(data[0])
    sti_raw.append(axis(round(vid_len / 2)))

  return normalize(sti_raw, True)

# Returns the Hist Intersect of a video (RG chromatized)
def getHistInt(vid, dir):
  lastFrame = None
  hist_img = []
  while (True):
    ret, data = vid.read()
    if (not ret): break

    # For the sake of performance, resize to 32 x 32
    data = cv2.resize(data, (32, 32))
    width = len(data)

    curFrame = chromaticity(data)
    bins = math.floor(1 + math.log2(width))
    axis = lambda frame, i: frame[i, :] if (dir == 'rows') else frame[:, i]

    if (not lastFrame is None):
      frame = []
      for i in range(width):
        hist_cur = hist(axis(curFrame, i), bins)
        hist_last = hist(axis(lastFrame, i), bins)
        frame.append(cv2.compareHist(hist_cur, hist_last, 2))
      hist_img.append(frame)
    lastFrame = curFrame

  hist_img = normalize(hist_img, True)
  hist_img = np.dot(np.dot(hist_img, (1.0/width)), 255)
  return 255 * hist_img


# vid = cv2.VideoCapture('./wipe.avi')
# # cv2.imshow('./test.png', getHistInt(vid, 'col'))
# cv2.imwrite('./test.png', getHistInt(vid, 'col'))
# cv2.waitKey(0)
# cv2.destroyAllWindows()

eel.start('index.html', size=(1024, 650))
