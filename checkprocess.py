import win32com.client
import os,time

def check_exsit(process_name):
    WMI = win32com.client.GetObject('winmgmts:')
    processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
    if len(processCodeCov) > 0:
        print '%s is exists' % process_name
    else:
        print '%s is not exists' % process_name
        os.system(process_name)

if __name__ == '__main__':
    while 1 == 1:
        sleep_time = 30
        time.sleep(sleep_time)
        #check_exsit('cyftp.exe')
        check_exsit('cyftp_jlzt.exe')
