# This script will take an output file and extract the final Standard Orientation from Gaussian output files.

import os
import numpy

atoms = input("How many atoms are there?")
type(atoms)
atoms = int(atoms)

geometry_file = os.path.join('geo.out')
xyz = open(geometry_file, 'r')
lines = xyz.readlines()

found = False

geom = []
i=0
for line in lines:
    if 'Standard orientation:' in line:
        geom.clear()
        found = True
    if i < 5 and found:
        i+=1
    elif i < atoms + 5 and found:
        geom.append(line)
        i+=1
    else:
        found = False
        i = 0

# Convert the list into an array to get the desired lines.
geom = [i.split() for i in geom]

rows = [row for row in geom]
for i, row in enumerate(rows):
    for j, value in enumerate(row):
        if value == '13':
            geom[i][j] = 'Al'
        if value == '8':
            geom[i][j] = 'O'
        if value == '12':
            geom[i][j] = 'Mg'
        if value == '14':
            geom[i][j] = 'Si'
        if value == '6':
            geom[i][j] = 'C'
        if value == '1':
            geom[i][j] = 'H'

geomarray = numpy.asarray(geom)

final = numpy.delete(geomarray,[0,2],1)
shape = numpy.shape(final)
print(final)
print(shape)
numpy.savetxt("tmp.txt", final, delimiter=" ", fmt='%s')
xyz.close()
