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

# initilizing FloatsInput array, the next 11 lines of code simply copy the csvinput
# array into another array as float values as opposed to strings

FloatsInput=[]
csvinputrows = len( csvinput )
floatrows = csvinputrows - 3
print " Creating floats array"
for i in range( floatrows ):
  FloatsInput.append( 0 )
for row in range( 3 , csvinputrows ):
  tmpArray=[]
  for column in range( len( csvinput[ row ] ) ):
    if len( csvinput[ row ][ column ] ) > 0:
      tmpArray.append( float( csvinput[ row ][ column ] ) )
  FloatsInput[ row - 3 ] = tmpArray
for i in range( floatrows ):
  print FloatsInput[ i ]

if csvinput[ 0 ][ 0 ] == "Free" or csvinput[ 0 ][ 0 ] == "free" \
    or csvinput[ 0 ][ 0 ] == "FREE":
    print "Running under the \"Free\" assumption"
    molcar = 1.0 -float( csvinput[ 2 ][ 0 ] ) -float( csvinput[ 2 ][ 1 ] )
    saltarray = []

print "The SERPENT material conditioner had finished running"
exit()

