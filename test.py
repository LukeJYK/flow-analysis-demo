#!/usr/bin/python
#encoding:utf-8

import os
from scapy.sendrecv import sniff
from scapy.utils import wrpcap
import shutil
import _winreg
import sys
import win32api
reload(sys)
sys.setdefaultencoding('utf8')

def pre_Download():
    print 'Waiting for downloading successfully...'
    print 'if you are OK,press y/Y'
    userString = raw_input()
    while userString == "Y" or userString == "y":
        print "Download successfully"
        break
    return True
def firstfile_name(t):
    dirs = os.listdir("C:\Users\lenovo\Desktop")
    for file in dirs:
        t.append(file)
    print t
    return t
def install_silent():
    cmd_install = "C:\\Users\\lenovo\\Desktop\\software_test\\cloudmusicsetup_2.5.0.196623.exe" + " " + "/S"
    os.system(cmd_install)
def differ(list1,list2):
    for i in range(0,len(list2)):
        flag = True
        for j in range(0,len(list1)):
            if(list1[j] == list2[i]):
                flag = False
                break
        if flag:
            return list2[i]
def soft_ware(str):
    path = 'C:\\Users\\lenovo\\Desktop\\' + str
    if os.path.exists(path) == 1:
        win32api.ShellExecute(0, 'open', path, '', '', 1)
        print "open software successfully"
    else:
        print "not find application"


def pre_getlist():
    j = 0
    dir = 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    prekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)

    try:
        value = []
        while 1:
            name = _winreg.EnumKey(prekey, j)
            subkey = _winreg.OpenKey(prekey, name)
            try:
                value,type= _winreg.QueryValueEx(subkey, 'DisplayName')
                # search_result.append(string)
                print value

            except WindowsError, e:
                pass

            j += 1

    except WindowsError, e:
        pass
    finally:
        _winreg.CloseKey(prekey)
        pass

def data_capture():
    dpkt = sniff(count=0, timeout=50)  # 这里是针对单网卡的机子，多网卡的可以在参数中指定网卡
    wrpcap("demo.pcap", dpkt)
def remove():
    alllist = os.listdir(u"D:\\pycharm project\\")
    try:
        Str = "demo"
        for i in alllist:
            aa = i.split(".")[0]
            if Str in aa.lower():
                oldname = u"D:\\pycharm project\\" + aa + ".pcap"
                newname = u"C:\\Users\\lenovo\\Desktop\\" + aa + ".pcap"
                shutil.copyfile(oldname, newname)
                print "remove successfully"
    except IOError, e:
        print "Input ERROR"
def get_list():
    j = 0
    dir = 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    prekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)
    try:
        while 1:
            name = _winreg.EnumKey(prekey, j)
            subkey = _winreg.OpenKey(prekey, name)
            value, type= '', ''
            try:
                value, type = _winreg.QueryValueEx(subkey, 'DisplayName')
                list1=list(value)
                string="".join(list1)
                print string
                #search_result.append(string)

            except WindowsError, e:
                pass
            j += 1

    except WindowsError, e:
        pass
    finally:
        _winreg.CloseKey(prekey)
        pass


def getProductCode(dir, productName):
    uninstallString = ''

    # get the key of the uninstall path
    # get the subkey,get the one which have the same name with productName
    # by the subkey,get the value of uninstall string of it
    try:
        global key
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)
        # print key
        j = 0
        while 1:
            name = _winreg.EnumKey(key, j)
            # print name
            # name = repr(name)
            path = dir + '\\' + name
            # print path

            subkey = _winreg.OpenKey(key, name)
            # print subkey
            value, type = '', ''

            try:
                value, type = _winreg.QueryValueEx(subkey, 'DisplayName')
            except Exception, e:
                pass

            if value == productName:
                try:
                    value2, type2 = _winreg.QueryValueEx(subkey, 'UninstallString')
                except Exception, e:
                    pass
                uninstallString = value2
                # print uninstallString
                return uninstallString
            _winreg.CloseKey(subkey)
            # print value,'    ',type---
            j += 1

    except WindowsError, e:
        print "not find"
    finally:
        _winreg.CloseKey(key)
pass
def uninstall_productbyCode(code):

    try:
        # win32api.ShellExecute(0, 'open', uninstall_cmd, '', '', 1)
        uninstall_cmd = code
        # uninstall_cmd = "msiexec  /x /quiet /norestart " + code
        # print uninstall_cmd
        for j in uninstall_cmd:
            if j[0] == "D" or j[0] == "C" or j[0] == "E":
                win32api.ShellExecute(0, 'open', uninstall_cmd, '', '', 1)
                break
            else:
                # uninstall_cmd = "msiexec  /x /quiet /norestart " + code
                # print uninstall_cmd
                os.system(uninstall_cmd) == 0
                break
    except TypeError, e:
        pass
def uninstall():
    try:
        print "uninstalling..."
        userString = raw_input()
        keypath = getProductCode('SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
                                     userString)
        uninstall_productbyCode(keypath)
    except UnboundLocalError, e:
        print "not found"

if __name__ == "__main__":
    pre_Download()
    m = []
    n = []
    firstfile_name(m)
    install_silent()
    firstfile_name(n)
    str = differ(m, n)
    while (str == None):
        firstfile_name(n)
        str = differ(m, n)
    print str
    soft_ware(str)
    data_capture()
    remove()
    pre_getlist()
    uninstall()
