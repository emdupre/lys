import cmd, os, traceback

from . import LoadFile
from . import Wave
from .CommandWindow import CommandWindow as cw
from .BasicWidgets import *

class ExtendShell(object):
    def __init__(self,home=None):
        self.__comlog=[]
        self.__ecom=ExtendCommand(self)

    def SendCommand(self,txt,message=True,save=True):
        if message:
            print(">",txt)
        if not len(txt)==0 and save:
            self.__comlog.append(txt)
        if txt=="cd":
            cd()
            return
        if txt=="pwd":
            print(pwd())
            return
        if txt=="exit()" or txt=="exit":
            self.__com.close()
        flg=False
        try:
            tmp=eval(txt,globals())
            if not tmp is None:
                print(tmp)
        except Exception:
            flg=True
        if flg:
            try:
                exec(txt,globals())
            except Exception:
                err=traceback.format_exc()
                try:
                    res=self.__ecom.onecmd(txt)
                except Exception as e:
                    sys.stderr.write('Invalid command.\n')
                    print(err)
    def GetCommandLog(self):
        return self.__comlog
    def SetCommandLog(self,log):
        self.__comlog=log
    def GetDictionary(self):
        return globals()

    def CommandWindow(self):
        self.__com=cw(self)
        return self.__com

    def __GetValidName(self,name):
        flg=True
        number=0
        while flg:
            if name+str(number) in globals():
                number+=1
            else:
                flg=False
        return name+str(number)
    def Load(self,name):
        nam,ext=os.path.splitext(os.path.basename(name))
        nam=self.__GetValidName(nam).replace(" ","_")
        exec(nam+'=LoadFile.load(\''+name+'\')',globals())
        print(nam+' is loaded from '+ext+' file')
        return eval(nam,globals())
    def clearLog(self):
        self.__com.clearLog()

class ExtendCommand(cmd.Cmd):
    def __init__(self,shell):
        self.__shell=shell
    def do_cd(self, arg):
        cd(arg)
    def do_mkdir(self,arg):
        mkdir(arg)
    def do_rm(self,arg):
        remove(arg)
    def do_cp(self,arg):
        lis=arg.split(" ")
    def do_workspace(self,arg):
        lis=arg.split(" ")
        w=lis[0].replace(" ","")
        AutoSavedWindow.SwitchTo(lis[0])
    def do_mv(self,arg):
        lis=arg.split(" ")
        move(lis[0],lis[1])
    def do_rename(self,arg):
        lis=arg.split(" ")
        move(lis[0],lis[1])
    def do_ls(self, arg):
        tmp=os.listdir()
        for file in tmp:
            print(file)
    def do_load(self,arg):
        self.__shell.Load(arg)
    def do_pwd(self,arg):
        print(pwd())
    def do_display(self,arg):
        g=Graph()
        try:
            w=eval(arg,globals())
            g.Append(w)
        except Exception:
            g.Append(arg)
    def do_append(self,arg):
        g=Graph.active()
        if g is None:
            return
        try:
            w=eval(arg,globals())
            g.Append(w)
        except Exception:
            g.Append(arg)
    def do_preview(self,arg):
        lis=arg.split(" ")
        lis2=[]
        for l in lis:
            try:
                lis2.append(eval(l))
            except Exception:
                lis2.append(l)
        PreviewWindow(*lis2)
    def do_clear(self, arg):
        self.__shell.clearLog()
