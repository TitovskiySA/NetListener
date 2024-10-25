#!/usr/bin/env python
#-*- coding: utf-8 -*-
#ver 27/11/2023

import socket
#import json
import pickle
import sys
import os
#import string # for buttons
#from pygame.locals import *
import wx
from wx.adv import TaskBarIcon as TaskBarIcon
from wx.adv import SplashScreen as SplashScreen
import wx.lib.buttons as buttons
import wx.aui # for throbber
import wx.lib.throbber # for throbber
from pubsub import pub
import threading
from threading import Thread
import time
import datetime  # импорт библиотеки дат и времени
from datetime import datetime, timedelta
import locale
import queue # для очередей потоков
import pyaudio # for work with sound stream
import wave # for work with wav files
import pythonping # для пинга
from pythonping import ping # для пинга
import queue
import struct #for trnsiving bytes

#should only require hiddenimports
#datas = collect_data_files('pyaudio')
#hiddenimports = collect_submodules('pyaudio')


#===========================================================================
# Main Window
class MainWindow(wx.Frame):

    # задаем конструктор
    def __init__(self, parent):
        #self.SizeWin = (310, 60)
    
        # создаем стиль окна без кнопок закрытия и тд
        styleWindow = (
            wx.MINIMIZE_BOX|
            wx.MAXIMIZE_BOX|
            wx.RESIZE_BORDER|
            wx.CAPTION|
            wx.SYSTEM_MENU|
            wx.CLOSE_BOX|
            wx.CLIP_CHILDREN
            )

        #задаем обращение к параметрам родительского класса (чтобы не создавать их заново)
        super().__init__(
            parent,
            title = "NetListener Server ver 0.1",
            #size = self.SizeWin,
            style = styleWindow)
        #------------------------------------------------------------------------------
        #задаем иконку
        frameIcon = wx.Icon(os.getcwd() + "\\images\\banner_server.png")
        self.SetIcon(frameIcon)

        #Creating thread for saving logs
        thr = LogThread()
        thr.setDaemon(True)
        thr.start()
            
        self.panel = MainPanel(self)
        #self.Center()
        self.Fit()
        self.Layout()
        self.Show(True)

#=======================================
#=======================================
#=======================================
#=======================================
# panel
class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent = parent)
        #Image on Background
        self.frame = parent
        self.SetBackgroundColour(wx.Colour("#bfdee8"))

        #Here's loading last config and announcing
        self.Preparing()

        #Here's creating panel
        self.CreatePanel()

    #-----------------------------------------------------------
    def CreatePanel(self):
        global MyDir
        self.CommonVbox = CommonVbox = wx.FlexGridSizer(rows = 1, cols = 6, hgap = 6, vgap = 6)
        CommonVbox.AddGrowableRow(0, 1)
        for col in range (0, 6):
            CommonVbox.AddGrowableCol(col, 1)

        #-------------------------------------------------------------
        #Preparing Images for throbber
        ThrIm = [
            "thr_gray.png", "thr_blue.png", "thr_green.png",
            "thr_yellow.png", "thr_red.png", "thr_orange.png"]
        ButtonSize = (50, 50)
        ThrImage = []
        for Image in ThrIm:
            Im = wx.Image(MyDir + "\\images\\" + Image).ConvertToBitmap()
            ThrImage.append(ScaleBitmap(Im, ButtonSize))

        #Throbber
        self.Throb = wx.lib.throbber.Throbber(
            self, wx.ID_ANY, ThrImage, frames = len(ThrImage), frameDelay = 1)
        self.Throb.SetCurrent(3)
        self.Throb.SetToolTip("Клиент не подключен")
        #self.Throb.Bind(wx.EVT_LEFT_DCLICK, self.DClickThrob)
        self.Throb.Bind(wx.EVT_RIGHT_DOWN, self.RClickThrob)
        CommonVbox.Add(self.Throb, -1, wx.ALL, 2)

        #Images for btns
        Images = [
            "BtnRecOn.png", "BtnRecOff.png",
            "BtnConnectOn.png", "BtnConnectOff.png",
            "BtnSettings.png", "BtnLic.png",
            "BtnInfo.png", "BtnFade.png"]
        BMPs = []

        for Image in Images:
            Im = wx.Image(MyDir + "\\images\\" + Image).ConvertToBitmap()
            BMPs.append(ScaleBitmap(Im, ButtonSize))

        #Rec Btn
        self.RecBtn = ChangeClickThrob(
            self, [BMPs[0], BMPs[1], BMPs[7]], 3, 1, AnswerTime = 100)
        self.RecBtn.SetCurrent(0)
        self.RecBtn.SetToolTip("Запись выключена")
        self.RecBtn.Bind(wx.EVT_LEFT_DOWN, self.ClickedRec)
        self.RecBtn.SetSize(ButtonSize)

        #Connect Btn
        self.ConnectBtn = ChangeClickThrob(
            self, [BMPs[2], BMPs[3], BMPs[7]], 3, 1, AnswerTime = 100)
        self.ConnectBtn.SetCurrent(0)
        self.ConnectBtn.SetToolTip("Нет активных соединений")
        self.ConnectBtn.Bind(wx.EVT_LEFT_DOWN, self.ClickedConn)
        self.ConnectBtn.SetSize(ButtonSize)

        #SettingsBtn
        SetBtn = wx.BitmapButton(self, wx.ID_ANY, BMPs[4])
        SetBtn.SetToolTip("Окно настроек")
        SetBtn.Bind(wx.EVT_BUTTON, self.OpenSettings)
        SetBtn.SetMinSize(ButtonSize)

        #LicenceBtn
        LicBtn = wx.BitmapButton(self, wx.ID_ANY, BMPs[5])
        LicBtn.SetToolTip("Лицензия")
        LicBtn.Bind(wx.EVT_BUTTON, self.OpenLic)
        LicBtn.SetMinSize(ButtonSize)

        #InfoBtn
        InfoBtn = wx.BitmapButton(self, wx.ID_ANY, BMPs[6])
        InfoBtn.SetToolTip("Справка по работе с программой")
        InfoBtn.Bind(wx.EVT_BUTTON, self.OpenInfo)
        InfoBtn.SetMinSize(ButtonSize)

        CommonVbox.Add(self.RecBtn, 0, wx.ALL, 3)
        CommonVbox.Add(self.ConnectBtn, 0, wx.ALL, 3)
        CommonVbox.Add(SetBtn, 0, wx.ALL, 3)
        CommonVbox.Add(LicBtn, 0, wx.ALL, 3)
        CommonVbox.Add(InfoBtn, 0, wx.ALL, 3)
       
        #AllVbox.Add(CommonVbox, 0, wx.ALL, 0)    
        self.SetSizer(self.CommonVbox)
        self.Fit()

        # Добавляем слушателя
        pub.subscribe(self.UpdateDisplay, "UpdateMainWin")
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        #self.frame.Bind(wx.EVT_ICONIZE, self.OnMinimize)

