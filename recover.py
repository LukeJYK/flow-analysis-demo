#!/usr/bin/python
#encoding:utf-8

# this function is used to get the uninstall string of a software in windows
# input:the dir which is a register key,the name of software product
# output:the uninstall string,if None,means no find

import _winreg
import os
import sys
import time
import win32api
reload(sys)
sys.setdefaultencoding('utf8')

#获取产品product ID从而便于获取卸载路径
def getProductCode(dir, productName):
    uninstallString = ''

    # get the key of the uninstall path
    # get the subkey,get the one which have the same name with productName
    # by the subkey,get the value of uninstall string of it
    try:
        global key
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)
        #print key
        j = 0
        while 1:
            name = _winreg.EnumKey(key, j)
            #print name
            # name = repr(name)
            path = dir + '\\' + name
            #print path

            subkey = _winreg.OpenKey(key, name)
            #print subkey
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
                #print uninstallString
                return uninstallString
            _winreg.CloseKey(subkey)
            #print value,'    ',type
            j += 1

    except WindowsError, e:
        print 'not find'
    finally:
        _winreg.CloseKey(key)
pass

# 卸载软件
def uninstall_productbyCode(code):

    try:
        #win32api.ShellExecute(0, 'open', uninstall_cmd, '', '', 1)
        uninstall_cmd = code
        #uninstall_cmd = "msiexec  /x /quiet /norestart " + code
        #print uninstall_cmd
        for j in uninstall_cmd:
            if j[0]=="D"or j[0]=="C" or j[0]=="E":
                win32api.ShellExecute(0, 'open', uninstall_cmd, '', '', 1)
                break
            else:
                #uninstall_cmd = "msiexec  /x /quiet /norestart " + code
                #print uninstall_cmd
                os.system(uninstall_cmd) == 0
                break

    except TypeError, e:
        pass
    time.sleep(10)
