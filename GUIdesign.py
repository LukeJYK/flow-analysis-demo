
        def pre_getlist():
            j = 0
            dir = 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
            prekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, dir)

            try:
                value=[]
                while 1:
                    name = _winreg.EnumKey(prekey, j)
                    subkey = _winreg.OpenKey(prekey, name)
                    try:
                        value = _winreg.QueryValueEx(subkey, 'DisplayName')
                        list1 = list(value)
                        string = "".join(list1)

                        # search_result.append(string)

                    except WindowsError, e:
                        pass

                    j += 1
                print value
            except WindowsError, e:
                pass
            finally:
                _winreg.CloseKey(prekey)
                pass
        def get_list():
            clear()
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
        btn3.clicked.connect(get_list)


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
                search_result.setText("not find")
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
                        getProductCode().string
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
                search_result.setText("uninstalling...")
                qStr = line.text()
                Str = unicode(qStr)
                keypath = getProductCode('SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
                                     Str)
                uninstall_productbyCode(keypath)
            except UnboundLocalError, e:
                search_result.setText("not found")
        btn4.clicked.connect(uninstall)
        def data_capture():
            dpkt = sniff(count=0,timeout=50)  # 这里是针对单网卡的机子，多网卡的可以在参数中指定网卡
            wrpcap("demo.pcap", dpkt)
        btn6.clicked.connect(data_capture)
        def remove():
            alllist = os.listdir(u"D:\\pycharm project\\")
            try:
                qStr = line.text()
                Str = unicode(qStr)
                for i in alllist:
                    aa = i.split(".")[0]
                    if Str in aa.lower():
                        oldname = u"D:\\pycharm project\\" + aa + ".pcap"
                        newname = u"C:\\Users\\lenovo\\Desktop\\" + aa + ".pcap"
                        shutil.copyfile(oldname, newname)
                        search_result.setText("remove successfully")

            except IOError, e:
                search_result.setText("Input ERROR")
        btn7.clicked.connect(remove)


        #設置窗口
        self.setGeometry(100, 150, 1600, 800)
        self.setWindowTitle("demo")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())