#encoding=utf-8
from datetime import datetime
from time import sleep,time,localtime
import psutil
import win32gui
import win32con
import win32api
from win32process import GetWindowThreadProcessId
from os.path import exists,join,isfile
from os import remove,listdir,getlogin,mkdir,walk,rmdir
from sys import exit
import traceback
from shutil import copyfile
import subprocess
import multiprocessing
import win10toast
import json
import re
import zipfile
import base64
import requests

def log(log):
    f = open("D:/schoolpctool_log.txt","a+",encoding="utf-8")
    f.write("["+datetime.strftime(datetime.now(),'%H:%M:%S')+"]"+log+"\n")
    f.close()
def get_window_pidandpath(hwnd):
    '''return:(path,pid)'''
    try:
        pid=GetWindowThreadProcessId(hwnd)[1]
        process=psutil.Process(pid)
        return (process.exe(),pid)
    except Exception:
        return None
def find_window(title, class_name):
    hwnd = win32gui.FindWindow(class_name, title)
    return hwnd
def delete_special_symbols(string:str):
    '''删去,./<>?等标点'''
    sp_symbols=(",",".","/",";","'","[","]","\\","-","=","`","~","<",">","?",":",'"',"{","}","|","_","+","，","。","、","？","‘","’","“","”","——","·"," ","!","@","#","$","%","^","&","*","(",")","！","￥","……","（","）")
    for i in sp_symbols:
        string=string.replace(i,"")
    return string
