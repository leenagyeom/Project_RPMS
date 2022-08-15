from flask import Flask, render_template, request, url_for
import sqlite3
import os
from pandas import NA
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageFilter
from pathlib import Path
import sys
import cv2
import io
import string
import re
from time import time

# sys.path.append('/workspace/detection/yolov7')
# from detect import detect_run

sys.path.append('/workspace/detection/yolov5/')
from detect import detect_run
from read_character import image_coordinate

from zmq import NULL
import ocr
app = Flask(__name__)
device = "cuda" if torch.cuda.is_available() else "cpu"

# 기본 템플릿
def template(content):
    return f'''
    <html>
    <head><link rel="stylesheet" href="{ url_for('static', filename='css/style.css') }"></head>
    <body>
        <div class="grid-container">
            <div class="header">
            	<h1><a href="/">Detection Web</a></h1>
            </div>
            <div class="left">
                <a href="/detection/"><h3>Detection</h3></a>
                <a href="/userList/"><h3>사용자 관리</h3></a>
            </div>
            {content}
        </div>
    </body>
    </html>
    '''

def solution(filename):
    detect_run(filename)
    ocr_result, predict = image_coordinate()

    # ocr_result, ocr_config = ocr.easy_ocr(filename)
    
    if re.match("(\d{2,3}\D\d{4})", ocr_result) == None:
        name = '인식오류'
    else:
        conn = sqlite3.connect('users.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE carNumber=?', (ocr_result, ))
        user = cursor.fetchone()
        conn.close()
        if user != None:
            name = user[1]
            #user[1]이 이름 user[2]가 차량번호
        else:
            name = "미등록"
    
    return name, ocr_result    
    

@app.route('/detection/')
def detection(filename=None, name=None, carNumber=None):
    return template(render_template('./detection.html'))


# 사진 업로드 눌렀을 때
@app.route('/upload', methods = ['POST'])
def upload():
    # File load
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if not file:
        return 
    # Set image from file
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))
    
    # Set image upload path 
    img_src = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    # Run model
    results = model(img, size=640)

    # Updates results.imgs with boxes and labels
    results.render()  
    
    for img in results.imgs:
        img_base64 = Image.fromarray(img)
        img_base64.save(img_src)
        
    # Crop image by boxes
    crops = results.crop(save=False)
    # conf = (crop[0]['conf'].item() * 100)
    
    # to save car numbers and names
    car_dict = {}

    
    # loop every cropped image
    for num, crop in enumerate(crops) :
        # if it's a plate over 50% probability
        if 'plate' in crop['label'] and crop['conf'].item() * 100 > 50 :
            image = crop['im']
            # Set cropped image and apply augmentation - grayscale, gaussianblur
            im = Image.fromarray(image)
            im = im.convert("L")
            im = im.filter(ImageFilter.GaussianBlur(radius =1))
    
    		# Set plate image save path to FILENAME_pl2.png
            plate_src = os.path.join(app.config['UPLOAD_FOLDER'], file.filename.split('.')[0] + '_pl' + str(num) + '.png')
            im.save(plate_src, 'png')
            #이미지를 upload 할 때 마다 실행
            price=0 #주차요금은 기본적으로 0원
            name, carNumber = solution(plate_src) #ocr로 차번호를 가져와서 db에 있는 이름을 가져온다
            car_dict[carNumber] = (name,price) #dictonary 형태로 차번호:{이름,주차요금}
            if name!="미등록" and name!="인식오류":
                conn = sqlite3.connect('users.sqlite3') #db에 접근
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET timeout =? WHERE name =? and timein!=?', (time(),name,NULL) )
                cursor.execute('UPDATE users SET timein =? WHERE name =? and timein=?', (time(),name,NULL) )

                cursor.execute('SELECT * FROM users WHERE name=?', (name, ))
                results = cursor.fetchall()
                
                cursor.execute('UPDATE users SET (cal,timein,timeout) =(?,?,?) WHERE name =? and timein!=? and timeout!=?', (results[0][4]-results[0][3],0,0,name,0,0))
                cursor.execute('SELECT * FROM users WHERE name=?', (name, ))
                fresults = cursor.fetchall()
                if fresults[0][5]!=0:
                    price=round(100*fresults[0][5])
                    car_dict[carNumber] = (name,price)
                    cursor.execute('UPDATE users SET cal =? WHERE name =? ', (0,name))
                conn.commit()
                conn.close()

    # call detection.html with car_dict
    return template(render_template('detection.html', filename=img_src, results=car_dict))

@app.route("/userList/")
def userList(innerContent=""):
    conn = sqlite3.connect('users.sqlite3')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, carNumber TEXT NOT NULL, timein INTEGER , timeout INTEGER ,cal INTEGER) ")
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    uList = f'''
      <div class="middle">
      <table id="users">
        <thead><tr><th>이름</th><th>차량번호</th><th>삭제</th></tr></thead>
        <tbody>
    '''
    for user in users:
        uList += f'<tr><td>{user[1]}</td><td>{user[2]}</td><td><a href="/delete/{user[0]}/">삭제</a></td></tr>'
    uList += f'</tbody></table>'
    content = f'''
    {uList}
    </div>
    <div class="right">
        <a class="insert" href="/insert/">신규 사용자 등록</a><br>
        {innerContent}
    </div>
    '''
    return template(content)


@app.route("/insert/")
def insert():
    content = '''
    <form action="/insert_process/" method="POST">
      <p><input type="text" name="name" placeholder="이름"></p>
      <p><input type="text" name="carNumber" placeholder="차량번호"></p>
      <p><input type="submit" value="등록"></p>
    </form>
    '''
    return userList(content)


@app.route("/insert_process/", methods=['POST'])
def insert_process():
    name = request.form['name'].replace(' ', '')
    carNumber = request.form['carNumber'].replace(' ', '')
    conn = sqlite3.connect('users.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, carNumber, timein, timeout,cal) VALUES (?,?,?,?,?)', (name, carNumber,0,0,0))
    conn.commit()
    conn.close()
    content = "등록 완료하였습니다."
    return userList(content)

@app.route('/delete/<int:num>/')
def delete(num):
    conn = sqlite3.connect('users.sqlite3')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id=?', (num,))
    conn.commit()
    conn.close()
    content = "삭제 완료하였습니다."
    return userList(content)


@app.route("/")
def index():
    return template("환영합니다.")


# 실행
if __name__ == "__main__":
    # 파일 업로드 폴더 경로
    UPLOAD_FOLDER = './static/images'
    Path("./" + UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    pt_file_path = "./models_train/best.pt"
    model = torch.hub.load('./yolov5', 'custom', path=pt_file_path, source='local')
    
    app.run(host='0.0.0.0', port=80, debug=True)