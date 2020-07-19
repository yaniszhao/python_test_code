import os,sys,traceback,ConfigParser,getopt
import time,shutil,stat,time,logging
from subprocess import *
import xml.etree.ElementTree as xmlEt

LOG=None

def create_log(filename):
    dirname=os.path.dirname(filename)
    if dirname=='':
        raise Exception,"[ERROR]file name is not legal"

    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    f=logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    h=logging.FileHandler(filename,'w')
    h.setFormatter(f)
    log=logging.Logger("check_custom_log")
    log.addHandler(h)
    return log

def debug_info():
    try:
        raise Exception
    except:
        f=sys.exe_info()[2].ta_frame.f_back
        return '['+'filename:'+os.path.basename(f.f_code.co_filename)+']' \
                +'['+'funname:'+f.f_code.co_name+']'+'['+'linenum:'+str(f.f_lineno)+']'

def log_wrap(fn):
    def wrap(msg,pr=False,info=True):
        debuginfo=''
        #add debug info
        if info is True:
            try:
                raise Exception
            except:
                f=sys.exe_info()[2].tb_frame.f_back
                debuginfo='['+'filename:'+os.path.basename(f.f_code.co_filename)+']' \
                        +'['+'funname:'+f.f_code.co_coname+']'+'['+'linenum:'+str(f.f_lineno)+']'
        msg=msg+debuginfo
        global LOG
        if LOG is None:
            print msg
        else:
            fn(LOG,msg,pr)
    return wrap

@log_wrap
def log_info(log,msg,pr):
    log.info(msg)
    if pr: print '[INFO]'+msg

@log_wrap
def log_error(log,msg,pr):
    log.error(msg)
    if pr: print '[ERROR]'+msg

def on_rm_error(func,path,exe_info):
    os.chmod(path,stat.S_IWRITE)
    os.unlink(path)

def remove_dir(dirpath):
    curdir=os.getcwd()
    try:
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath,onerror=on_rm_error)
        elif os.path.isfile(dirpath):
            os.remove(curdir)
    except Exception,e:
        os.chdir(curdir)
        raise e

def shell_cmd(cmdline,inmsg=None,exit=True):
    p=Popen(cmdline,stdin=PIPE,stdout=PIPE,stderr=PIPE,shell=True)
    if inmsg:
        p.stdin.write(inmsg)
    out,err=p.communicate()
    if p.returncode != 0:
        if exit == True:
            print "p.returncode isn't 0, exit!"
            sys.exit(p.returncode)
    
    return p.returncode,out,err

def get_src_compare_path(path):
    if os.name == 'nt':
        return os.path.abspath(path).replace('\\','/')
    else:
        return os.path.abspath(path)

def get_sdk_version(sdk_dir):
    sdk_dir=sdk_dir+r'/product/package'
    return str(os.listdir(sdk_dir)[0])

def BASIC_get_des_compare_path(path,sdk_dir,installtool_dir):
    if (path == None) or (sdk_dir == None) or (installtool_dir == None):
        raise Exception,"arg isn't legal"
    ver=get_sdk_version(sdk_dir)
    if path.find('$SDK') != -1:
        path=path.replace('$SDK',sdk_dir)
    if path.find('$VERSION') != -1:
        path=path.replace('$VERSION',ver)
    if path.find('$INSTALLTOOL') != -1:
        path=path.replace('$INSTALLTOOL',installtool_dir)
    return path

def AC_get_des_compare_path(path,sdk_dir,cfgmsp_dir):
    ver=get_sdk_version(sdk_dir)
    if path.find('$SDK') != -1:
        path=path.replace('$SDK',sdk_dir)
    if path.find('$VERSION') != -1:
        path=path.replace('$VERSION',ver)
    if path.find('$CFG_MSP') != -1:
        path=path.replace('$CFG_MSP',cfgmsp_dir)
    return path

def create_file(path):
    if not os.path.isfile(path):
        with open(path,'w'): pass
    else:
        raise Exception,"file not exist"

def write_file(path,str):
    if os.path.isfile(path):
        with open(path,'w') as f:
            f.write(str)
    else:
        raise Exception,"file not exist"

def copy_dir(srcdir,dstdir):
    if (not os.path.isdir(dstdir)) and os.path.isdir(srcdir):
        shutil.copytree(srcdir, dstdir)
    elif os.path.isdir(dstdir):
        raise Exception,"destination directory exist"
    elif not os.path.isdir(srcdir):
        raise Exception,"source directory not exist"

