from PyQt5.QtWidgets import *
import threading
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDockWidget, QListWidget
from PyQt5.QtGui import *
import face_recognition
import cv2
import os
from recognition.test import detect
from recognition.test import setOPT
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication,QMessageBox,QTableWidgetItem
import psycopg2
import time

# 窗口主类
class MainWindow(QTabWidget):
    # 基本配置不动，然后只动第三个界面
    def __init__(self):
        # 初始化设置
        super().__init__()
        self.setWindowTitle('人脸识别系统')
        self.resize(1100, 650)
        self.setWindowIcon(QIcon("UI_images/logo.png"))
        # 要上传的图片路径
        self.up_img_name = ""
        # 要检测的图片名称
        self.input_fname = ""
        # 要检测的视频名称
        self.source = ''
        self.video_capture = cv2.VideoCapture(0)
        # 初始化中止事件
        self.stopEvent = threading.Event()
        self.stopEvent.clear()
        # 初始化人脸向量
        self.known_names, self.known_encodings = self.initFaces()
        # 加载lbp检测器
        # 加载人脸识别模型
        # 初始化界面
        self.initUI()
        self.set_down()

    # 初始化视频检测界面
    def set_down(self):
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.DisplayLabel.setPixmap(QPixmap("UI_images/界面二.jpg"))
        self.DisplayLabel2.setPixmap(QPixmap("UI_images/界面二.jpg"))

    # 初始化数据库的人脸
    def initFaces(self):
        # 存储知道人名列表
        known_names = []
        # 存储知道的特征值
        known_encodings = []
        # 遍历存储人脸图片的文件夹
        db_folder = "C:/Users/86183/Desktop/FaceRecognition-master/images/db_faces"
        face_imgs = os.listdir(db_folder)
        # 遍历图片，将人脸图片转化为向量
        for face_img in face_imgs:
            face_img_path = os.path.join(db_folder, face_img)
            face_name = face_img.split(".")[0]
            face_img_path = os.path.join(db_folder, face_img).replace('\\', '/')
            print("Loading image from:", face_img_path)
            load_image = face_recognition.load_image_file(face_img_path)  # 加载图片
            image_face_encoding = face_recognition.face_encodings(load_image)[0]  # 获得128维特征值
            known_names.append(face_name)  # 添加到人名的列表
            known_encodings.append(image_face_encoding)  # 添加到向量的列表
        return known_names, known_encodings

    # 初始化界面
    def initUI(self):
        # 设置字体
        font_v = QFont('楷体', 14)
        generally_font = QFont('楷体', 15)
        # 图片检测
        img_widget = QWidget()
        img_layout = QVBoxLayout()
        img_f_title = QLabel("上传人脸图像")  # 设置标题
        img_f_title.setAlignment(Qt.AlignCenter)  # 设置标题位置为居中
        img_f_title.setFont(QFont('楷体', 18))  # 设置标题字体大小
        # todo 要上传的人脸图像
        self.img_f_img = QLabel()  # 设置第一个界面上要显示的图片
        self.img_f_img.setPixmap(QPixmap("UI_images/界面一.jpg"))
        self.img_f_img.setAlignment(Qt.AlignCenter)  # 设置图片居中
        self.face_name = QLineEdit()  # 设置当前图片对应的人名
        img_up_btn = QPushButton("上传图片")  # 设置上传图片的按钮
        img_det_btn = QPushButton("开始上传")  # 设置开始上传的按钮
        img_up_btn.clicked.connect(self.up_img)  # 联系到相关函数
        img_det_btn.clicked.connect(self.up_db_img)  # 连接到相关函数
        # 设置组件的样式
        img_up_btn.setFont(generally_font)
        img_det_btn.setFont(generally_font)
        img_up_btn.setStyleSheet("QPushButton{color:white}"
                                 "QPushButton:hover{background-color: rgb(2,180,110);}"
                                 "QPushButton{background-color:rgb(2,110,180)}"
                                 "QPushButton{border:2px}"
                                 "QPushButton{border-radius:5px}"
                                 "QPushButton{padding:5px 5px}"
                                 "QPushButton{margin:5px 5px}")
        img_det_btn.setStyleSheet("QPushButton{color:white}"
                                  "QPushButton:hover{background-color: rgb(2,180,110);}"
                                  "QPushButton{background-color:rgb(2,110,180)}"
                                  "QPushButton{border:2px}"
                                  "QPushButton{border-radius:5px}"
                                  "QPushButton{padding:5px 5px}"
                                  "QPushButton{margin:5px 5px}")
        # 将组件添加到布局上，然后设置主要的widget为当前的布局
        img_layout.addWidget(img_f_title)
        img_layout.addWidget(self.img_f_img)
        img_layout.addWidget(self.face_name)
        img_layout.addWidget(img_up_btn)
        img_layout.addWidget(img_det_btn)
        img_widget.setLayout(img_layout)

        '''
        *** 4. 视频识别界面 ***
        '''
        video_widget = QWidget()
        video_layout = QVBoxLayout()
        # 设置视频识别区的标题
        self.video_title2 = QLabel("视频识别区")
        self.video_title2.setFont(font_v)
        self.video_title2.setAlignment(Qt.AlignCenter)
        self.video_title2.setFont(font_v)
        # 设置显示的界面
        self.DisplayLabel = QLabel()
        self.DisplayLabel.setPixmap(QPixmap(""))
        self.btn_open_rsmtp = QPushButton("检测摄像头")
        self.btn_open_rsmtp.setFont(font_v)
        # 设置打开摄像头的按钮和样式
        self.btn_open_rsmtp.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton:hover{background-color: rgb(2,180,110);}"
                                          "QPushButton{background-color:rgb(2,110,180)}"
                                          "QPushButton{border:2px}"
                                          "QPushButton{border-radius:5px}"
                                          "QPushButton{padding:5px 5px}"
                                          "QPushButton{margin:5px 5px}")
        # 设置选择文件的的按钮和样式
        self.btn_open = QPushButton("开始识别（选择文件）")
        self.btn_open.setFont(font_v)
        self.btn_open.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton:hover{background-color: rgb(2,180,110);}"
                                    "QPushButton{background-color:rgb(2,110,180)}"
                                    "QPushButton{border:2px}"
                                    "QPushButton{border-radius:5px}"
                                    "QPushButton{padding:5px 5px}"
                                    "QPushButton{margin:5px 5px}")
        # 设置结束演示的按钮和样式
        self.btn_close = QPushButton("结束检测")
        self.btn_close.setFont(font_v)
        self.btn_close.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton:hover{background-color: rgb(2,180,110);}"
                                     "QPushButton{background-color:rgb(2,110,180)}"
                                     "QPushButton{border:2px}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{padding:5px 5px}"
                                     "QPushButton{margin:5px 5px}")
        # 将组件添加到布局上
        self.btn_open_rsmtp.clicked.connect(self.open_local)
        self.btn_open.clicked.connect(self.open)
        self.btn_close.clicked.connect(self.close)
        video_layout.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(self.video_title2)
        video_layout.addWidget(self.DisplayLabel)
        self.DisplayLabel.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(self.btn_open_rsmtp)
        video_layout.addWidget(self.btn_open)
        video_layout.addWidget(self.btn_close)
        video_widget.setLayout(video_layout)
        '''
        *** 5. yolo视频检测界面 ***
        '''
        about_widget = QWidget()
        about_layout = QVBoxLayout()
        # 设置视频识别区的标题
        self.about_title2 = QLabel("视频识别区")
        self.about_title2.setFont(font_v)
        self.about_title2.setAlignment(Qt.AlignCenter)
        self.about_title2.setFont(font_v)
        # 设置显示的界面
        self.DisplayLabel2 = QLabel()
        self.DisplayLabel2.setPixmap(QPixmap(""))
        self.btn_open_rsmtp2 = QPushButton("检测摄像头")
        self.btn_open_rsmtp2.setFont(font_v)
        # 设置打开摄像头的按钮和样式
        self.btn_open_rsmtp2.setStyleSheet("QPushButton{color:white}"
                                          "QPushButton:hover{background-color: rgb(2,180,110);}"
                                          "QPushButton{background-color:rgb(2,110,180)}"
                                          "QPushButton{border:2px}"
                                          "QPushButton{border-radius:5px}"
                                          "QPushButton{padding:5px 5px}"
                                          "QPushButton{margin:5px 5px}")
        # 设置选择文件的的按钮和样式
        self.btn_open2 = QPushButton("开始识别（选择文件）")
        self.btn_open2.setFont(font_v)
        self.btn_open2.setStyleSheet("QPushButton{color:white}"
                                    "QPushButton:hover{background-color: rgb(2,180,110);}"
                                    "QPushButton{background-color:rgb(2,110,180)}"
                                    "QPushButton{border:2px}"
                                    "QPushButton{border-radius:5px}"
                                    "QPushButton{padding:5px 5px}"
                                    "QPushButton{margin:5px 5px}")
        #设置结束演示的按钮和样式
        self.btn_close2 = QPushButton("结束检测")
        self.btn_close2.setFont(font_v)
        self.btn_close2.setStyleSheet("QPushButton{color:white}"
                                     "QPushButton:hover{background-color: rgb(2,180,110);}"
                                     "QPushButton{background-color:rgb(2,110,180)}"
                                     "QPushButton{border:2px}"
                                     "QPushButton{border-radius:5px}"
                                     "QPushButton{padding:5px 5px}"
                                     "QPushButton{margin:5px 5px}")
        # 将组件添加到布局上
        self.btn_open_rsmtp2.clicked.connect(self.open_local2)
        self.btn_open2.clicked.connect(self.open)
        self.btn_close2.clicked.connect(self.close)
        about_layout.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(self.about_title2)
        about_layout.addWidget(self.DisplayLabel2)
        self.DisplayLabel2.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(self.btn_open_rsmtp2)
        about_layout.addWidget(self.btn_open2)
        about_layout.addWidget(self.btn_close2)
        about_widget.setLayout(about_layout)
        # 分别添加子页面
        self.addTab(img_widget, "上传人脸")
        self.addTab(video_widget, '视频检测（HOG + Linear SVM+dlib）')
        self.addTab(about_widget, '视频检测（yolo+facenet）')
        self.setTabIcon(0, QIcon('UI_images/图片.png'))
        self.setTabIcon(1, QIcon('UI_images/直播.png'))
        self.setTabIcon(2, QIcon('UI_images/logo_about.png'))

    # 第一个界面的函数
    def up_img(self):
        # 打开文件选择框
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'Image files(*.jpg , *.png)')
        # 获取上传的文件名称
        img_name = openfile_name[0]
        if img_name == '':
            pass
        else:
            # 上传之后显示并做归一化处理
            src_img = cv2.imread(img_name)
            src_img_height = src_img.shape[0]
            src_img_width = src_img.shape[1]
            target_img_height = 400
            ratio = target_img_height / src_img_height
            target_img_width = int(src_img_width * ratio)
            # 将图片统一处理到高为400的图片，方便在界面上显示
            target_img = cv2.resize(src_img, (target_img_width, target_img_height))
            cv2.imwrite("UI_images/tmp/toup.jpg", target_img)
            self.img_f_img.setPixmap(QPixmap("UI_images/tmp/toup.jpg"))
            self.up_img_name = "UI_images/tmp/toup.jpg"

    def up_db_img(self):
        # 首先判断该图像是否有一个人脸，多个人脸或者没有人脸都不行
        face_name = self.face_name.text()
        if face_name == "":
            QMessageBox.information(self, "不能为空", "请填写人脸姓名")
        else:
            load_image = face_recognition.load_image_file(self.up_img_name)  # 加载图片
            image_face_encoding = face_recognition.face_encodings(load_image)  # 获得128维特征值
            encoding_length = len(image_face_encoding)  # 获取人脸得数量
            if encoding_length == 0:  # 如果没有人脸，提示用户重新上传
                QMessageBox.information(self, "请重新上传", "当前图片没有发现人脸")
            elif encoding_length > 1:  # 如果人脸有多个，也提示用户重新上传
                QMessageBox.information(self, "请重新上传", "当前图片发现多张人脸")
            else:
                face_encoding = image_face_encoding[0]  # 获取解析得到得人脸数量
                img = cv2.imread(self.up_img_name)  # 将上传得图片保存在db目录下
                img_path = face_name + '.jpg'
                cv2.imwrite("images/db_faces/" + img_path, img)
                # 上传之后重新对字典进行处理
                self.known_names.append(face_name)
                self.known_encodings.append(face_encoding)
                QMessageBox.information(self, "上传成功", "数据已上传！")

    '''
    ### 3. 视频识别相关功能 ### 
    '''

    # 关闭事件 询问用户是否退出
    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     '退出',
                                     "是否要退出程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            event.accept()
        else:
            event.ignore()

    # 读取录像文件
    def open(self):
        # 选择录像文件进行读取
        mp4_fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.mp4')
        if mp4_fileName:
            # 启动录像文件读取得线程并在画面上实时显示
            self.source = mp4_fileName
            self.video_capture = cv2.VideoCapture(self.source)
            th = threading.Thread(target=self.display_video)
            th.start()


    def open_local(self):
        # 选择录像文件进行读取
        mp4_filename = 0
        self.source = mp4_filename
        # 读取摄像头进行实时得显示
        self.video_capture = cv2.VideoCapture(self.source)
        th = threading.Thread(target=self.display_video)
        th.start()

    def open_local2(self):
        # 选择录像文件进行读取
        mp4_filename = 0
        self.source = mp4_filename
        # 读取摄像头进行实时得显示
        self.video_capture = cv2.VideoCapture(self.source)
        th = threading.Thread(target=self.display_video2)
        th.start()

    # 退出进程
    def close(self):
        # 点击关闭按钮后重新初始化界面
        self.stopEvent.set()
        self.set_down()

    # todo 执行人脸识别主进程
    #法一：HOG + Linear SVM+dlib
    def display_video(self):
        # 首先把打开按钮关闭
        self.btn_open.setEnabled(False)
        self.btn_close.setEnabled(True)
        process_this_frame = True
        while True:
            ret, frame = self.video_capture.read()  # 读取摄像头
            # opencv的图像是BGR格式的，而我们需要是的RGB格式的，因此需要进行一个转换。
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将图像转化为rgb颜色通道
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 检查人脸 按照1.1倍放到 周围最小像素为5
            # face_zone = self.face_detect.detectMultiScale(gray_frame, scaleFactor=2, minNeighbors=2)  # maxSize = (55,55)
            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_frame)  # 获得所有人脸位置
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)  # 获得人脸特征值
                face_names = []  # 存储出现在画面中人脸的名字
                for face_encoding in face_encodings:  # 和数据库人脸进行对比
                    # 如果当前人脸和数据库的人脸的相似度超过0.5，则认为人脸匹配
                    matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
                    if True in matches:
                        first_match_index = matches.index(True)
                        # 返回相似度最高的作为当前人脸的名称
                        name = self.known_names[first_match_index]
                    else:
                        name = "unknown"
                    face_names.append(name)
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print(timestamp, name)

                    # 写入数据库********************************************************************************
                    conn = create_conn()
                    cur = conn.cursor()  # 创建光标：
                    mstrsql = "insert into Detect values('{}','{}')".format(timestamp, name)
                    print(mstrsql)
                    cur.execute(mstrsql)  # 执行SQL指令
                    cur.execute("select * from Detect;")  # 执行SQL指令
                    results = cur.fetchall()  # (1)获取所有结果：
                    result = cur.fetchone()  # (2)获取一条结果：
                    print(results)  # 将获取的结果打印

                    conn.commit()  # 提交当前事务：
                    cur.close()  # 关闭光标：
                    conn.close()  # 关闭数据库连接：
                    # *************************************************************************************

            process_this_frame = not process_this_frame
            # 将捕捉到的人脸显示出来
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # 画人脸矩形框
                # 加上人名标签
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # 抓取图片并进行实时保存
            frame = frame
            frame_height = frame.shape[0]
            frame_width = frame.shape[1]
            frame_scale = 500 / frame_height
            frame_resize = cv2.resize(frame, (int(frame_width * frame_scale), int(frame_height * frame_scale)))
            cv2.imwrite("images/tmp.jpg", frame_resize)
            self.DisplayLabel.setPixmap(QPixmap("images/tmp.jpg"))
            if cv2.waitKey(25) & self.stopEvent.is_set() == True:
                self.stopEvent.clear()
                self.DisplayLabel.clear()
                self.btn_close.setEnabled(False)
                self.btn_open.setEnabled(True)
                self.set_down()
                break
        self.btn_open.setEnabled(True)
        self.btn_close.setEnabled(False)
        self.set_down()

    #法二：yolov5+facenet
    # 首先把打开按钮关闭
    # def display_video2(self):
    #     # 首先把打开按钮关闭
    #     self.btn_open.setEnabled(False)
    #     self.btn_close.setEnabled(True)
    #     process_this_frame = True
    #     while True:
    #         ret, frame = self.video_capture.read()  # 读取摄像头
    #         # opencv的图像是BGR格式的，而我们需要是的RGB格式的，因此需要进行一个转换。
    #         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将图像转化为rgb颜色通道
    #         # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #         # 检查人脸 按照1.1倍放到 周围最小像素为5
    #         # face_zone = self.face_detect.detectMultiScale(gray_frame, scaleFactor=2, minNeighbors=2)  # maxSize = (55,55)
    #         if process_this_frame:
    #             face_locations = face_recognition.face_locations(rgb_frame)  # 获得所有人脸位置
    #             face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)  # 获得人脸特征值
    #             face_names = []  # 存储出现在画面中人脸的名字
    #             for face_encoding in face_encodings:  # 和数据库人脸进行对比
    #                 # 如果当前人脸和数据库的人脸的相似度超过0.5，则认为人脸匹配
    #                 matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
    #                 if True in matches:
    #                     first_match_index = matches.index(True)
    #                     # 返回相似度最高的作为当前人脸的名称
    #                     name = self.known_names[first_match_index]
    #                 else:
    #                     name = "unknown"
    #                 face_names.append(name)
    #                 timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #                 print(timestamp, name)
    #
    #                 # 写入数据库********************************************************************************
    #                 conn = create_conn()
    #                 cur = conn.cursor()  # 创建光标：
    #                 mstrsql = "insert into Detect values('{}','{}')".format(timestamp, name)
    #                 print(mstrsql)
    #                 cur.execute(mstrsql)  # 执行SQL指令
    #                 cur.execute("select * from Detect;")  # 执行SQL指令
    #                 results = cur.fetchall()  # (1)获取所有结果：
    #                 result = cur.fetchone()  # (2)获取一条结果：
    #                 print(results)  # 将获取的结果打印
    #
    #                 conn.commit()  # 提交当前事务：
    #                 cur.close()  # 关闭光标：
    #                 conn.close()  # 关闭数据库连接：
    #                 # *************************************************************************************
    #
    #         process_this_frame = not process_this_frame
    #         # 将捕捉到的人脸显示出来
    #         for (top, right, bottom, left), name in zip(face_locations, face_names):
    #             cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # 画人脸矩形框
    #             # 加上人名标签
    #             cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
    #             font = cv2.FONT_HERSHEY_DUPLEX
    #             cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    #         # 保存图片并进行实时的显示
    #         frame = frame
    #         frame_height = frame.shape[0]
    #         frame_width = frame.shape[1]
    #         frame_scale = 500 / frame_height
    #         frame_resize = cv2.resize(frame, (int(frame_width * frame_scale), int(frame_height * frame_scale)))
    #         cv2.imwrite("images/tmp.jpg", frame_resize)
    #         self.DisplayLabel2.setPixmap(QPixmap("images/tmp.jpg"))
    #         if cv2.waitKey(25) & self.stopEvent.is_set() == True:
    #             self.stopEvent.clear()
    #             self.DisplayLabel2.clear()
    #             self.btn_close.setEnabled(False)
    #             self.btn_open.setEnabled(True)
    #             self.set_down()
    #             break
    #     self.btn_open.setEnabled(True)
    #     self.btn_close.setEnabled(False)
    #     self.set_down()

    def display_video2(self):
        self.btn_open.setEnabled(False)
        self.btn_close.setEnabled(True)
        process_this_frame = True

        while True:
            options = setOPT()
            detect(options)

        self.btn_open.setEnabled(True)
        self.btn_close.setEnabled(False)
        self.set_down()


