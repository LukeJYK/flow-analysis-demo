import os
import shutil
alllist=os.listdir(u"D:\\pycharm project\\")
for i in alllist:
    aa=i.split(".")[0]
    #print aa
    if 'demo' in aa.lower():
        oldname = u"D:\\pycharm project\\" + aa + ".pcap"
        newname = u"C:\\Users\\lenovo\\Desktop\\" + aa + "1.pcap"
        shutil.copyfile(oldname, newname)