def decompress_folder(srcfile,desfold,specfile='',clean_des_dir=False,runback=False):
    srcfile=srcfile.replace('\\','/')
    desfold=desfold.replace('\\','/')
    log_info('srcfile:%s'%srcfile)
    log_info('desfold:%s'%desfold)
    #judge srcfile
    if not os.path.isfile(srcfile):
        raise Exception,"ERROR:file[%s] doesn't exist!"%srcfile
    #judge desfold
    if os.path.isdir(desfold):
        if clean_des_dir:
            remove_dir(desfold)
            log_info('remove idr:%s'%desfold)
    #get cmdline
#    if os.name == 'nt':
#        if runback:
#            cmdline=r'Winrar x -t -o-p -inul -ibck %s %s'%(srcfile,desfold)
#        else:
#            cmdline=r'Winrar x -t -o-p -inul       %s %s'%(srcfile,desfold)
    if runback:
        cmdline=r'unzip -o -q %s %s -d %s'%(srcfile,specfile,desfold)
    else:
        cmdline=r'unzip -o    %s %s -d %s'%(srcfile,specfile,desfold)
    #excutre
    try:
        ret,out,err=shell_cmd(cmdline,exit=False)
    except Exception,e:
        log_error('shell_cmd exception')
        raise e
    if ret != 0:
        log_error("shell_cmd ret=%s,out=%s,err=%s"%(ret,out,err))
        raise Exception,"shell_cmd error!"

def comp_two_files(file1,file2,mode):
    file_is_ok=True
    salt=str(time.time()).replace('.','_')
    tmpdir=os.getcwd()+'/tmp'+salt
    if os.name == 'nt': tmpdir=tmpdir.replace('\\','/')
    os.mkdir(tmpdir)
    log_info("mkdir-->%s"%tmpdir)
    #create two compare fold
    cmpdir1=tmpdir+'/cmpdir1'
    cmpdir2=tmpdir+'/cmpdir2'
    os.mkdir(cmpdir1)
    os.mkdir(cmpdir2)
    log_info('mkdir-->%s'%cmpdir1)
    log_info('mkdir-->%s'%cmpdir2)
    newfile1=cmpdir1+'/'+file1.split('/')[-1]
    newfile2=cmpdir2+'/'+file2.split('/')[-1]
    #copy tmp files
    if mode == 'MODE_FILE':
        if not os.path.isfile(file1):
            log_error('file not exist:%s'%file1)
            remove_dir(tmpdir)
            log_info('remove dir:%s'%tmpdir)
            raise Exception,'file not exist:%s'%file1
        if not os.path.isfile(file2):
            log_error('file not exist:%s'%file2)
            remove_dir(tmpdir)
            log_info('remove dir:%s'%tmpdir)
            raise Exception,'file not exist:%s'%file2
        shutil.copy(file1,newfile1)
        shutil.copy(file2,newfile2)
        log_info('copy file:%s-->%s'%(file1,newfile1))
        log_info('copy file:%s-->%s'%(file2,newfile2))
    if mode == 'MODE_DIR':
        if not os.path.isdir(file1):
            log_error('dir not exist:%s'%file1)
            remove_dir(tmpdir)
            log_info('remove dir:%s'%tmpdir)
            raise Exception,'dir not exist:%s'%file1
        if not os.path.isdir(file2):
            log_error('dir not exist:%s'%file2)
            remove_dir(tmpdir)
            log_info('remove dir:%s'%tmpdir)
            raise Exception,'dir not exist:%s'%file2
        copy_dir(file1,newfile1)
        copy_dir(file2,newfile2)
        log_info('copy dir:%s-->%s'%(file1,newfile1))
        log_info('copy dir:%s-->%s'%(file2,newfile2))
    else:
        log_error("comp_two_files:arg.mode is invalid!")
        remove_dir(tmpdir)
        log_info('remove dir:%s'%tmpdir)
        raise Exception,"comp_two_files:arg.mode is invalid!"
    #create report.xml
    reportfile=tmpdir+'/report.xml'
    create_file(reportfile)
    log_info('create file:%s'%reportfile)
    #create BCscipt.txt
    bcsriptstr=''+ \
            'load %1 %2'+'\n'+ \
            'Expand All'+'\n'+ \
            'select all'+'\n'+ \
            'file report layout:XML options:display mismatches output-to:%3'+'\n'
    bcsriptfile=tmpdir+'/BCscript.txt'
    create_file(bcsriptfile)
    log_info('create file%s'%bcsriptfile)
    write_file(bcsriptfile,bcsriptstr)
    #excute
    cmdline="bcompare.exe /silent /closescript @"+bcsriptfile+" "+cmpdir1+" "+cmpdir2+" "+reportfile
    log_info("cmdline=%s"%cmdline)
    try:
        ret=os.system(cmdline)
    except Exception,e:
        log_error("excute cmdline Exception!")
        remove_dir(tmpdir)
        log_info('remove dir:%s'%tmpdir)
        raise e
    #excute result
    if ret != 0:
        log_error("excute cmdline fail:%s"%cmdline)
        remove_dir(tmpdir)
        log_info('remove dir:%s'%tmpdir)
        raise Exception,"excute cmdline fail:%s"%cmdline
    else:
        with open(reportfile) as f:
            text=f.read()
            if "linecomp status" in text:
                log_info("There are some differences, please check it!")
                file_is_ok=False
    #end
    remove_dir(tmpdir)
    log_info('remove dir:%s'%tmpdir)
    return file_is_ok