#=====================================================================================
    #preparing different folders and peremennie
    def Preparing(self):
        
        # Creating folders
        global MyDir, RecordQueue, CurrentRecord
        folders = ["Logs", "MyProfiles", "MyRecords"]
        RecordQueue = queue.Queue()
        for folder in folders:
            try:
                if folder not in os.listdir(MyDir):
                    os.mkdir(folder)
            except Exception as Err:
                ToLog("Can't create " + folder + " folder because of = " + str(Err))

        # Clear old logs
        ClearLogs()
        
                          #self.Settings = [
        #               [MainPos],
        #               folder for records
        #               [(ip, password), (ip, password).....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds],
        #               ServerPort]
                     
        self.Settings = [
            [{100, 100}],
            MyDir + "\\MyRecords",
            [("192.168.1.1", "12345678")],
            [1024, pyaudio.paInt16, 1, 44100, 10],
            10001]
                
        #self.Log = " "
        #for POPUP menu
        self.ConnMenu = wx.NewIdRef(count = 1)
        self.AboutMenu = wx.NewIdRef(count = 1)
        
        #Loading last cfg
        self.LoadConfig(Auto = True)
        
        #Moving to pos
        try:
            self.frame.Move((int(self.Settings[0][0]), int(self.Settings[0][1])))
        except Exception as Err:
            ToLog("Error moving Main Window because of = " + str(Err))

        #starting stream
        self.CreateStream()
        
        #creating RecThread
        self.CreateThreads()
        
        return  
#===========================================================================================
    #coding format from string to pyadio format
    def StrCodeToAudio(self, data, ToAudio = True):
        try:
            self.dict1 = ["paFloat32", "paInt32", "paInt24", "paInt16",
                             "paInt8", "paUInt8", "paCustomFormat"]
            self.dict2 = [pyaudio.paFloat32, pyaudio.paInt32, pyaudio.paInt24,
                          pyaudio.paInt16, pyaudio.paInt8, pyaudio.paUInt8,
                          pyaudio.paCustomFormat]
            for i in range (0, len(self.dict1)):
                if ToAudio == True and data == self.dict1[i]:
                    print("Changed format from " + str(self.dict1[i]))
                    return self.dict2[i]
                if ToAudio == False and data == self.dict2[i]:
                    print("Changed format from " + str(self.dict2[i]))
                    return self.dict1[i]
                
        except Exception as Err:
            ToLog("Failed to code format str to audio, Error code = " + str(Err))
            raise Exception
            

#==================================================================================
    def DoLoad(self, evt):
        ToLog("Load button pressed")
        self.LoadConfig()
#==================================================================================
    def LoadConfig(self, Auto = False):
        #try opening last profile
        global MyDir
        try:
            if Auto == True:
                ToLog("AutoLoad function started")
                file = open(MyDir + "\\lastcfgsrv.cfg", "r")
            else:
                DialogLoad = wx.FileDialog(
                    self,
                    "Загрузить настройки профиля",
                    defaultDir = MyDir + "\\MyProfiles",
                    wildcard = "CFG files (*.cfg)|*cfg",
                    style = wx.FD_OPEN)
                if DialogLoad.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    Dir = DialogLoad.GetDirectory()
                    file = open(Dir + "\\" + DialogLoad.GetFilename(), "r")

            Strings = file.read().splitlines()
            print(str(Strings))
            file.close()

                           #self.Settings = [
        #               [MainPos],
        #               folder for records,
        #               [(ip, password), (ip, password).....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds],
        #               ServerPort]

            for String in Strings:
                String = String.split()
                print("string after Split = " + str(String))
                if String[0] == "MyPos":
                    self.Settings[0] = [String[1], String[2]]
                elif String[0] == "PathToRec":
                    self.Settings[1] = String[1]
                elif String[0] == "Server":
                    temp = (String[1], String[2])[:]
                    if self.Settings[2] == [("192.168.1.1", "12345678")]:
                        self.Settings[2] = [temp]
                    else:
                        self.Settings[2].append(temp)
                elif String[0] == "WAVformat":
                    self.Settings[3] = [int(String[1]), self.StrCodeToAudio(String[2]), int(String[3]), int(String[4]), int(String[5])]
                elif String[0] == "ServerPort":
                    if String[1].isdigit():
                        self.Settings[4] = int(String[1])
                    else:
                        ToLog("Error loading port in Server = " + str(temp) + ", port will be = 10001")
                        self.Settings[4] = 10001
                    
            ToLog("Succesfully loaded Settings:")
            for strings in self.Settings:
                ToLog("\t" + str(strings))

            #trying loaded path
            try:
                os.chdir(self.Settings[1])
            except Exception as Err:
                wx.MessageBox(
                    "При проверке пути для сохранения файлов аудиозаписи" +
                    "\nвозникла ошибка:" + "\n\n" + str(Err) +
                    "\n\nПуть для сохранения изменён на " +
                    MyDir + "\\MyRecords"," ", wx.OK)
                self.Settings[1] = MyDir + "\\MyRecords"

        except Exception as Err:
            ToLog("Failed to load config from file, Error code = " + str(Err))
            if Auto == True:
                self.Settings = [
                    [{100, 100}],
                    MyDir + "\\MyRecords",
                    [("192.168.1.1", "12345678")],
                    [1024, pyaudio.paInt16, 1, 44100, 10],
                    10001]
            raise Exception
                  
        return
