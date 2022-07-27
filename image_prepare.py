import pyautogui
from PIL import ImageGrab, Image, ImageEnhance
import numpy as np

pic = 'src/MySnapshot.png'

def do_scrnshot_and_convert():
    x, y = pyautogui.position()
    w = x + 35
    h = y + 35
    x = x - 35
    y = y - 35
    snapshot = ImageGrab.grab(bbox=(x, y, w, h))
    snapshot.save(pic)
    image_file = Image.open(pic)  # open colour image
    enhancer = ImageEnhance.Contrast(image_file)
    factor = 2 # increase contrast
    im_output = enhancer.enhance(factor) # make more contrast
    res = im_output.crop((0, 0, 65, 40)) #(left, top, right, bottom)7
    data = np.array(res)

    converted = np.where(data == 10, 10, 10)

    img = Image.fromarray(converted.astype('uint8'))
    img.save('src/new_pic.jpg')
    res.save('src/result.png')
