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
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__=="__main__":
    if is_admin():
        try:
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
            while password!="":#edited
                print("密码错误")
                password=pwinput.pwinput("输入密码：")
            remove("D:/tools/config")
            f= open("D:/tools/config","w",encoding="utf-8")
            f.write(datar)
            f.close()
            win32api.SetFileAttributes('D:/tools/config', win32con.FILE_ATTRIBUTE_HIDDEN)
            copyfile('D:/tools/config',join("C:/Users/",getlogin(),"spt_config_backup"))
            print("修改完毕")
            if input("是否重启(y/n)?:")=='y':
                subprocess.Popen("shutdown /r /t 0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
        except Exception as e:
            traceback.print_exc()
            input()
    else:
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,__file__,None,1)