#===============================================================================
    def DoSave(self, evt):
        ToLog("Save button pressed")
        self.SaveConfig()
#===============================================================================
    #save config
    def SaveConfig(self, Auto = False):
        global MyDir
        try:
            if Auto == True:
                ToLog("AutoSave function started")
                Dir = MyDir
                file = open(MyDir + "\\lastcfgsrv.cfg", "w")
            else:
                DialogSave = wx.FileDialog(
                    self,
                    "Сохранить настройки в профиль",
                    defaultDir = MyDir + "\\MyProfiles",
                    wildcard = "CFG files (*.cfg)|*cfg",
                    style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if DialogSave.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    try: 
                        UserPath = DialogSave.GetDirectory()
                        if DialogSave.GetFilename().find(".cfg") != -1:
                            file = open(UserPath + "\\" + DialogSave.GetFilename(), "w")
                        else:
                            file = open(UserPath + "\\" + DialogSave.GetFilename() + ".cfg", "w")
                    except Exception as Err:
                        ToLog("Ошибка при выборе папки профиля, код ошибки = " + str(Err))
                        self.WarningWin("Ошибка при выборе папки профиля, код ошибки = " + str(Err))
                        return

                           #self.Settings = [
        #               [MainPos],
        #               folder for records
        #               [(ip, password), (ip, password).....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds],
        #               ServerPort]


            MyPos = self.frame.GetPosition()
            print("dirsave = " + MyDir)
            
            file.write("MyPos " + str(MyPos[0]) + " " + str(MyPos[1]) + "\n")
            file.write("PathToRec " + str(self.Settings[1]) + "\n")
            for server in self.Settings[2]:
                file.write("Server " + str(server[0]) + " " +
                           str(server[1]) + "\n")
            file.write("WAVformat " + str(self.Settings[3][0]) + " " +
                       self.StrCodeToAudio(self.Settings[3][1], ToAudio = False) + " " +
                       str(self.Settings[3][2]) + " " + str(self.Settings[3][3]) +
                       " " + str(self.Settings[3][4]) + "\n")
            file.write("ServerPort " + str(self.Settings[4]))
            
            ToLog(
                "Saved params:\n\t" +
                "MyPos " + str(MyPos[0]) + " " + str(MyPos[1]) + "\n\t" +
                "PathToRec " + str(self.Settings[1]) + "\n\t" +
                "Servers " + str(self.Settings[2]) + "\n\t" +
                "WAVformat " + str(self.Settings[3][0]) + " " +
                self.StrCodeToAudio(self.Settings[3][1], ToAudio = False) + " " +
                str(self.Settings[3][2]) + " " + str(self.Settings[3][3]) +
                " " + str(self.Settings[3][4]) + "\n\t" +
                "ServerPort " + str(self.Settings[4]) + "\n")
            file.write("\n--------------------end of file--------------------" + "\n")
            file.close()

        except Exception as Err:
            ToLog("Ошибка при сохранении профиля, код ошибки = " + str(Err))
            self.WarningWin("Ошибка при сохранении профиля, код ошибки = " + str(Err))
            raise Exception
        return
#=======================================================================================
    #Licence
    def OpenLic(self, evt):
        global MyDate
        try:
            ToLog("License button pressed")
            LICENSE = (
                "Данная программа является свободным программным обеспечением\n"+
                "Вы вправе распространять её и/или модифицировать в соответствии\n"+
                "с условиями версии 2 либо по Вашему выбору с условиями более\n"+
                "поздней версии Стандартной общественной лицензии GNU, \n"+
                "опубликованной Free Software Foundation.\n"+
                "Подробнее Вы можете ознакомиться с лицензией по ссылке " +
                "https://www.gnu.org/licenses/gpl-3.0.html\n\n\n" + 
                "Эта программа создана в надежде, что будет Вам полезной, однако\n"+
                "на неё нет НИКАКИХ гарантий, в том числе гарантии товарного\n"+
                "состояния при продаже и пригодности для использования в\n"+
                "конкретных целях.\n"+
                "Для получения более подробной информации ознакомьтесь со \n"+
                "Стандартной Общественной Лицензией GNU.\n\n"+
                "Данная программа написана на Python\n\n"
                "Автор: Титовский С.А.\n" + "Дизайн: Наумов Н.А.\n\n" +
                "Версия 0.1 от " + MyDate)
            wx.MessageBox(LICENSE, "Лицензия", wx.OK)
        except Exception as Err:
            ToLog("Error in OpenLic func, Error code = " + str(Err))
            raise Exception
        return

#==============================================================================================
    def OpenInfo(self, event):
        ToLog("OpenInfo button pressed")
        try:
            path = os.path.realpath(self.MyDir + "\\info")
            os.startfile(path + "\\AboutServer.pdf")
        except Exception as Err:
            try:
                os.startfile(path)
            except Exception as Err:
                wx.MessageBox("Возникла ошибка при открытии папки со справкой", "Справка", wx.OK)
                ToLog("Ошибка показа справки с кодом = " + str(Err))
        return
    
#===========================================================================================
    #opening settings
    def OpenSettings(self, evt):
        try:
            ToLog("Open Settings Btn pressed")
            dlg = SettingDlg(label = "Сетевые настройки", path = self.Settings[1],
                             waveformat = [self.Settings[3][0], self.StrCodeToAudio(self.Settings[3][1], ToAudio = False),
                                           self.Settings[3][2], self.Settings[3][3], self.Settings[3][4]])
            if dlg.ShowModal() == wx.ID_OK:
                self.Settings[3] = [
                    int(dlg.Choices[0].GetStringSelection()),
                    self.StrCodeToAudio(dlg.Choices[1].GetStringSelection()),
                    int(dlg.Choices[2].GetStringSelection()),
                    int(dlg.Choices[3].GetStringSelection()),
                    int(dlg.Choices[4].GetStringSelection())]
                self.Settings[1] = dlg.DirText.GetValue()
                ToLog("New params of wav loaded, now settings:")
                for strings in self.Settings:
                    ToLog("\t" + str(strings))

                if self.RestartStream() == False:
                    ToLog("Error in dlg, Error code = " + str(Err))
                    wx.MessageBox(
                        "При загрузке настроек аудиозаписи возникла ошибка" +
                        "\n" + str(Err) + 
                        "\nПроверьте настройки аудиозаписи", " ", wx.OK)
                    
                self.OffThread(self.RecThread)
                self.RecThread.join()
                self.OffThread(self.ConnThread)
                self.ConnThread.join()
                self.CreateThreads()
                            
        except Exception as Err:
            ToLog("Failed to load wav settings, from frame, Error code = " + str(Err))
            #raise Exception
        
#=======================================================================================
    # Close Clicked
    def OnCloseWindow(self, evt):
        ToLog("Close Button Clicked")
        try:
            self.SaveConfig(Auto = True)
            print("close")
            print("waiting for end of thread")
            self.OffThread(self.RecThread)
            self.OffThread(self.ConnThread)
            self.RecThread.join()
            self.ConnThread.join()
            self.StopStream()
            ToLog("Application closed")
            evt.Skip()
            wx.Exit()
            sys.exit()

        except Exception as Err:
            ToLog("Failed to closing program, Error code = " + str(Err))
            ToLog("Application closed")
            self.OffThread(self.RecThread)
            self.OffThread(self.ConnThread)
            wx.Exit()
            sys.exit()
            #raise Exception
#=======================================================================================
    def RClickThrob(self, evt):
        #right-click on throb
        global Connect
        try:
            global Connect
            menu = wx.Menu()
            if self.Thread.pause == False:
                menu.Append(self.ConnMenu, "Отключить сервер")
                self.Bind(wx.EVT_MENU, self.DoPauseThread, id = self.ConnMenu)
            else:
                menu.Append(self.ConnMenu, "Включить сервер")
                self.Bind(wx.EVT_MENU, self.DoResumeThread, id = self.ConnMenu)
            menu.AppendSeparator()
            menu.Append(self.AboutMenu, "О соединении...")
            self.Bind(wx.EVT_MENU, self.AboutConn, id = self.AboutMenu)
            return self.PopupMenu(menu)
        except Exception as Err:
            ToLog("Error of Popup menu because of = " + str(Err))
        return
#=========================================
    #creating stream
    def CreateStream(self):
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format = self.Settings[3][1], channels = self.Settings[3][2],
                rate = self.Settings[3][3], input = True,
                frames_per_buffer = self.Settings[3][0])
            ToLog("New Stream created")
            return True
        except Exception as Err:
            ToLog("Error creating new stream, Error code = " + str(Err))
            return False
            #raise Exception
