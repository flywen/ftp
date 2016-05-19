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
        logger.debug(('开始连接到 %s' %(self.host)).decode('utf-8').encode('gbk'))
        ftp.connect(self.host, 21)
        ftp.login(self.user, self.passwd)
        logger.debug(('成功连接到服务器').decode('utf-8').encode('gbk'))
        logger.info(('开始更新\n').decode('utf-8').encode('gbk'))
        ftp.cwd('./')

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)
    
    def get_filename(self, line):
        #line是ftp.dir()出来的文件列表，包含了目录或文件名及其各种信息
        #line[0]的值是d(文件夹)或-(文件)
        #list_nlst是ftp.nlst()出来的文件列表，只包含目录或文件名
        #pos = line.rfind(':')
        pp = ''
        #while(line[pos] != ' '):
        #    pos += 1
        #while(line[pos] == ' '):
        #    pos += 1

        for i in self.list_nlst:
            if i in line:
                pp = i
        #36:39是月，40:42是日
        file_arr = [line[0], line[36:39], line[40:42], pp]
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
            logger.debug('Start download file %s' %localfile)
            file_handler = open(localfile, 'wb')
            bufsize = 1024
            try:
                self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write, bufsize)
            except Exception as error:
                logger.warning(error)
            logger.info('file %s download success!' %localfile)
            file_handler.close()

    def start_down(self, localdir, remotedir):
        try:
            self.ftp.cwd(remotedir)
        except Exception, e:
            logger.warning(str(e).decode('utf-8').encode('gbk'))
            return

        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        self.file_list = []
        
        self.list_nlst = self.ftp.nlst()
        for i in self.list_nlst:
            logger.debug(('本目录文件列表: %s' %i).decode('utf-8').encode('gbk'))

        try:
            self.ftp.dir(self.get_file_list)
        except Exception:
            pass

        remotenames = self.file_list
        for item in remotenames:
            if nowmonth != item[1]:
                continue
            if int(item[2]) < shiftday:
                continue
            filetype = item[0]
            filename = item[3].decode('utf-8').encode('gbk')
            local = os.path.join(localdir, filename)
            if filetype == 'd':
                self.start_down(local, filename)
            elif filetype == '-':
                self.download_file(local, filename)
        self.ftp.cwd('..')

if __name__=='__main__':

    timeout = 20
    socket.setdefaulttimeout(timeout)

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

    nowmonth = time.strftime('%b')
    nowday = time.strftime('%d')
    shiftday = int(nowday) - shift

    go = CYFTP(host, user, passwd)
    go.login()
    go.start_down(localpath, remotepath)

    
    logger.info(('更新成功\n\n').decode('utf-8').encode('gbk'))
    