# 定义一个类专门处理GUI
class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象

        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load("C:/Users/86183/Desktop/FaceRecognition-master/main.ui")
        self.ui.setWindowTitle('人脸识别')#设置窗口名称
        self.ui.c_button.clicked.connect(self.close_main_window)  # 按钮按下 执行函数self.close_main_window

        self.login = QUiLoader().load("C:/Users/86183/Desktop/FaceRecognition-master/login.ui")
        self.login.button3.clicked.connect(self.close_login_window)
        self.login.button1.clicked.connect(self.Sign_in)
        self.login.button2.clicked.connect(self.Register)

    def close_main_window(self):#关闭窗口
        self.ui.close()

    def add_cell(self, row, column, txt):  # 修改单个单元格的内容
        item = QTableWidgetItem()
        item.setText(txt)
        self.ui.table1.setItem(row, column, item)

    def init_table(self, tab_list):
        self.row = int(len(tab_list))  # 获得行数
        self.ui.table1.setRowCount(self.row)  # 初始化行数
        for i in range(self.row):
            temp = list(tab_list[i])
            for j in range(5):  # 循环写入5个属性
                self.add_cell(i, j, str(temp[j]))

    def close_login_window(self):  # 关闭窗口
        self.login.close()
        cur.close()
        conn.close()

    def add_cell(self, row, column, txt):  # 修改单个单元格的内容
        item = QTableWidgetItem()
        item.setText(txt)
        self.ui.table1.setItem(row, column, item)

    def init_table(self, tab_list):
        self.row = int(len(tab_list))  # 获得行数
        self.ui.table1.setRowCount(self.row)  # 初始化行数
        for i in range(self.row):
            temp = list(tab_list[i])
            for j in range(2):  # 循环写入2个属性
                self.add_cell(i, j, str(temp[j]))

    def Sign_in(self):
        user = self.login.user.text()  # 获取输入框的内容
        password = self.login.password.text()
        val = (user, password)
        cur.execute('select * from userinformation where uname = %s and upassword = %s;', val)
        result = cur.fetchall()  # 获取所有结果
        conn.commit()
        if result == []:
            QMessageBox.about(self.login, '提示', '密码错误或用户不存在')
        else:
            QMessageBox.about(self.login, '提示', '登录成功')
            self.login.close()
            #self.ui.show()
            mainWindow.show()

    def Register(self):
        user = self.login.user.text()  # 获取输入框的内容
        password = self.login.password.text()
        cur.execute(f'select * from userinformation where uname = \'%s\' ;' % (user))
        result = cur.fetchall()  # 获取所有结果
        conn.commit()
        val = (user, password)
        if result != []:
            QMessageBox.about(self.login, '提示', '用户已存在')
        else:
            cur.execute("insert into userinformation VALUES (%s,%s);", val)
            conn.commit()
            QMessageBox.about(self.login, '提示', '注册成功')

# 定义一个连接OpenGauss的函数
def create_conn():
    database = 'project'
    user = 'dboper'
    password = 'cqy123456?'
    host = '192.168.136.131'
    port = '26000'
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)  # 连接数据库
    return conn

if __name__ == "__main__":
    # 加载页面
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    msgBox = QMessageBox()
    stats = Stats()
    try:
        conn = create_conn()
    except Exception as e:
        msgBox.about(stats.ui, '提示窗口', str(e))

    else:
        #msgBox.about(mainWindow, '提示窗口', '数据库连接成功  ')  # 弹窗提示
        msgBox.about(stats.ui, '提示窗口', '数据库连接成功  ')  # 弹窗提示

        ######     获得detect表的全部内容       ######
        cur = conn.cursor()  # 创建光标
        # cur.execute("select * from Detect;")  # 执行SQL指令
        # results = cur.fetchall()  # 获取所有结果
        # conn.commit()
        ######       将数据写入UI               ######
        #mainWindow.init_table(results)

        stats.login.show()  # 登录界面显示
        sys.exit(app.exec_())  # 事件处理循环  要不然程序一闪而过  死循环

