import zipfile
from zipfile import ZipFile
from PIL import Image,ImageDraw, ImageFont
import pytesseract
import cv2 as cv
import numpy as np

face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

def get_contact_sheet_height(albm):
    h1 = 0
    h2 = 0
    h = 0
    for subalbm in albm:
        h1 = h1 + subalbm[0].height
        h2 = h2 + ((len(subalbm)+3)//5)*120
    h = h1 + h2
    return h

target_file = input('Please enter the target file for your search.\nchoose from images.zip and small_img.zip: ')
print('Your target file is: ' + target_file)

src_str = input('Please enter your keyword: ')
print('You are searching for the string: ' + src_str)

zp_file = zipfile.ZipFile('readonly/' + target_file, 'r')

zp_filename_lst = []
for file in zp_file.infolist():
    zp_filename_lst.append(str(file).split(' ')[1].strip('filename=').strip('.'))

zp_file.extractall(path='readonly/')

capt_font = ImageFont.truetype('readonly/fanwood-webfont.ttf', size = 20)

file_album = []
zip_lst = zp_file.infolist()

for file in zip_lst:
    #myzip = ZipFile('readonly/'+ str(file), 'r')
    small_file = zp_file.open(file.filename)
    #im = Image.open(small_file)
    #some_file = myzip.open(str(file))
    pic_ori = Image.open(small_file)
    pic_gry = Image.open(small_file).convert('L')
    print('------- now processing' + file.filename + '-------')
    file_subalbum = []
    text_pic_gry = pytesseract.image_to_string(pic_gry)
    if src_str.lower() in text_pic_gry.lower():
        pic_gry.save("temp_file.png")
        file_pic = cv.imread("temp_file.png")
        file_face = face_cascade.detectMultiScale(file_pic, 1.85)
        if len(file_face) == 0:
            print('keyword found but no faces')
            file_caption = Image.new('RGB', (600,80), color='white')
            ImageDraw.Draw(file_caption).text((1, 25), 'Results found in file{}\nBut there were no faces in that file!'.format(file.filename), font=capt_font, fill=(0,0,0))
            file_subalbum.append(file_caption)
        elif len(file_face) > 0:
            print('keyword found with face(s)')
            file_caption = Image.new('RGB', (600,40), color='white')
            ImageDraw.Draw(file_caption).text((1,5), 'Result found in file {}'.format(file.filename),font = capt_font, fill = (0,0,0))
            file_subalbum.append(file_caption)
            for face in file_face:
                face_box = (face[0], face[1], face[0] + face[2], face[1] + face[3])
                file_subalbum.append(pic_ori.crop(face_box))
            print(str(len(file_face)) + " face(S) found")
        file_album.append(file_subalbum)
    else:
        print('no keword found')
contact_sheet = Image.new('RGB', (600,get_contact_sheet_height(file_album)), color='black')

y = 0
sub_y = 0
caption_height = 0
for a in range(len(file_album)):
    x = 0
    contact_sheet.paste(file_album[a][0], (x , y))
    caption_height = file_album[a][0].height
    y = y + caption_height
    if len(file_album[a]) > 1:
        for b in range(1, len(file_album[a])):
            x = ((b-1)%5) * 120
            sub_y = ((b-1)//5) * 120
            if file_album[a][b].height > 120:
                contact_sheet.paste(file_album[a][b].resize((120, 120)),(x, y+sub_y))
            else:
                contact_sheet.paste(file_album[a][b], (x, y + sub_y))
        y = y + sub_y + 120

display(contact_sheet)
