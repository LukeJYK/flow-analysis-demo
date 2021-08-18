#!/usr/bin/python
#encoding:utf-8
import recover
import win32api
import win32con
import _winreg
import os

global userString

global cmd_install

#若下载成功输入Y
def pre_Download():
    print 'Waiting for downloading successfully...'
    print 'if you are OK,press y/Y'
    userString = raw_input()
    while userString == "Y" or userString == "y":
        print "Download successfully"
        return True

def pre_listname():
    j = 0
    dir = 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    prekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)
    list1=[]
    try:
        while 1:
            name = _winreg.EnumKey(prekey, j)
            subkey = _winreg.OpenKey(prekey, name)
            try:
                value, type = _winreg.QueryValueEx(subkey, 'DisplayName')
                value1 = str(value)
                list1.append(value1)

                # search_result.append(string)

            except WindowsError, e:
                pass
            j += 1

    except WindowsError, e:
            pass
    finally:
        _winreg.CloseKey(prekey)

        pass

    return list1
#静默安装exe文件
def install_silent():
    install_path="C:\\Users\\lenovo\\Desktop\\wyyyy_2.5.0.196623.exe" + " "+"/S"
    os.system(install_path)
    print "set up  successfully!"
#输入打开软件名称打开软件
def openSoftware():
    inputname = raw_input()
    path = 'C:\\Users\\lenovo\\Desktop\\' + inputname + '.lnk'
    if os.path.exists(path)==1:
        win32api.ShellExecute(0, 'open', path, '', '', 1)
        print "open software successfully"
    else:
        print "not find application"


#打印所有可以卸载的软件名称
def print_name():
    list2 = []
    j = 0
    dir = 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    prekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)
    try:
        while 1:
            name = _winreg.EnumKey(prekey, j)
            subkey = _winreg.OpenKey(prekey, name)
            value, type = '', ''
            try:
                value, type = _winreg.QueryValueEx(subkey, 'DisplayName')
                value2 =str(value)
                list2.append(value2)
            except WindowsError, e:
                pass
            j += 1
    except WindowsError, e:
        print
    finally:
        _winreg.CloseKey(prekey)
        pass
    print list2
    return list2





#获取uninstall路径
def get_keypath():
    inputname1 = raw_input()
    keypath = recover.getProductCode('SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall', inputname1)
    return keypath


if __name__ == "__main__":
    pre_Download()
    pre_listname()


    remove()


