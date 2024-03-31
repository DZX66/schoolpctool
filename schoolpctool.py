#encoding=utf-8
import psutil
import win32gui
import win32con
import win32api
import subprocess
import multiprocessing
import win10toast
import json
import re
import zipfile
import base64
import requests
import traceback
from datetime import datetime
from win32com.client import Dispatch
from time import sleep,time,strptime,mktime
from win32process import GetWindowThreadProcessId
from os.path import exists,join,isfile
from os import remove,listdir,getlogin,mkdir,walk,rmdir
from sys import exit
from shutil import copyfile
import lang as language


def log(log:str):
    '''写日志'''
    f = open("D:/schoolpctool_log.txt","a+",encoding="utf-8")
    f.write("["+datetime.strftime(datetime.now(),'%H:%M:%S')+"]"+log+"\n")
    f.close()

def get_window_pidandpath(hwnd:int):
    '''根据句柄获取pid和程序路径
    return:(path,pid)
    if it catches exception, return None'''
    try:
        pid=GetWindowThreadProcessId(hwnd)[1]
        process=psutil.Process(pid)
        return (process.exe(),pid)
    except Exception:
        return None

def delete_special_symbols(string:str):
    '''删去,./<>?等标点'''
    sp_symbols=(",",".","/",";","'","[","]","\\","-","=","`","~","<",">","?",":",'"',"{","}","|","_","+","，","。","、","？","‘","’","“","”","——","·"," ","!","@","#","$","%","^","&","*","(",")","！","￥","……","（","）")
    for i in sp_symbols:
        string=string.replace(i,"")
    return string

def ifProcessRunning(process_name:str):
    """判断某个程序是否在运行。原理：获取正在运行程序的pid，通过pid获取程序名，再按程序名进行判断"""
    pl = psutil.pids()
    result = "PROCESS_IS_NOT_RUNNING"
    for pid in pl:
        try:
            if (psutil.Process(pid).name() == process_name):
                if isinstance(pid, int):
                    result = "PROCESS_IS_RUNNING"
        except:
            pass
    return result

def get_all_window() -> tuple[tuple[str,str,str]]:
    '''获取当前所有窗口信息 return:((title,class,hwnd:str)*n)'''
    # 获取所有窗口的句柄
    windows = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, windows)

    # 遍历窗口句柄，获取窗口标题和类名
    window_infos = []
    for hwnd in windows:
        try:
            if win32gui.GetWindowText(hwnd)!="":
                window_infos.append((win32gui.GetWindowText(hwnd),win32gui.GetClassName(hwnd),str(hwnd)))
        except:
            pass

    return window_infos