def webblock(brokenexes,brokenapps,white_list,is_notice,is_strict_match,broken_sites,key_words):
    try:
        log("[wb]启动")

        r = subprocess.Popen('wmic process where name="schoolpctool.exe" CALL setpriority 256', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #给予spt最高资源分配优先级
        ret=str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
        ret = ret.replace("\r","")   # 去\r
        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
        log('[wb]执行wmic process where name="schoolpctool.exe" CALL setpriority 256返回：\n'+ret)
        while True:
            if broken_sites!=():
                #检查hosts
                try:
                    contents=["\ufeff# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names. Each\n# entry should be kept on an individual line. The IP address should\n# be placed in the first column followed by the corresponding host name.\n# The IP address and the host name should be separated by at least one\n# space.\n#\n# Additionally, comments (such as these) may be inserted on individual\n# lines or following the machine name denoted by a '#' symbol.\n#\n# For example:\n#\n#      102.54.94.97     rhino.acme.com          # source server\n#       38.25.63.10     x.acme.com              # x client host\n\n# localhost name resolution is handled within DNS itself.\n#	127.0.0.1       localhost\n#	::1             localhost\n\n#[!]This hosts file is controlled by schoolpctool,which means it is invalid to edit it.\n\n"]
                    for i in broken_sites:
                        contents.append("127.0.0.1 "+i+"\n")
                    content="".join(contents)
                    f = open("C:\Windows\System32\drivers\etc\hosts","r",encoding="utf-8")
                    hosts=f.read()
                    f.close()
                    if hosts!=content:
                        log("[wb]重新写入hosts...")
                        mf=open("D:/model","w",encoding="utf-8")
                        mf.write(content)
                        mf.close()
                        copyfile("D:/model","C:\Windows\System32\drivers\etc\hosts")
                        remove("D:/model")
                except PermissionError:
                    pass
            
            #检查运行程序
            all_window=get_all_window()
            for window in all_window:
                if not is_strict_match:
                    window_title=delete_special_symbols(window[0])
                else:
                    window_title=window[0]
                #白名单
                is_allowed=False
                for i in white_list:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        is_allowed=True
                if is_allowed:
                    continue
                #检测是否违规
                hwnd=int(window[2])
                res=get_window_pidandpath(hwnd)
                if res==None:
                    continue
                banned=False
                for i in brokenexes:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret=str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if "拒绝访问" in ret:
                            log("[wb]权限不足。")
                            exit()
                        sleep(1)
                        remove(res[0])
                        log("[wb]删除了"+res[0]+" 因为"+window[0]+"("+window[1]+")违反："+i[0]+"("+i[1]+")")
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n已禁止违规程序\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+"已关闭并删除\nstart https://dzx66.github.io/spt_help.html\n")
                        banned=True
                        break
                if banned:
                    continue
                for i in brokenapps:
                    if (re.match(i[0],window_title,flags=re.I) != None)and (re.match(i[1],window[1],flags=re.I) != None):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret=str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if "拒绝访问" in ret:
                            log("[wb]权限不足。")
                            exit()
                        log("[wb]关闭了"+window[0]+"("+window[1]+") 因为违反："+i[0]+"("+i[1]+")")
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n已禁止违规窗口\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+"已关闭\nstart https://dzx66.github.io/spt_help.html\n")
                        banned=True
                        break
                if banned:
                    continue
                if not is_strict_match:
                    window_title=window_title.casefold()
                for i in key_words:
                    if not is_strict_match:
                        i = i.casefold()
                    if (i in window_title):
                        r = subprocess.Popen("taskkill /F /PID "+str(res[1]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        ret=str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8")
                        ret = ret.replace("\r","")   # 去\r
                        ret = re.sub(r'\n$', '', ret)  # 去末尾空行
                        log("[wb]"+ret)
                        if "拒绝访问" in ret:
                            log("[wb]权限不足。")
                            exit()
                        log("[wb]关闭了"+window[0]+"("+window[1]+") 因为触发关键词："+i)
                        if is_notice:
                            with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                                f.write("toast\n已禁止违规窗口\n"+(window[0] if len(window[0])<=10 else window[0][:10]+"...")+"触发关键词“"+i+"”\nstart https://dzx66.github.io/spt_help.html\n")
                        break
            sleep(1)
            if exists("D:/tools/EMERGENCY"):
                with open("D:/tools/EMERGENCY","r",encoding="utf-8") as f:
                    content=f.readlines()
                remove("D:/tools/EMERGENCY")
                if content[0][:-1]=="":
                    sleep_time=int(content[1][:-1])
                    mf=open("D:/model","w",encoding="utf-8")
                    mf.write("\ufeff# Copyright (c) 1993-2009 Microsoft Corp.\n#\n# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.\n#\n# This file contains the mappings of IP addresses to host names. Each\n# entry should be kept on an individual line. The IP address should\n# be placed in the first column followed by the corresponding host name.\n# The IP address and the host name should be separated by at least one\n# space.\n#\n# Additionally, comments (such as these) may be inserted on individual\n# lines or following the machine name denoted by a '#' symbol.\n#\n# For example:\n#\n#      102.54.94.97     rhino.acme.com          # source server\n#       38.25.63.10     x.acme.com              # x client host\n\n# localhost name resolution is handled within DNS itself.\n#	127.0.0.1       localhost\n#	::1             localhost\n\n")
                    mf.close()
                    copyfile("D:/model","C:\Windows\System32\drivers\etc\hosts")
                    remove("D:/model")
                    log("[wb]紧急暂停了webblock")
                    if is_notice:
                        with open(join("D:/tools/toast/","wb_"+str(time())),"w",encoding="utf-8") as f:
                            f.write("toast\n紧急暂停\n紧急暂停了webblock功能，持续"+timechange(sleep_time)+"\nstart https://dzx66.github.io/spt_help.html\n")
                    sleep(sleep_time)
                else:
                    log("[wb]检测到紧急暂停标识文件，但密码不匹配")

    except Exception as e:
        log("[wb]"+traceback.format_exc())


def ifProcessRunning(process_name):
    # 判断某个程序是否在运行
    # 原理：获取正在运行程序的pid，通过pid获取程序名，再按程序名进行判断
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
def desktop_control(debug,lightframe_path,wait_start_seconds,screenshots_path,is_notice,enable_rslr,enable_ssm):
    try:
        #初始化
        rslr_working=enable_rslr
        ssm_working=enable_ssm
        if (not exists(lightframe_path)) and rslr_working:
            log("[dc-rslr]未找到"+lightframe_path)
            rslr_working=False
        if (not exists(screenshots_path)) and ssm_working:
            mkdir(screenshots_path)
            f=open(join(screenshots_path,"如需将截屏移动到桌面，请将文件重命名，使之不以“截屏文件”开头"),"w",encoding="utf-8")
            f.close()
        desktop_path=join("C:/Users/",getlogin(),"Desktop")#桌面文件夹目录
        listening=(("LightFrame.ClocksFrame","LightFrame.Clocks"),("LightFrame.CalendarsFrame","LightFrame.Calendars"))#窗口标题，类名

        log("[dc]启动")

        if rslr_working:
            #等待lightframe开机自启
            waittime=0
            while find_window(listening[0][0], listening[0][1]) == 0 or find_window(listening[1][0], listening[1][1]) == 0:
                sleep(1)
                waittime+=1
                if waittime>=wait_start_seconds:
                    log("[dc-rslr]timeout:已等待"+str(wait_start_seconds)+"秒，时间/日历窗口还未启动。")
                    if ifProcessRunning("LightFrame.exe")=="PROCESS_IS_NOT_RUNNING":
                        log("[dc-rslr]lightframe并未运行，请检查自启动。")
                        rslr_working=False
                        break
                    else:
                        log("[dc-rslr]lightframe正在运行，请检查是否设置了时间和日历组件。")
                        rslr_working=False
                        break

            log("[dc-rslr]开始监听。")

        while True:
            if debug:
                log("[dc]新循环")
            
            #rslr
            if rslr_working:
                try:
                    is_needrestart = False
                    #检测时间窗口
                    hwnd = find_window(listening[0][0], listening[0][1]) #获取句柄

                    if hwnd == 0:
                        log("[dc-rslr]时间窗口未找到！重启窗口...")
                        is_needrestart=True
                    
                    #检测日历窗口
                    hwnd = find_window(listening[1][0], listening[1][1]) #获取句柄

                    if hwnd == 0:
                        log("[dc-rslr]日历窗口未找到！重启窗口...")
                        is_needrestart=True
                    if debug:
                        log("[dc-rslr]is_needrestart:"+str(is_needrestart))
                    if is_needrestart:
                        r = subprocess.Popen("taskkill /F /IM lightframe.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束lightframe
                        log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
                        subprocess.Popen("start "+lightframe_path, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000) #启动lightframe
                        sleep(4)
                        #检测是否成功
                        if debug:
                            log("[dc-rslr]检测是否成功...")

                        hwnd = find_window(listening[0][0], listening[0][1]) #获取句柄

                        if hwnd == 0:
                            log("[dc-rslr]时间窗口未重启成功，检查是否设置了时间窗口")
                            rslr_working=False
                        
                        hwnd = find_window(listening[1][0], listening[1][1]) #获取句柄

                        if hwnd == 0:
                            log("[dc-rslr]日历窗口未重启成功，检查是否设置了日历窗口")
                            rslr_working=False
                        if debug:
                            log("[dc-rslr]检测完成")
                except Exception as e:
                    log("[dc-rslr]"+traceback.format_exc())
                    rslr_working=False
            
            #ssm
                        
            if ssm_working:
                try:
                    moved_files=[]
                    for i in listdir(desktop_path):
                        if (re.match("^截屏文件.*\.png$",i,flags=re.I) != None) and (isfile(join(desktop_path,i))):
                            try:
                                copyfile(join(desktop_path,i),join(screenshots_path,i))
                                remove(join(desktop_path,i))
                            except PermissionError:
                                pass
                            else:
                                log("[ssm]移动文件："+i)
                                if is_notice:
                                    moved_files.append(i)
                    if is_notice and moved_files!=[]:
                        sleep(3)
                        with open(join("D:/tools/toast/","ssm_"+str(time())),"w",encoding="utf-8") as f:
                            f.write("toast\n截屏文件已整理\n"+moved_files[0]+("等"+str(len(moved_files))+"个文件" if len(moved_files)>1 else "")+"已移动到“截图”文件夹\nstart "+screenshots_path+"\n")
                except Exception as e:
                    log("[dc-ssm]"+traceback.format_exc())
                    ssm_working=False
            sleep(1)
            if not (rslr_working or ssm_working):
                log("[dc]rslr和ssm都停止了工作，desktop_control子进程结束。")
                exit()
        
    except Exception as e:
        log("[dc]"+traceback.format_exc())

def get_all_window():
    '''return:((title,class,hwnd:str)*n)'''
    # 获取所有窗口的句柄
    windows = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, windows)

    # 遍历窗口句柄，获取窗口标题和类名
    window_infos=[]
    for hwnd in windows:
        try:
            if win32gui.GetWindowText(hwnd)!="":
                window_infos.append((win32gui.GetWindowText(hwnd),win32gui.GetClassName(hwnd),str(hwnd)))
        except:
            pass

    return window_infos

def timechange(seconds:int,is_tick:bool=False):
    '''把秒数转化成时段长度表示（x小时x分钟x秒）,若is_tick为真,转化为时刻（x时x分x秒）'''
    if seconds<60:
        return str(seconds)+"秒"
    elif seconds%60==0 and seconds<3600:
        return str(seconds//60)+("分钟" if not is_tick else "分")
    elif seconds<3600:
        return str(seconds//60)+("分钟" if not is_tick else "分")+str(seconds%60)+"秒"
    elif seconds%60==0:
        if seconds%3600==0:
            return str(seconds//3600)+("小时" if not is_tick else "时")
        else:
            return str(seconds//3600)+("小时" if not is_tick else "时")+str(seconds%3600//60)+("分钟" if not is_tick else "分")
    else:
        return str(seconds//3600)+("小时" if not is_tick else "时")+str(seconds%3600//60)+("分钟" if not is_tick else "分")+str(seconds%60)+"秒"
def lw_log(log):
    #备份
    valid_file="D:/listenwindows_log.txt"
    backup1=join("C:/Users/",getlogin(),"spt_lwlog_backup1.txt")
    backup2="D:/tools/spt_lwlog_backup2.txt"
    #备份存在性检测
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
    #备份差异性检测
    f1 = open(valid_file,"r",encoding="utf-8")
    b1=f1.read()
    f1.close()
    f2 = open(backup1,"r",encoding="utf-8")
    b2=f2.read()
    f2.close()
    f3 = open(backup2,"r",encoding="utf-8")
    b3=f3.read()
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
    #增加日志
    timenow=datetime.strftime(datetime.now(),'%H:%M:%S')
    f = open(valid_file,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()
    f = open(backup1,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()
    f = open(backup2,"a+",encoding="utf-8")
    f.write("["+timenow+"]"+log+"\n")
    f.close()
def listenwindows(log_max_items):
    try:
        with open("D:/listenwindows_log.txt","a+",encoding="utf-8") as f1:
            f1.seek(0)
            content=f1.readlines()
            if len(content)>=log_max_items:
                over=len(content)-log_max_items
                content=content[-log_max_items:]
                f1.close()
                f = open("D:/listenwindows_log.txt","w",encoding="utf-8")
                for i in content:
                    f.write(i)
                f.close()
                copyfile("D:/listenwindows_log.txt",join("C:/Users/",getlogin(),"spt_lwlog_backup1.txt"))
                copyfile("D:/listenwindows_log.txt","D:/tools/spt_lwlog_backup2.txt")
                log("[lw]日志溢出"+str(over)+"条，已删除")
        windows=get_all_window()
        lw_log("\n"+datetime.strftime(datetime.now(),'%Y-%m-%d')+"\n")
        log("[lw]启动")
        listening={}#关注的窗口
        sleep(5)
        last_log=("","")
        while True:
            new_windows=get_all_window()
            for i in new_windows:
                if i not in windows:
                    listening[i]=time()
            for i in windows:
                if i not in new_windows and i in listening:
                    if last_log[0]==i[0] and last_log[1]==i[1]:
                        lw_log("关闭窗口: 同上"+"["+i[2]+"]"+" 用时 "+timechange(int(time()-listening[i])))
                    else:
                        lw_log("关闭窗口:"+i[0]+"("+i[1]+")"+"["+i[2]+"]"+" 用时 "+timechange(int(time()-listening[i])))
                    last_log=(i[0],i[1])
                    listening.pop(i)
            windows=new_windows
            sleep(1)
    except Exception as e:
        log("[lw]"+traceback.format_exc())

def automatic_functions(allowed_before_time,allowed_after_time):
    try:
        log("[ash]启动")
        localtimenow=localtime()
        timenow=localtimenow.tm_hour*60+localtimenow.tm_min
        if timenow<allowed_before_time or timenow>allowed_after_time:
            log("[ash]不正常的时间："+str(timenow)+"<"+str(allowed_before_time)+"或"+str(timenow)+">"+str(allowed_after_time))
            #创建提示文件
            f=open("D:/tools/AUTOSHUTDOWNED","w",encoding="utf-8")
            f.close()
            with open(join("D:/tools/toast/","ash_"+str(time())),"w",encoding="utf-8") as f:
                f.write("toast\n不正常的时间\n当前时间在规定开机时间"+timechange(allowed_before_time*60,True)+"之前，或"+timechange(allowed_after_time*60,True)+"之后，将在10秒后自动关机\nstart https://dzx66.github.io/spt_help.html\n")
            sleep(10)
            subprocess.Popen("shutdown /p", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
    except Exception as e:
        log("[ash]"+traceback.format_exc())
def unpack(unzip_dir_path,zip_save_path,password:str=""):
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
def auto_update(version,is_notice):
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
                    f.write("toast\n已更新至最新版本\n新版本"+version+"已生效，点击可查看更新日志\nstart https://github.com/DZX66/schoolpctool\n")
        #检查更新
        for i in range(3):
            try:
                x=requests.get("https://dzx66.github.io/schoolpctoolversion.txt")
                if x.text.split("\n")[0] != "schoolpctool":
                    raise Exception("返回的内容不正常")
            except Exception as e:
                log("[au]"+traceback.format_exc())
                if i<2:
                    log("[au]检查更新时出错，重新尝试..."+str(i+1)+"/3次")
                else:
                    log("[au]检查更新时出错")
                    exit()
                sleep(3)
            else:
                break
        
        x=x.text.split("\n")
        latest_version = x[1]
        download_url = x[2]
        if latest_version==version:
            log("[au]版本已是最新！")
            exit()
        if download_url=="none":
            log("[au]有最新版本："+latest_version+"，但无下载链接，请稍后重试。")
            exit()
        #下载更新
        log("[au]有最新版本："+latest_version+"，开始下载更新包......")
        log("[au]下载地址："+download_url)
        for i in range(3):
            try:
                file=requests.get(download_url)
            except Exception as e:
                log("[au]"+traceback.format_exc())
                if i<2:
                    log("[au]下载更新包时出错，重新尝试..."+str(i+1)+"/3次")
                else:
                    log("[au]下载更新包时出错")
                    exit()
                sleep(3)
            else:
                break
        f=open("D:/tools/new_version.zip","wb")
        f.write(file.content)
        f.close()
        log("[au]更新包下载完成，开始解压.......")
        unpack("D:/tools/update","D:/tools/new_version.zip","")
        log("[au]解压完成，添加自启动...")
        r = subprocess.Popen("schtasks /create /sc onlogon /tn schoolpctool_update /rl highest /tr D:/tools/update/update_process.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #添加自启动
        log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
        f=open("D:/tools/UPDATEPREPARED","w",encoding="utf-8")
        f.close()
        log("[au]更新已准备完成，等待重启...")
    except Exception as e:
        log("[au]"+traceback.format_exc())

def toaster(mark):
    try:
        if not exists("D:/tools/toast"):
            mkdir("D:/tools/toast")
        toaster=win10toast.ToastNotifier()
        if not exists("D:/tools/icon.ico"):
            log("[toaster]警告：D:/tools/icon.ico不存在，通知的图标无法正常显示！")
        log("[toaster]启动")
        while True:
            queue=[]#消息队列
            valid_files=[]
            for root, dirs, files in walk("D:/tools/toast", topdown=False):
                for name in files:
                    f=open(join(root, name),"r",encoding="utf-8")
                    content=f.readlines()
                    f.close()
                    if content[0][:-1]=="toast":
                        queue.append((content[1][:-1],content[2][:-1],content[3][:-1]))
                        valid_files.append(join(root, name))
            for i in valid_files:
                remove(i)
            if len(queue)>0:
                title=queue[0][0]
                cmd=queue[0][2]
            try:
                if len(queue)==1:
                    log("[toaster]发送了通知\n标题："+title+"\n内容："+queue[0][1]+"\n"+mark+"\n命令："+cmd)
                    toaster.show_toast(title,queue[0][1]+"\n"+mark,duration=5,callback_on_click=lambda:subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000),icon_path="D:/tools/icon.ico")
                elif len(queue)>1:
                    is_same_title=True
                    for i in queue:
                        if i[0]!=title:
                            is_same_title=False
                    is_same_cmd=True
                    for i in queue:
                        if i[2]!=cmd:
                            is_same_cmd=False
                    contents=""
                    for i in queue:
                        contents+=i[1]+"\n"
                    if is_same_title and is_same_cmd:
                        log("[toaster]发送了通知\n标题："+title+"\n内容："+contents+mark+"\n命令："+cmd)
                        toaster.show_toast(title,contents+mark,duration=5,callback_on_click=lambda:subprocess.Popen(i[2], shell=True, stdout=subprocess.PIPE, creationflags=0x08000000),icon_path="D:/tools/icon.ico")
                    elif is_same_title:
                        log("[toaster]发送了通知\n标题："+title+"\n内容："+contents+mark+"\n命令：None")
                        toaster.show_toast(title,contents+mark,duration=5,callback_on_click=None,icon_path="D:/tools/icon.ico")
                    else:
                        log("[toaster]发送了通知\n标题：schoolpctool通知\n内容："+contents+mark+"\n命令：None")
                        toaster.show_toast("schoolpctool通知",contents+mark,duration=5,callback_on_click=None,icon_path="D:/tools/icon.ico")
            except Exception as e:
                error=traceback.format_exc()
                log("[toaster]"+error)
                log("[toaster]发送通知时出错")
                if "pywintypes.error: (-2147467259, 'Shell_NotifyIcon', '未指定的错误')" in error:
                    log("[toaster]估计是explorer.exe崩溃导致的错误，此版本无法解决")
                    exit()
            sleep(5)
    except Exception as e:
        log("[toaster]"+traceback.format_exc())
def check_config(config):
    '''检查config完整性'''
    KEYS=('language', 'is_notice', 'screenshots_path', 'lightframe_path', 'listenwindows_log_max_items', 'wait_lightframe_autostart_seconds', 'allowed_time_start', 'allowed_time_end', 'strict_match', 'mark', 'brokenapps', 'brokenexes', 'white_list', 'key_words', 'broken_sites', 'enable_features')
    for i in KEYS:
        if i not in config:
            return False
    return True
if __name__=="__main__":
    try:
        multiprocessing.freeze_support()

        VERSION="beta0.24"

        #检测自动更新提示准备完成文件
        if exists("D:/tools/UPDATEPREPARED"):
            exit()
        #检测提示文件
        if exists("D:/tools/AUTOSHUTDOWNED"):
            remove("D:/tools/AUTOSHUTDOWNED")
        elif exists("D:/tools/UPDATEFINISHED"):
            pass
        else:
            f=open("D:/schoolpctool_log.txt","w",encoding="utf-8")
            f.close()
        #创建版本提示文件
        with open("D:/tools/VERSION","w",encoding="utf-8") as f:
            f.write(VERSION)
        CONFIG_DEFAULT={"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"enable_features":{"restartlightframe":False,"webblock":True,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True}}
        CONFIG_A={"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"enable_features":{"restartlightframe":False,"webblock":True,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True}}
        CONFIG_B={"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","交错战线","第五人格","scp","芙宁娜","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com"),"enable_features":{"restartlightframe":False,"webblock":True,"screenshotsmove":False,"listenwindows":True,"autoshutdown":True,"autoupdate":True}}
        CONFIG_C={"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"Ciallo～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$"),("^更改日期和时间$","^Shell_Dialog$"),("^资源监视器$","^WdcWindow$"),("^Everything$","^EVERYTHING$"),("^磁盘管理$","^MMCMainFrame$"),("^.*Edge.*$",".*")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$"),("^哔哩哔哩安装向导$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$"),("^.*智学网.*$",".*"),("^.*微信文件传输助手网页版.*$",".*"),("^.*pdf.*$",".*"),("^.*新标签页.*$",".*"),("^.*无标题.*$",".*"),("^.*zhixue.*$",".*"),("^.*weixin.*$",".*"),("^.*schoolpctool.*$",".*"),("^.*以观书法.*$",".*"),("^.*成绩报告.*$",".*"),("^.*试卷.*$",".*"),("^.*账号.*$",".*")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","千恋万花","柚子社","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","魔女的夜宴","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","","赛马娘","闪耀优俊少女","","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","强制删除","unlocker","uninstall","","新闻","热搜","⚪神","强制关闭","交错战线","adguard","第五人格","microsoftstore","幻塔","pvz"),"broken_sites":('ys.mihoyo.com', 'mhyy.mihoyo.com', 'autopatchcn.yuanshen.com', 'sr.mihoyo.com', 'www.bh3.com', 'download-porter.mihoyo.com', 'bundle.bh3.com', 'autopatchcn.bhsr.com', 'www.yuanshen.com', 'www.miyoushe.com', 'genshin.hoyoverse.com', 'a.4399.cn', 'webstatic.mihoyo.com', 'bbs.mihoyo.com', 'www..com', '.com', '.cn', 'www.4399.com', 'news.4399.com', 'my.4399.com', 'ssjj.4399.com', 'www..com', 'h.4399.com', 'www.7k7k.com', 'news.7k7k.com',"www.douyin.com","tieba.baidu.com","baijiahao.baidu.com","top.baidu.com"),"enable_features":{"restartlightframe":True,"webblock":True,"screenshotsmove":True,"listenwindows":True,"autoshutdown":True,"autoupdate":True}}
        CONFIG_DEBUG={"language":"zh-cn","is_notice":True,"screenshots_path":"D:/screenshots","lightframe_path":"D:/lightframe.exe","listenwindows_log_max_items":8000,"wait_lightframe_autostart_seconds":120,"allowed_time_start":390,"allowed_time_end":1290,"strict_match":False,"mark":"～(∠·ω< )⌒★","brokenapps":(("^云·原神$","^Qt5152QWindowIcon$"),("^原神$","^Qt5QWindowIcon$"),("^原神$","^UnityWndClass$"),("^崩坏：星穹铁道$","^Qt5QWindowIcon$"),("^崩坏：星穹铁道$","^UnityWndClass$"),("^任务管理器$","^TaskManagerWindow$"),("^任务计划程序$","^MMCMainFrame$"),("^注册表编辑器$","^RegEdit_RegEdit$"),("^本地组策略编辑器$","^MMCMainFrame$")),"brokenexes":(("^云·原神 安装程序$","^Qt5156QWindowIcon$"),("^崩坏：星穹铁道 安装程序$","^Qt5QWindowIcon$"),("^原神 安装程序$","^Qt5QWindowIcon$")),"white_list":(("^.*$","^OrpheusBrowserHost$"),(".*","^CabinetWClass$"),(".*","^screenClass$"),(".*","^PPTFrameClass$"),(".*","^OpusApp$"),(".*","^XLMAIN$"),(".*","^PP12FrameClass$"),("^WPS.*$","^Qt5QWindowIcon$"),(".*","^GSP5MainWin$")),"key_words":("原神","","genshin","星穹铁道","phigros","游戏","英雄联盟","王者荣耀","伪人","传说之下","undertale","羽毛球","明日方舟","曼德拉记录","崩坏3","碧蓝档案","蔚蓝档案","崩坏三","崩3","bluearchive","我的世界","minecraft","绝区零","米哈游","重返未来","赛马娘","闪耀优俊少女","泰坦陨落","瓦洛兰特","植物大战僵尸","火绒","360官网","卡巴斯基","杀毒","瑞星","金山毒霸","2345安全","360安全","第五人格","幻塔","pvz"),"broken_sites":(),"enable_features":{"restartlightframe":True,"webblock":True,"screenshotsmove":True,"listenwindows":True,"autoshutdown":False,"autoupdate":False}}
        #读取配置文件或备份
        if exists("D:/tools/DEBUG"):
            config=CONFIG_DEBUG
            log("[父进程]debug开启")
        else:
            is_exists1=exists("D:/tools/config")
            if is_exists1:
                is_failed1=False
                try:
                    #读取D:/tools/config
                    f= open("D:/tools/config","r",encoding="utf-8")
                    datar=str(base64.b64decode(f.read().encode("utf-8")),encoding="utf-8")
                    f.close()
                    f2=open("D:/spt_temp.json","w",encoding="utf-8")
                    f2.write(datar)
                    f2.close()
                    f2=open("D:/spt_temp.json","r",encoding="utf-8")
                    config=json.load(f2)
                    f2.close()
                    remove("D:/spt_temp.json")
                    if not check_config(config):
                        raise ValueError("配置文件不完整")
                except:
                    log("[父进程]"+traceback.format_exc())
                    log("[父进程]D:/tools/config读取失败")
                    is_failed1=True
                else:
                    copyfile("D:/tools/config",join("C:/Users/",getlogin(),"spt_config_backup"))
            if (not is_exists1) or is_failed1:
                is_exists2=exists(join("C:/Users/",getlogin(),"spt_config_backup"))
                if is_exists2:
                    is_failed2 = False
                    try:
                        #读取备份
                        f= open(join("C:/Users/",getlogin(),"spt_config_backup"),"r",encoding="utf-8")
                        datar=str(base64.b64decode(f.read().encode("utf-8")),encoding="utf-8")
                        f.close()
                        f2=open("D:/spt_temp.json","w",encoding="utf-8")
                        f2.write(datar)
                        f2.close()
                        f2=open("D:/spt_temp.json","r",encoding="utf-8")
                        config=json.load(f2)
                        f2.close()
                        remove("D:/spt_temp.json")
                        if not check_config(config):
                            raise ValueError("配置文件不完整")
                    except:
                        log("[父进程]"+traceback.format_exc())
                        log("[父进程]备份读取失败")
                        is_failed2=True
                    else:
                        copyfile(join("C:/Users/",getlogin(),"spt_config_backup"),"D:/tools/config")
                if (not is_exists2) or is_failed2:
                    #创建配置文件
                    if exists("D:/tools/SPECIAL_A"):
                        config=CONFIG_A
                    elif exists("D:/tools/SPECIAL_B"):
                        config=CONFIG_B
                    elif exists("D:/tools/SPECIAL_C"):
                        config=CONFIG_C
                    elif exists("D:/tools/DEBUG"):
                        config=CONFIG_DEBUG
                    else:
                        config=CONFIG_DEFAULT
                    f=open("D:/tools/config","w",encoding="utf-8")
                    datar=json.dumps(config, sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False)
                    f.write(str(base64.b64encode(datar.encode("utf-8")),encoding="utf-8"))
                    f.close()
                    win32api.SetFileAttributes('D:/tools/config', win32con.FILE_ATTRIBUTE_HIDDEN)
                    copyfile("D:/tools/config",join("C:/Users/",getlogin(),"spt_config_backup"))
        #启动子进程
        log("[父进程]启动，版本："+VERSION+"，配置：\n"+str(config))
        #rslr=restartlightframe;lw=listenwindows;wb=webblock;ssm=screenshotsmove;ash=autoshutdown;au=autoupdate
        if config['enable_features']['restartlightframe'] or config['enable_features']['screenshotsmove']:
            dc=multiprocessing.Process(target=desktop_control,args=(False,config['lightframe_path'],config["wait_lightframe_autostart_seconds"],config['screenshots_path'],config["is_notice"],config['enable_features']['restartlightframe'],config['enable_features']['screenshotsmove']))
            dc.start()
        if config['enable_features']['listenwindows']:
            lw=multiprocessing.Process(target=listenwindows,args=(config["listenwindows_log_max_items"],))
            lw.start()
        if config['enable_features']['webblock']:
            wb=multiprocessing.Process(target=webblock,args=(tuple(config['brokenexes']),tuple(config['brokenapps']),tuple(config["white_list"]),config["is_notice"],config["strict_match"],tuple(config["broken_sites"]),tuple(config["key_words"])))
            wb.start()
        if config['enable_features']['autoshutdown']:
            ash=multiprocessing.Process(target=automatic_functions,args=(config['allowed_time_start'],config['allowed_time_end']))
            ash.start()
        if config['enable_features']['autoupdate']:
            ash=multiprocessing.Process(target=auto_update,args=(VERSION,config["is_notice"]))
            ash.start()
        if config["is_notice"]:
            toast=multiprocessing.Process(target=toaster,args=(config["mark"],))
            toast.start()
        while True:
            sleep(3600)
            log("[父进程]运行正常。")
    except Exception as e:
        log("[父进程]"+traceback.format_exc())
