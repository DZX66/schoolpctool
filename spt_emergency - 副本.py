#encoding=utf-8
import ctypes
import traceback
import sys
import pwinput
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__=="__main__":
    if is_admin():
        try:
            print("这是schoolpctool的webblock的紧急暂停功能。")
            password=pwinput.pwinput("输入密码：")
            while password!="":#edited
                print("密码错误")
                password=pwinput.pwinput("输入密码：")
            f= open("D:/tools/EMERGENCY","w",encoding="utf-8")
            f.close()
        except Exception as e:
            traceback.print_exc()
            input()
    else:
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,__file__,None,1)