def timechange(seconds:int,lang: dict[str,str],is_tick:bool=False):
    '''把秒数转化成时段长度表示（x小时x分钟x秒）,若is_tick为真,转化为时刻（x:x:x）'''
    if is_tick:
            h = seconds//3600
            m = seconds%3600//60
            s = seconds%3600%60
            h1 = str(h) if h != 0 else "00"
            m1 = str(m) if m != 0 else "00"
            s1 = str(s) if s != 0 else "00"
            return h1 + ":" + m1 + ":" + s1
    else:
        if seconds<60:
            return str(seconds)+lang["second"]
        elif seconds%60==0 and seconds<3600:
            return str(seconds//60)+lang["minute"]
        elif seconds<3600:
            return str(seconds//60)+lang["minute"]+str(seconds%60)+lang["second"]
        elif seconds%60==0:
            if seconds%3600==0:
                return str(seconds//3600)+lang["hour"]
            else:
                return str(seconds//3600)+lang["hour"]+str(seconds%3600//60)+lang["minute"]
        else:
            if seconds%3600<60:
                return str(seconds//3600)+lang["hour"]+str(seconds%60)+lang["second"]
            else:
                return str(seconds//3600)+lang["hour"]+str(seconds%3600//60)+lang["minute"]+str(seconds%60)+lang["second"]

def lw_log(log:str):
    # 备份
    valid_file="D:/listenwindows_log.txt"
    backup1=join("C:/Users/",getlogin(),"spt_lwlog_backup1.txt")
    backup2="D:/tools/spt_lwlog_backup2.txt"
    # 备份存在性检测
    if (not exists(valid_file)) or (not exists(backup1)) or (not exists(backup2)):
        if exists(backup1):
            copyfile(backup1,valid_file)
            copyfile(backup1,backup2)
        elif exists(backup2):
            copyfile(backup2,valid_file)
            copyfile(backup2,backup1)
        elif exists(valid_file):
            copyfile(valid_file,backup1)
            copyfile(valid_file,backup2)
    # 备份差异性检测
    f1 = open(valid_file,"r",encoding="utf-8")
    b1 = f1.read()
    f1.close()
    f2 = open(backup1,"r",encoding="utf-8")
    b2 = f2.read()
    f2.close()
    f3 = open(backup2,"r",encoding="utf-8")
    b3 = f3.read()
    f3.close()
    if b1==b2 and b1!=b3:
        copyfile(valid_file,backup2)
    elif b1==b3 and b1!=b2:
        copyfile(valid_file,backup1)
    elif b2==b3 and b1!=b2:
        copyfile(backup1,valid_file)
    elif b1!=b2 and b2!=b3 and b1!=b3:
        copyfile(backup1,valid_file)
        copyfile(backup1,backup2)
    # 增加日志
    timenow = datetime.strftime(datetime.now(),'%H:%M:%S')
    f = open(valid_file,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()
    f = open(backup1,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()
    f = open(backup2,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()

def unpack(unzip_dir_path:str,zip_save_path:str,password:str=""):
    '''解压zip文件，unzip_dir_path:保存路径，zip_save_path:zip文件路径，pwd:密码'''
    with zipfile.ZipFile(file=zip_save_path, mode='r',) as zf:
            # 解压到指定目录,首先创建一个解压目录
            if not exists(unzip_dir_path):
                mkdir(unzip_dir_path)
            for old_name in zf.namelist():
                # 获取文件大小，目的是区分文件夹还是文件，如果是空文件应该不好用。
                file_size = zf.getinfo(old_name).file_size
                # 由于源码遇到中文是cp437方式，所以解码成gbk，windows即可正常
                new_name = old_name.encode('cp437').decode('gbk')
                # 拼接文件的保存路径
                new_path = join(unzip_dir_path, new_name)
                # 判断文件是文件夹还是文件
                if file_size > 0:
                   # 是文件，通过open创建文件，写入数据
                    with open(file=new_path, mode='wb') as f:
                        # zf.read 是读取压缩包里的文件内容
                        f.write(zf.read(old_name,pwd=password.encode("utf-8")))
                else:
                    # 是文件夹，就创建
                    mkdir(new_path)

def check_config(config:dict):
    '''检查config完整性'''
    KEYS = ('language', 'is_notice', 'screenshots_path', 'lightframe_path', 'listenwindows_log_max_items', 'wait_lightframe_autostart_seconds', 'allowed_time_start', 'allowed_time_end', 'strict_match', 'mark', 'brokenapps', 'brokenexes', 'white_list', 'key_words', 'broken_sites', 'enable_features')
    for i in KEYS:
        if i not in config:
            return False
    return True

def get_beijin_time():
    '''获取网络时间'''
    try:
        url = 'https://www.baidu.com'
        request_result = requests.get(url=url)
        if request_result.status_code == 200:
            headers = request_result.headers
            net_date = headers.get("date")
            gmt_time = strptime(net_date[5:25], "%d %b %Y %H:%M:%S")
            bj_timestamp = int(mktime(gmt_time) + 8 * 60 * 60)
            return datetime.fromtimestamp(bj_timestamp)
    except Exception as exc:
        return None
    
def org_str(string:str):
    """取消转义，返回原始字符串"""
    a = string
    a = a.replace("\\","\\\\")
    a = a.replace("\n","\\n")
    a = a.replace("\r","\\r")
    a = a.replace("\t","\\t")
    a = a.replace("\b","\\b")
    a = a.replace("\"","\\\"")
    a = a.replace("\'","\\\'")
    a = a.replace("\f","\\f")
    a = a.replace("\a","\\a")
    a = a.replace("\v","\\v")
    return a

# 以下是子进程

def desktop_control(debug: bool,lightframe_path: str,wait_start_seconds: int,screenshots_path: str,is_notice:  bool,enable_rslr: bool,enable_ssm,lang: dict[str,str], desktop_path: str):
    '''桌面相关，包含两个子功能：rslr(restartlightframe)和ssm(screenshotsmove)
    rslr确保lightframe不被关闭，ssm将桌面上的截屏文件移动到D盘'''
    try:
        # 初始化
        rslr_working = enable_rslr
        ssm_working = enable_ssm
        if (not exists(lightframe_path)) and rslr_working:
            log("[dc-rslr]"+lang["not_found"].format(obj=lightframe_path))
            rslr_working = False
        if (not exists(screenshots_path)) and ssm_working:
            mkdir(screenshots_path)
            f = open(join(screenshots_path,lang["ssm_tip"]),"w",encoding="utf-8")
            f.close()
        if desktop_path == "":
            desktop_path = join("C:/Users/",getlogin(),"Desktop")  # 桌面文件夹目录
        if not exists(desktop_path):
            log("[dc]"+lang["not_found"].format(obj=desktop_path))
            exit()
        listening = (("LightFrame.ClocksFrame","LightFrame.Clocks"),("LightFrame.CalendarsFrame","LightFrame.Calendars"))  # rslr窗口标题，类名

        log("[dc]"+lang["start"])

        if rslr_working:
            # 等待lightframe开机自启
            waittime = 0
            while win32gui.FindWindow(listening[0][1], listening[0][0]) == 0 or win32gui.FindWindow(listening[1][1], listening[1][0]) == 0:
                sleep(1)
                waittime += 1
                if waittime>=wait_start_seconds:
                    log("[dc-rslr]"+lang["lightframe_window_missing"].format(str(wait_start_seconds)))
                    if ifProcessRunning("LightFrame.exe")=="PROCESS_IS_NOT_RUNNING":
                        log("[dc-rslr]"+lang["lightframe_is_not_running"])
                        rslr_working = False
                        break
                    else:
                        log("[dc-rslr]"+lang["lightframe_is_running"])
                        rslr_working = False
                        break

            log("[dc-rslr]"+lang["listening_start"])

        while True:
            if debug:
                log("[dc]"+lang["new_loop"])
            
            # rslr
            if rslr_working:
                try:
                    is_needrestart = False
                    # 检测时间窗口
                    hwnd = win32gui.FindWindow(listening[0][1], listening[0][0]) # 获取句柄

                    if hwnd == 0:
                        log("[dc-rslr]"+lang["time_window_missing"])
                        is_needrestart = True
                    
                    # 检测日历窗口
                    hwnd = win32gui.FindWindow(listening[1][1], listening[1][0]) # 获取句柄

                    if hwnd == 0:
                        log("[dc-rslr]"+lang["calendar_window_missing"])
                        is_needrestart = True
                    # 重启lightframe
                    if debug:
                        log("[dc-rslr]is_needrestart:"+str(is_needrestart))
                    if is_needrestart:
                        r = subprocess.Popen("taskkill /F /IM lightframe.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) # 强制结束lightframe
                        log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
                        subprocess.Popen("start "+lightframe_path, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000) # 启动lightframe
                        sleep(4)
                        # 检测是否成功
                        if debug:
                            log("[dc-rslr]"+lang["check_if_success"])

                        hwnd = win32gui.FindWindow(listening[0][1], listening[0][0]) # 获取句柄

                        if hwnd == 0:
                            log("[dc-rslr]"+lang["time_window_restart_failed"])
                            rslr_working=False
                        
                        hwnd = win32gui.FindWindow(listening[1][1], listening[1][0]) # 获取句柄

                        if hwnd == 0:
                            log("[dc-rslr]"+lang["calendar_window_restart_failed"])
                            rslr_working=False
                        if debug:
                            log("[dc-rslr]"+lang["checking_end"])
                except Exception as e:
                    log("[dc-rslr]"+traceback.format_exc())
                    rslr_working = False
            
            # ssm
                        
            if ssm_working:
                try:
                    # 移动文件
                    moved_files = []
                    for i in listdir(desktop_path):
                        if (re.match("^截屏文件.*\.png$",i,flags=re.I) != None) and (isfile(join(desktop_path,i))):
                            try:
                                copyfile(join(desktop_path,i),join(screenshots_path,i))
                                remove(join(desktop_path,i))
                            except PermissionError:
                                pass
                            else:
                                log("[ssm]"+lang["file_move"].format(file=i))
                                if is_notice:
                                    moved_files.append(i)
                    # 通知
                    if is_notice and moved_files!=[]:
                        sleep(3)
                        with open(join("D:/tools/toast/","ssm_"+str(time())),"w",encoding="utf-8") as f:
                            if len(moved_files)>1:
                                f.write("toast\n"+lang["screenshots_sorted"]+"\n"+lang["toast_move_files"].format(file0=moved_files[0],num=str(len(moved_files)))+"\nstart "+screenshots_path+"\n")
                            else:
                                f.write("toast\n"+lang["screenshots_sorted"]+"\n"+lang["toast_move_file"].format(file0=moved_files[0])+"\nstart "+screenshots_path+"\n")
                except Exception as e:
                    log("[dc-ssm]"+traceback.format_exc())
                    ssm_working = False
            sleep(1)
            if not (rslr_working or ssm_working):
                #子进程结束
                log("[dc]"+lang["process_dc_end"])
                exit()
        
    except Exception as e:
        log("[dc]"+traceback.format_exc())

def webblock(brokenexes: tuple[tuple[str, str]],brokenapps: tuple[tuple[str, str]],white_list: tuple[tuple[str, str]],is_notice: bool,is_strict_match: bool,broken_sites: tuple[str],key_words: tuple[str],lang: dict[str,str]):
    '''最大恶魔（什），关闭（有的会删除）违规的窗口'''
    try:
        log("[wb]"+lang["start"])

        r = subprocess.Popen('wmic process where name="schoolpctool.exe" CALL setpriority 256', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) # 给予spt最高资源分配优先级
        ret = str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
        ret = ret.replace("\r","")   # 去\r
        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
        log('[wb]'+lang["increase_priority"]+ret)
        while True:
            if broken_sites!=():
                # 检查hosts
                try:
                    # 生成目标hosts文件内容
                    contents = ["\ufeff# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names. Each\n# entry should be kept on an individual line. The IP address should\n# be placed in the first column followed by the corresponding host name.\n# The IP address and the host name should be separated by at least one\n# space.\n#\n# Additionally, comments (such as these) may be inserted on individual\n# lines or following the machine name denoted by a '#' symbol.\n#\n# For example:\n#\n#      102.54.94.97     rhino.acme.com          # source server\n#       38.25.63.10     x.acme.com              # x client host\n\n# localhost name resolution is handled within DNS itself.\n#	127.0.0.1       localhost\n#	::1             localhost\n\n#[!]This hosts file is controlled by schoolpctool,which means it is invalid to edit it.\n\n"]
                    for i in broken_sites:
                        contents.append("127.0.0.1 "+i+"\n")
                    content = "".join(contents)
                    with open("C:\Windows\System32\drivers\etc\hosts","r",encoding="utf-8") as f:
                        hosts = f.read()
                    if hosts!=content:
                        # 覆盖hosts
                        log("[wb]"+lang["write_hosts"])
                        mf = open("D:/model","w",encoding="utf-8")
                        mf.write(content)
                        mf.close()
                        copyfile("D:/model","C:\Windows\System32\drivers\etc\hosts")
                        remove("D:/model")
                except PermissionError:
                    pass
            
            # 检查运行窗口
            all_window = get_all_window()
            for window in all_window:
                if not is_strict_match:
                    # 非严格匹配
                    window_title = delete_special_symbols(window[0])
                else:
                    window_title = window[0]
                # 白名单
                is_allowed = False
                for i in white_list:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        is_allowed = True
                if is_allowed:
                    continue
                # 检测是否违规
                hwnd = int(window[2])
                res = get_window_pidandpath(hwnd)
                if res==None:
                    continue
                banned = False
                # 检查是否违反brokenexes的规则
                for i in brokenexes:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret=str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if lang["access_denied"] in ret:
                            log("[wb]"+lang["no_access"])
                            exit()
                        sleep(1)
                        remove(res[0])
                        log("[wb]"+lang["delete_log"].format(file_path=res[0],window_title=window[0],window_class=window[1],rule_title=i[0],rule_class=i[1]))
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n"+lang["illegal_program"]+"\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+lang["closed_and_deleted"]+"\nstart https://dzx66.github.io/spt_help.html\n")
                        banned = True
                        break
                if banned:
                    continue
                # 检查是否违反brokenapps的规则
                for i in brokenapps:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret = str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if lang["access_denied"] in ret:
                            log("[wb]"+lang["no_access"])
                            exit()
                        log("[wb]"+lang["close_log"].format(window_title=window[0],window_class=window[1],rule_title=i[0],rule_class=i[1]))
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n"+lang["illegal_window"]+"\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+lang["closed"]+"\nstart https://dzx66.github.io/spt_help.html\n")
                        banned = True
                        break
                if banned:
                    continue
                if not is_strict_match:
                    window_title = window_title.casefold()  # 转小写
                # 检查是否违反keywords
                for i in key_words:
                    if not is_strict_match:
                        i = i.casefold()
                    if (i in window_title):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret = str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if lang["access_denied"] in ret:
                            log("[wb]"+lang["no_access"])
                            exit()
                        log("[wb]"+lang["keyword_log"].format(window_title=window[0],window_class=window[1],keyword=i))
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n"+lang["illegal_window"]+"\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+lang["trigger_keyword"].format(keyword=i)+"\nstart https://dzx66.github.io/spt_help.html\n")
                        break
            sleep(1)
            # 紧急暂停
            if exists("D:/tools/EMERGENCY"):
                with open("D:/tools/EMERGENCY","r",encoding="utf-8") as f:
                    content = f.readlines()
                remove("D:/tools/EMERGENCY")
                if content[0][:-1]=="":
                    sleep_time = int(content[1][:-1])
                    with open("D:/model","w",encoding="utf-8") as mf:
                        mf.write("\ufeff# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names. Each\n# entry should be kept on an individual line. The IP address should\n# be placed in the first column followed by the corresponding host name.\n# The IP address and the host name should be separated by at least one\n# space.\n#\n# Additionally, comments (such as these) may be inserted on individual\n# lines or following the machine name denoted by a '#' symbol.\n#\n# For example:\n#\n#      102.54.94.97     rhino.acme.com          # source server\n#       38.25.63.10     x.acme.com              # x client host\n\n# localhost name resolution is handled within DNS itself.\n#	127.0.0.1       localhost\n#	::1             localhost\n\n")
                    copyfile("D:/model","C:\Windows\System32\drivers\etc\hosts")
                    remove("D:/model")
                    log("[wb]"+lang["suspend"])
                    if is_notice:
                        with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                            f.write("toast\n"+lang["suspend_title"]+"\n"+lang["suspend_content"].format(time=timechange(sleep_time,lang))+"\nstart https://dzx66.github.io/spt_help.html\n")
                    sleep(sleep_time)
                else:
                    log("[wb]"+lang["suspend_wrong_password"])

    except Exception as e:
        log("[wb]"+traceback.format_exc())

def listenwindows(log_max_items: int,lang: dict[str,str]):
    '''监听并记录打开的窗口'''
    try:
        # 删除多余的记录
        with open("D:/listenwindows_log.txt","a+",encoding="utf-8") as f1:
            f1.seek(0)
            content = f1.readlines()
            if len(content)>=log_max_items:
                over = len(content)-log_max_items
                content = content[-log_max_items:]
                f1.close()
                f = open("D:/listenwindows_log.txt","w",encoding="utf-8")
                for i in content:
                    f.write(i)
                f.close()
                copyfile("D:/listenwindows_log.txt",join("C:/Users/",getlogin(),"spt_lwlog_backup1.txt"))
                copyfile("D:/listenwindows_log.txt","D:/tools/spt_lwlog_backup2.txt")
                log("[lw]"+lang["log_overflow"].format(num=str(over)))
        # 初始化
        windows = get_all_window()
        lw_log("\n"+datetime.strftime(datetime.now(),'%Y-%m-%d')+"\n")
        log("[lw]"+lang["start"])
        listening: dict[tuple[str,str,str],float] = {}  # 关注的窗口
        sleep(5)
        last_log = ("","")
        while True:
            new_windows = get_all_window()
            for i in new_windows:
                if i not in windows:
                    listening[i] = time()
            for i in windows:
                if i not in new_windows and i in listening:
                    if last_log[0]==i[0] and last_log[1]==i[1]:
                        lw_log(lang["close_window"]+ lang["same"]+"["+i[2]+"]"+lang["time_use"]+timechange(int(time()-listening[i]),lang))
                    else:
                        lw_log(lang["close_window"]+i[0]+"("+i[1]+")"+"["+i[2]+"]"+lang["time_use"]+timechange(int(time()-listening[i]),lang))
                    last_log = (i[0],i[1])
                    listening.pop(i)
            windows = new_windows
            sleep(1)
            # 响应控制台获取当前运行的窗口
            if exists("D:/tools/GETWINDOWS"):
                remove("D:/tools/GETWINDOWS")
                with open("D:/tools/WINDOWS","w",encoding="utf-8") as f:
                    for i in windows:
                        if i in listening:
                            f.write(i[0]+"\t("+i[1]+")\t["+i[2]+"]\t持续时间:"+str(timechange(int(time()-listening[i]),lang))+"\n")
                        else:
                            f.write(i[0]+"\t("+i[1]+")\t["+i[2]+"]\t自启动时便存在\n")
                            
    except Exception as e:
        log("[lw]"+traceback.format_exc())

def automatic_functions(allowed_before_time: int,allowed_after_time: int,lang: dict[str,str]):
    '''开机使做的一次性事情：自动关机(ash)'''
    try:
        log("[ash]"+lang["start"])
        localtimenow = get_beijin_time()
        if localtimenow:
            timenow = int(localtimenow.strftime("%H"))*60+int(localtimenow.strftime("%M"))
            if timenow<allowed_before_time or timenow>allowed_after_time:
                log("[ash]"+lang["illegal_time"]+lang["colon"]+str(timenow)+"<"+str(allowed_before_time)+lang["or"]+str(timenow)+">"+str(allowed_after_time))
                #创建提示文件
                f = open("D:/tools/AUTOSHUTDOWNED","w",encoding="utf-8")
                f.close()
                with open(join("D:/tools/toast/","ash_"+str(time())),"w",encoding="utf-8") as f:
                    f.write("toast\n"+lang["illegal_time"]+"\n"+lang["toast_illegal_time"].format(allowed_time_start=timechange(allowed_before_time*60,lang,True),allowed_time_end=timechange(allowed_after_time*60,lang,True))+"\nstart https://dzx66.github.io/spt_help.html\n")
                sleep(10)
                subprocess.Popen("shutdown /p", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
    except Exception as e:
        log("[ash]"+traceback.format_exc())

def auto_update(version: str,is_notice: bool,lang: dict[str,str]):
    '''自动更新'''
    try:
        sleep(5)
        if exists("D:/tools/AUTOSHUTDOWNED"):
            exit()
        if exists("D:/tools/UPDATEFINISHED"):
            remove("D:/tools/UPDATEFINISHED")
            remove("D:/tools/new_version.zip")
            for root, dirs, files in walk("D:/tools/update", topdown=False):
                for name in files:
                    remove(join(root, name))
                for name in dirs:
                    rmdir(join(root, name))
            rmdir("D:/tools/update")
            if is_notice:
                with open(join("D:/tools/toast/","au_"+str(time())),"w",encoding="utf-8") as f:
                    f.write("toast\n"+lang["auto_updated"]+"\n"+lang["toast_auto_updated"].format(version=version)+"\nstart https://github.com/DZX66/schoolpctool\n")
        #检查更新
        for i in range(3):
            try:
                x = requests.get("https://gitee.com/dzx_3_0/schoolpctool/raw/master/latest_version.txt")
                res = x.text
                if res.split("\r")[0] == "schoolpctool" and res.split("\r")[3] == "schoolpctool":
                    res = res.split("\r")
                elif res.split("\n")[0] == "schoolpctool" and res.split("\n")[3] == "schoolpctool":
                    res = res.split("\n")
                elif res.split("\r\n")[0] == "schoolpctool" and res.split("\r\n")[3] == "schoolpctool":
                    res = res.split("\r\n")
                else:
                    raise Exception(lang["error_illegal_package"].format(content=org_str(res)))
            except Exception as e:
                log("[au]"+traceback.format_exc())
                if i<2:
                    log("[au]"+lang["error_check_update"]+lang["retry"].format(times=str(i+1)))
                else:
                    log("[au]"+lang["error_check_update"])
                    exit()
                sleep(3)
            else:
                break
        
        x = res
        latest_version = x[1]
        download_url = x[2]
        if latest_version==version:
            log("[au]"+lang["latest_version"])
            exit()
        if download_url=="none":
            log("[au]"+lang["no_download_url"].format(latest_version=latest_version))
            exit()
        #下载更新
        log("[au]"+lang["start_download"].format(latest_version=latest_version))
        log("[au]"+lang["download_url"]+download_url)
        for i in range(3):
            try:
                file = requests.get(download_url)
            except Exception as e:
                log("[au]"+traceback.format_exc())
                if i<2:
                    log("[au]"+lang["error_download"]+lang["retry"].format(times=str(i+1)))
                else:
                    log("[au]"+lang["error_download"])
                    exit()
                sleep(3)
            else:
                break
        f = open("D:/tools/new_version.zip","wb")
        f.write(file.content)
        f.close()
        log("[au]"+lang["unpacking"])
        unpack("D:/tools/update","D:/tools/new_version.zip","")
        log("[au]"+lang["add_self_starting"])
        r = subprocess.Popen("schtasks /create /sc onlogon /tn schoolpctool_update /rl highest /tr D:/tools/update/update_process.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) # 添加自启动
        log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
        f = open("D:/tools/UPDATEPREPARED","w",encoding="utf-8")
        f.close()
        log("[au]"+lang["prepared"])
    except Exception as e:
        log("[au]"+traceback.format_exc())

def toaster(mark: str,lang: dict[str,str]):
    '''通知子进程'''
    try:
        if not exists("D:/tools/toast"):
            mkdir("D:/tools/toast")
        toaster = win10toast.ToastNotifier()
        if not exists("D:/tools/icon.ico"):
            log("[toaster]"+lang["icon_missing"])
        log("[toaster]"+lang["start"])
        while True:
            queue = []  # 消息队列
            valid_files = []
            for root, dirs, files in walk("D:/tools/toast", topdown=False):
                for name in files:
                    f = open(join(root, name),"r",encoding="utf-8")
                    content = f.readlines()
                    f.close()
                    if len(content)>=4:
                        if content[0][:-1]=="toast":
                            queue.append((content[1][:-1],content[2][:-1],content[3][:-1]))
                            valid_files.append(join(root, name))
            for i in valid_files:
                remove(i)
            if len(queue)>0:
                title = queue[0][0]
                cmd = queue[0][2]
            try:
                if len(queue)==1:
                    log("[toaster]"+lang["call_toast"].format(title=title,content=queue[0][1]+"\n"+mark,command=cmd))
                    toaster.show_toast(title,queue[0][1]+"\n"+mark,duration=5,callback_on_click=lambda:subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000),icon_path="D:/tools/icon.ico")
                elif len(queue)>1:
                    is_same_title = True
                    for i in queue:
                        if i[0]!=title:
                            is_same_title = False
                    is_same_cmd = True
                    for i in queue:
                        if i[2]!=cmd:
                            is_same_cmd = False
                    contents = ""
                    for i in queue:
                        contents += i[1]+"\n"
                    if is_same_title and is_same_cmd:
                        log("[toaster]"+lang["call_toast"].format(title=title,content=contents+mark,command=cmd))
                        toaster.show_toast(title,contents+mark,duration=5,callback_on_click=lambda:subprocess.Popen(i[2], shell=True, stdout=subprocess.PIPE, creationflags=0x08000000),icon_path="D:/tools/icon.ico")
                    elif is_same_title:
                        log("[toaster]"+lang["call_toast"].format(title=title,content=contents+mark,command="None"))
                        toaster.show_toast(title,contents+mark,duration=5,callback_on_click=None,icon_path="D:/tools/icon.ico")
                    else:
                        log("[toaster]"+lang["call_toast"].format(title=lang["toast_title_default"],content=contents+mark,command="None"))
                        toaster.show_toast("schoolpctool通知",contents+mark,duration=5,callback_on_click=None,icon_path="D:/tools/icon.ico")
            except Exception as e:
                error = traceback.format_exc()
                log("[toaster]"+error)
                log("[toaster]"+lang["error_toasting"])
                if "pywintypes.error: (-2147467259, 'Shell_NotifyIcon'," in error:
                    log("[toaster]"+lang["explorer_crashing"])
                    exit()
            sleep(5)
    except Exception as e:
        log("[toaster]"+traceback.format_exc())

def backup_docs(target_dir: str,lang: dict[str,str],hard_drive_syms: tuple[str],types: tuple[str]):
    '''自动备份文档'''
    try:
        log("[bd]"+lang["start"])
        recent_dir = join("C:/Users/",getlogin(),"AppData/Roaming/Microsoft/Windows/Recent")
        if not exists(recent_dir):
            log("[bd]"+lang["recent_dir_not_found"].format(path=recent_dir))
            exit()
        if not exists(target_dir):
            mkdir(target_dir)
        last_files = []
        for a,b,c in walk(recent_dir):
            if a == recent_dir:
                last_files = c
        shell = Dispatch("WScript.Shell")
        while True:
            files = []
            for a,b,c in walk(recent_dir):
                if a == recent_dir:
                    files = c
            for i in files:
                is_target = False
                for u in types:
                    if i.endswith(u+".lnk"):
                        is_target = True
                if is_target:
                    if i not in last_files:
                        shortcut = shell.CreateShortCut(join(recent_dir,i))
                        org_file : str = shortcut.TargetPath
                        is_in_u_disk = True
                        for u in hard_drive_syms:
                            if org_file.startswith(u):
                                is_in_u_disk = False
                        if is_in_u_disk:
                            try:
                                copyfile(org_file,join(target_dir,i[:-4]))
                            except FileNotFoundError:
                                pass
                            except PermissionError:
                                pass
                            else:
                                log("[bd]"+lang["file_backuped"].format(org=org_file,target_dir=target_dir))
            last_files = files
            sleep(3)
        
    except Exception as e:
        log("[bd]"+traceback.format_exc())

if __name__=="__main__":
    try:
        multiprocessing.freeze_support()  # 防止一直开子进程

        VERSION = "beta0.34"

        # 检测自动更新提示准备完成文件
        if exists("D:/tools/UPDATEPREPARED"):
            exit()
        # 检测提示文件
        if exists("D:/tools/AUTOSHUTDOWNED"):
            remove("D:/tools/AUTOSHUTDOWNED")
        elif exists("D:/tools/UPDATEFINISHED"):
            pass
        else:
            f = open("D:/schoolpctool_log.txt","w",encoding="utf-8")
            f.close()
        # 创建版本提示文件
        with open("D:/tools/VERSION","w",encoding="utf-8") as f:
            f.write(VERSION)
        
        CONFIG_DEFAULT = {"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"backup_types":(".doc",".docx",".ppt",".pptx",".pdf",".xls",".xlsx",".mp4",".mp3",".wav",".gsp",".png",".jpg",".jpeg",".mov",".ogg",".m4a"),"backup_docs_dir":"D:/backup_docs","hard_drive_syms":("C","D"),"enable_features":{"restartlightframe":False,"webblock":False,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True,"backup_docs":True},"desktop_path":""}
        CONFIG_A = {"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"backup_types":(".doc",".docx",".ppt",".pptx",".pdf",".xls",".xlsx",".mp4",".mp3",".wav",".gsp",".png",".jpg",".jpeg",".mov",".ogg",".m4a"),"backup_docs_dir":"D:/backup_docs","hard_drive_syms":("C","D"),"enable_features":{"restartlightframe":False,"webblock":False,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True,"backup_docs":True},"desktop_path":""}
        CONFIG_B = {"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","交错战线","第五人格","scp","芙宁娜","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"backup_types":(".doc",".docx",".ppt",".pptx",".pdf",".xls",".xlsx",".mp4",".mp3",".wav",".gsp",".png",".jpg",".jpeg",".mov",".ogg",".m4a"),"backup_docs_dir":"D:/backup_docs","hard_drive_syms":("C","D"),"enable_features":{"restartlightframe":False,"webblock":False,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True,"backup_docs":True},"desktop_path":""}
        CONFIG_C = {"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"Ciallo～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$"),("^更改日期和时间$","^Shell_Dialog$"),("^资源监视器$","^WdcWindow$"),("^Everything$","^EVERYTHING$"),("^磁盘管理$","^MMCMainFrame$"),("^.*Edge.*$",".*")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$"),("^哔哩哔哩安装向导$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$"),("^.*智学网.*$",".*"),("^.*微信文件传输助手网页版.*$",".*"),("^.*pdf.*$",".*"),("^.*新标签页.*$",".*"),("^.*无标题.*$",".*"),("^.*zhixue.*$",".*"),("^.*weixin.*$",".*"),("^.*schoolpctool.*$",".*"),("^.*以观书法.*$",".*"),("^.*成绩报告.*$",".*"),("^.*试卷.*$",".*"),("^.*账号.*$",".*")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","千恋万花","柚子社","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","魔女的夜宴","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","","赛马娘","闪耀优俊少女","","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","强制删除","unlocker","uninstall","","新闻","热搜","⚪神","强制关闭","交错战线","adguard","第五人格","microsoftstore","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www..com', '.com', '.cn', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'www..com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com","baijiahao.baidu.com","top.baidu.com"),"backup_types":(".doc",".docx",".ppt",".pptx",".pdf",".xls",".xlsx",".mp4",".mp3",".wav",".gsp",".png",".jpg",".jpeg",".mov",".ogg",".m4a"),"backup_docs_dir":"D:/backup_docs","hard_drive_syms":("C","D"),"enable_features":{"restartlightframe":False,"webblock":False,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True,"backup_docs":True},"desktop_path":""}
        CONFIG_DEBUG = {"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":(),"backup_types":(".doc",".docx",".ppt",".pptx",".pdf",".xls",".xlsx",".mp4",".mp3",".wav",".gsp",".png",".jpg",".jpeg",".mov",".ogg",".m4a"),"hard_drive_syms":("C","D"),"backup_docs_dir":"D:/backup_docs","enable_features":{"restartlightframe":False,"webblock":False,"screenshotsmove":False,"listenwindows":True,"autoshutdown":False,"autoupdate":True,"backup_docs":False},"desktop_path":""}
        # 读取配置文件或备份
        if exists("D:/tools/DEBUG"):
            config = CONFIG_DEBUG
            log("[parent process]debug mode.")
        else:
            is_exists1 = exists("D:/tools/config")
            if is_exists1:
                is_failed1 = False
                try:
                    #读取D:/tools/config
                    f = open("D:/tools/config","r",encoding="utf-8")
                    datar = str(base64.b64decode(f.read().encode("utf-8")),encoding="utf-8")
                    f.close()
                    f2 = open("D:/spt_temp.json","w",encoding="utf-8")
                    f2.write(datar)
                    f2.close()
                    f2 = open("D:/spt_temp.json","r",encoding="utf-8")
                    config = json.load(f2)
                    f2.close()
                    remove("D:/spt_temp.json")
                    if not check_config(config):
                        raise ValueError("config file is not completed.")
                except:
                    log("[parent process]"+traceback.format_exc())
                    log("[parent process]To read D:/tools/config is failed.")
                    is_failed1 = True
                else:
                    copyfile("D:/tools/config",join("C:/Users/",getlogin(),"spt_config_backup"))
            if (not is_exists1) or is_failed1:
                is_exists2 = exists(join("C:/Users/",getlogin(),"spt_config_backup"))
                if is_exists2:
                    is_failed2 = False
                    try:
                        # 读取备份
                        f = open(join("C:/Users/",getlogin(),"spt_config_backup"),"r",encoding="utf-8")
                        datar = str(base64.b64decode(f.read().encode("utf-8")),encoding="utf-8")
                        f.close()
                        f2 = open("D:/spt_temp.json","w",encoding="utf-8")
                        f2.write(datar)
                        f2.close()
                        f2 = open("D:/spt_temp.json","r",encoding="utf-8")
                        config = json.load(f2)
                        f2.close()
                        remove("D:/spt_temp.json")
                        if not check_config(config):
                            raise ValueError("config file is not completed.")
                    except:
                        log("[parent process]"+traceback.format_exc())
                        log("[parent process]To read backup is failed.")
                        is_failed2 = True
                    else:
                        copyfile(join("C:/Users/",getlogin(),"spt_config_backup"),"D:/tools/config")
                if (not is_exists2) or is_failed2:
                    # 创建配置文件
                    if exists("D:/tools/SPE_A"):
                        config = CONFIG_A
                    elif exists("D:/tools/SPE_B"):
                        config = CONFIG_B
                    elif exists("D:/tools/SPE_C"):
                        config = CONFIG_C
                    elif exists("D:/tools/DEBUG"):
                        config = CONFIG_DEBUG
                    else:
                        config = CONFIG_DEFAULT
                    f = open("D:/tools/config","w",encoding="utf-8")
                    datar = json.dumps(config, sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False)
                    f.write(str(base64.b64encode(datar.encode("utf-8")),encoding="utf-8"))
                    f.close()
                    win32api.SetFileAttributes('D:/tools/config', win32con.FILE_ATTRIBUTE_HIDDEN)
                    copyfile("D:/tools/config",join("C:/Users/",getlogin(),"spt_config_backup"))
        # 设置语言
        if config["language"]=="zh-cn":
            lang = language.zh_cn
        elif config["language"]=="jp":
            lang = language.jp
        else:
            lang = language.en
        
        # autoshutdown子进程有特殊性，提前启动
        if config['enable_features']['autoshutdown']:
            ash = multiprocessing.Process(target=automatic_functions,args=(config['allowed_time_start'],config['allowed_time_end'],lang))
            ash.start()
            
        # 等待时间同步
        get_time_fails = 0
        while True:
            it = get_beijin_time()
            if it:
                internet_time = it.timestamp()
                local_time = datetime.now().timestamp()
                if abs(internet_time-local_time) < 10:
                    break
            else:
                get_time_fails += 1
                if get_time_fails >= 5:
                    log("["+lang["parent_process"]+"]"+lang["cannot_get_time"])
                    break
            sleep(5)
        # 启动子进程
        log("["+lang["parent_process"]+"]"+lang["parent_begin"].format(version=VERSION)+str(config))
        # rslr=restartlightframe;lw=listenwindows;wb=webblock;ssm=screenshotsmove;ash=autoshutdown;au=autoupdate
        if config['enable_features']['restartlightframe'] or config['enable_features']['screenshotsmove']:
            dc = multiprocessing.Process(target=desktop_control,args=(False,config['lightframe_path'],config["wait_lightframe_autostart_seconds"],config['screenshots_path'],config["is_notice"],config['enable_features']['restartlightframe'],config['enable_features']['screenshotsmove'],lang,config["desktop_path"]))
            dc.start()
        if config['enable_features']['listenwindows']:
            lw = multiprocessing.Process(target=listenwindows,args=(config["listenwindows_log_max_items"],lang))
            lw.start()
        if config['enable_features']['webblock']:
            wb = multiprocessing.Process(target=webblock,args=(tuple(config['brokenexes']),tuple(config['brokenapps']),tuple(config["white_list"]),config["is_notice"],config["strict_match"],tuple(config["broken_sites"]),tuple(config["key_words"]),lang))
            wb.start()
        if config['enable_features']['autoupdate']:
            ash = multiprocessing.Process(target=auto_update,args=(VERSION,config["is_notice"],lang))
            ash.start()
        if config["is_notice"]:
            toast = multiprocessing.Process(target=toaster,args=(config["mark"],lang))
            toast.start()
        if config['enable_features']['backup_docs']:
            bd = multiprocessing.Process(target=backup_docs,args=(config["backup_docs_dir"],lang,config["hard_drive_syms"],config["backup_types"]))
            bd.start()
        while True:
            sleep(3600)
            log("["+lang["parent_process"]+"]"+lang["all_is_fine"])
    except Exception as e:
        log("[parent_process]"+traceback.format_exc())
