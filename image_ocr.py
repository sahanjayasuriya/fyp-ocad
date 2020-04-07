import pytesseract
from PIL import Image

img = Image.open('storage/91007067_150253999805213_3765468678183714816_n.jpg')
text = pytesseract.image_to_string(img)
print(text)
