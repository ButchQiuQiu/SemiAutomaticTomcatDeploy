# coding:utf-8
import os
import time
import sys
import subprocess

"""
@author: 李皓
@create: 2021-07-02 21:04
部署脚本,堡垒机不能ssh客户端直连所以为半自动
"""


def deployProcess(backupPath=None, beManualKill=False):
    """
    部署主要流程
    :return: void
    """
    # 查询tomcat根路径
    tomcatPath = findTomcatPath()
    webappPath = tomcatPath + "/webapps"
    print("tomcat应用目录:" + webappPath)
    # 进入tomcat下的webapps目录,删除所有war包并且上传
    if os.system("cd " + webappPath + " && rm -rf " + webappPath + "/*.war && rz -v") == 0:
        # 查询并且记录war包的应用文件夹-------------------------------------------
        p = os.popen("cd " + webappPath + " && ls *.war")
        searchStr = p.read()
        p.close()
        appDirList = searchStr[:len(searchStr) - 1].split("\n")
        # 整合删除所有应用文件夹命令
        deleteAppDir = "rm -rf " + webappPath + "/"
        for appDir in appDirList:
            deleteAppDir += appDir[:len(appDir) - 4] + " "
        # 如果用户启用了备份功能,开始备份war包
        if backupPath is not None:
            backupWar(tomcatPath, backupPath)
        # 如果用户开启了手动决定kill进程,手动输入后kill进程---------------------------
        if beManualKill:
            try:
                input("已执行上传备份步骤,输入回车后脚本才会Kill掉tomcat重启部署......")
            # catch掉仅回车产生的异常
            except BaseException:
                pass
        # 结束tomcat进程
        os.system("ps -ef | grep tomcat | grep -v grep | cut -c 9-15 | xargs kill -s 9")
        # 如果应用文件夹有待删除的->删除所有应用文件夹
        if deleteAppDir.strip() != ("rm -rf " + webappPath + "/").strip():
            print("删除应用文件夹 命令:" + deleteAppDir)
            os.system(deleteAppDir)
        # 部署项目并且追踪tomcat日志 . TODO 待观察 此子进程将会fork独立出来. 避免随着脚本关闭导致tomcat自动关闭
        subprocess.Popen("cd " + tomcatPath + "/bin && ./startup.sh", shell=True, preexec_fn=os.setsid)
        # 追踪日志
        os.system("tail -f " + tomcatPath + "/logs/catalina.out")
    else:
        print("进入webapps目录/删除/上传失败:" + webappPath + "  ,请检查脚本")
    pass


def findTomcatPath():
    """
    2种方案查询tomcat的根目录
    :return: str,tomcat根目录
    """
    tomcatPath = ""
    # 查询tomcat的进程-----------------------------------------------------------------------
    p = os.popen("ps aux | grep tomcat")
    searchTomcatByProcess = p.read()
    p.close()
    # 如果进程中有tomcat
    if searchTomcatByProcess.find('g.file=') != -1:
        # 解析出tomcat的webapps路径
        tomcatPath = searchTomcatByProcess[
                     searchTomcatByProcess.find('g.file=') + 7:searchTomcatByProcess.find('/conf/l')]
    # 否则,搜索tomcat路径-----------------------------------------------------------------------
    else:
        print("tomcat未启动,开始搜索tomcat路径......")
        p = os.popen("find / -name *tomcat-juli.jar*")
        searchTomcatByPathStr = p.read()
        searchTomcatListByPath = searchTomcatByPathStr.strip().split('\n')
        p.close()
        # 循环格式化tomcat路径
        for i in range(0, len(searchTomcatListByPath)):
            searchTomcatListByPath[i] = searchTomcatListByPath[i][:len(searchTomcatListByPath[i]) - 20]
        # 如果只搜索到这一个路径,确认tomcat路径
        if len(searchTomcatListByPath) == 1:
            tomcatPath = searchTomcatListByPath[0]
        # 否则,让用户选择正确的一个tomcat目录
        elif len(searchTomcatListByPath) > 1:
            print("当前系统可能存在多个tomcat目录,请输入以下tomcat目录中正确的那个序号然后回车!!!")
            while True:
                for i in range(0, len(searchTomcatListByPath)):
                    print("序号 " + str(i) + " : " + str(searchTomcatListByPath[i]))
                try:
                    no = input()
                    if no != -1:
                        tomcatPath = searchTomcatListByPath[no]
                        break
                except BaseException:
                    print("输入的非数字/不在序号范围内. 请重新输入")
    if tomcatPath == "":
        print("当前系统未找到tomcat!!!")
        exit()
    return tomcatPath


def backupWar(tomcatWebPath, backupWarPath):
    """
    备份war包
    备份规则:把上传后的war包复制至备份目录
    :param tomcatWebPath:   tomcat的应用目录
    :param backupWarPath:   备份目录
    :return: void
    """
    # 获取备份目录的最新文件夹
    # 查询备份目录下的文件夹排序为最新优先-----------------------------------------------------------------------
    p = os.popen("ls " + backupWarPath + " -t -F | grep '/$'")
    # 获取并处理已备份的最新文件夹
    backedUpNewest = p.read().strip().split('\n')[0]
    p.close()
    # 如果当前文件夹有文件,去除/字符
    if backedUpNewest != "":
        backedUpNewest = backedUpNewest[:len(backedUpNewest) - 1]
    # 备份目录中最新的文件夹
    backedUpDate = backedUpNewest[:8]
    # 需要新建的备份文件夹
    backupPathNewFolder = backupWarPath + "/" + time.strftime("%Y%m%d")
    # 如果也有今日的备份文件夹,新建文件夹时,加上序号+1
    if time.strftime("%Y%m%d") == backedUpDate:
        # 避免int转换时的报错,如果报错,序号默认为1
        try:
            backupPathNewFolder += str(int(backedUpNewest[8:]) + 1)
        except BaseException:
            backupPathNewFolder += "1"
    # 否则,新建文件夹时序号为1
    else:
        backupPathNewFolder += "1"
    # 新建文件夹
    print("新建文件夹命令:" + "mkdir " + backupPathNewFolder)
    if os.system("mkdir " + backupPathNewFolder) == 0:
        # 复制tomcatWebPath路径下的war包
        backupCMD = "cp " + tomcatWebPath + "/webapps/*.war " + backupPathNewFolder
        print("备份命令:" + backupCMD)
        if os.system(backupCMD) == 0:
            pass
        else:
            print("备份失败,请检查脚本. 备份命令:" + backupCMD)
            exit()
    else:
        print("创建备份文件夹失败,请检查脚本......")
        exit()


if __name__ == '__main__':
    # 扫描用户启动时输入的配置参数--------------------
    # 备份目录
    backupPath = None
    # 是否人工决定杀进程. 用于多个服务器同时重启tomcat. 优化用户体验.
    beManualKill = False
    for i in range(1, len(sys.argv)):
        argStr = str(sys.argv[i])
        if argStr[:11] == "backupPath:":
            backupPath = argStr[11:]
        elif argStr == "manualKill":
            beManualKill = True
    # 部署流程-------------------------------------
    deployProcess(backupPath=backupPath, beManualKill=beManualKill)
    print("部署成功")
