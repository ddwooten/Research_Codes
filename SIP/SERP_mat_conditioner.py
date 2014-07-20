# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import pdb as pdb
import scipy as sp
import time as time

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

def trunc( f , n ):
  ''' Truncates/pads a float f to n decimal places no rounding '''
  slen = len( '%.*f' % ( n , f ) )
  return str( f )[:slen]

print "Fuel Material Conditioner beginning"

# Here we define two stirngs we will use later to format the input for the serpent file

dzeros = "00"
tzeros = "000"

#inputfile = raw_input( "Please enter file name, local path only, of csv file to open \n" )
inputfile = "test2.csv"
print "Opening csv file now"

csvfile = open( inputfile, "r" )

print "Reading file now"

reader = csvreader.reader( csvfile )

# initilizing array
csvinput = []

# This creates an array of strings from the csv file
for row in reader:
  csvinput.append( row )

# This prints out the read in csv file, it should be commented out for
# real runs
for row in range( len ( csvinput ) ):
  print csvinput[ row ]

# This extracts the row in cvs input where the actual info begins and
# not header stuff.

StartRow = int( csvinput[ 0 ][ 1 ] )

# This extracts the temperature of the region being written and
# converts it to useful string for input

Temperature = csvinput[ 2 ][ 2 ]
if len( Temperature ) > 3:
  Temp = Temperature[ 0 : 2 ]
else:
  Temp = "0" + Temperature[ 0 : 1 ]
print "This is the temperature " + str(Temp)

# This extracts the name of the material being written

material = csvinput[ 0 ][ 2 ]

# This creates the dictionary of lookup values for the salt constituents.
# This is a patch for the original inability to have a mutliple species
# carrier salt.

CarrierComp = {}
for i in range( 1 , int( csvinput[ 3 ][ 0 ] ) * 2 , 2 ):
  CarrierComp[ int( csvinput[ 3 ][ i ] ) ] = float( csvinput[ 3 ][ i + 1 ] ) * \
      ( 1.0 / 100 )
print CarrierComp

# initilizing FloatsInput array, the next 13 lines of code simply copy the csvinput
# array into another array as float values as opposed to strings

FloatsInput=[]
csvinputrows = len( csvinput )
# Total rows in FloatsInput
floatrows = csvinputrows - StartRow
print " Creating floats array"
for i in range( floatrows ):
  FloatsInput.append( 0 )
# This is a clumsy way to turn csvinputs into floats, tmp array isn't
# really needed
for row in range( StartRow , csvinputrows ):
  tmpArray=[]
  for column in range( len( csvinput[ row ] ) ):
    if len( csvinput[ row ][ column ] ) > 0:
      tmpArray.append( float( csvinput[ row ][ column ] ) )
  FloatsInput[ row - StartRow ] = tmpArray
for i in range( floatrows ):
  print FloatsInput[ i ]

# This is the Free section. Ratio of componenets not given, simply
# max solubilities which are used.

if csvinput[ 0 ][ 0 ] == "Free" or csvinput[ 0 ][ 0 ] == "free" \
    or csvinput[ 0 ][ 0 ] == "FREE":
  print "Running under the \"Free\" assumption"
# molcar is the molar percentage of base salt after additions of fuel salt
  molcar = 1
# This simply calculates the molar percentage of base salt
  for column in range( len( FloatsInput[ 0 ] ) ):
    molcar -= FloatsInput[ 0 ][ column ] / 100
# This converts all weight percentages to atomic percentages by
# looping over a catagory given in weight and doing the appropriate
# math
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
# This ends the weight to atom percent converter
# Right below is where the atomic percentage of a carrier componenet is
# adjusted to the molar percentage. This is where the use of the
# dictionary should occur
    if FloatsInput[ row ][ 2 ] == 1:
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ 5 ] * \
          CarrierComp[ int( FloatsInput[ row ][ 0 ] ) ] )
# This is where the mol fraction of the fuel group constituent is
# inserted into the floats array for each group appropriately
    if FloatsInput[ row ][ 2 ] > 2:
      FloatsInput[ row ].append( FloatsInput[ 0 ][ int( FloatsInput[ row ][ 2 ] ) - 3 ] )
