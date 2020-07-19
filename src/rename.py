
import os,re

rule = '.+\.mp4$'
li = os.listdir(os.getcwd())
for file in li:
    if re.search(rule,file):
        cmd = "mv %s %s"%(file,file.replace(".mp4", ".m"))
        print cmd
#        os.system(cmd)

#通过os.rename修改文件名去掉空格
rule = ' '
li = os.listdir(os.getcwd())
for file in li:
    if re.search(rule,file):
        #cmd = "mv %s %s"%(file,file.replace(" ", "_"))
        #print cmd
        #os.system(cmd)
	os.rename(file,file.replace(" ", "_"))