#==========================================
    #breaking prev stream
    def StopStream(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            ToLog("Sream terminated")
        except Exception as Err:
            ToLog("Error breaking stream, Error code = " + str(Err))
            #raise Exception
#==========================================
    #RestartStream
    def RestartStream(self):
        self.StopStream()
        return self.CreateStream()

#==========================================
    def RefreshThreadPams(self, thread, pams):
        try:
            thread.RefreshPams(pams)
        except Exception as Err:
            ToLog("Error in RefreshThreadPams func, Error code = " + str(Err))
            #raise Exception
#==========================================
    def ResumeThread(self, thread):
        try:
            thread.Resume()
        except Exception as Err:
            ToLog("Error in ResumeThread func, Error code = " + str(Err))
            #raise Exception
#==========================================
    def PauseThread(self, thread):
        try:
            thread.Pause()
        except Exception as Err:
            ToLog("Error in PauseThread func, Error code = " + str(Err))
            #raise Exception
#==========================================
    def OffThread(self, thread):
        try:
            thread.OffThread()
        except Exception as Err:
            ToLog("Error in OffThread func, Error code = " + str(Err))
            #raise Exception
#==========================================
    def TryThread(self, thread):
        try:
            if thread.is_alive() == False:
                return "dead"
            else:
                return thread.TryThread()
        except Exception as Err:
            ToLog("Error in TryThread func, Error code = " + str(Err))
            #raise Exception
#=========================================
    def CreateThreads(self):
        try:
            self.evtRec = threading.Event()
            self.evtConn = threading.Event()
            self.RecThread = RecThread("RecThread", self.evtRec, self.p, self.stream, self.Settings)
            self.ConnThread = ConnThread("ConnThread", self.evtConn, self.p, self.stream, self.Settings)
            for thread in [self.RecThread, self.ConnThread]:
                thread.setDaemon(True)
                thread.start()
        except Exception as Err:
            ToLog("Error in CreateThreads func, Error code = " + str(Err))
            #raise Exception
       
#===================================
    #Rec Clicked
    def ClickedRec(self, evt):
        try:
            if self.TryThread(self.RecThread) == "waiting":
                ToLog("Rec Button Pressed, RecThread is switched to On")
                self.RefreshThreadPams(self.RecThread, self.Settings)
                self.ResumeThread(self.RecThread)
                self.RecBtn.Clicked(1)
                self.RecBtn.SetToolTip("Запись включена")

            elif self.TryThread(self.RecThread) == "running":
                ToLog("Rec Button Pressed, RecThread is switched to Off")
                self.PauseThread(self.RecThread)
                self.RecBtn.Clicked(0)
                self.RecBtn.SetToolTip("Запись выключена")

        except Exception as Err:
            ToLog("Error in ClickedRec function, Error code = " + str(Err))
            #raise Exception

#===================================
    #Conn Clicked
    def ClickedConn(self, evt):
        try:
            if self.TryThread(self.ConnThread) == "waiting":
                ToLog("Connect Button Pressed, ConnThread is switched to On")
                self.RefreshThreadPams(self.ConnThread, self.Settings)
                self.ResumeThread(self.ConnThread)
                self.ConnectBtn.Clicked(1)
                self.ConnectBtn.SetToolTip("Connect is On")

            elif self.TryThread(self.ConnThread) == "running":
                ToLog("Connect Button Pressed, ConnectThread is switched to Off")
                self.PauseThread(self.ConnThread)
                self.ConnectBtn.Clicked(0)
                self.ConnectBtn.SetToolTip("Connect is Off")

        except Exception as Err:
            ToLog("Error in ClickedConn function, Error code = " + str(Err))
            #raise Exception

#=============================================================================================
    # Updating Window
    def UpdateDisplay(self, mess):
        try:
            ToLog("Message to MainWin = " + str(mess))
        except Exception as Err:
            ToLog("Error in UpdateDisplay MainWin Func, Error code = " + str(Err))
            
#Treads
#======================
#======================
#======================
#======================
#MyThreadClass
class MyThread(threading.Thread):
    def __init__(self, myname, evt, pams):
        super().__init__()
        self.pams = pams
        self.name = myname
        self.stop = False
        self.pause = False
        self.evt = evt

    #---------------------------------------------------
    def ToWin(self, message):
        try:
            wx.CallAfter(pub.sendMessage, "UpdateMainWin", mess = message)
        except Exception:
            ToLog("Не смог отправить сообщение в главное меню")
            #raise Exception

    #------------------------------------------------------
    def OffThread(self):
        ToLog("I'm " + self.name + " and I have stop command")
        self.evt.set()
        self.stop = True

    #------------------------------------------------------
    def Pause(self):
        ToLog("I'm " + self.name + " and I have pause command")
        #self.pause = True
        self.evt.clear()

    #-------------------------------------------------------
    def Resume(self):
        ToLog("I'm " + self.name + " and I have resume command")
        #self.pause = False
        self.evt.set()

    #-------------------------------------------------------
    def RefreshPams(self, pams):
        ToLog("I'm " + self.name + " and I have refresh pams command")
        self.pams = pams

    #-------------------------------------------------------
    def TryThread(self):
        if self.stop == True:
            return "dead"
        elif self.evt.isSet():
            return "running"
        else:
            return "waiting"


#======================
#======================
#======================
#======================
#SavingRecThread
class RecThread(MyThread):
                               #self.Settings = [
        #               [MainPos],
        #               folder for records
        #               [(ip, password), (ip, password).....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds],
        #               ServerPort]
    def __init__(self, name, evt, p, stream, settings):
        super().__init__(name, evt, settings)
        self.settings = settings
        self.test = True
        self.p = p
        self.stream = stream
        #self.stop = False
        #self.pause = False

    #------------------------------------
    def run(self):
        ToLog("RecThread started")
        try:
            self.SaveWAVFile()
        except Exception as Err:
            ToLog("Error in SaveFile Function, Error code = " + str(Err))
            raise Exception
        ToLog("Saving RecThread Finished")

    #------------------------------------
    def ReadFrames(self):
        frames = []
        if self.test == True:
            self.TimeRec = 1
        else:
            self.TimeRec = self.settings[3][4]
    
        for i in range (0, int(self.settings[3][3] / self.settings[3][0] * self.TimeRec)):
            if self.stop == True or not self.evt.isSet():
                break
            data = self.stream.read(self.settings[3][0])
            frames.append(data)
        return frames

    #-------------------------------------
    def SaveWAVFile(self):
        while True:
            if self.stop == True:
                break
            self.sample = self.p.get_sample_size(self.settings[3][1])
            frames = self.ReadFrames()
            SaveWAVThread = SavingWAVThread(frames, self.sample, self.test, self.settings)
            SaveWAVThread.start()
            self.test = False
            print("Iteration of savefile thread")
            self.evt.wait()
            
#======================
#======================
#======================
#======================
#Saving Records Thread
class SavingWAVThread(threading.Thread):
    def __init__(self, DataToSave, Samplesize, test, Settings):
        super().__init__()
        self.data = DataToSave
        self.settings = Settings
        self.sample = Samplesize
        self.test = test

    #--------------------------------------
    def run(self):
        ToLog("SavingWAVThread Started")
        try:
            struct = time.localtime(time.time())
            StrTime = time.strftime("%Y.%m.%d_%H.%M.%S", struct)
            self.Filename = self.settings[1] + "\\record_" + StrTime + ".wav"
            wf = wave.open(self.Filename, "wb")
            wf.setnchannels(self.settings[3][2])
            wf.setsampwidth(self.sample)
            wf.setframerate(self.settings[3][3])
            wf.writeframes(b''.join(self.data))
            wf.close()
            ToLog("Saved record in file: " + str(self.Filename))
            self.ClearTestFile()
        except Exception as Err:
            ToLog("Error in SavingWAVThread, Error code = " + str(Err))
            #raise Exception
        ToLog("SavingWAVThread Finished")

    #---------------------------------------
    def ClearTestFile(self):
        if self.test == True:
            os.remove(self.Filename)
            ToLog("Delete test recording file")
  

#======================
#======================
#======================
#======================
#NetConnectThread
class ConnThread(MyThread):
                               #self.Settings = [
        #               [MainPos],
        #               folder for records
        #               [(ip, password), (ip, password).....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds],
        #               ServerPort]
    def __init__(self, name, evt, p, stream, settings, tcp = True, timeout = 3, numclient = 5):
        super().__init__(name, evt, settings)
        self.settings = settings
        self.tcp = tcp
        self.socktimeout = timeout
        self.numclient = numclient
        self.stop = False
        self.stream = stream
       
        
    #------------------------------------
    def run(self):
        ToLog("Connect Thread started")

        while True:
            if self.stop == True:
                break
            print("===============iter StartServer Thread==================")
            try:
                self.StartServer()
            except Exception as Err:
                ToLog("Error in self.StartServer, Error code = " + str(Err))
                #raise Exception
                break
            self.evt.wait()
        ToLog("Connect Thread finished")
        
    #--------------------------------------
    def StartServer(self):
        ToLog("StartServer function started")
        if self.tcp == True:
            print("==============Iteration TCP Thread==============")
            self.TCPServer()
        else:
            print("==============Iteration UDP Thread==============")
            self.UDPServer()
        ToLog("StartServer function finished")

    #---------------------------------------
    def TCPServer(self):
        ToLog("TCPServer function started")
        #create socket with lifetime 1 sec
        self.sock = socket.socket()
        self.sock.settimeout(self.socktimeout)
        self.sock.bind(("", self.settings[4]))

        #socket listened by 5 clients, for now
        self.sock.listen(self.numclient)

        try:
            self.conn, self.addr = self.sock.accept()
            ToLog("Create TCP socket with client = " + str(self.addr))
            self.TransvTCP()
        except socket.timeout:
            print("Socket lifetime exceed")
        except socket.error as msg:
            ToLog("SOCKET ERROR CODE = " + str(msg))
            ToLog("strerror" + os.strerror(msg.errno))
           
        except Exception as Err:
            ToLog("Error creating socket, Error code = " + str(Err))
            #raise Exception

        #try:
        #    self.sock.shutdown(socket.SHUT_RDWR)
        #except Exception as Err:
        #    pass

        #try:
        #    self.sock.send(b"end")
        #except Exception as Err:
        #    pass
        self.sock.close()
        ToLog("TCPServer function finished")

    #---------------------------------------
    def TransvTCP(self):
        ToLog("TransvTCP function started")
        data = None
        while True:
            if self.stop == True or not self.evt.isSet():
                break
            data = self.stream.read(self.settings[3][0])
            a = pickle.dumps(data)
            message = struct.pack("Q", len(a)) + a
            self.conn.sendall(message)
        ToLog("TransvTCP function finished")

    #----------------------------------------
    def UDPServer(self):
        ToLog("UDPServer function started")
        #create socket with lifetime 1 sec
        self.BUFF_SIZE = 65536
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        self.sock.settimeout(self.socktimeout)
        self.sock.bind(("", self.settings[4]))

        #socket listened by 5 clients, for now
        #sock.listen(5)

        try:
            self.TransvUDP()
        except socket.timeout:
            print("Socket lifetime exceed")
        except Exception as Err:
            ToLog("Error creating socket, Error code = " + str(Err))
            #raise Exception

        ToLog("TransvTCP function finished")

    #----------------------------------------
    def TransvUDP(self):
        ToLog("TransvUDP function started")
        data = None
        while True:
            if self.stop == True or not self.evt.isSet():
                break
            msg, client_addr = self.sock.recvfrom(self.BUFF_SIZE)
            #try:
                #msg, client_addr = self.sock.recvfrom(self.BUFF_SIZE)
            #except socket.timeout:
            #    print("Socket lifetime exceed")
            #    return
            ToLog("Create UDP socket with client = " + str(client_addr))

            while True:
                if self.stop == True or not self.evt.isSet():
                    break
                data = self.stream.read(self.settings[3][0])
                self.sock.sendto(data, client_addr)
                ToLog("Sending some data to client, then sleep")
                time.sleep(0.8 * self.settings[3][0] / self.settings[3][3])
        ToLog("TransvUDP function finished")
  
#=============================================
#=============================================
#=============================================
#=============================================
# SetDlg
class SettingDlg(wx.Dialog):
                       #self.Settings = [
        #               [MainPos],
        #               folder for records
        #               [[ip, port, password], [ip, port, password].....]
        #               [CHUNK, FORMAT, CHANNELS, RATE, seconds]]
    def __init__(
        self, label = "Настройки", path = os.getcwd(),
        waveformat = [1024, "pyaudio.paInt16", 1, 44100, 60]):
        #self.label = label
        #self.ip = ciscoIP
        self.value = [
            ["512", "1024", "2048"],
            ["paFloat32", "paInt32", "paInt24", "paInt16",
             "paInt8", "paUInt8", "paCustomFormat"],
            ["1", "2"],
            ["8000", "11025", "16000", "22050", "32000", "44100",
             "48000", "96000", "192000"],
            ["10", "60", "120", "300", "600", "1200", "3600"]]

        print("loaded waveformat = " + str(waveformat))
        SendChoices = [1, 3, 0, 5, 1, path]
        for i in range (0, len(self.value)):
            for ii in range (0, len(self.value[i])):
                if str(waveformat[i]) == self.value[i][ii]:
                    SendChoices[i] = ii
  
        wx.Dialog.__init__(self, None, -1, label)
        #global MyDir
        labels = [
            "Размер блока данных формата .WAV (Chunk Data Size)",
            "Формат", "Количество каналов (моно, стерео)",
            "Частота дискретизации (Sample Rate)",
            "Предельная продолжительность файла записи, секунд",
            "Директория для сохранения файлов записи"]
        posSText = []
        #for i in range (0, len(labels)):
        #posSText = [(10, 10), (10, 70), (10, 130), (10, 190), (10, 250), ()]
        for i in range (0, len(labels)):
            text = wx.StaticText(self, wx.ID_ANY, labels[i], pos = (10, 10 + 60*i))
            text.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        #posChoices = [(10, 35), (10, 95), (10, 155), (10, 215)]
        self.Choices = []
        for i in range(0, len(labels)):
            if i != len(labels) - 1:
            #temp = wx.ListBox(self, wx.ID_ANY, pos = posChoices[i], size = (280, 30), choices = self.value[i])
                temp = wx.Choice(self, wx.ID_ANY, pos = (10, 35 + 60*i), size = (380, 30),
                                 choices = self.value[i])
                temp.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
                temp.SetSelection(SendChoices[i])
                self.Choices.append(temp)

        self.DirText = wx.TextCtrl(
            self, wx.ID_ANY, labels[-1], pos = (10, 35 + 60*(len(labels)-1)),
            size = (330, 30), style = wx.TE_READONLY)
        self.DirText.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.DirText.SetValue(path)

        DirBtn = wx.Button(self, wx.ID_ANY, "...", pos = (360, 35 + 60*(len(labels)-1)) ,size = (30, 30))
        DirBtn.Bind(wx.EVT_BUTTON, self.ChooseDir)
        DirBtn.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
                
        #OKButton = wx.Button(self, wx.ID_OK, "OK", pos = (140, 260), size = (120, 30))
        OKButton = wx.Button(self, wx.ID_OK, "OK", pos = (140, 20 + 60*len(labels)), size = (120, 30))
        OKButton.SetDefault()
        OKButton.SetFont(wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        #self.SetClientSize((400, 300))
        self.SetClientSize((400, 60 + len(labels)*60))
        self.Bind(wx.EVT_CLOSE, self.NoClose)
    
    def NoClose(self, evt):
        print("No Close")


    def ChooseDir(self, evt):
        print ("Choose Directory")
        dlgDir = wx.DirDialog(
            parent = None,
            message = "Выберите папку для записей",
            defaultPath = os.getcwd(),
            style = wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)

        if dlgDir.ShowModal() == wx.ID_OK:
            print("Новая расшаренная папка = " + str(dlgDir.GetPath()))
            self.DirText.SetValue(str(dlgDir.GetPath()))
            
        return           
#=============================================
#=============================================
#=============================================
#=============================================
#NewServerDialog
class NClientDlg(wx.Dialog):
    def __init__(self, label, curserv = ["localhost", "123"]):
        self.label = label
        self.curserv = curserv
        wx.Dialog.__init__(self, None, -1, label, size = (300,300))
        labels = ["IP-адрес", "Пароль для подключения"]
        posSText = [(10, 10), (10, 80)]
        for i in range (0, len(labels)):
            text = wx.StaticText(self, wx.ID_ANY, labels[i], pos = posSText[i])
            text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        posText = [(10, 45), (10, 115)]
        self.Value = []
        for i in range(0, len(posText)):
            temp = wx.TextCtrl(self, wx.ID_ANY, "", pos = posText[i], size = (260, 30), style = wx.TE_CENTRE)
            temp.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            temp.SetValue(self.curserv[i])
            self.Value.append(temp)
        OKButton = wx.Button(self, wx.ID_OK, "OK", pos = (10, 225), size = (120, 30))
        OKButton.SetDefault()
        OKButton.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        OTButton = wx.Button(self, wx.ID_CANCEL, "Отмена", pos = (150, 225), size = (120, 30))
        OTButton.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        return


#=============================================
#=============================================
#=============================================
#=============================================
# scaling bitmaps
def ScaleBitmap(bitmap, size):
    image = bitmap.ConvertToImage()
    image = image.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
    return wx.Image(image).ConvertToBitmap()

#=================================
#=================================
#=================================
#=================================
# Окно приветствия
class MySplashScreen(SplashScreen):
    def __init__(self, MyDir, parent = None):
        super(MySplashScreen, self).__init__(
            bitmap = wx.Bitmap(name = MyDir + "\\banner_server.png", type = wx.BITMAP_TYPE_PNG),
            splashStyle = wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
            milliseconds = 1500,
            parent = None,
            id = -1,
            pos = wx.DefaultPosition,
            size = wx.DefaultSize,
            style =wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.Show(True)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        event.Skip()
        self.Hide()

#=============================================
#=============================================
#=============================================
#=============================================
# mythrob#1
class SimpleClickThrob(wx.lib.throbber.Throbber):
    def __init__(self, parent, ListOfFrames, NumOfFrames, FrameDelay, AnswerTime = 200, AnswerFrame = False):
        wx.lib.throbber.Throbber.__init__(self, parent, wx.ID_ANY, ListOfFrames, frames = NumOfFrames, frameDelay = FrameDelay)
        print("I created my throbber class")
        self.CurFrame = 0
        self.AnswerTime = AnswerTime
        if AnswerFrame == False:
            self.AnswerFrame = NumOfFrames - 1
        else:
            self.AnswerFrame = AnswerFrame
        #print("AnswerFrame = " + str(self.AnswerFrame))

    def Clicked(self):
        #print("Clicked func started")
        self.SetCurrent(self.AnswerFrame, clicked = True)
        wx.MilliSleep(self.AnswerTime)
        self.SetCurrent(self.CurFrame, clicked = True)
        #print("Clicked func ended")
        
    def SetCurrent(self, num, clicked = False):
        wx.lib.throbber.Throbber.SetCurrent(self, num)
        if clicked == False:
            self.CurFrame = num
            #print("Now CurFrame = " + str(self.CurFrame))

    def GetCurrent(self):
        #print("asked CurFrame")
        return self.CurFrame
    
#=============================================
#=============================================
#=============================================
#=============================================
# mythrob#2
class ChangeClickThrob(wx.lib.throbber.Throbber):
    def __init__(self, parent, ListOfFrames, NumOfFrames, FrameDelay, AnswerTime = 200, AnswerFrame = False):
        wx.lib.throbber.Throbber.__init__(self, parent, wx.ID_ANY, ListOfFrames, frames = NumOfFrames, frameDelay = FrameDelay)
        print("I created my throbber class")
        self.CurFrame = 0
        self.AnswerTime = AnswerTime
        if AnswerFrame == False:
            self.AnswerFrame = NumOfFrames - 1
        else:
            self.AnswerFrame = AnswerFrame
        #print("AnswerFrame = " + str(self.AnswerFrame))

    def Clicked(self, EndFrame):
        #print("Clicked func started")
        self.SetCurrent(self.AnswerFrame, clicked = True)
        wx.MilliSleep(self.AnswerTime)
        self.SetCurrent(EndFrame)
        #print("Clicked func ended")
        
    def SetCurrent(self, num, clicked = False):
        wx.lib.throbber.Throbber.SetCurrent(self, num)
        if clicked == False:
            self.CurFrame = num
            #print("Now CurFrame = " + str(self.CurFrame))

    def GetCurrent(self):
        #print("asked CurFrame")
        return self.CurFrame
#=============================================
#=============================================
#=============================================
#=============================================
# ClearOldLogs
def ClearLogs():
    global LogDir
    try:
        while len(os.listdir(LogDir)) >= 10:
            if len(os.listdir(LogDir)) < 10:
                    break
            try:
                os.remove(os.path.abspath(FindOldest(LogDir)))
                print("DELETING FILE " + str(FindOldest(LogDir)))
            except Exception as Err:
                ToLog("Old file with logs wasn't deleted, Error code = " + str(Err))
                #raise Exception
                break
    except Exception as Err:
        ToLog("Error of clearing dir with logs, Error code = " + str(Err))
        #raise Exception
#=============================================
#=============================================
#=============================================
#=============================================   
# DeleteOldest
def FindOldest(Dir):
    try:
        List = os.listdir(Dir)
        fullPath = [Dir + "/{0}".format(x) for x in List]
        oldestFile = min(fullPath, key = os.path.getctime)
        return oldestFile
    except Exception as Err:
        ToLog("Error of finding oldest file in dir, Error code = " + str(Err))
        #raise Exception
        return False

#=============================================
#=============================================
#=============================================
#=============================================
# Tolog - renew log
def ToLog(message, startThread = False):
    try:
        global LogQueue
        LogQueue.put(str(datetime.today())[10:19] + "  " + str(message) + "\n")
    except Exception as Err:
        print("Error of ToLog function, Error code = " + str(Err))
        
#=============================================
#=============================================
#=============================================
#=============================================
# Thread for saving logs
class LogThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        global LogQueue
        ToLog("LogThread started!!!")
        self.writingQueue()
        ToLog("LogThread finished!!!")

    def writingQueue(self):
        global LogQueue
        while True:
            try:
                if LogQueue.empty():
                    time.sleep(3)
                    continue
                else:
                    file = open(LogDir + "\\" + str(datetime.today())[0:10] + ".cfg", "a")
                    while not LogQueue.empty():
                        mess = LogQueue.get_nowait()
                        file.write(mess)
                        print("Wrote to Log:\t" + mess)
                    file.close()
            except Exception as Err:
                print("Error writing to Logfile, Error code = " + str(Err))
                raise Exception
                    
'''============================================================================'''
# Определение локали!
locale.setlocale(locale.LC_ALL, "")

global LogDir, MyDir, MyDate,LogQueue
LogDir = os.getcwd() + "\\Logs"
LogQueue = queue.Queue()
ToLog("Application started")

MyDate = " 27.11.2023"
MyDir = os.getcwd()
            
ex = wx.App()

WINDOW = MySplashScreen(MyDir + "\\images")
MainWindow(None)


ex.MainLoop()




















