# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
#from plot import PlotCanvas
import pyqtgraph as pg
import numpy as np
import threading
import time
from interval import Interval
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QVBoxLayout, QWidget, QMessageBox, QFileDialog
import queue
import ctypes
from usb3 import *
from PyQt5.QtCore import QThread, pyqtSignal
import os.path
from numpy import fft
import multiprocessing as mp


global fd_usb


class message(QThread):
    signal = pyqtSignal()
    def __init__(self, Window):
        super(message, self).__init__()
        self.window = Window

    def run(self):
        self.signal.emit()


class Ui_MainWindow(object):
    item = [{'handle': None, 'x': 30, 'y': 50, 'cmd': CMD_SET_TX_FREQ, 'default': '1234e6',
            'text': "发送频率(Hz)\n70MHz~6GHz", 'entry': None},
            {'handle': None, 'x': 30, 'y': 110, 'cmd': CMD_SET_TX_BANDWIDTH, 'default': '5e6',
            'text': "发送带宽(HZ)\n200KHz~56MHz", 'entry': None},
            {'handle': None, 'x': 30, 'y': 170, 'cmd': CMD_SET_TX_GAIN, 'default': '10',
            'text': "发送衰减(dB)\n0~89dB", 'entry': None},

            {'handle': None, 'x': 30, 'y': 260, 'cmd': CMD_SET_RX_FREQ, 'default': '915e6',
            'text': "接收频率(Hz)\n70MHz~6GHz", 'entry': None},
            {'handle': None, 'x': 30, 'y': 320, 'cmd': CMD_SET_RX_BANDWIDTH, 'default': '5e6',
            'text': "接收带宽(Hz)\n200KHz~56MHz", 'entry': None},
            {'handle': None, 'x': 30, 'y': 380, 'cmd': CMD_SET_RX_GAIN, 'default': '10',
            'text': "接收增益(dB)\n1~71dB", 'entry': None},   

            {'handle': None, 'x': 30, 'y': 470, 'cmd': CMD_SET_SAMPLERATE, 'default': '20e6',
            'text': "采样率(HZ)\n2.5MHz~40MHz", 'entry': None},            
            {'handle': None, 'x': 30, 'y': 530, 'cmd': CMD_SET_MODE,
            'text': "收发模式", 'combo': ["发送", "接收", "停止", "双工"], "default": 3},
            {'handle': None, 'x': 30, 'y': 590, 'cmd': CMD_SET_CHANNEL,
            'text': "通道选择", 'combo': ["1", "2", "4"], "default": 0}]    


    def setupUi(self, MainWindow, qCmd, qSend, qRecv):  
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 900)
        #_translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle("OSDR控制面板")     

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)       

        self.cmd = qCmd
        self.send = qSend
        self.recv = qRecv

        for i in self.item:
            label = QtWidgets.QLabel(MainWindow)
            label.setText(i["text"])            
            label.setGeometry(QtCore.QRect(i['x'], i['y'], 110, 60))
            label.setFont(font)

            if ('entry' in i):
                lineEdit = QtWidgets.QLineEdit(MainWindow)
                lineEdit.setText(i['default'])
                lineEdit.setGeometry(QtCore.QRect(i['x']+120, i['y']+15, 160, 20))
                lineEdit.setFont(font)
                i['handle'] = lineEdit

            elif ('scale' in i):
                i["label"] = QtWidgets.QLabel(MainWindow)
                i["label"].setText("15")            
                i["label"].setGeometry(QtCore.QRect(i['x']+260, i['y']+15, 20, 20))
                i["label"].setFont(font)                

                i["handle"] = QtWidgets.QSlider(MainWindow)
                i["handle"].setGeometry(QtCore.QRect(i['x']+120, i['y']+15, 130, 20))
                i["handle"].setOrientation(QtCore.Qt.Horizontal)
                i["handle"].setMaximum(i['scale'][1])
                i["handle"].setSingleStep(i['scale'][2])
                i["handle"].setTickPosition(QtWidgets.QSlider.TicksAbove)                
                i["handle"].setFont(font)
                #i["handle"].valueChanged.connect(lambda: self.onSliderChange(i["handle"], i["lable"]))

            elif ('combo' in i):
                comboBox = QtWidgets.QComboBox(MainWindow)
                comboBox.setGeometry(QtCore.QRect(i['x']+120, i['y']+15, 160, 20))
                comboBox.setObjectName("comboBox")
                for s in i['combo']:
                    comboBox.addItem(s)           
                comboBox.setCurrentIndex(i["default"])
                comboBox.setFont(font)
                i["handle"] = comboBox     

        self.button_set = QtWidgets.QPushButton(MainWindow)
        self.button_set.setGeometry(QtCore.QRect(210, 660, 100, 30))
        self.button_set.setText("设置")
        self.button_set.setFont(font)
        self.button_set.clicked.connect(self.onclick_set)

        label = QtWidgets.QLabel(MainWindow)
        label.setText("长度")
        label.setGeometry(QtCore.QRect(30, 710, 30, 30))
        label.setFont(font)

        self.lineEdit_size = QtWidgets.QLineEdit(MainWindow)
        self.lineEdit_size.setText("16384")
        self.lineEdit_size.setGeometry(QtCore.QRect(70, 710, 60, 30))
        self.lineEdit_size.setFont(font)   

        self.button_save = QtWidgets.QPushButton(MainWindow)
        self.button_save.setGeometry(QtCore.QRect(140, 710, 60, 30))
        self.button_save.setText("保存波形")
        self.button_save.setFont(font)
        self.button_save.clicked.connect(self.onclick_save)         

        self.button_recv = QtWidgets.QPushButton(MainWindow)
        self.button_recv.setGeometry(QtCore.QRect(210, 710, 100, 30))
        self.button_recv.setText("接收")
        self.button_recv.setFont(font)
        self.button_recv.clicked.connect(self.onclick_recv)

        self.lineEdit_file = QtWidgets.QLineEdit(MainWindow)
        self.lineEdit_file.setText(" ")
        self.lineEdit_file.setGeometry(QtCore.QRect(30, 760, 100, 30))
        self.lineEdit_file.setFont(font)     

        self.button_file = QtWidgets.QPushButton(MainWindow)
        self.button_file.setGeometry(QtCore.QRect(140, 760, 60, 30))
        self.button_file.setText("选择文件")
        self.button_file.setFont(font)
        self.button_file.clicked.connect(self.onclick_file)

        self.button_send = QtWidgets.QPushButton(MainWindow)
        self.button_send.setGeometry(QtCore.QRect(210, 760, 100, 30))
        self.button_send.setText("发送")
        self.button_send.setFont(font)
        self.button_send.clicked.connect(self.onclick_send)

        self.label_state = QtWidgets.QLabel(MainWindow)
        self.label_state.setText("OSDR未连接")            
        self.label_state.setGeometry(QtCore.QRect(30, 810, 350, 30))
        self.label_state.setFont(font)        

        self.fig = plt.Figure()
        self.canvas = FC(self.fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.widget = QtWidgets.QWidget(MainWindow)
        self.widget.setGeometry(QtCore.QRect(350, 50, 1200, 800))
        self.widget.setObjectName("widget")
        self.widget.setLayout(layout)

        self.message_str = None
        self.message = message(self)
        self.message.signal.connect(self.ui_message_show)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    # 通过信号槽让非UI线程也可调用QMessageBox
    def ui_message_show(self):
        QMessageBox(QMessageBox.Warning, "OSDR控制面板", self.message_str).exec_()


    def ui_message(self, str):
        self.message_str = str
        self.message.start()


    def ui_button(self, param):
        if ("s_str" in param):
            self.button_send.setText(param["s_str"])
        if ("s_state" in param):
            self.button_send.setEnabled(param["s_state"])
        if ("r_str" in param):
            self.button_recv.setText(param["r_str"])
        if ("r_state" in param):
            self.button_recv.setEnabled(param["r_state"])
        if ("sa_str" in param):
            self.button_save.setText(param["sa_str"])
        if ("sa_state" in param):
            self.button_save.setEnabled(param["sa_state"])
        if ("state" in param):
            self.button_set.setEnabled(param["state"])
        elif ((self.button_send.text() == "发送") and (self.button_recv.text() == "接收")):
            self.button_set.setEnabled(True)


    def onclick_set(self):
        # 强制刷新
        #QtWidgets.QApplication.processEvents()
        self.ui_button({"state": False, "s_state": False, "r_state": False})
        #self.cmd.put("set param")

        try:
            arr = []
            
            for i in ui.item:
                # 添加识别符
                if ('entry' in i):
                    str = i['handle'].text()
                    data = int(float(str))
                elif ('scale' in i):
                    str = i['handle'].value()
                    data = int(float(str))     
                elif ('combo' in i):
                    str = i['handle'].currentIndex()
                    data = int(float(str))

                param = {"cmd": i["cmd"], "data": data, "text": i["text"]}
                arr.append(param)
            """
            i = ui.item[6]
            str = i['handle'].text()
            data = int(float(str))  
            param = {"cmd": i["cmd"], "data": data, "text": i["text"]}
            arr.append(param)
            """
            self.cmd.put(arr)
        except ValueError:
            ui.ui_message(i['text'] + "\r\n无效字符: " + str)
            ui.ui_button({"state": True, "s_state": True, "r_state": True})      


    def onclick_save(self):
        path = QFileDialog.getSaveFileName(None, "保存波形", "./", 
                                           "Bin Files (*.bin);;All Files (*)") 
        print(path) 
        self.recv.put({"cmd": "save", "data": path[0]})        

    def onclick_recv(self):
        if (self.button_recv.text() == "接收"):
            self.ui_button({"state": False, "sa_state": False, 
                            "r_state": False, "r_str": "停止接收"})
            # 接收长度
            str = self.lineEdit_size.text()
            self.recv.put({"cmd": "start", "data": str})
        else:
            self.ui_button({"state": False, "r_state": False, "r_str": "接收"})
            self.recv.put({"cmd": "stop", "data": None})      

    def onclick_file(self):
        path = QFileDialog.getOpenFileName(None, "选择发送文件","./",
                                           "Bin Files (*.bin);;All Files (*)") 
        print(path)
        self.lineEdit_file.setText(path[0])

    def onclick_send(self):
        if (self.button_send.text() == "发送"):
            self.ui_button({"state": False, "s_state": False, "s_str": "停止发送"})
            self.send.put({"cmd": "start", "data": self.lineEdit_file.text()})
        else:
            self.ui_button({"state": False, "s_state": False, "s_str": "发送"})
            self.send.put({"cmd": "stop", "data": None})      


    def update_plot(self, arr):
        try:
            ax = self.fig.add_subplot(211)
            ax.cla() # 清空
            ax.plot(arr[::2])

            ax = self.fig.add_subplot(212)
            ax.cla()
            ax.plot(arr[1::2])            

            self.canvas.draw() # 绘制
        
        except Exception as e:
            #print(e)
            pass


def ui_set_thread(u_queue, c_queue):
    global fd_usb
    state = True

    while (True):
        time.sleep(0.01)
        try:
            arr = c_queue.get()

            state = True
            for i in arr:
                result = usb3_set_param(fd_usb, i["cmd"], i["data"])
                if (result["code"] != 0):
                    u_queue.put({"cmd": "msg", "data": i["text"] + "\r\n" + result["err"]})
                    state = False                
                    break                

            if (state):
                u_queue.put({"cmd": "msg", "data": "设置成功"})
            # 恢复按钮状态 
            u_queue.put({"cmd": "btn", "data": {"state": True, "s_state": True, "r_state": True}}) 

        except Exception as err:
            print("set cmd error:" + str(err))
            pass

def ui_send_thread(u_queue, s_queue):
    global fd_usb
    send = False
    a_len = 0

    while(True):
        time.sleep(0.01)
        try:
            operate = s_queue.get_nowait()
            print(operate)
            if ("cmd" in operate):
                cmd = operate["cmd"]
                print(cmd)
                if (cmd == "start"):
                    # 读取文件，将文件内容存入数组
                    f_path = operate["data"]
                    if (os.path.isfile(f_path)):
                        print(f_path)
                        f_obj = open(f_path, "rb")
                        f_data = f_obj.read()
                        #print(f_data)
                        f_obj.close()
                        a_len = 0
                        #ui.ui_button({"s_state": True})
                        send = True
                    else:
                        u_queue.put({"cmd": "msg", "data": "文件不存在： " + f_path})
                        u_queue.put({"cmd": "btn", "data": {"s_state": True, "s_str": "发送"}})

                elif (cmd == "stop"):
                    u_queue.put({"cmd": "btn", "data": {"s_state": True, "s_str": "发送"}})               
                    send = False
        except Exception as e:
            #print("usb send thread error !" + str(e))
            pass                    
            
        if (send):
            # 保持连续传输
            if (a_len == 0):
                a_len = len(f_data)
                print("len = ", a_len)
                a_data = bytearray(f_data)
            # 每次传输后，a_data的指针位置会自动增加
            result = usb3_write(fd_usb, str(a_data), a_len)
            #result = {"cnt": 10}
            if (result["cnt"] > 0):
                a_len -= result["cnt"]
                # 最好只设置一次，待修改
                u_queue.put({"cmd": "btn", "data": {"s_state": True}})
            else:
                # 发送长度为0，表示发送失败
                send = False
                print(result["err"])
                u_queue.put({"cmd": "msg", "data": "数据发送错误\r\n" + result["err"]})
                u_queue.put({"cmd": "btn", "data": {"s_state": True, "s_str": "发送"}})


def ui_recv_thread(u_queue, r_queue):
    global fd_usb
    recv = False
    u_buf = None
    u_len = 0
    u_cnt = 0
    s_buf = None

    while(True):
        time.sleep(0.01)
        try:
            operate = r_queue.get_nowait()
            if ("cmd" in operate):
                cmd = operate["cmd"]
                print(cmd)
                if (cmd == "start"):
                    try:
                        str = operate["data"]
                        u_len = int(str)
                        if (u_len in Interval(0, 999999)):
                            u_cnt = u_len
                            u_buf = None
                            s_buf = None
                            recv = True
                            u_queue.put({"cmd": "btn", "data": {"r_state": True}})
                            continue
                        else:
                            u_queue.put({"cmd": "msg", "data": "长度超出范围：0 ~ 999999"})
                    except ValueError:
                        u_queue.put({"cmd": "msg", "data": "长度无效字符：" + str})

                    u_queue.put({"cmd": "btn", "data": {"r_state": True, "r_str": "接收", "sa_state": True}})
                    
                elif (cmd == "stop"):
                    u_queue.put({"cmd": "btn", "data": {"r_state": True, "r_str": "接收", "sa_state": True}})
                    recv = False
                elif (cmd == "save"):
                    if (type(s_buf) == np.ndarray):
                        f_path = operate["data"]
                        f_obj = open(f_path, "wb")
                        f_obj.write(s_buf)
                        f_obj.close()
                    else:
                        u_queue.put({"cmd": "msg", "data": "未收到数据或数据长度不足"})

        except Exception as err:
            #print("usb recv thread error: " + err)
            pass

        if (recv):
            if (u_cnt > 16384):
                t_len = 16384
            else:
                t_len = u_cnt
            t_buf = ctypes.c_buffer(t_len)            
            result = usb3_read(fd_usb, t_buf, t_len)
            t_len = result["cnt"]
            print(t_len)
            if (t_len > 0):
                t_buf = t_buf[0 : t_len]
                if (type(u_buf) == np.ndarray):
                    u_buf = np.concatenate((u_buf, np.frombuffer(t_buf, dtype=np.int8)))
                else:
                    u_buf = np.frombuffer(t_buf, dtype=np.int8)

                u_cnt -= t_len
                if (u_cnt == 0):
                    u_cnt = u_len
                    #s_buf = u_buf
                    #u_buf = None
                    # 发给ui线程前确保队列为空，因为usb接收的速度远大于ui显示速度
                    if (u_queue.empty()):
                        s_buf = u_buf
                        u_queue.put({"cmd": "plot", "data": s_buf})
                        
                    u_buf = None
                #u_queue.put({"cmd": "btn", "data": {"r_state": True}})
            else:
                # 传输长度为0，说明传输失败
                # 清除波形
                recv = False
                print(result["err"])
                u_queue.put({"cmd": "msg", "data": "数据接收错误\r\n" + result["err"]})
                u_queue.put({"cmd": "btn", "data": {"r_state": True, "r_str": "接收", "sa_state": True}})


def ui_usb_thread(u_queue):
    global fd_usb
    fd_usb = None
    while (True):
        time.sleep(0.01)
        if (fd_usb == None):
            result = usb3_detect()
            #print(result)
            fd_usb = result["fd"]
            u_queue.put({"cmd": "conn", "data": result["error"]})
            continue


def ui_thread(ui, queue):
    while (True):
        try:
            #time.sleep(0.1)
            #operate = queue.get_nowait()
            operate = queue.get()
            if ("cmd" in operate):
                cmd = operate["cmd"]
                #print(operate)
                if (cmd == "msg"):
                    ui.ui_message(operate["data"])
                elif (cmd == "btn"):
                    ui.ui_button(operate["data"])
                elif (cmd == "conn"):
                    ui.label_state.setText(operate["data"])
                elif (cmd == "plot"):
                    buf = operate["data"]
                    #queue.put({"cmd": "wait"})
                    ui.update_plot(buf)

        except Exception as err:
            pass


def usb_process(c_queue, s_queue, r_queue, u_queue):
    thread_ui_set = threading.Thread(target = ui_set_thread, args = (u_queue, c_queue))
    thread_ui_set.start()    

    thread_ui_send = threading.Thread(target = ui_send_thread, args = (u_queue, s_queue))
    thread_ui_send.start()   

    thread_ui_recv = threading.Thread(target = ui_recv_thread, args = (u_queue, r_queue))
    thread_ui_recv.start()   
    
    thread_ui_usb = threading.Thread(target = ui_usb_thread, args = (u_queue,))
    thread_ui_usb.start()       


if __name__ == "__main__":
    c_queue = mp.Queue()
    s_queue = mp.Queue()
    r_queue = mp.Queue()
    u_queue = mp.Queue()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, c_queue, s_queue, r_queue)
    MainWindow.show()

    thread_ui = threading.Thread(target = ui_thread, args = (ui, u_queue))
    thread_ui.start()
    
    process_usb = mp.Process(target = usb_process, args=(c_queue, s_queue, r_queue, u_queue))
    process_usb.start()
    """
    process_usb = threading.Thread(target = usb_process, args=(c_queue, s_queue, r_queue, u_queue))
    process_usb.start()
    """
    app.exec_()

