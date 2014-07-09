# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import numpy as np

""" SERP_mat_conditioner is a simple python script that takes in a tab delimited input
    file which contains parameters and options and outputs the appropriate fuel
    composition in atomic percent inside of a SERPENT file that is also specified in the
    input file. A sample input file is given below
    <<
    < Combined/Seperate >
    < Free/Preserved >
    < Path_to_SERPENT_input_file.txt >
    < A of isotope n , Z of n , < C , A , F , H >, BNC , BNH , Abudance >
    >>
    The < CAFH > flag determines how the < Abundance > value is handled. This will be
    made more clear in the body of the code through comments and doc strings """

print "Fuel Material Conditioner beginning"

inputfile = raw_input( "Please enter file name, local path only, of csv file to open \n" )

print "Opening csv file now"

csvfile = open( inputfile, "r" )

print "Reading file now"

reader = csvreader.reader( csvfile )

# initilizing array
csvinput = []

for row in reader:
  csvinput.append( row )

for row in range( len ( csvinput ) ):
  print csvinput[ row ]


print "The SERPENT material conditioner had finished running"
exit()

