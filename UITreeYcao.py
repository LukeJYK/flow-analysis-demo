#encoding=utf-8
import os
import sys
from uiautomator import Device
import time
import re
import xml.dom.minidom
import pdb
import subprocess
import shutil
# from TimeException_test_by_ycao201801151427 import *
import threading
import subprocess
import TimeoutExceptionYcao

'''
当前，考虑触发部分。首先，策略以深度优先;同时需要考虑，触发当前控件后，是否需要通过back键来恢复到之前的界面。
深度优先，以递归方式完成;判断是否back，以被触发的控件是否仍然存在于当前界面中
其次，仍然需要考虑逻辑上的循环问题,可以参考之前《静态代码分析挖掘控制流图》中的循环判断方式，进行解决
'''

default_encoding='utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

def running_stop(time_gap):
    def running_time_stop(func):
        def stop_function_running_time(*args,**kwargs):
            print '当前执行函数为 : ' + func.__name__
            start_time = time.time()
            print 'start time : ' + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(start_time))
            threads = []
            thread1 = threading.Thread(target=func(*args,**kwargs),)
            thread2 = threading.Thread(target=time.sleep(time_gap),)
            thread1.start()
            thread2.start()
            while(True):
                print thread2.is_alive()
                if thread2.is_alive() == False:
                    os.exit()

            # func(*args,**kwargs)
            end_time = time.time()
            print 'end time : ' + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))
        return stop_function_running_time
    return running_time_stop

def validity_confirm_by_time(time_limite,time_type):
    '''
    函数执行效果判断修饰器
    :param timeout: 超时时间
    :param time_type: 时间判断方向，True为运行超时，False为时间过短
    :return:
    '''
    def confirm(func):
        def confirm_by_running_time(*args,**kwargs):
            time_gap = 0
            if time_type == False:           ###时间过短判断
                while(time_gap < time_limite):
                    start_time = time.time()
                    func(*args,**kwargs)
                    end_time = time.time()
                    time_gap = int(end_time) - int(start_time)
            else:                           ###超时判断
                start_time = time.time()
                func(*args, **kwargs)
                end_time = time.time()
                time_gap = int(end_time) - int(start_time)
                if time_gap > time_limite:
                    print '执行 %s 函数超时' %(func.__name__)
        return confirm_by_running_time
    return confirm

def validity_confirm_by_fileNum(file_number,file_path,number_type):
    '''
    依据文件个数判断函数执行效果
    :param file_number: 文件个数
    :param number_type: 文件个数判断方向，True为个数溢出，False为个数不足
    :return:
    '''
    def confirm(func):
        def confirm_by_file_number(*args,**kwargs):
            initial_fileNum = 0
            final_fileNum = 0
            for rt,dirs,files in os.walk(file_path):
                initial_fileNum = len(files)
            func(*args,**kwargs)
            for rt,dirs,files in os.walk(file_path):
                final_fileNum = len(files)
            if number_type == False:
                if final_fileNum - initial_fileNum < file_number:
                    print '文件个数不足，需要重新执行函数'
                    func(*args,**kwargs)
            else:
                if final_fileNum - initial_fileNum > file_number:
                    print '文件个数溢出，执行可能出现了问题'
        return confirm_by_file_number
    return confirm




