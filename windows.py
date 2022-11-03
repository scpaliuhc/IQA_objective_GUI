import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle
import PIL.Image as Image
import numpy as np

class ObWindow(QtWidgets.QMainWindow):    
    def __init__(self,ui):
        """构造函数"""
        super().__init__()
        self.ui=ui
        self.ui.setupUi(self)
        self.setWindowTitle('Objective Score')        
        self.time = QTimer(self)
        self.time.setInterval(1000)
        self.newWin=None

        self.init_Signal_Slot()
        self.cur_score = -1
        self.ref_imgPixmap = QPixmap('Not Exsit')
        self.other_imgPixmap = QPixmap('Not Exsit')
        self.size_step=10 
        self.isLeftPressed=False
        self.isMoving=False      
        
    def load_breakpoints(self):
        try:
            with open('breakpoint', 'rb') as f:
                breakpoint=pickle.load(f)
            self.global_dic,self.current_ref,self.current_ae,self.root_path=breakpoint
        except:
            self.global_dic,self.current_ref,self.current_ae,self.root_path=None,None,None,None
        try:
            if self.global_dic is not None:
                self.ref_keys=list(self.global_dic.keys())
                self.ae_keys=list(self.global_dic[self.ref_keys[self.current_ref]].keys())
                self.load_pic()
        except:
            msg_box = QMessageBox.warning(self, '警告', '请先删除breakpoint')



    def init_Signal_Slot(self):
        self.radio_btn_list = [self.ui.radioButton_1, self.ui.radioButton_2, self.ui.radioButton_3, self.ui.radioButton_4, self.ui.radioButton_5, self.ui.radioButton_6, self.ui.radioButton_7, self.ui.radioButton_8, self.ui.radioButton_9, self.ui.radioButton_10, self.ui.radioButton_11]
        # for btn in self.radio_btn_list:
        #     btn.clicked.connect(self.rb_press)
        self.ui.openButton.clicked.connect(self.open)
        self.ui.nextButton.clicked.connect(self.next)
        self.ui.preButton.clicked.connect(self.pre)
        self.ui.confButton.clicked.connect(self.conf)
        self.time.timeout.connect(self.refresh)

    def refresh(self):
        if self.max_time>=0:
            self.ui.time_label.setText(f'{self.max_time} s')
            self.max_time-=1
            if self.max_time<0:
                root,ref,method,ae=self.root_path,self.ref_keys[self.current_ref],self.ae_keys[self.current_ae].split('_')[2],self.ae_keys[self.current_ae]
                ref=np.array(Image.open(os.path.join(root,'ref',ref)))
                ae=np.array(Image.open(os.path.join(root,'ae',method,ae)))
                diff_pic=ae-ref
                # diff_pic=diff_pic+np.abs(np.min(diff_pic))
                diff_pic=diff_pic.astype(np.uint8)
                

                if self.newWin is None:
                    self.newWin=DiffWindow(diff_pic,self.img_size_ini.width(), self.img_size_ini.height())
                elif self.newWin.isVisible():
                    self.newWin.close()
                    self.newWin=DiffWindow(diff_pic,self.img_size_ini.width(), self.img_size_ini.height())
                self.newWin.show()
                self.newWin.move(self.diff_location_x,self.diff_location_y)
                self.newWin.exec_()
        else:
            self.time.stop()
    
    def timer_schedule(self):
        self.max_time=4
        self.time.stop()
        self.time.start()  
    
    def load_pic(self):
        method=self.ae_keys[self.current_ae].split('_')[2]
        self.load_pic_core(self.root_path,self.ref_keys[self.current_ref],method,self.ae_keys[self.current_ae])
        self.repaint()
        
        self.update_status_bar()
    
    def load_pic_core(self,root,ref,method,ae):
        try:
            print('加载图片：',ref,ae)
            self.ref_imgPixmap = QPixmap(os.path.join(root,'ref',ref))
        except:
            self.ref_imgPixmap = QPixmap('Not Exsit')
            
        try:
            self.other_imgPixmap = QPixmap(os.path.join(root,'ae',method,ae))
        except:
            self.other_imgPixmap = QPixmap('Not Exsit')

    def open(self):
        self.root_path = QtWidgets.QFileDialog.getExistingDirectory(self, "请选择文件夹路径", os.getcwd())
        self.global_dic={}
        try:
            for file in os.listdir(os.path.join(self.root_path,'ref')):
                self.global_dic[file] = {}
        except:
            msg_box = QMessageBox.warning(self, '警告', '未在该目录中发现ref文件夹!')
            return 
        
        try:
            for method in os.listdir(os.path.join(self.root_path,'ae')):
                for file in os.listdir(os.path.join(self.root_path,'ae',method)):
                    splits=file.split('_')
                    ref_name=f'{splits[0]}_{splits[1]}.png'
                    self.global_dic[ref_name][file]=-1
        except:
            msg_box = QMessageBox.warning(self, '警告', '未在该目录中发现ae文件夹!')
            return 
        self.current_ref,self.current_ae=0,0
        self.ref_keys=list(self.global_dic.keys())
        self.ae_keys=list(self.global_dic[self.ref_keys[self.current_ref]].keys())
        self.load_pic()

    def update_status_bar(self):
        self.ui.ref_label.setText(f"{self.current_ref+1}/{len(self.global_dic.keys())}") 
        self.ui.ae_label.setText(f"{self.current_ae+1}/{len(self.ae_keys)}") 
        score=self.global_dic[self.ref_keys[self.current_ref]][self.ae_keys[self.current_ae]]
       
        if score > -1:
            self.radio_btn_list[int((1-score)*10)].setChecked(True)
            self.ui.status_label.setText('True')
        else:
            for btn in self.radio_btn_list:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
                btn.setAutoExclusive(True)
            self.ui.status_label.setText('False')
    
    def next(self):
        #update self.current_ref、self.current_ae、self.ae_keys
        if self.current_ae<len(self.ae_keys)-1:
            self.current_ae+=1
        else:
            if self.current_ref<len(self.global_dic.keys())-1:
                self.current_ae=0
                self.current_ref+=1
                self.ae_keys=list(self.global_dic[self.ref_keys[self.current_ref]].keys())
            else:
                #遍历完
                msg_box = QMessageBox.warning(self, '警告', '已是最后一张!')
                self.save_scores()
        self.load_pic()    
    
    def pre(self):
        if self.current_ae >= 1:
            self.current_ae -= 1
        else:
            if self.current_ref >= 1:
                self.current_ref -= 1
                self.ae_keys=list(self.global_dic[self.ref_keys[self.current_ref]].keys())
                self.current_ae = len(self.ae_keys)-1
                
            else:
                #遍历完
                msg_box = QMessageBox.warning(self, '警告', '已是第一张!')
        self.load_pic()
         
    def conf(self):
        score = [btn.text() for btn in self.radio_btn_list if btn.isChecked()][0]
        self.cur_score = float(score)
        self.global_dic[self.ref_keys[self.current_ref]][self.ae_keys[self.current_ae]]=self.cur_score
        self.next()
        self.timer_schedule()

    # def rb_press(self):
    def get_coordinates_size(self):
        x1=self.ui.topHL.geometry().x()
        y1=self.ui.topHL.geometry().y()
        w1=self.ui.topHL.geometry().width()
        h1=self.ui.topHL.geometry().height()

        x2=self.ui.scoresVL.geometry().x()
        y2=self.ui.scoresVL.geometry().y()
        w2=self.ui.scoresVL.geometry().width()
        h2=self.ui.scoresVL.geometry().height()

        self.img_h = y2-y1-h1-10
        self.img_w = (w1-10)//2
        self.ref_x_ini=x1
        self.ref_y_ini=y1+h1+5
        self.ref_start_ini=QPoint(self.ref_x_ini,self.ref_y_ini)
        self.other_x_ini=x1+self.img_w+10
        self.other_y_ini=y1+h1+5
        self.other_start_ini=QPoint(self.other_x_ini,self.other_y_ini)
        
        self.ref_start=QPoint(self.ref_x_ini,self.ref_y_ini)
        self.other_start=QPoint(self.other_x_ini,self.other_y_ini)
        self.img_size=QSize(self.img_w,self.img_h)
        self.img_size_ini=QSize(self.img_w,self.img_h)

        print('图片尺寸:',self.img_size_ini)

    
    def resizeEvent(self, event):
        self.get_coordinates_size()
        self.repaint()
        # self.repaint()

    def update_pic(self):
        self.ref_scaledImg = self.ref_imgPixmap.scaled(self.img_size)
        self.other_scaledImg = self.other_imgPixmap.scaled(self.img_size)
        self.imgPainter = QPainter()                   
        self.imgPainter.begin(self)          
        self.other_start=QPoint(self.ref_start.x()+self.img_w+10,self.ref_start.y())        
        self.update_pic_core(self.ref_start_ini,self.img_w,self.img_h,self.ref_start,self.ref_scaledImg,self.imgPainter) 
        self.update_pic_core(self.other_start_ini,self.img_w,self.img_h,self.other_start,self.other_scaledImg,self.imgPainter) 
        self.imgPainter.end() 
    
    def update_pic_core(self,ref_ini,img_w,img_h,start,img,imgPainter):
        rect =QRect(ref_ini.x(),ref_ini.y(),img_w,img_h)
        imgPainter.setPen(QPen(QtCore.Qt.red,3,QtCore.Qt.SolidLine))
        imgPainter.drawRect(rect)
        x=start.x() if start.x()>ref_ini.x() else ref_ini.x()
        y=start.y() if start.y()>ref_ini.y() else ref_ini.y()
        off_x=ref_ini.x()-start.x() if start.x()<ref_ini.x() else 0
        off_y=ref_ini.y()-start.y() if start.y()<ref_ini.y() else 0
        imgPainter.drawPixmap(QPoint(x,y), img.copy(QRect(off_x,off_y,img_w+ref_ini.x()-x,img_h+ref_ini.y()-y)))

    def paintEvent(self,event):
        self.update_pic()

        self.diff_location_x=self.geometry().x()+self.geometry().width()+10
        self.diff_location_y=self.geometry().y()
        
    
    def save_scores(self):
        with open('breakpoint', 'wb') as f:
            pickle.dump([self.global_dic,self.current_ref,self.current_ae,self.root_path],f)

    def closeEvent(self, event):
        self.save_scores()
        if self.newWin is not None:
            if self.newWin.isVisible():
                self.newWin.close()
        return super().closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: 
            print('左键按下') 
            self.isLeftPressed = True;                 
            self.preMousePosition = event.pos()
        if event.button() == QtCore.Qt.RightButton:  
            print('右键按下') 
            self.isLeftPressed = True;                 
            self.preMousePosition = event.pos()     
    
    def wheelEvent(self, event):
        angle=event.angleDelta()   
        angleX=angle.x()         
        angleY=angle.y()         
        if angleY > 0:           
            self.img_size=QSize(self.ref_scaledImg.width()+self.size_step,self.ref_scaledImg.height()+self.size_step)
            newWidth = event.x() - (self.ref_scaledImg.width() * (event.x()-self.ref_start.x())) / (self.ref_scaledImg.width()-self.size_step/2)
            newHeight = event.y() - (self.ref_scaledImg.height() * (event.y()-self.ref_start.y())) / (self.ref_scaledImg.height()-self.size_step/2)
            self.ref_start = QPoint(newWidth, newHeight)                   
            newWidth = event.x() - (self.other_scaledImg.width() * (event.x()-self.other_start.x())) / (self.other_scaledImg.width()-self.size_step/2)
            newHeight = event.y() - (self.other_scaledImg.height() * (event.y()-self.other_start.y())) / (self.other_scaledImg.height()-self.size_step/2)
            self.other_start = QPoint(newWidth, newHeight)                    
            self.repaint()       
        else:                    

            self.img_size=QSize(self.ref_scaledImg.width()-self.size_step,self.ref_scaledImg.height()-self.size_step)
            newWidth = event.x() - (self.ref_scaledImg.width() * (event.x()-self.ref_start.x())) / (self.ref_scaledImg.width()+self.size_step/2)
            newHeight = event.y() - (self.ref_scaledImg.height() * (event.y()-self.ref_start.y())) / (self.ref_scaledImg.height()+self.size_step/2)
            self.ref_start = QPoint(newWidth, newHeight)                   
            newWidth = event.x() - (self.other_scaledImg.width() * (event.x()-self.other_start.x())) / (self.other_scaledImg.width()+self.size_step/2)
            newHeight = event.y() - (self.other_scaledImg.height() * (event.y()-self.other_start.y())) / (self.other_scaledImg.height()+self.size_step/2)
            self.other_start = QPoint(newWidth, newHeight)                    
            self.repaint()       
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: 
            print('左键松开')     
            self.isLeftPressed = False;  
        elif event.button() == QtCore.Qt.RightButton:          
            self.img_size=QSize(self.img_w,self.img_h)
            self.ref_start = QPoint(self.ref_x_ini, self.ref_y_ini)
            self.other_start = QPoint(self.other_x_ini, self.other_y_ini)
            self.repaint()
            print("右键松开")  # 响应测试语句
    
    def mouseMoveEvent(self,event):
        print('鼠标移动')
        if self.isLeftPressed:   
            self.endMousePosition = event.pos() - self.preMousePosition        
            self.ref_start = self.ref_start + self.endMousePosition      
            self.preMousePosition = event.pos()         
            self.repaint()    

    def keyPressEvent(self, event):
        if event.key() == 16777220 or event.key() == 16777221: ## conf
            try:
                self.conf()
            except:
                msg_box = QMessageBox.warning(self, '警告', '先选择分数!')
        elif event.key() == 65: ##pre
            self.pre()
        elif event.key() == 68: ##next
            self.next()
        elif event.key() == 46: # . 代表1
            self.radio_btn_list[0].setChecked(True)
        elif event.key() >=48 and event.key()<=57: ##0至0.9
            self.radio_btn_list[58-event.key()].setChecked(True)