def decompress_custom_files_from_sdk(custom_file,sdk_zip,sdk_dir,product):
    #decompress version.ini to get product version
    ver_ini='product/package/*/version.ini'
    log_info("ver_ini:%s"%ver_ini)
    decompress_folder(sdk_zip,sdk_dir,ver_ini)
    log_info("decompress version.ini ok!")
    #decompress install tool zip or cfg_msp.zip
    installtool_dir=None
    cfgmsp_dir=None
    if product == 'BASIC':
        installtool_zip='tools/evm_install_tool.zip'
        log_info('installtool_zip:%s'%installtool_zip)
        decompress_folder(sdk_zip,sdk_dir,installtool_zip)
        log_info("get %s from sdk"%installtool_zip)
        installtool_dir=sdk_dir+'tools/evm_install_tool'
        log_info('installtool_dir:%s'%installtool_dir)
        decompress_folder(sdk_dir+'/'+installtool_zip,installtool_dir)
        log_info("decompress evm_install_tool.zip ok!")
    elif product == 'AC':
        cfgmsp_zip='tools/cfgmsp.zip'
        log_info('cfgmsp_zip:%s'%cfgmsp_zip)
        decompress_folder(sdk_zip,sdk_dir,cfgmsp_zip)
        log_info("get %s from sdk"%cfgmsp_zip)
        cfgmsp_dir=sdk_dir+'tools/EulerLinu/cfg_msp'
        log_info('cfgmsp_dir:%s'%cfgmsp_dir)
        decompress_folder(sdk_dir+'/'+cfgmsp_zip,cfgmsp_dir)
        log_info("decompress cfgmsp.zip ok!")
    root=None
    with open(custom_file,'r') as f:
        try:
            tree=xmlEt.parse(f)
            root=tree.getroot()
        except Exception,e:
            log_error("open file:%s error"%custom_file)
            raise Exception,e
    for iter in root.iter("customFile"):
        desfile=iter.find("desFile").text
        if product == 'BASIC':
            desfile=BASIC_get_des_compare_path(desfile,sdk_dir,installtool_dir)
        elif product == 'AC':
            desfile=AC_get_des_compare_path(desfile,sdk_dir,cfgmsp_dir)
        if not os.path.isdir(desfile):
            path=desfile.split(sdk_dir+'/')[1]
            log_info('path:%s'%path)
            decompress_folder(sdk_zip,sdk_dir,path)
    for iter in root.iter("customFile"):
        desdir=iter.find("desDirectory").text
        if product == 'BASIC':
            desdir=BASIC_get_des_compare_path(desdir,sdk_dir,installtool_dir)
        elif product == 'AC':
            desdir=AC_get_des_compare_path(desdir,sdk_dir,cfgmsp_dir)
        if not os.path.isdir(desdir):
            path=desdir.split(sdk_dir+'/')[1]
            log_info('path:%s'%path)
            decompress_folder(sdk_zip,sdk_dir,path)
    return installtool_dir,cfgmsp_dir

def get_compare_result(custom_file,sdk_dir,installtool_dir,cfgmsp_dir):
    every_file_is_ok=True
    dirty_list=[]
    log_info("begin to compare...",pr=True)
    #open file
    root=None
    with open(custom_file,'r') as f:
        try:
            tree=xmlEt.parse(f)
            root=tree.getroot()
        except Exception,e:
            log_error("open file:%s error"%custom_file)
            raise Exception,e
    #get files
    for iter in root.iter("customFile"):
        v1=iter.find("srcFile").text
        v2=iter.find("desFile").text
        v1=get_src_compare_path(v1)
        if product == 'BASIC':
            v2=BASIC_get_des_compare_path(v2,sdk_dir,installtool_dir)
        elif product == 'AC':
            v2=AC_get_des_compare_path(v2,sdk_dir,cfgmsp_dir)
        log_info("v1=%s"%v1)
        log_info("v2=%s"%v2)
        try:
            if comp_two_files(v1,v2,'MODE_FILE') == False:
                every_file_is_ok=False
                dirty_list.append(v1)
        except Exception,e:
            log_error("except Exception:%s"%e)
            raise e
    #get dirs
    for iter in root.iter("customFile"):
        v1=iter.find("srcDirectory").text
        v2=iter.find("desDirectory").text
        v1=get_src_compare_path(v1)
        if product == 'BASIC':
            v2=BASIC_get_des_compare_path(v2,sdk_dir,installtool_dir)
        elif product == 'AC':
            v2=AC_get_des_compare_path(v2,sdk_dir,cfgmsp_dir)
        log_info("v1=%s"%v1)
        log_info("v2=%s"%v2)
        try:
            if comp_two_files(v1,v2,'MODE_DIR') == False:
                every_file_is_ok=False
                dirty_list.append(v1)
        except Exception,e:
            log_error("except Exception:%s"%e)
            raise e
    return every_file_is_ok,dirty_list