class instance_control():
    def __init__(self,device,start_str,xmlFilePath):
        '''
        :param device:设备实例
        '''
        self.device = device
        self.count = 0                                  ###用于控制递归深度的计数器
        self.start_str = start_str                      ###启动APP的主活动名称
        self.app_pkg = start_str.split('/')[0]          ###APP的包名，用于筛选活动
        self.analysed_button_dict = {}                  ###已触发的活动信息，字典结构
        self.back_count = 0                             ###返回键计数器
        self.analysing_path = []                        ###用于存储当前正在分析的路径
        self.analysed_path = []                         ###用于存储已经分析完成的路径
        self.auto_touch_count = 0                       ###触发总次数
        self.xml_file_path = xmlFilePath                ###UI界面描述XML文件存放目录
        self.scroll_count = 0

    def run_adb_cmd(self,cmd):
        print '启动指定APP'
        args=['adb']
        args.extend(cmd)
        ret=None
        adb = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        ret = adb.communicate()
        if "error: device not found" in ret[1]:
            print 'device not found'
        else:
            return ret

    # @validity_confirm(10,False)
    def press_DF(self,uui_text="",uui_class="",uui_bounds=""):
        # print self.count
        back_flag = True
        if self.count > 0 :
            if uui_class + ' : ' + uui_text in self.analysed_button_dict.keys():        ###该控件之前已经被触发过，返回
                if uui_bounds in self.analysed_button_dict[uui_class + ' : ' + uui_text]:
                    print '该控件已被触发'
                    return False
            else:
                self.analysed_button_dict[uui_class + ' : ' + uui_text] = []
            if uui_class + ' : ' + uui_text + ' : ' + uui_bounds in self.analysing_path and self.count > 1:            ###出现循环
                print '该控件在当前触发顺序中已经被触发，出现循环，返回'
                # print 'return in 99'
                return False
            try:
                self.device.wait.idle()
                if uui_text == '' and uui_bounds != '':          ###标签为空，此时应该按照坐标位置来进行点击
                    x1 = uui_bounds.split('[')[1].split(',')[0]
                    y1 = uui_bounds.split(',')[1].split(']')[0]
                    x2 = uui_bounds.split('][')[1].split(',')[0]
                    y2 = uui_bounds.split(',')[-1].split(']')[0]
                    self.device.click((int(x1)+int(x2))/2,(int(y1)+int(y2))/2)
                else:
                    self.device(test=uui_text,className=uui_class).click()
                    print '触发成功'
                self.device.wait.update()
                if self.analysed_button_dict.has_key(uui_class + ' : ' + uui_text):
                    pass
                else:
                    self.analysed_button_dict[uui_class + ' : ' + uui_text] = []
                self.analysed_button_dict[uui_class + ' : ' + uui_text].append(uui_bounds)
                if self.count == 1:             ###起始根节点
                    self.analysing_path = []
                    self.analysing_path.append(uui_class + ' : ' + uui_text + ' : ' + uui_bounds)

                    # print '当前正在触发的控件顺序 ： '
                    # print self.analysing_path
                    # print 'continue in 110'
                else:
                    self.analysing_path.append(uui_class + ' : ' + uui_text + ' : ' + uui_bounds)
                    # print '当前正在触发的控件顺序 ： '
                    # print self.analysing_path
                    # print 'continue in 114'
            except Exception as e:
                print e
                print '触发出现问题'
                if 'JsonRPC Error code: -32002' in str(e):
                    print '当前界面不存在 ： ' + uui_class + ' : ' + uui_text + ' : ' + uui_bounds + '控件'
                    ###重新运行深度触发函数
                    self.init_environment()
                    # self.count = 0
                    self.press_DF()
                elif 'test is not allowed.' == str(e):
                    # print 'Found it!!!'
                    if uui_class + ' : ' + uui_text in self.analysed_button_dict.keys():  ###该控件之前已经被触发过，返回
                        if uui_bounds in self.analysed_button_dict[uui_class + ' : ' + uui_text]:
                            print '该控件已被触发'
                            return None
                    coordinate_list = []
                    x1 = uui_bounds.split('[')[1].split(',')[0]
                    y1 = uui_bounds.split(',')[1].split(']')[0]
                    x2 = uui_bounds.split('][')[1].split(',')[0]
                    y2 = uui_bounds.split(',')[-1].split(']')[0]
                    coordinate_list.append(str(int((int(x1)+int(x2)) / 2)))
                    coordinate_list.append(str(int((int(y1) + int(y2)) / 2)))
                    cmd = ['shell','input','tap']
                    cmd.extend(coordinate_list)
                    ''''''
                    # print cmd
                    self.run_adb_cmd(cmd)
                    self.analysed_button_dict[uui_class + ' : ' + uui_text].append(uui_bounds)
                    time.sleep(2)
                    # self.init_environment()
                    self.count = 0
                    self.press_DF()
                    # time.sleep(5)
                else:
                    return False
        else:
            print '深度优先策略触发APP'
            # print 'continue in 121'
        # time.sleep(3)
        self.device.wait.idle()
        xmll = self.device.dump(self.xml_file_path + str(self.count) + ".xml")
        # if self.count == 0:
        #     print xmll
        dom = xml.dom.minidom.parse(self.xml_file_path + str(self.count) + ".xml")
        root = dom.documentElement
        self.count += 1
        for r in root.getElementsByTagName('node'):
            ui_text = r.getAttribute("text")
            ui_class = r.getAttribute("class")
            ui_bounds = r.getAttribute("bounds")
            if ui_text == '允许' and r.getAttribute('clickable') == 'true':
                ###系统类组件，应该触发
                self.press_DF(ui_text,ui_class,ui_bounds)
            if ui_text == 'OK' and r.getAttribute('clickable') == 'true':
                ###系统类组件，应该触发
                self.press_DF(ui_text, ui_class, ui_bounds)
            if (':' not in ui_text) and r.getAttribute('package') == self.app_pkg and r.getAttribute('clickable') == 'true':    ###ui_text != '' and
                # print ui_class + ' : ' + ui_text
                if uui_class == ui_class and uui_text == ui_text and uui_bounds == ui_bounds:           ###上一次触发的控件仍然存在于当前UI界面中，应该暂时不去触发它
                    back_flag = False
                    continue
                if ui_class + ' : ' + ui_text in self.analysed_button_dict.keys():  ###该控件之前已经被触发过，返回
                    continue
                if ui_class == 'android.widget.RelativeLayout' or ui_class == 'android.view.View':       ###该控件是跳转到主屏幕
                    continue
                print '当前正在触发的控件为 : ' + str(self.count-1) + ' : ' + ui_class + ' : ' + ui_text + ' : ' + ui_bounds
                if self.press_DF(ui_text,ui_class,ui_bounds) == True:
                    if back_flag == True:
                        self.device.wait.idle()
                        self.device.press.back()
                        self.device.wait.update()
                    else:
                        self.device.wait.idle()
                        if uui_text == '':          ###控件文本标签为空，此时应该以坐标触发控件
                            x1 = uui_bounds.split('[')[1].split(',')[0]
                            y1 = uui_bounds.split(',')[1].split(']')[0]
                            x2 = uui_bounds.split('][')[1].split(',')[0]
                            y2 = uui_bounds.split(',')[-1].split(']')[0]
                            self.device.click((int(x1) + int(x2)) / 2, (int(y1) + int(y2)) / 2)
                        else:
                            self.device(text=uui_text, className=uui_class).click()
                        self.device.wait.update()
                else:
                    continue
                back_flag = True
                if self.count == 1:
                    if self.analysing_path not in self.analysed_path:
                        self.analysed_path.append(self.analysing_path)
                        # print '当前已经触发完毕的控件顺序 : '
                        # print self.analysed_path
                    else:                   ###此处表明，该路径已经被触发过，需要考虑是否返回？？？
                        # print 'hehehehe'
                        pass

        return True

    def init_environment(self):
        # print '初始化触发环境'
        for rt,dirs,files in os.walk(self.xml_file_path):
            if files != []:
                for file in files:
                    file_path = rt + '/' + file
                    os.remove(file_path)
        self.analysing_path = []
        self.count = 0
        self.scroll_count = 0

    @validity_confirm_by_time(30,True)
    def handle_ad(self):                                ###处理APP启动时的广告
        self.device.wait.idle()
        print 'APP广告预处理'
        # self.device.dump("hierarchy.xml")
        original_xml = ''
        if os.path.exists(self.xml_file_path + "start.xml") == True:
            with open("/home/cy/桌面/auto_touch_xml/start.xml",'r') as f:
                original_xml = f.read()
        new_xml = self.device.dump(self.xml_file_path + "start.xml")
        update_related_button = []
        other_related_button = []
        # with open("/home/cy/桌面/auto_touch_xml/start.xml",'w+') as f:
        #     f.write(xmll)
        dom = xml.dom.minidom.parse(self.xml_file_path + "start.xml")
        root = dom.documentElement
        for r in root.getElementsByTagName('node'):
            if r.getAttribute('package') == self.app_pkg:
                if '更新' in r.getAttribute('text') or '安装' in r.getAttribute('text') or 'update' in r.getAttribute('text'):
                    # print '更新相关的控件' + ' : ' + r.getAttribute('resource-id') + ' : ' + r.getAttribute('text') + ' : ' + r.getAttribute('class')
                    if r.getAttribute('clickable') == 'true':
                        update_related_button.append(r.getAttribute('resource-id') + ' : ' + r.getAttribute('text') + ' : ' + r.getAttribute('class'))
                else:
                    # print '其他类型的控件' + ' : ' + r.getAttribute('resource-id') + ' : ' + r.getAttribute('text') + ' : ' + r.getAttribute('class')
                    if r.getAttribute('clickable') == 'true':
                        other_related_button.append(r.getAttribute('resource-id') + ' : ' + r.getAttribute('text') + ' : ' + r.getAttribute('class'))
                if r.getAttribute('scrollable') == 'true' and (original_xml != new_xml) and self.scroll_count < 10:
                    print '存在划窗'
                    x1 = r.getAttribute('bounds').split('[')[1].split(',')[0]
                    y1 = r.getAttribute('bounds').split(',')[1].split(']')[0]
                    x2 = r.getAttribute('bounds').split('][')[1].split(',')[0]
                    y2 = r.getAttribute('bounds').split(',')[-1].split(']')[0]
                    # print "(%s,%s),(%s,%s)" % (x1,y1,x2,y2)
                    # print 0.9*int(x2)
                    # print 0.9*int(y2)
                    # print 0.9*int(x1)
                    # print 0.9*int(y1)
                    # self.device.swipe(0.9*int(x2),0.9*int(y2),0.9*int(x2),0.9*int(y1))
                    self.device.swipe(0.9 * int(x2), 0.9 * int(y2), 0.9 * int(x1), 0.9 * int(y2))
                    self.device.wait.idle()
                    self.scroll_count += 1
                    self.handle_ad()
                    # print 1.1*int(x1)
                    # print 1.1*int(y1)
                    # print 0.9*int(x2)
                    # print 0.9*int(y2)
                if '跳过' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                    self.device(resourceId=r.getAttribute('resource-id')).click()
                    self.device.wait.idle()
                    self.handle_ad()
                if '忽略' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                    self.device(resourceId=r.getAttribute('resource-id')).click()
                    self.device.wait.idle()
                    self.handle_ad()
                if '以后再说' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                    self.device(resourceId=r.getAttribute('resource-id')).click()
                    self.device.wait.idle()
                    self.handle_ad()
            if '允许' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                self.device(resourceId=r.getAttribute('resource-id')).click()
                self.device.wait.idle()
                self.handle_ad()
            if '确定' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                self.device(text=r.getAttribute('text'),className=r.getAttribute('class'),resourceId=r.getAttribute('resource-id')).click()
                print '已经触发 ‘确定’ 按钮'
                self.device.wait.idle()
                self.handle_ad()
            if '取消' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                self.device(text=r.getAttribute('text'),className=r.getAttribute('class'),resourceId=r.getAttribute('resource-id')).click()
                print '已经触发 ‘取消’ 按钮'
                self.device.wait.idle()
                self.handle_ad()
            if 'Yes' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                self.device(text=r.getAttribute('text'),className=r.getAttribute('class'),resourceId=r.getAttribute('resource-id')).click()
                print '已经触发 ‘Yes’ 按钮'
                self.device.wait.idle()
                self.handle_ad()
            if 'No' in r.getAttribute('text') and r.getAttribute('clickable') == 'true':
                self.device(text=r.getAttribute('text'),className=r.getAttribute('class'),resourceId=r.getAttribute('resource-id')).click()
                print '已经触发 ‘取消’ 按钮'
                self.device.wait.idle()
                self.handle_ad()

        if update_related_button != []:
            for button in other_related_button:
                if button.split(' : ')[-1] == 'android.widget.TextView':
                    continue
                elif button.split(' : ')[-1] == 'android.widget.ScrollView':
                    continue
                elif button.split(' : ')[0] == '':
                    continue
                else:
                    # print '开始触发 : ' + button.split(' : ')[0]
                    self.device(resourceId=button.split(' : ')[0]).click()

    @validity_confirm_by_fileNum(3,'/home/cy/桌面/11-14PcapCatch/ApkXml',False)
    def run(self):
        self.init_environment()
        cmd = ['shell','am','start','-n',self.start_str]
        self.run_adb_cmd(cmd)
        # time.sleep(10)
        self.device.wait.update()
        self.device.wait.idle()
        self.handle_ad()
        time.sleep(5)
        while(self.auto_touch_count < 3):
            try:
                self.press_DF()
                break
            except Exception as e:
                if 'UiObjectNotFoundException' in str(e):
                    print e
                    self.init_environment()
                    continue
                else:
                    print e
                    break

