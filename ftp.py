#!/usr/bin/env python
# coding=utf-8

from ftplib import FTP
import os,sys,string,datetime,time
import socket
reload(sys)
sys.setdefaultencoding("utf-8")

class CYFTP:

    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.ftp = FTP()
        self.file_list = []
    def __del__(self):
        self.ftp.close()

    def login(self):
        ftp = self.ftp
        ftp.set_pasv(True)
        print ('开始连接到 %s' %(self.host)).decode('utf-8').encode('gbk')
        ftp.connect(self.host, 21)
        ftp.login(self.user, self.passwd)
        print ('成功连接到服务器').decode('utf-8').encode('gbk')
        log.write(('%s 开始更新\n' %nowtime).decode('utf-8').encode('gbk'))
        ftp.cwd('./')

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_filename(self, line):
        pos = line.rfind(':')
        while(line[pos] != ' '):
            pos += 1
        while(line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr

    def is_same(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
        except:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(localfile)
        except:
            localfile_size = -1
        if remotefile_size == localfile_size:
            return 1
        else:
            return 0

    def download_file(self, localfile, remotefile):
        if self.is_same(localfile, remotefile):
            return
        else:
            print ('开始下载文件 %s' %localfile).decode('utf-8').encode('gbk')
            log.write(('文件 %s 下载成功\n' %localfile).decode('utf-8').encode('gbk'))
            file_handler = open(localfile, 'wb')
            self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write)
            file_handler.close()

    def start_down(self, localdir='./', remotedir='./'):
        self.ftp.cwd(remotedir)
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remotenames = self.file_list
        for item in remotenames:
            filetype = item[0]
            filename = item[1].decode('utf-8')
            #filename = item[1].decode('GBK')
            local = os.path.join(localdir, filename)
            if filetype == 'd':
                self.start_down(local, filename)
            elif filetype == '-':
                self.download_file(local, filename)
        self.ftp.cwd('..')

if __name__=='__main__':
    host = '192.168.1.204'
    user = 'administrator'
    passwd = 'Server2014'

    nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
    log = open('log.txt', 'a')

    go = CYFTP(host, user, passwd)
    go.login()
    go.start_down()

    log.write(('%s 更新成功\n\n' %nowtime).decode('utf-8').encode('gbk'))
    log.close()