class DiffWindow(QDialog):                            
    def __init__(self,pic,w,h):
        super(DiffWindow, self).__init__()
        self.resize(w,h)                                                   
        self.setWindowTitle("Diff Img")     
        self.isLeftPressed = bool(False)                                       
        self.isImgLabelArea = bool(True)                                      
        self.diff_pic=pic
        self.curr_scale_idx=0
        self.scales=[1,5,10,20,30]
        self.pic2qpixmap(self.diff_pic,self.scales[self.curr_scale_idx])

    def pic2qpixmap(self,pic,scaled=1):     
        pic=pic*scaled
        pic=Image.fromarray(pic)
        r, g, b = pic.split()
        pic = Image.merge("RGB", (b, g, r))
        tmp = pic.convert("RGBA")
        tmp = tmp.tobytes("raw", "RGBA")
        qim  = QtGui.QImage(tmp, pic.size[0], pic.size[1], QtGui.QImage.Format_ARGB32)
        self.imgPixmap = QPixmap.fromImage(qim)
        self.scaledImg = self.imgPixmap.scaled(self.size()) 
        self.singleOffset = QPoint(0, 0)     
        self.setWindowTitle(f"Diff Img x{scaled}")              

    def paintEvent(self,event):
        self.imgPainter = QPainter()                                           
        self.imgFramePainter = QPainter()                                      
        self.imgPainter.begin(self)                                            
        self.imgPainter.drawPixmap(self.singleOffset, self.scaledImg)          
        self.imgPainter.end()       
 
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:                             
            self.isLeftPressed = True;                                         
            self.preMousePosition = event.pos()                                
        
    def wheelEvent(self, event):
        angle=event.angleDelta() / 8                                           
        angleX=angle.x()                                                       
        angleY=angle.y()                                                       
        if angleY > 0:                                                        
            self.curr_scale_idx = self.curr_scale_idx+1 if self.curr_scale_idx < len(self.scales)-1 else len(self.scales)-1                                           
        else:                                                                  
            self.curr_scale_idx = self.curr_scale_idx-1 if self.curr_scale_idx>1 else 0
        self.pic2qpixmap(self.diff_pic,self.scales[self.curr_scale_idx])                     
        self.repaint()                                                     
            

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:                            
            self.isLeftPressed = False;  
        elif event.button() == QtCore.Qt.RightButton:                                
            self.singleOffset = QPoint(0, 0)                                   
            self.scaledImg = self.imgPixmap.scaled(self.size())                
            self.repaint()                                                     

    def mouseMoveEvent(self,event):
        if self.isLeftPressed:                                                 
            self.endMousePosition = event.pos() - self.preMousePosition        
            self.singleOffset = self.singleOffset + self.endMousePosition     
            self.preMousePosition = event.pos()                                
            self.repaint()                                                    
    def keyPressEvent(self, event):
        print(event.key())
        if event.key() == 16777216:
            self.closeEvent(None)
