import sys
import os
from glob import glob
import random
from pprint import pprint
from proc_defs import *
from ast import literal_eval

file_header = "./data/"

if len(sys.argv) < 2:
	file_path = random.sample(glob(file_header+"*"),1)[0] + "/"
	q = file_path[len(file_header):]
else:
	q = "+".join(sys.argv[1:])
	if os.path.exists(file_header+q) and os.path.isdir(file_header+q):
		file_path = file_header + q + "/"
	else:
		print("Incorrect folder name. Valid folders:")
		pprint(glob(file_header+"*"))
		sys.exit(1)

print("Topic:\t"+q)
print("Path:\t"+file_path)

l_files = [".".join(p.split(".")[:-2]) for p in glob(file_path+"*.title.txt")]

vectors = []
titles = []
urls = []
for l_file in l_files:
	#auth/subt/text/title .txt
	with open(l_file+".text.txt") as fp: text = fp.readline().strip()
	with open(l_file+".title.txt") as fp: title = fp.readline().strip()
	with open(l_file+".subt.txt") as fp: subtitle = fp.readline().strip()
	with open(l_file+".url.txt") as fp: url = fp.readline().strip()
	with open(l_file+".auth.txt") as fp:
		auth_name = fp.readline().strip()
		auth_url = fp.readline().strip()
	
	# Creating/Reading Feature Vector
	if os.path.exists(l_file + ".res.txt"):
		with open(l_file+".res.txt") as fp:
			feat_v = literal_eval(fp.readline().strip())
		print "f",
	else:
		feat_v = []
		try:
			feat_v.append(biasedWords(text))
		except KeyboardInterrupt:
			raise
		except:
			feat_v.append(None)
		
		try:
			feat_v.append(wikiWordsToWatch(text))
		except KeyboardInterrupt:
			raise
		except:
			feat_v.append(None)
		
		try:
			feat_v.append(featCount(auth_url))
		except KeyboardInterrupt:
			raise
		except:
			feat_v.append(None)
		
		try:
			feat_v.append(sentiText(text,q.replace("+"," ")))
		except KeyboardInterrupt:
			raise
		except:
			feat_v.append(None)
		
		if all([k is not None for k in feat_v]):
			with open(l_file+".res.txt",'w') as fp:
				fp.write(str(feat_v))
		print "c",
	
	print feat_v
	if all([k is not None for k in feat_v]):
		vectors.append(feat_v)
		titles.append(title)
		urls.append(url)
	#break

# The hierarchical clustering starts here.
print("Data acquired. Starting processing")

import numpy as np
from sklearn import preprocessing
from math import sqrt
from scipy.cluster import hierarchy as hier
from scipy.spatial import distance
import json

def L2Dist(v1, v2):
	if len(v1) != len(v2):
		raise TypeError("Vectors not of same length")
		return None
	
	value = 0.0
	for i in range(len(v1)):
		value += (v1[i]-v2[i])**2
	
	value = sqrt(value)
	return value

def scale_linear_bycolumn(rawpoints, high=1.0, low=-1.0):
	mins = np.min(rawpoints, axis=0)
	maxs = np.max(rawpoints, axis=0)
	rng = maxs - mins
	rng[rng == 0] = 1	# If max = min for feature.
	return high - (((high - low) * (maxs - rawpoints)) / rng)

# Taking small sample for testing purposes
SAMPLE_SIZE = 25
vectors = vectors[:SAMPLE_SIZE]
titles = titles[:SAMPLE_SIZE]
urls = urls[:SAMPLE_SIZE]
# ----------------------------------------

# Normalize
vectors = np.array(vectors)
vects2 = scale_linear_bycolumn(vectors)

# Calculate the distance matrix
dist = distance.pdist(vects2)
links = hier.linkage(dist)

# -- K-Means --
from scipy.cluster.vq import kmeans2, vq, kmeans
nClust = 5
centroid, _ = kmeans(vects2,nClust)
idx, ds = vq(vects2, centroid)

fp = open('kmeans'+q+'.txt','w')
for i in range(nClust):
	for j,x in enumerate(idx):
		if i==x:
			fp.write("C"+str(x)+"\t")
			fp.write(str(j+1)+"\t")
			fp.write(titles[j]+"\n")
	fp.write('\n')
fp.close()

print idx

# --

hts = [l[2] for l in links]
alpha = int(SAMPLE_SIZE * 0.2)

# -- Removing outliers
avg = 1.0*sum(hts[alpha:-alpha])/len(hts[alpha:-alpha])
htd = [i for i in range(len(hts)) if (1.0*hts[i]/avg)>1.5]

remove = []
for i in htd:
	if links[i][0] < SAMPLE_SIZE:
		remove.append(links[i][0])
	if links[i][1] < SAMPLE_SIZE:
		remove.append(links[i][1])

# --

vects2_f = []
x_axis_f = []
for i in range(SAMPLE_SIZE):
	if i in remove:
		continue
	x_axis_f.append(i+1)
	vects2_f.append(vects2[i])

vects2_f = np.array(vects2_f)

# Display Graphs using Mathematica
fp = open("./array.nb","w")
# Convert to a format Mathematica understands
fp.write('Needs["HierarchicalClustering`"]'+'\n')

fp.write("vectlist = ")
fp.write(str(vects2_f.tolist()).replace('[','{').replace(']','}'))
fp.write('\n')

fp.write("labels = ")
fp.write('{')
fp.write(','.join(['"'+title.replace('"',"'")+'"' for title in titles]))
fp.write('}')
fp.write('\n')

fp.write("range = " + str(x_axis_f).replace('[','{').replace(']','}'))
fp.write('\n')

fp.write('diag=DendrogramPlot[vectlist, LeafLabels->range, PlotLabel->"'+q+'", ImageSize->1000,Linkage->Single]'+'\n')
fp.write(r'Export["'+q+r'.png",diag]'+'\n')

fp.write("height = " + str(hts).replace('[','{').replace(']','}'))
fp.write('\n')
fp.write('diag=ListPlot[height]\n')
fp.write(r'Export["'+q+r'_ht.png",diag]'+'\n')

fp.write("htdiff = " + str(htd).replace('[','{').replace(']','}'))
fp.write('\n')
fp.write('diag1=ListPlot[htdiff, ImageSize->1000, PlotRange->All]\n')
fp.write(r'Export["'+q+r'_htdiff.png",diag1]'+'\n')


fp.close()

os.system('math < array.nb')

tree = [0]*len(vects2)
for i in range(len(vects2)):
	tree[i] = {"text":'<a href = "{}" target = "_blank">{}</a>'.format(urls[i],titles[i])}

for i in xrange(len(links)):
	n1, n2, dist, _ = links[i]
	n1 = int(n1)
	n2 = int(n2)
	tree.append({"text" : "{} ({:.3f})".format(i,dist), "children" : [tree[n1],tree[n2]]})
	tree[n1] = None
	tree[n2] = None


tree1 = {"id" : "#", "children" : [k for k in tree if k is not None]}

print tree1
fp = open("./jsons/"+q+"_tree.json","w")
fp.write(json.dumps(tree1))
fp.close()
