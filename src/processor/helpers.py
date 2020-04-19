import cv2
import numpy as np
import base64

def normalize(arr, align=False):
  # formats & normalizes an img arr
  norm = np.asarray(arr, dtype=np.uint8)
  if (align):
    norm = np.rot90(norm)
    norm = cv2.flip(norm, 0)
  return norm

def chromaticity(arr):
  # returns the chromaticity in R,G format
  chroma = []
  for i in range(len(arr)):
    axisArr = []
    for j in range(len(arr[i])):
      r, g, b = arr[i][j][0], arr[i][j][1], arr[i][j][2]
      # the 0 converts uint8 to int
      sum = (0 + r + g + b)

      if (sum == 0): axisArr.append([0,0])
      else: axisArr.append([
        int((r / sum) * 255),
        int((g / sum) * 255)
      ])
    chroma.append(axisArr)
  return normalize(chroma)

def hist(img, bins):
  # converts a single frame/image into a hist
  return cv2.calcHist(img,
    [0, 1], None,
    [bins, bins],
    [0, 256, 0, 256]
  )

def imgBase64(img_arr):
  # converts an image array into base64
  # to be used as a generated img on the front-end
  ret, buf = cv2.imencode('.png', img_arr)
  data_uri = base64.b64encode(buf).decode('ascii')
  return 'data:image/png;base64,{0}'.format(data_uri)