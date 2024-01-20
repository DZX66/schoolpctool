#encoding=utf-8
import psutil
from shutil import copyfile
from datetime import datetime
from time import sleep
from os.path import exists,join
from os import remove,getlogin
import subprocess
import traceback
from sys import exit
def log(log):
    f = open("D:/schoolpctool_update_log.txt","a+",encoding="utf-8")
    f.write("["+datetime.strftime(datetime.now(),'%H:%M:%S')+"]"+log+"\n")
    f.close()
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
def try_remove(path):
    if exists(path):
        remove(path)
if __name__=="__main__":
    try:
        f = open("D:/schoolpctool_update_log.txt","w",encoding="utf-8")
        f.close()
        if not exists("D:/tools/UPDATEPREPARED"):
            f=open("D:/tools/UPDATEPREPARED","w",encoding="utf-8")
            f.close()
        #等待主程序结束
        waittime=0
        wait_start_seconds=20
        sleep(3)
        while ifProcessRunning("schoolpctool.exe")=="PROCESS_IS_RUNNING":
            sleep(1)
            waittime+=1
            if waittime>=wait_start_seconds:
                log("timeout:已等待"+str(wait_start_seconds)+"秒，主程序还未结束。")
                r = subprocess.Popen("taskkill /F /IM schoolpctool.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
                sleep(5)
                if ifProcessRunning("schoolpctool.exe")=="PROCESS_IS_RUNNING":
                    log("尝试结束主程序，但未成功。")
                    exit()
        try_remove("D:/tools/schoolpctool.exe")
        try_remove("D:/spt_config.exe")
        try_remove("D:/spt_emergency.exe")
        try_remove("D:/spt_console.exe")
        try_remove("D:/tools/config")
        try_remove(join("C:/Users/",getlogin(),"spt_config_backup"))
        try_remove("D:/tools/UPDATEPREPARED")
        r = subprocess.Popen("schtasks /delete /tn schoolpctool_update /F", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #删除更新程序自启
        log(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
        #复制新文件
        copyfile("D:/tools/update/schoolpctool.exe","D:/tools/schoolpctool.exe")
        copyfile("D:/tools/update/spt_console.exe","D:/spt_console.exe")
        copyfile("D:/tools/update/icon.ico","D:/tools/icon.ico")
        #...
        f=open("D:/tools/UPDATEFINISHED","w",encoding="utf-8")
        f.close()
        subprocess.Popen("start D:/tools/schoolpctool.exe", shell=True, stdout=subprocess.PIPE, creationflags=0x08000000) #启动
        exit()
    except Exception as e:
        log(traceback.format_exc())