#encoding=utf-8
import ctypes
import traceback
import sys
import win32con
import win32api
import base64
import subprocess
from os import remove,system,getlogin
from os.path import exists,join
from shutil import copyfile
import pwinput
from time import sleep
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__=="__main__":
    if is_admin():
        try:
            #检查版本适配
            VERSION="beta0.32"
            if exists("D:/tools/VERSION"):
                with open("D:/tools/VERSION","r",encoding="utf-8") as f:
                    spt_version=f.read()
            else:
                spt_version="unknown"
            system("title schoolpctool控制台"+VERSION)
            while True:
                cmd=""
                while cmd not in ("1","2","3","4","5","6"):
                    system("cls")
                    print("这是schoolpctool的控制台")
                    if VERSION!=spt_version:
                        if spt_version=="unknown":
                            print("D:/tools/VERSION未找到，无法检查版本适配，可能是schoolpctool版本过低（beta0.23及以下）或本机未安装schoolpctool")
                        else:
                            print("版本不适配！本机的schoolpctool版本为"+spt_version+"，而控制台版本为"+VERSION)
                            print("这可能是自动更新出错，或者作者忘了修改控制台版本。")
                        print("针对此问题，你应该检查一下，若确认对使用无影响，可以继续。")
                    system('tasklist /fi "imagename eq schoolpctool.exe"')
                    print("="*10)
                    print("1.修改配置文件")
                    print("2.启用webblock紧急暂停")
                    print("3.查看特殊标识")
                    print("4.打开帮助页")
                    print("5.重启schoolpctool")
                    print("6.关闭schoolpctool")
                    print("="*10)
                    cmd=input("请选择服务：")
                if cmd=="1":
                    #读取配置文件
                    f= open("D:/tools/config","r",encoding="utf-8")
                    datar=str(base64.b64decode(f.read().encode("utf-8")),encoding="utf-8")
                    f.close()
                    f2=open("D:/spt_config_user.json","w",encoding="utf-8")
                    f2.write(datar)
                    f2.close()

                    #主界面
                    if exists(join("C:/Users/",getlogin(),".vscode")):
                        system("start D:\spt_config_user.json")
                    else:
                        print("请用网页版vscode打开D:/spt_config_user.json")
                        system("start https://vscode.dev/")
                    print("请修改后保存")
                    system("pause")
                    f2=open("D:/spt_config_user.json","r",encoding="utf-8")
                    datar=str(base64.b64encode(f2.read().encode("utf-8")),encoding="utf-8")
                    f2.close()
                    remove("D:/spt_config_user.json")
                    password=pwinput.pwinput("输入密码：")
                    while password!="":
                        print("密码错误")
                        password=pwinput.pwinput("输入密码：")
                    remove("D:/tools/config")
                    f= open("D:/tools/config","w",encoding="utf-8")
                    f.write(datar)
                    f.close()
                    win32api.SetFileAttributes('D:/tools/config', win32con.FILE_ATTRIBUTE_HIDDEN)
                    copyfile('D:/tools/config',join("C:/Users/",getlogin(),"spt_config_backup"))
                    print("修改完毕")
                    if input("是否重新启动schoolpctool(y/n)?:")=='y':
                        r=subprocess.Popen("taskkill /F /IM schoolpctool.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                        print(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
                        sleep(2) #等一等
                        subprocess.Popen("start D:/tools/schoolpctool.exe", shell=True, stdout=subprocess.PIPE, creationflags=0x08000000) #启动
                elif cmd=="2":
                    print("这是schoolpctool的webblock的紧急暂停功能。")
                    time="0"
                    while int(time)<=60:
                        time=input("持续时间（单位：秒，默认为3600）：")
                        if time=="":
                            time = "3600"
                        elif int(time)<=60:
                            print("需大于60秒")
                    password=pwinput.pwinput("输入密码：")
                    while password!="":
                        print("密码错误")
                        password=pwinput.pwinput("输入密码：")
                    f= open("D:/tools/EMERGENCY","w",encoding="utf-8")
                    f.write(password+"\n"+time+"\n")
                    f.close()
                elif cmd=="3":
                    tags=("SPE_A","SPE_B","SPE_C","AUTOSHUTDOWNED","UPDATEPREPARED","UPDATEFINISHED","DEBUG","EMERGENCY")
                    for i in tags:
                        if exists(join("D:/tools/",i)):
                            print("存在"+i)
                    system("pause")
                elif cmd=="4":
                    system("start https://dzx66.github.io/spt_help.html")
                elif cmd=="5":
                    password=pwinput.pwinput("输入密码：")
                    while password!="":
                        print("密码错误")
                        password=pwinput.pwinput("输入密码：")
                    r=subprocess.Popen("taskkill /F /IM schoolpctool.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                    print(str(str(r.communicate()[0],"gbk").encode("utf-8"),"utf-8"))
                    sleep(2) #等一等
                    subprocess.Popen("start D:/tools/schoolpctool.exe", shell=True, stdout=subprocess.PIPE, creationflags=0x08000000) #启动
                    system("pause")
                elif cmd=="6":
                    password=pwinput.pwinput("输入密码：")
                    while password!="":
                        print("密码错误")
                        password=pwinput.pwinput("输入密码：")
                    subprocess.Popen("taskkill /F /IM schoolpctool.exe", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000) #强制结束
                    system("pause")
        except Exception as e:
            traceback.print_exc()
            input()
    else:
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,__file__,None,1)