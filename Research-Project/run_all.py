import os
import sys
from glob import glob

if len(sys.argv) < 2:
	sys.exit(1)
else:
	fn = sys.argv[1]

f = glob("./data/*")

print [ ff.split('\\')[-1] for ff in f ]

for ff in f:
	q = ff.split('\\')[-1]	# Windows
	q = q.replace('+',' ')
	
	os.system("python " + fn + " " + q)
