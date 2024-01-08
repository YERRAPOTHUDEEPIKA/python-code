import subprocess

cmd = "node pix.js"
proc = subprocess.Popen(cmd,shell=True,bufsize=256,stdout=subprocess.PIPE)
c=1
for line in proc.stdout:
str1 = line.restrip().decode('UTF-8')
c = c+1
print(c,symc)
if "symbol: '"in str1:
print(str1)