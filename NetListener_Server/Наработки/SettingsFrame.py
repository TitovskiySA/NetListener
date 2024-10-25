import wx
import string
import socket
import os

class dlg(wx.Dialog):
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
        

        #self.Choices[0].SetSelection(1)
        #self.Choices[1].SetSelection(3)
        #self.Choices[2].SetSelection(0)
        #self.Choices[3].SetSelection(5)
        #self.Choices[4].SetSelection(1)

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
        

    #=====================================================================================
        
app = wx.App()
dlg1 = dlg(label = "Сетевые настройки")
#dlg1.Show(True)
if dlg1.ShowModal() == wx.ID_OK:
    print("Pressed OK")
    print("values0 = " + dlg1.Choices[0].GetStringSelection())
    print("values1 = " + dlg1.Choices[1].GetStringSelection())
    print("values2 = " + dlg1.Choices[2].GetStringSelection())
    print("values3 = " + dlg1.Choices[3].GetStringSelection())
dlg1.Destroy()
