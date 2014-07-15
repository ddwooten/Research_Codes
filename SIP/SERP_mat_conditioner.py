# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import pdb as pdb
import scipy as sp
import pulp as pulp

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

#inputfile = raw_input( "Please enter file name, local path only, of csv file to open \n" )
inputfile = "test2.csv"
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

# This is the Free section. Ratio of componenets not given, simply
# max solubilities which are used.

if csvinput[ 0 ][ 0 ] == "Free" or csvinput[ 0 ][ 0 ] == "free" \
    or csvinput[ 0 ][ 0 ] == "FREE":
  print "Running under the \"Free\" assumption"
  molcar = 1
  for column in range( len( FloatsInput[ 0 ] ) ):
    molcar -= FloatsInput[ 0 ][ column ] / 100
  for row in range( 1 , floatrows ):
    if FloatsInput[ row ][ 6 ] < 0:
      componentType = FloatsInput[ row ][ 2 ]
      masstotal = 0
      for i in range( 1 , floatrows ):
        if FloatsInput[ i ][ 2 ] == componentType:
          masstotal += FloatsInput[ i ][ 5 ] / FloatsInput[ i ][ 1 ]
      for i in range( 1, floatrows ):
        if FloatsInput[ i ][ 2 ] == componentType:
          FloatsInput[ i ][ 5 ] = 100 * FloatsInput[ i ][ 5 ] / FloatsInput[ i ][ 1 ] \
              / masstotal
          FloatsInput[ i ][ 6 ] = 1
    if FloatsInput[ row ][ 2 ] == 1:
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ 5 ] )
    if FloatsInput[ row ][ 2 ] > 2:
      FloatsInput[ row ].append( FloatsInput[ 0 ][ int( FloatsInput[ row ][ 2 ] ) - 3 ] )
  molsTotal = 0
  for i in range( floatrows ):
    print FloatsInput[ i ]
  for i in range( 1 , floatrows ):
    if FloatsInput[ i ][ 2 ] > 2:
      molsTotal += FloatsInput[ 0 ][ int(FloatsInput[ i ][ 2 ] ) - 3 ] * FloatsInput[ i ][ 3 ] * \
          FloatsInput[ i ][ 5 ] / ( 100 )
    if FloatsInput[ i ][ 2 ] == 2:
      SaltTotal = 0
      for j in range( 1 , floatrows ):
        if FloatsInput[ j ][ 4 ] != 0:
          molsTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ] * \
              FloatsInput[ i ][ 5 ] * FloatsInput[ j ][ 5 ] / (100 * 100 )
          SaltTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ] * \
              FloatsInput[ i ][ 5 ] * FloatsInput[ j ][ 5 ] / (100 * 100 )
      FloatsInput[ i ].append( SaltTotal )
    if FloatsInput[ i ][ 2 ] == 1:
      molsTotal += FloatsInput[ i ][ 3 ] * FloatsInput[ i ][ 5 ] * \
          FloatsInput[ i ][ 7 ] / ( 100 )
  for i in range( 1 , floatrows ):
    FloatsInput[ i ].append( FloatsInput[ i ][ 7 ] * FloatsInput[ i ][ 5 ] \
        / ( molsTotal ) )

# This is the preserved seperate solver. I.E. the ratios of the different
# groups to one another are given, as are their max solubilities. A solution
# must be found that maximizes the groups in the salt but preserves their ratio.

if csvinput[ 0 ][ 0 ] == "Preserved" or csvinput[ 0 ][ 0 ] == "preserved" \
    or csvinput[ 0 ][ 0 ] == "PRESERVED":
  print "Running under the \"Preserved\" assumption"
  # initilize ratios array
  ratio = []
  for column in range( len( csvinput[ 1 ] ) ):
    ratio.append( float( csvinput[ 1 ][ column ] ) )
  # initilize multiplier array
  mult = []
  for column in range( len( ratio ) ):
    mult.append( FloatsInput[ 0 ][ column ] / ratio[ column ] )
  multiplier = max( ratio )
  solubility = ratio * multiplier
  molcar = 1
  for column in range( len( solubility ):
    molcar -= solublitiy[ column ]
  for row in range( 1 , floatrows ):
    if FloatsInput[ row ][ 6 ] < 0:
      componentType = FloatsInput[ row ][ 2 ]
      masstotal = 0
      for i in range( 1 , floatrows ):
        if FloatsInput[ i ][ 2 ] == componentType:
          masstotal += FloatsInput[ i ][ 5 ] / FloatsInput[ i ][ 1 ]
      for i in range( 1, floatrows ):
        if FloatsInput[ i ][ 2 ] == componentType:
          FloatsInput[ i ][ 5 ] = 100 * FloatsInput[ i ][ 5 ] / FloatsInput[ i ][ 1 ] \
              / masstotal
          FloatsInput[ i ][ 6 ] = 1
    if FloatsInput[ row ][ 2 ] == 1:
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ 5 ] )
    if FloatsInput[ row ][ 2 ] > 2:
      FloatsInput[ row ].append( FloatsInput[ 0 ][ int( FloatsInput[ row ][ 2 ] ) - 3 ] )
  molsTotal = 0
  for i in range( floatrows ):
    print FloatsInput[ i ]
  for i in range( 1 , floatrows ):
    if FloatsInput[ i ][ 2 ] > 2:
      molsTotal += FloatsInput[ 0 ][ int(FloatsInput[ i ][ 2 ] ) - 3 ] * FloatsInput[ i ][ 3 ] * \
          FloatsInput[ i ][ 5 ] / ( 100 )
    if FloatsInput[ i ][ 2 ] == 2:
      SaltTotal = 0
      for j in range( 1 , floatrows ):
        if FloatsInput[ j ][ 4 ] != 0:
          molsTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ] * \
              FloatsInput[ i ][ 5 ] * FloatsInput[ j ][ 5 ] / (100 * 100 )
          SaltTotal += FloatsInput[ j ][ 4 ] * FloatsInput[ j ][ 7 ] * \
              FloatsInput[ i ][ 5 ] * FloatsInput[ j ][ 5 ] / (100 * 100 )
      FloatsInput[ i ].append( SaltTotal )
    if FloatsInput[ i ][ 2 ] == 1:
      molsTotal += FloatsInput[ i ][ 3 ] * FloatsInput[ i ][ 5 ] * \
          FloatsInput[ i ][ 7 ] / ( 100 )
  for i in range( 1 , floatrows ):
    FloatsInput[ i ].append( FloatsInput[ i ][ 7 ] * FloatsInput[ i ][ 5 ] \
for i in range( floatrows ):
  print FloatsInput[ i ]

print "The SERPENT material conditioner has finished running"
exit()