# molsTotal is a way of summing up all the contributions of the molar
# constituents. For example, if U is 24 mol percent of the fuel, and Li
# is 100 percent of the carrier and the carrier is 76 mol percent and
# the other const is F, molsTotal = 24 + 76 (Li) + 76 (F). The trick we
# get into is for the host, say F. We don't have a mols for F, we simply
# calculate them (in the if == 2 section) by the mols of everything
# that uses fluoride. Then we get atomic percentage, in the salt, of
# all components
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
# For comments on how sections work, see the above Free solver.

if csvinput[ 0 ][ 0 ] == "Preserved" or csvinput[ 0 ][ 0 ] == "preserved" \
    or csvinput[ 0 ][ 0 ] == "PRESERVED":
  print "Running under the \"Preserved\" assumption"
  # initilize ratios array
  ratio = []
  for column in range( len( csvinput[ 1 ] ) ):
    if len ( csvinput[ 1 ][ column ] ) > 0:
      ratio.append( float( csvinput[ 1 ][ column ] ) )
  # initilize multiplier array
  print " Displaying ratio array"
  print ratio
  mult = []
# The only thing I will explain is this. What this does,
# is because the total mol fraction of a perserved ratio of
# fuel components is limited by the componenet with the least
# solubility, this finds the minimum multiplier of the ratio
# that will determine the mol percents.
  for column in range( len( ratio ) ):
    mult.append( FloatsInput[ 0 ][ column ] / ratio[ column ] )
  print " Displaying multiplier array"
  print mult
  multiplier = min( mult )
  print " Displaying multiplier"
  print multiplier
  print "Adusting FloatsInput 0th row "
  for column in range( len( FloatsInput[ 0 ] ) ):
    FloatsInput[ 0 ][ column ] = ratio[ column ] * multiplier
  print FloatsInput[ 0 ]
  molcar = 1
  for column in range( len( FloatsInput[ 0 ] ) ):
    molcar -= FloatsInput[ 0 ][ column ] / 100
  print "The value of molcar is " + str(molcar)
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
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ 5 ] * \
          CarrierComp[ int( FloatsInput[ row ][ 0 ] ) ] )
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
# This here truncates the floating atomic percentages to 6 decimal palces,
# or 1/10,000 of a percent accuracy
for row in range( 1 , floatrows ):
  FloatsInput[ row ][ 8 ] = trunc( ( FloatsInput[ row ][ 8 ] / 100.0 ) , 6 )
for i in range( floatrows ):
  print FloatsInput[ i ]

HostFileName = csvinput[ 2 ][ 0 ][ 1 : len( csvinput[ 2 ][ 0 ] ) - 1 ]

print HostFileName

HostFile = open( HostFileName , "r" )

# This is going to be the index where to grab the file name

NameStartIndex = HostFileName.rfind("/") + 1

# This is going to be the index where to chop off the extension

NameEndIndex = HostFileName.rfind(".")

BaseName = HostFileName[ NameStartIndex : NameEndIndex ]

NameExtension = csvinput[ 2 ][ 1 ][ 1 : len( csvinput[ 2 ][ 1 ] ) - 1 ]

NewFileName = BaseName + "_" + NameExtension + "_" + time.strftime( "%d_%m_%Y" ) \
    + ".txt"

print NewFileName

NewFile = open( str( NewFileName ) , "w" )

NewFile.write( "% ------ Created on " + time.strftime( "%d %m %Y") + " at " + \
    time.strftime( "%H:%M" ) + "\n" )

# This loops through the host file writting out its contents to the new file. It contains an if
# statement to catch the fuel material section and insert the new data

for line in HostFile:
  if line.find( "mat " + material ) > 0:
    NewFile.write( line )
    for row in range( 1, floatrows - 1 ):
      Z = str( FloatsInput[ row ][ 0 ] )
      A = str( FloatsInput[ row ][ 1 ] )
      Isotope = Z + A + "." + Temp + "c"
      NewFile.write( "{:<10}{}".format( Isotope , FloatsInput[ row ][ 9 ] ) + "\n" )
  else:
    NewFile.write( line )

HostFile.close()

NewFile.close()

print "The SERPENT material conditioner has finished running"
exit()

