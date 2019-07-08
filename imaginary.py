import os
import numpy as np

def gen_input():
    np.savetxt("ultimate.txt", ultimate, delimiter=" ", fmt='%s')
    temp = open('ultimate.txt', 'r')
    f = open("geomI.com", 'w+')
    f.write("#N wB97XD/6-31+G(d,p) OPT FREQ\n")
    f.write("\nimaginary frequencies\n\n")
    f.write("0 1\n")
    f.write(temp.read())
    f.write("\n")
    f.close()
    temp.close()

def pbs():
    f = open('geomI.pbs', 'w+')
    f.write("#!/bin/sh\n")
    f.write("#PBS -N geomI\n")
    f.write("#PBS -S /bin/sh\n")
    f.write("#PBS -j oe\n")
    f.write("#PBS -j oe\n")
    f.write("#PBS -m abe\n")
    f.write("#PBS -l cput=100:00:00\n")
    f.write("#PBS -l mem=3gb\n")
    f.write("#PBS -l nodes=1:ppn=2\n")
    f.write("#PBS -l file=100gb\n\n")

    f.write("export g09root=/usr/local/apps/\n")
    f.write(". $g09root/g09/bsd/g09.profile\n\n")

    f.write("scrdir=/tmp/bnp.$PBS_JOBID\n\n")

    f.write("mkdir -p $scrdir\n")
    f.write("export GAUSS_SCRDIR=$scrdir\n")
    f.write("export OMP_NUM_THREADS=1\n")

    f.write("printf 'exec_host = '\n")
    f.write("head -n 1 $PBS_NODEFILE\n\n")

    f.write("cd $PBS_O_WORKDIR\n")
    f.write("/usr/local/apps/bin/g09setup geomI.com geomI.out")

#This will determine how many lines after the Frequencies line that it will append.
atoms = input("How many atoms are there?")
type(atoms)
atoms = int(atoms)

# Basic read from file stuff.
output_file = os.path.join('geo.out')
file = open(output_file, 'r')
lines = file.readlines()

# Lists we will need later.
frequencies = []
frequencies_lines = []
truncated_lines = []

# This separates lines and line numbers so that we can refer to them later.
for count,line in enumerate(lines):
    if "Frequencies" in line:
        frequencies.append(line)
        frequencies_lines.append(count)

# This converts the ugly readlines into a nparray while removing everything but the data.
# This is not necessary but helps me visualize the data and should be commented out later.
frequencies = [i.split() for i in frequencies]
frequencies = np.asarray(frequencies)
frequencies = np.delete(frequencies,1,1)
frequencies = np.delete(frequencies,0,1)
frequencies = frequencies.astype(float)

shape = np.shape(frequencies)

# This will determine the number of imaginary frequencies.
count = 0
for rows in range(shape[0]):
    for cols in range(shape[1]):
        if frequencies[rows,cols] < 0:
            print("Imaginary frequencies found.")
            count += 1

#The count will be necessary for how many times other functions must loop.

#This grabs the necessary line numbers.
for numbers in range(count):
    truncated_lines.append(frequencies_lines[numbers])


new_lines = []

# This will grab the lines as added in the previous step.
# Maybe rethink this so you can use 'frequencies' instead of lines which defeats the purpose of the steps you've taken already?
x = 0
for n in truncated_lines:
    if x < count:
        for i in range(truncated_lines[x]+5,truncated_lines[x]+atoms+5,1):
            new_lines.append(lines[i])
        x += 1

# Now, we must refine the data and split them into groups.
new_lines = [i.split() for i in new_lines]
new_lines = np.asarray(new_lines)
shape1 = np.shape(new_lines)

np.set_printoptions(threshold=np.inf)
new_lines = np.delete(new_lines,0,1)
new_lines = np.delete(new_lines,0,1)
shape2 = np.shape(new_lines)

np.set_printoptions(threshold=np.inf)
new_lines = np.split(new_lines,count,0)

d={}
c={}
for x in range(count):
    d["new_lines{0}".format(x)] = new_lines[x]
    c["new_lines{0}".format(x)] = x

# Now we need to split the columns, and use modulo in order to determine which column in each split to use.


# THIS IS THE PROBLEM
splitlist={}
for i in range(count):
    splitlist["split_list{0}".format(i)] = np.split(d.get("new_lines{0}".format(i)),3,1)

"""
We will comment out this stuff in a minute.

test = {}

test["test1"] = splitlist.get("new_lines1")[1]

print(test.get("test1"))

"""

final ={}
#Now, to determine which columns we need, since each item in split shows the array across the entire line.
#For imaginary frequencies 1, I need the 0th. For 2, the 1st, and for 3, the 2nd.
for i in range(count):
    if i < 3:
        final["frequencycol{0}".format(i)] = splitlist.get("split_list0")[i]
    elif i >= 3:
        final["frequencycol{0}".format(i)] = splitlist.get("split_list1")[i % 3]
    elif count > 6:
        print("You need to add more statements in lines 108...")


shapefinal = np.shape(final.get("frequencycol0"))

# WE NOW HAVE THE COLUMNS. NOW TO ADD THE X Y AND Z TO THE XYZ OF THE STANDARD GEOMETRY.
#Import the XYZ from the temp file.

tempfile = os.path.join('tmp.txt')
tempxyz = np.genfromtxt(tempfile,usecols=(1,2,3),dtype=float)
labels = np.genfromtxt(tempfile,usecols=0,dtype=str)

shapetemp = np.shape(tempxyz)

ultimate = tempxyz

xlist = []
ylist = []
zlist =[]

for i in range(count):
    for x in range(atoms):
        xlist.append(final.get("frequencycol{0}".format(i))[x,0])
        ylist.append(final.get("frequencycol{0}".format(i))[x,1])
        zlist.append(final.get("frequencycol{0}".format(i))[x,2])

#for x in range(atoms):
#    ultimate[x,0] = tempxyz[x,0] + float(xlist[x])
#    ultimate[x,1] = tempxyz[x,1] + float(ylist[x])
#    ultimate[x,2] = tempxyz[x,2] + float(zlist[x])

x2 = []
y2 = []
z2 = []

for i in range(3):
    for a in range(atoms):
        for x in range(a,len(xlist),atoms):
            if i == 0:
                x2.append(float(xlist[x]))
            if len(x2) == 5:
                xtotal = sum(x2)
                ultimate[a,0] = (float(xtotal) + tempxyz[a,0])
                x2.clear()

            elif i == 1:
                y2.append(float(ylist[x]))
            if len(y2) == 5:
                ytotal = sum(y2)
                ultimate[a,1] = (float(ytotal) + tempxyz[a,1])
                y2.clear()

            elif i == 2:
                z2.append(float(zlist[x]))
            if len(z2) == 5:
                ztotal = sum(z2)
                ultimate[a,2] = (float(ztotal) + tempxyz[a,2])
                z2.clear()
np.round_(ultimate,decimals=2, out=ultimate)
ultimate = np.column_stack((labels,ultimate))
print(ultimate)

gen_input()
pbs()
