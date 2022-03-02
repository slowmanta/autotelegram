import glob
import json
import os
import tkinter
from tkinter import *
from tkinter import ttk
import pathlib


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
        self.windowHeight = 150
        tkinter.Frame.__init__(self, parent)
        createProfileLabel = Label(self, text='Chrome', font=('bold', 14), pady=5)
        createProfileLabel.grid(row=1, column=0)

        createProfileLabel = Label(self, text='Firefox', font=('bold', 14), pady=5)
        createProfileLabel.grid(row=1, column=1)

        settingChromeBtn = Button(self, text='Thiết Lập', width=22, height=2,
                                  command=lambda: controller.show_frame('Chrome'))
        settingChromeBtn.grid(row=2, column=0, pady=5, padx=6.5)

        settingFirefoxBtn = Button(self, text='Thiết Lập', width=22, height=2,
                                   command=lambda: controller.show_frame('Firefox'))
        settingFirefoxBtn.grid(row=2, column=1, pady=5, padx=6.5)

        autoChromeBtn = Button(self, text='Chạy Auto', width=22, height=2,
                               command=lambda: controller.show_frame('Chrome'))
        autoChromeBtn.grid(row=3, column=0, pady=5, padx=6.5)

        autoFirefoxBtn = Button(self, text='Chạy Auto', width=22, height=2,
                                command=lambda: controller.show_frame('Chrome'))
        autoFirefoxBtn.grid(row=3, column=1)


class Chrome(tkinter.Frame):
    def __init__(self, parent, controller):
        self.textProfilePopup = None
        self.groupNamePopup = None
        self.groupNameData = {}
        self.profileData = {}
        self.windowWidth = 1202
        self.windowHeight = 310
        self.settingPath = str(pathlib.Path.cwd()) + '\\settings\\chrome\\'
        tkinter.Frame.__init__(self, parent)
        Button(self, text='Group Name', width=15, height=2, command=self.groupNameView) \
            .grid(row=0, column=0, padx=5, pady=5)

        Button(self, text='Open Profile', width=15, height=2, command=self.groupNameView) \
            .grid(row=1, column=0, padx=5, pady=5)

        Button(self, text='Add Profile', width=15, height=2, command=self.groupNameView) \
            .grid(row=2, column=0, padx=5, pady=5)

        Button(self, text='Text Profile', width=15, height=2, command=self.textProfileView) \
            .grid(row=3, column=0, padx=5, pady=5)

        Button(self, text='Delete Profile', width=15, height=2, command=self.deleteProfile) \
            .grid(row=4, column=0, padx=5, pady=5)

        Button(self, text='Back', width=15, height=2, command=lambda: controller.show_frame('FirstPage')) \
            .grid(row=5, column=0, padx=5, pady=5)

        Label(self, text='List Profiles', font=('bold', 16)) \
            .grid(row=0, column=1, padx=20, pady=5)

        self.listProfileTv = ttk.Treeview(self)
        self.listProfileTv.grid(row=1, rowspan=5, column=1, padx=20, pady=5)

        self.listProfileTv['columns'] = ('name', 'path', 'text', 'stt')
        self.listProfileTv.column('#0', anchor=CENTER, width=50)
        self.listProfileTv.column('name', anchor=CENTER, width=125)
        self.listProfileTv.column('path', anchor=W, width=400)
        self.listProfileTv.column('text', anchor=W, width=350)
        self.listProfileTv.column('stt', anchor=CENTER, width=125)

        self.listProfileTv.heading('#0', text='No.', anchor=CENTER)
        self.listProfileTv.heading('name', text='Profile Name', anchor=CENTER)
        self.listProfileTv.heading('path', text='Profile Path', anchor=W)
        self.listProfileTv.heading('text', text='Profile Text', anchor=W)
        self.listProfileTv.heading('stt', text='Status', anchor=CENTER)

        profileDatas = self.getProfileData()
        number = 1
        for profileName in profileDatas:
            profilePath = profileDatas[profileName]['path']
            profileText = profileDatas[profileName]['text']
            profileStatus = 'Signed in' if profileDatas[profileName]['stt'] == 1 else 'Not Sign in'
            self.listProfileTv.insert(parent='', index='end', text=number,
                                      values=(profileName, profilePath, profileText, profileStatus))
            number = number + 1

    def runAuto(self):
        print('Firefox: Run Auto')

    def groupNameView(self):
        self.groupNamePopup = Toplevel(self)
        self.groupNamePopup.geometry("276x110")
        self.groupNamePopup.title("Update Group Name")
        groupName = open(self.settingPath + 'group_name.txt', 'r').read()
        Label(self.groupNamePopup, text="Group Name", font=('bold', 14)).grid(row=0)
        groupNameInput = StringVar(value=groupName)
        self.groupNameData['groupNameEntry'] = Entry(self.groupNamePopup, textvariable=groupNameInput, width=40)
        self.groupNameData['groupNameEntry'].grid(row=1, padx=5, ipadx=10, ipady=5)
        Button(self.groupNamePopup, text='Update', width=15, height=2, command=self.saveGroupName) \
            .grid(row=2, padx=5, pady=5)

    def saveGroupName(self):
        groupName = self.groupNameData['groupNameEntry'].get()
        groupNameFile = open(self.settingPath + 'group_name.txt', 'w')
        groupNameFile.write(groupName)
        groupNameFile.close()
        self.groupNamePopup.destroy()

    def addProfile(self):
        print("Add Profile")

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
            profileName = profileDataItem.get('values')[0]
            profileDatas = self.getProfileData()
            if profileName in profileDatas.keys():
                profileDatas[profileName]['text'] = profileText
                self.updateProfileData(profileDatas)

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
            os.rmdir(profilePath)
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


class Firefox(tkinter.Frame):
    def __init__(self, parent, controller):
        self.windowWidth = 350
        self.windowHeight = 200
        tkinter.Frame.__init__(self, parent)

    def createProfile(self):
        print('Chrome: Create Profile')

    def runAuto(self):
        print('Chrome: Run Auto')


if __name__ == '__main__':
    app = AutoTelegram()
    app.mainloop()
