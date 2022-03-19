import ctypes
import json
import shutil
import threading
import time
import tkinter
from datetime import datetime
from tkinter import *
from tkinter import ttk
import pathlib
from selenium import webdriver
from selenium.webdriver import Keys, ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class AutoTelegram(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.title('Auto Chat Telegram')
        self.frames = {}
        for F in (FirstPage, Chrome, Firefox):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("FirstPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        self.geometry(f'{frame.windowWidth}x{frame.windowHeight}')
        frame.tkraise()


class FirstPage(tkinter.Frame):
    def __init__(self, parent, controller):
        self.windowWidth = 360
        self.windowHeight = 105
        tkinter.Frame.__init__(self, parent)

        settingChromeBtn = Button(self, text='Chrome', width=22, height=2,
                                  command=lambda: controller.show_frame('Chrome'))
        settingChromeBtn.grid(row=0, column=0, pady=8, padx=6.5)

        settingFirefoxBtn = Button(self, text='Firefox', width=22, height=2,
                                   command=lambda: controller.show_frame('Firefox'))
        settingFirefoxBtn.grid(row=0, column=1, pady=8, padx=6.5)

        Label(self, text="Developed by Nam MT", width=30, fg='red').grid(row=1, columnspan=2)
        Label(self, text="fb.com/congionho33", width=30, fg='blue').grid(row=2, columnspan=2)


class Chrome(tkinter.Frame):
    def __init__(self, parent, controller):
        self.isAutoRuning = False
        self.autoLogText = None
        self.addProfilePopup = None
        self.textProfilePopup = None
        self.settingPopup = {}
        self.autoLog = None
        self.settingData = {}
        self.profileData = {}
        self.windowWidth = 1170
        self.windowHeight = 410
        self.settingPath = str(pathlib.Path.cwd()) + '\\settings\\chrome\\'
        self.serviceChrome = ChromeService(str(pathlib.Path.cwd()) + r'\chromedriver.exe')
        tkinter.Frame.__init__(self, parent)

        Button(self, text='Group Name', width=25, height=2, command=self.groupNameView) \
            .grid(row=0, column=0, padx=5, pady=5)

        Button(self, text='Open Profile', width=25, height=2, command=self.openProfile) \
            .grid(row=1, column=0, padx=5, pady=5)

        Button(self, text='Add Profile', width=25, height=2, command=self.addProfileView) \
            .grid(row=2, column=0, padx=5, pady=5)

        Button(self, text='Text Profile', width=25, height=2, command=self.textProfileView) \
            .grid(row=3, column=0, padx=5, pady=5)

        Button(self, text='Delete Profile', width=25, height=2, command=self.deleteProfile, bg='#c82333', fg='#fff') \
            .grid(row=4, column=0, padx=5, pady=5)

        Button(self, text='Number Of Running Window', width=25, height=2, command=self.threadView, bg='#17a2b8', fg='#fff') \
            .grid(row=5, column=0, padx=5, pady=5)

        Button(self, text='Run Auto', width=25, height=2, command=self.runAuto, bg='#28a745', fg='#fff') \
            .grid(row=6, column=0, padx=5, pady=5)

        Button(self, text='Back', width=25, height=2, command=lambda: controller.show_frame('FirstPage'), bg='#e2e6ea', fg='#212529') \
            .grid(row=7, column=0, padx=5, pady=5)

        Label(self, text='List Profiles', font=('bold', 16)) \
            .grid(row=0, column=1, padx=20, pady=5)

        self.listProfileTv = ttk.Treeview(self, height=15)
        self.listProfileTv.grid(row=1, rowspan=7, column=1, padx=20, pady=5)

        self.listProfileTv['columns'] = ('name', 'path', 'text', 'stt')
        self.listProfileTv.column('#0', anchor=CENTER, width=50)
        self.listProfileTv.column('name', anchor=CENTER, width=125)
        self.listProfileTv.column('path', anchor=W, width=400)
        self.listProfileTv.column('text', anchor=W, width=250)
        self.listProfileTv.column('stt', anchor=CENTER, width=125)

        self.listProfileTv.heading('#0', text='No.', anchor=CENTER)
        self.listProfileTv.heading('name', text='Profile Name', anchor=CENTER)
        self.listProfileTv.heading('path', text='Profile Path', anchor=W)
        self.listProfileTv.heading('text', text='Profile Text', anchor=W)
        self.listProfileTv.heading('stt', text='Status', anchor=CENTER)
        self.loadListProfile()

    def runAuto(self):
        self.autoLog = Toplevel(self)
        self.autoLog.geometry("540x450")
        self.autoLog.title("Auto Runing")
        self.autoLogText = Text(self.autoLog, width=65)
        autoLogScb = Scrollbar(self.autoLog, orient=VERTICAL)
        autoLogScb.config(command=self.autoLogText.yview)
        self.autoLogText.config(yscrollcommand=autoLogScb.set)
        self.autoLogText.grid(column=0, row=0)
        autoLogScb.grid(column=1, row=0, sticky=S + N)
        Button(self.autoLog, text='Stop', width=15, height=2, command=self.stopAuto, bg='red', fg='#fff', font='bold') \
            .grid(row=2, column=0, pady=7)

        self.logAutoRuning('Initialization...')

        self.isAutoRuning = True
        profileDatas = self.getProfileData()
        if len(profileDatas) > 0:
            threading.Thread(target=self.initAuto, args=(profileDatas,)).start()

    def initAuto(self, profileDatas):
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        firstNow = datetime.now().second
        firstRun = True
        setting = self.getSetting()
        groupName = setting['groupName']
        maxThread = int(setting['thread'])
        key = 0
        threads = []
        while self.isAutoRuning:
            nowSecond = datetime.now().second
            if firstNow == nowSecond or firstRun:
                self.logAutoRuning('Start Spam...')
                width = 480
                height = 480
                widthN = 0
                heightN = 0
                for profileName in profileDatas:
                    pathProfile = profileDatas[profileName]['path']
                    textProfile = profileDatas[profileName]['text'].split(',')
                    tempKeyText = key % textProfile.__len__()
                    text = textProfile[tempKeyText]
                    resWidth = width * widthN
                    resHeight = height * heightN
                    if resWidth > screensize[0]:
                        heightN = heightN + 1
                        widthN = 0
                        resWidth = width * widthN
                        resHeight = height * heightN
                    if resHeight > screensize[1]:
                        heightN = 0
                        widthN = 0
                        resWidth = width * widthN
                        resHeight = height * heightN

                    position = {'x': resWidth, 'y': resHeight}
                    if len(profileDatas) == 1:
                        threadWorks = threading.Thread(target=self.autoFunction,
                                                       args=(pathProfile, groupName, text, position))
                        threadWorks.start()
                        threadWorks.join()
                    else:
                        if len(threads) < maxThread or (maxThread > len(profileDatas) > len(threads)):
                            threadWorks = threading.Thread(target=self.autoFunction,
                                                           args=(pathProfile, groupName, text, position))
                            threads.append(threadWorks)

                        if len(threads) == maxThread or len(threads) == len(profileDatas):
                            for thread in threads:
                                thread.start()
                            for thread in threads:
                                thread.join()
                            widthN = 0
                            heightN = 0
                            threads = []
                            threadWorks = threading.Thread(target=self.autoFunction,
                                                           args=(pathProfile, groupName, text, position))
                            threads.append(threadWorks)
                    widthN = widthN + 1
                threads = []
                key = key + 1
                firstRun = False
                self.logAutoRuning('===== END =====')
                self.logAutoRuning('-----------------------------')

    def autoFunction(self, pathProfile, groupName, text, position):
        profileName = pathProfile.split("\\")[-1]
        ### Chrome
        try:
            userDataProfileDir = str(fr'--user-data-dir={pathProfile}')
            options = ChromeOptions()
            options.add_argument(userDataProfileDir)
            options.add_argument("--disable-extensions")
            options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
            driver = webdriver.Chrome(service=self.serviceChrome, options=options)
            driver.set_window_size(480, 480)
            driver.set_window_position(position['x'], position['y'])
            url = "https://web.telegram.org/z"
            driver.get(url)
            try:
                self.logAutoRuning(profileName + ': Running')
                searchInput = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "telegram-search-input")))
                searchInput.click()
                time.sleep(2)
                searchInput.send_keys(groupName)
                resultFilter = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "chat-selection")))
                searchInput.send_keys(Keys.RETURN)
                time.sleep(2)

                if driver.find_element(By.CSS_SELECTOR, '.messages-layout .ScrollDownButton button'):
                    driver.find_element(By.CSS_SELECTOR, '.messages-layout .ScrollDownButton button').click()
                    time.sleep(2)

                textInput = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "editable-message-text")))
                textInput.clear()
                textInput.send_keys(text)
                textInput.send_keys(Keys.RETURN)
                # buttonSend = WebDriverWait(driver, 5).until(
                #     EC.presence_of_element_located((By.CLASS_NAME, "send")))
                # buttonSend.click()
                # self.logAutoRuning(profileName + ': Submit Text...')
                time.sleep(2)
                self.logAutoRuning(profileName + ': Done...')
                driver.close()
            except Exception as e:
                self.logAutoRuning(profileName + ':' + e)
                # self.logAutoRuning(profileName + ': Quit Browser...')
                driver.close()
        except Exception as e:
            self.logAutoRuning(profileName + ': Error Browser')
            # self.logAutoRuning(profileName + ': Quit Browser...')

    def stopAuto(self):
        self.isAutoRuning = False
        self.autoLogText.insert('end', 'Stopping...\n')
        self.autoLog.destroy()

    def logAutoRuning(self, msg):
        self.autoLogText.insert('end', str(datetime.now()) + f': {msg}\n')

    def groupNameView(self):
        self.settingPopup['groupName'] = Toplevel(self)
        self.settingPopup['groupName'].geometry("276x110")
        self.settingPopup['groupName'].title("Update Group Name")
        setting = self.getSetting()
        Label(self.settingPopup['groupName'], text="Group Name", font=('bold', 14)).grid(row=0)
        groupNameInput = StringVar(value=setting['groupName'])
        self.settingData['groupNameEntry'] = Entry(self.settingPopup['groupName'], textvariable=groupNameInput, width=40)
        self.settingData['groupNameEntry'].grid(row=1, padx=5, ipadx=10, ipady=5)
        Button(self.settingPopup['groupName'], text='Update', width=15, height=2, command=self.saveGroupName) \
            .grid(row=2, padx=5, pady=5)

    def saveGroupName(self):
        setting = self.getSetting()
        setting['groupName'] = self.settingData['groupNameEntry'].get()
        self.updateSetting(setting)
        self.settingPopup['groupName'].destroy()

    def threadView(self):
        self.settingPopup['thread'] = Toplevel(self)
        self.settingPopup['thread'].geometry("276x110")
        self.settingPopup['thread'].title("Update Number Of Running Window")
        setting = self.getSetting()

        Label(self.settingPopup['thread'], text="Number Of Running Window", font=('bold', 14)).grid(row=0)
        threadInput = StringVar(value=setting['thread'])
        self.settingData['threadEntry'] = Entry(self.settingPopup['thread'], textvariable=threadInput, width=40)
        self.settingData['threadEntry'].grid(row=1, padx=5, ipadx=10, ipady=5)
        Button(self.settingPopup['thread'], text='Update', width=15, height=2, command=self.threadSave) \
            .grid(row=2, padx=10, pady=5, ipadx=10)

    def threadSave(self):
        setting = self.getSetting()
        setting['thread'] = self.settingData['threadEntry'].get()
        self.updateSetting(setting)
        self.settingPopup['thread'].destroy()

    def addProfileView(self):
        self.addProfilePopup = Toplevel(self)
        self.addProfilePopup.geometry("276x110")
        self.addProfilePopup.title("Add Profile")

        Label(self.addProfilePopup, text="Profile Name", font=('bold', 14)).grid(row=0)
        profileNameInput = StringVar()
        self.profileData['profileNameEntry'] = Entry(self.addProfilePopup, textvariable=profileNameInput, width=40)
        self.profileData['profileNameEntry'].grid(row=1, padx=5, ipadx=10, ipady=5)
        Button(self.addProfilePopup, text='Save', width=15, height=2, command=self.saveAddProfile) \
            .grid(row=2, padx=5, pady=5)

    def saveAddProfile(self):
        profileName = self.profileData['profileNameEntry'].get()
        if profileName != '':
            profilePath = self.settingPath + 'profiles'
            profileData = self.getProfileData()
            profileData[profileName] = {'name': profileName, 'path': f'{profilePath}\\{profileName}', 'text': '',
                                        'stt': 0}
            self.updateProfileData(profileData)
            self.loadListProfile()
            self.addProfilePopup.destroy()
            threading.Thread(target=self.verifySignedIn, args=(profileName,)).start()

    def verifySignedIn(self, profileName):
        profileData = self.getProfileData()
        profilePath = profileData[profileName]['path']
        try:
            options = ChromeOptions()
            options.add_argument(fr'user-data-dir={profilePath}')
            driver = webdriver.Chrome(service=self.serviceChrome, options=options)
            url = "https://web.telegram.org/z"
            driver.get(url)
            WebDriverWait(driver, 9999).until(EC.presence_of_element_located((By.ID, "telegram-search-input")))
            driver.quit()
            profileData[profileName]['stt'] = 1
            self.updateProfileData(profileData)
            self.loadListProfile()
        except Exception as e:
            print("Error Create Profile: " + str(e))

    def textProfileView(self):
        profileFocus = self.listProfileTv.focus()
        if profileFocus != '':
            self.textProfilePopup = Toplevel(self)
            self.textProfilePopup.geometry("276x110")
            self.textProfilePopup.title("Update Text Profile")
            textProfile = ''
            profileDataItem = self.listProfileTv.item(profileFocus)
            profileName = profileDataItem.get('values')[0]
            profileDatas = self.getProfileData()
            if profileName in profileDatas:
                textProfile = profileDatas[profileName]['text']

            Label(self.textProfilePopup, text="Text Profile", font=('bold', 14)).grid(row=0)
            textProfileInput = StringVar(value=textProfile)
            self.profileData['textProfileEntry'] = Entry(self.textProfilePopup, textvariable=textProfileInput, width=40)
            self.profileData['textProfileEntry'].grid(row=1, padx=5, ipadx=10, ipady=5)
            Button(self.textProfilePopup, text='Update', width=15, height=2, command=self.saveTextProfile) \
                .grid(row=2, padx=5, pady=5)

    def saveTextProfile(self):
        profileFocus = self.listProfileTv.focus()
        if profileFocus != '':
            profileText = self.profileData['textProfileEntry'].get()
            profileDataItem = self.listProfileTv.item(profileFocus)
            profileName = str(profileDataItem.get('values')[0])
            profileDatas = self.getProfileData()
            if profileName in profileDatas.keys():
                profileDatas[profileName]['text'] = profileText
                self.updateProfileData(profileDatas)
                self.loadListProfile()
        self.textProfilePopup.destroy()

    def deleteProfile(self):
        profileFocus = self.listProfileTv.focus()
        if profileFocus != '':
            profileDataItem = self.listProfileTv.item(profileFocus)
            profileName = profileDataItem.get('values')[0]
            profilePath = profileDataItem.get('values')[1]
            profileDatas = self.getProfileData()
            del profileDatas[profileName]
            self.updateProfileData(profileDatas)
            shutil.rmtree(profilePath)
            self.listProfileTv.delete(profileFocus)
            print("Deleted Profile")
        else:
            print('No Profile')

    def getProfileData(self):
        return json.loads(open(self.settingPath + r'profile_data.json', 'r').read())

    def updateProfileData(self, profileDatas):
        fileProfileDatas = open(self.settingPath + 'profile_data.json', 'w')
        fileProfileDatas.write(json.dumps(profileDatas))
        fileProfileDatas.close()

    def getSetting(self):
        return json.loads(open(self.settingPath + r'setting.json', 'r').read())

    def updateSetting(self, settingData):
        fileProfileDatas = open(self.settingPath + 'setting.json', 'w')
        fileProfileDatas.write(json.dumps(settingData))
        fileProfileDatas.close()

    def loadListProfile(self):
        self.listProfileTv.delete(*self.listProfileTv.get_children())
        profileDatas = self.getProfileData()
        number = 1
        for profileName in profileDatas:
            profilePath = profileDatas[profileName]['path']
            profileText = profileDatas[profileName]['text']
            profileStatus = 'Signed in' if profileDatas[profileName]['stt'] == 1 else 'Not Sign in'
            self.listProfileTv.insert(parent='', index='end', text=number,
                                      values=(profileName, profilePath, profileText, profileStatus))
            number = number + 1

    def openProfile(self):
        profileFocus = self.listProfileTv.focus()
        if profileFocus != '':
            profileData = self.getProfileData()
            profileDataItem = self.listProfileTv.item(profileFocus)
            profileName = str(profileDataItem.get('values')[0])
            profilePath = str(profileDataItem.get('values')[1])
            profileStt = profileData[profileName]['stt']
            try:
                options = ChromeOptions()
                options.add_argument(fr'user-data-dir={profilePath}')
                driver = webdriver.Chrome(service=self.serviceChrome, options=options)
                url = "https://web.telegram.org/z"
                driver.get(url)
                if profileStt == 0:
                    WebDriverWait(driver, 9999).until(EC.presence_of_element_located((By.ID, "telegram-search-input")))
                    profileData[profileName]['stt'] = 1
                    self.updateProfileData(profileData)
                    self.loadListProfile()

            except Exception as e:
                print("Error Create Profile: " + str(e))


class Firefox(tkinter.Frame):
    def __init__(self, parent, controller):
        self.windowWidth = 350
        self.windowHeight = 200
        tkinter.Frame.__init__(self, parent)
        Label(self, text="In Development...", width=20, height=5, font=('bold', 16)).pack()
        Button(self, text='Back', width=25, height=2, command=lambda: controller.show_frame('FirstPage'), bg='#e2e6ea',
               fg='#212529').pack()



if __name__ == '__main__':
    app = AutoTelegram()
    app.mainloop()
