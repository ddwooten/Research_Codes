# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import numpy as np

""" SERP_mat_conditioner is a simple python script that takes in a comma delimited input
    file which contains parameters and options and outputs the appropriate fuel
    composition in atomic percent inside of a SERPENT file that is also specified in the
    input file. A sample input file is given below
    <<
    < Combined/Seperate >
    < Free/Preserved >
    < Path_to_SERPENT_input_file.txt >
    < A of isotope n , Z of n , < 1 , 2, 3, 4 >, BNC , BNH , Abudance, < 1 , -1  >
    >>
    The < 1234 > flag determines how the < Abundance > value is handled. This will be
    made more clear in the body of the code through comments and doc strings The < 1-1> fl    ag determines if the Abudnace is given in weight percent for its < 1234 > flag or atom    ic """

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

# initilizing FloatsInput array, the next 13 lines of code simply copy the csvinput
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
    molcar = 1.0 - FloatsInput[ 0 ][ 0 ]/100 - FloatsInput[ 0 ][ 1 ]/100
    for row in range( 1 , floatrows ):
      if FloatsInput[ row ][ 7 ] < 0:
        componentType = FloatsInput[ row ][ 2 ]
        masstotal = 0
        for i in range( 1 , floatrows ):
          if FloatsInput[ i ][ 2 ] == componentType:
            masstotal += FloatsInput[ i ][ 5 ] / FloatsInput[ i ][ 1 ]
        for i in range( 1, floatrows ):
          if FloatsInput[ i ][ 2 ] == componentType:
            FloatsInput[ i ][ 5 ] = 100 * FloatsInput[ i ][ 6 ] / FloatsInput[ i ][ 2 ] \
                / masstotal
            FlaotsInput[ i ][ 7 ] = 1
      if FloatsInput[ row ][ 2 ] == 1:
        FloatsInput[ row ].append( molcar * FloatsInput[ row ][ 5 ] )
    molsTotal = 0
    for i in range( 1 , floatrows ):
      if FloatsInput[ i ][ 2 ] == 3:
        molsTotal += FloatsInput[ 0 ][ 0 ] * FloatsInput[ i ][ 3 ] * \
            FloatsInput[ i ][ 5 ] / ( 100 * 100 )
        FloatsInput[ i ].append( FloatsInput[ 0 ][ 0 ] )
      if FloatsInput[ i ][ 2 ] == 4:
        molsTotal += FloatsInput[ 0 ][ 1 ] * FloatsInput[ i ][ 3 ] * \
            Floatsinput[ i ][ 5 ] / ( 100 * 100 )
        FloatsInput[ i ].append( FloatsInput[ 0 ][ 1 ] )
      if FloatsInput[ i ][ 2 ] == 2:
        SaltTotal = 0
        for j in range( 1 , floatrows ):
          molsTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ] * \
              FloatsInput[ i ][ 5 ] / ( 100 * 100 )
          SaltTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ]
        FloatsInput[ i ].append( SaltTotal * FloatsInput[ i ][ 5 ] )
      if FloatsInput[ i ][ 2 ] == 1:
        molsTotal += FloatsInput[ i ][ 3 ] * FloatsInput[ i ][ 5 ] * \
            FloatsInput[ i ][ 7 ] / ( 100 * 100 )
    for i in range( 1 , floatrows ):
      FloatsInput[ i ].append( FloatsInput[ i ][ 7 ] / molsTotal )

for i in range( floatrows ):
  print FloatsInput[ i ]

print "The SERPENT material conditioner has finished running"
exit()