@TimeoutExceptionYcao.timelimited(120)
def mains(Emu,start_str,xmlFilePath):
    d = Device(Emu)
    if start_str == '':
        print 'Start string is blank.Error!'
        return None
    else:
        instance = instance_control(d,start_str,xmlFilePath)
        instance.run()




def test():
    time.sleep(1)
    print 'aaa'
    raise Exception('He He!!')

if __name__ == '__main__':
    # try:
    #     test()
    #     print 'Test Falied'
    # except Exception as e:
    #     print e
    #     print 'Test success'

    if len(sys.argv) == 3:
        mains("",sys.argv[1],sys.argv[2])
    elif len(sys.argv) == 4:
        mains(sys.argv[1],sys.argv[2],sys.argv[3])

    # d=Device('CVH7N16B02000162')
    # print d
    # instance = instance_control(d,'com.sankuai.meituan.takeoutnew/com.sankuai.meituan.takeoutnew.ui.page.boot.WelcomeActivity')
    # instance.run()



    # cmd = ['adb','devices']
    # cmd_process = subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # ret = cmd_process.communicate()
    # for i in range(0,len(ret) - 1):
    #     print ret[i].split('\n')[1]
    #     device_num = ret[i].split('\n')[1]
    # print time.time()
    # thread = threading.Thread(target=mains(device_num,'com.sankuai.meituan.takeoutnew/com.sankuai.meituan.takeoutnew.ui.page.boot.WelcomeActivity',))
    # thread.start()
    # thread.join(120)
    # print time.time()
else:
    pass


    # press_DF(d)

    # d.dump("hierarchy.xml")
    # xml=d.dump()
    # print xml
    # d(resourceId='com.sankuai.meituan.takeoutnew:id/bc1').click()

    # print d.info
    # d.screen.off()
    # time.sleep(5)
    # d.wakeup()
    # d.notification()
    # d.press.back()
    # d.freeze_rotation(False)
    # d.dump("hierarchy.xml")
    # xml=d.dump()
    # print xml
    # d(text="排行榜",className="android.widget.TextView").click()
    # d(text="哔哩哔哩",className="android.widget.TextView").click()

    # tv.danmaku.bili/tv.adnmaku.bilibi.ui.splash.SplashActivity    tv.danmaku.bili/tv.danmaku.bili.ui.splash.SplashActivity
