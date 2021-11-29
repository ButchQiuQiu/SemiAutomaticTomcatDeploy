# 说明

## 注意事项
1. 堡垒机不能ssh客户端直连所以为半自动,uat环境/root/已放置脚本
2. linux环境必须包含rz和python这两个一般centos的linux服务器都自带,没有的话可以自行安装.
3. 正式环境运行脚本请保证脚本为svn库最新版,并且视情况开启脚本的功能: 备份和手动kill进程

# 使用说明
* 使用命令后,弹出的文件框选中新的war包确认即可.

## 命令:
1. 不启用备份/人工决策kill功能
```bash
# /root/deploy.py为脚本所在的路径 
python /root/deploy.py
```
2. 启动备份和人工决策kill功能
```bash
# "/root/deploy.py"为脚本所在的路径, "backupPath:/root/" 中的/root/为备份的路径,视项目规定自定义, manualKill为打开人工决策kill功能
python /root/deploy.py backupPath:/root/ manualKill
```

## 备份和手动kill进程 介绍
1. 脚本的备份逻辑: 备份当前上传的war包->创建文件夹的逻辑为:八马部署文档中的`2.上传文件`流程
2. 手动kill:     在结束进程的前脚本会暂停,直到用户输入回车才会重启tomcat,方便多个正式环境同时重启.

# 例子
    #号开头的为注释,其他为linux命令行记录
```bash
# 输入命令  "python deploy.py"脚本在当前文件夹也就是root下, "backupPath:/root/" /root/为这次命令的备份目录,"manualKill"开启人工决策kill
[root@tms_dev_app01 ~] python deploy.py backupPath:/root/ manualKill
# 如果tomcat未启动并且莫名奇妙系统有多个tomcat命令,然后和脚本交互选择正确的tomcat
tomcat未启动,开始搜索tomcat路径......
当前系统可能存在多个tomcat目录,请输入以下tomcat目录中正确的那个序号然后回车!!!
序号 0 : /usr/local/src/tomcat/apache-tomcat-8.5.42
序号 1 : /mnt/local/src/tomcat/apache-tomcat-8.5.42
0
# 输入回车后脚本就会杀掉tomcat进程并且重启跟踪日志,方便多台服务器同时重启
已执行上传备份步骤,输入回车后脚本才会Kill掉tomcat重启部署......
```