def check_custom_files_all_ok(custom_file,sdk_zip,product):
    custom_file=os.path.abspath(custom_file).replace('\\','/')
    sdk_zip=os.path.abspath(sdk_zip).replace('\\','/')
    print "custom_file:%s%s"%(custom_file,debug_info())
    print "sdk_zip:%s%s"%(sdk_zip,debug_info())
    curdir=os.getcwd().replace('\\','/')
    custom_dir=os.path.dirname(custom_file).replace('\\','/')
    os.chdir(custom_dir)
    #create sdk dir and log file
    salt=str(time.time()).replace('.','_')
    log_file=custom_dir+'/check_custom_'+salt+'.log'
    global LOG;LOG=create_log(log_file)
    sdk_dir=sdk_zip.split('.')[0]+'_'+salt
    os.mkdir(sdk_dir)
    #decompress files in custom.xml
    try:
         (installtool_dir,cfgmsp_dir)= \
            decompress_custom_files_from_sdk(custom_file,sdk_zip,sdk_dir,product)
    except Exception,e:
        log_error("except Exception:%s"%e)
        remove_dir(sdk_dir)
        log_info('remove dir:%s'%sdk_dir)
        raise e
    #get_compare_result
    try:
        (every_file_is_ok,dirty_list)= \
            get_compare_result(custom_file,sdk_zip,installtool_dir,cfgmsp_dir)
    except Exception,e:
        log_error("except Exception:%s"%e)
        remove_dir(sdk_dir)
        log_info('remove dir:%s'%sdk_dir)
        raise e
    
    log_info("dirty_list=%s"%dirty_list)
    if every_file_is_ok:
        log_info("[[result=%s]]all files ok!"%every_file_is_ok,pr=True)
    else:
        log_info("[[result=%s]]some files are dirty, please check it!"%every_file_is_ok,pr=True)
    #end
    remove_dir(sdk_dir)
    log_info('remove dir:%s'%sdk_dir)
    return every_file_is_ok

def help():
    print ''+ \
    'Usage: check_custom.py [-h][--help][--cusfile=][--sdkfile=][--product=]'+'\n\t'+ \
    '-h, --help                display this help and exit'+'\n\t'+ \
    '    --cusfile=CUSFILE     CUSFILE is custom file path'+'\n\t'+ \
    '    --sdkfile=SDKFILE     SDKFILE is sdk zip file'+'\n\t'+ \
    '    --product=PRODUCT     PRODUCT is BASIC or AC'+'\n\t'

if __name__ == '__main__':
    custom_file=os.path.abspath('./custom.xml')
    sdk_file=os.path.abspath('../../../../platform/msp/sdk/SDK-lite.zip')
    product='BASIC'
    
    print "sys.argv:%s"%sys.argv:
    try:
        opts,args=getopt.getopt(sys.argv[1:],'dh',["help","cusfile=","sdkfile=","product="])
    except getopt.GetoptError:
        help();exit(-1)
        
    print "opts:%s"%opts
    print "args:%s"%args
    if len(args) > 0:
        print ("bad arguments!"),"args num:%s"%len(args)
        help();exit(-1)
    for (key,val) int opts：
        if key == '-d':
            pass
        if key == '-h' or key == "--help":
            help();exit(0)
        if key == "--cusfile":
            custom_file=val
            print "custom_file-->%s%s"%(custom_file,debug_info())
        if key == "--sdkfile":
            sdkfile=val
            print "sdkfile-->%s%s"%(sdkfile,debug_info())
        if key == "--sdkfile":
            product=val
            print "product-->%s%s"%(product,debug_info())
    
    if os.name == 'nt':
        custom_file=custom_file.replace('\\','/')
        sdk_file=sdk_file.replace('\\','/')
    print "custom_file:%s%s"%(custom_file,debug_info())
    print "sdkfile:%s%s"%(sdkfile,debug_info())
    print "product:%s%s"%(product,debug_info())
    
    ret=check_custom_files_all_ok(custom_file,sdkfile,product)
    
    print re
    print 'Done!!!'
    exit(0 if ret==True else -1)