#!/usr/bin/env python
# coding=utf-8

from ftplib import FTP
import ConfigParser
import os,sys,string,datetime,time
import socket
import chardet
import logging
import logging.config
import pdb
reload(sys)
sys.setdefaultencoding("utf-8")

class CYFTP:
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.ftp = FTP()
        self.file_list = []
        self.list_nlst = []
    def __del__(self):
        self.ftp.close()

    def login(self):
        ftp = self.ftp
        ftp.set_pasv(True)
        #print ('开始连接到 %s' %(self.host)).decode('utf-8').encode('gbk')
        logger.debug(('开始连接到 %s' %(self.host)).decode('utf-8').encode('gbk'))
        ftp.connect(self.host, 21)
        ftp.login(self.user, self.passwd)
        #print ('成功连接到服务器').decode('utf-8').encode('gbk')
        logger.debug(('成功连接到服务器').decode('utf-8').encode('gbk'))
        #log.write(('%s 开始更新\n' %nowtime).decode('utf-8').encode('gbk'))
        logger.info(('开始更新\n').decode('utf-8').encode('gbk'))
        ftp.cwd('./')

    def get_file_list(self, line):
        ret_arr = []
        #print "ftp.dir(): %s" %line
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)
    
    def get_filename(self, line):
        #print line
        #m = raw_input()
        #line是ftp.dir()出来的文件列表，包含了目录或文件名及其各种信息
        #line[0]的值是d(文件夹)或-(文件)
        #list_nlst是ftp.nlst()出来的文件列表，只包含目录或文件名
        pos = line.rfind(':')
        pp = ''
        while(line[pos] != ' '):
            pos += 1
        while(line[pos] == ' '):
            pos += 1

        for i in self.list_nlst:
            if i in line:
                pp = i

        file_arr = [line[0], pp]
        #print file_arr
        #m = raw_input()
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
            logger.debug(('开始下载文件 %s' %localfile).decode('utf-8').encode('gbk'))
            #print ('开始下载文件 %s' %localfile).decode('utf-8').encode('gbk')
            #log.write(('文件 %s 下载成功\n' %localfile).decode('utf-8').encode('gbk'))
            file_handler = open(localfile, 'wb')
            bufsize = 1024
            try:
                self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write, bufsize)
            except Exception as error:
                #print(error)
                logger.warning(error)
            logger.info(('文件 %s 下载成功' %localfile).decode('utf-8').encode('gbk'))
            file_handler.close()

    def start_down(self, localdir, remotedir):
        try:
            self.ftp.cwd(remotedir)
        except Exception, e:
            #print e
            logger.warning(str(e).decode('utf-8').encode('gbk'))
            return

        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        self.file_list = []
        
        self.list_nlst = self.ftp.nlst()
        for i in self.list_nlst:
            #print ('本目录文件列表: %s' %i).decode('utf-8').encode('gbk')
            logger.debug(('本目录文件列表: %s' %i).decode('utf-8').encode('gbk'))

        try:
            self.ftp.dir(self.get_file_list)
        except Exception:
            pass

        remotenames = self.file_list
        for item in remotenames:
            filetype = item[0]
            filename = item[1].decode('utf-8')
            #print localdir
            #print filename
            local = os.path.join(localdir, filename)
            #local = localdir+filename
            #print local
            if filetype == 'd':
                self.start_down(local, filename)
            elif filetype == '-':
                self.download_file(local, filename)
        self.ftp.cwd('..')

if __name__=='__main__':

    timeout = 20
    socket.setdefaulttimeout(timeout)
    #sleep_time = 10
    #time.sleep(sleep_time)

    #通过logging.config模块配置日志
    logging.config.fileConfig('loggers.conf')
    logger = logging.getLogger('cyftp')

    #从配置文件获取参数
    cp = ConfigParser.ConfigParser()
    cp.read('cyftp.conf')
    host = cp.get('host', 'host')
    user = cp.get('host', 'user')
    passwd = cp.get('host', 'passwd')
    localpath = cp.get('path', 'localpath')
    remotepath = cp.get('path', 'remotepath')
    shift = cp.getint('path', 'shift')

    nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
    #log = open('log.txt', 'a')

    go = CYFTP(host, user, passwd)
    go.login()

    day = int(time.strftime('%d'))
    month = int(time.strftime('%m'))
    start_day = day-shift+1
    end_day = day+1
    for i in range(start_day, end_day):
        if i > 0:
            #pdb.set_trace()
            month_day = (str(month)+'月'+str(i)+'日/').decode('utf-8').encode('gbk')
            month_day1 = time.strftime('%m-')+str(i)
            localpath_full = localpath+month_day1
            remotepath_full = remotepath+month_day
            go.start_down(localpath_full, remotepath_full)

    logger.info(('更新成功\n\n').decode('utf-8').encode('gbk'))
    #log.write(('%s 更新成功\n\n' %nowtime).decode('utf-8').encode('gbk'))
    #log.close()
