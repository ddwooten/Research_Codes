# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import pdb as pdb
import time as time
import sys as sys
import logging as logging

""" SERP_mat_conditioner is a simple python script that takes in a comma delimited input
    file which contains parameters and options and outputs the appropriate fuel
    composition in atomic percent inside of a SERPENT file that is also specified in the
    input file. A sample input file is given below
    <<
    < Free/Preserved , [number of header lines] , [Material Name] , [Density Option] , [Temperature in K]
        , [ logger option] >
    < [Path_to_SERPENT_input_file.txt] , [Mid Part of New File Name] >
    < [ Ratio of group n] , [Ratio of group n + 1] , [ ....N] >
    < [ Number of carrier salt species ] , [ Z of n species ] , [Ratio of n species ] ,  [ Z of N ] , [ R of N] >
    < [ Num of salt species ] , [ Z of non host ] , [ Density of species with Z and host ] .... [ Nth species ] >
    < [ele],[iso],[grp],[cth],[htc],[pct],[ptt],[mof],[atf] #These are the columns in the input files below which
      #correspond to the above catagories >
    <  [ Comments ] >
    < [ele] , [iso] , [grp], [htc] ,[cth] , [pct],[ptt]
    >>
    [logger option] sets theh logger default level. 0 for all, > 10 for just info and crits
    [Material Name] is the exact material name used in SERPENT
    [ Density Option] -1 indicates a desire to calculate density using the density array (row 4) a
      positive number will be taken as the input density
    [ Ratio of group n] in the 2nd row is for the preserved option where a spent fuel ratio is
      desired to be preserved
    [ele] is the Z number of each isotope
    [iso] is the A number of each isotope
    [grp] is the salt calculation group (detemrines how it is handled)
      1 = Salt Constituent, think Na in NaCl
      2 = Salt Primary Carrier, think Cl in NaCl
      3...N = all other groups, generally assumed to be fuel
    [htc] is the number of group 2 atoms per that element in the salt
    [cth] is the number of that element atoms per group 2 atom
    [pct] is the input atomic or weight percentage within the group. Unless it is group 1
      in which case it is the atomic percentage of that element's isotope within that element
    [ptt] where -1 indicates a weight percentage and 1 indicates an atomic percentage for input
      option [pct]
    """
def trunc( f , n ):
  ''' Truncates/pads a float f to n decimal places no rounding '''
  slen = len( '%.*f' % ( n , f ) )
  return str( f )[:slen]

#print "Fuel Material Conditioner beginning"

# Here we define two stirngs we will use later to format the input for the serpent file

dzeros = "00"
tzeros = "000"

inputfile = raw_input( "Please enter file name, local path only, of csv file to open \n" )
#print "Opening csv file now"

csvfile = open( inputfile, "r" )

#print "Reading file now"

reader = csvreader.reader( csvfile )

# initilizing array
csvinput = []

# This creates an array of strings from the csv file
for row in reader:
  csvinput.append( row )

HostFileName = csvinput[ 1 ][ 0 ][ 1 : len( csvinput[ 1 ][ 0 ] ) - 1 ]

HostFile = open( HostFileName , "r" )

# This is going to be the index where to grab the file name

NameStartIndex = HostFileName.rfind("/") + 1

# This is going to be the index where to chop off the extension

NameEndIndex = HostFileName.rfind(".")

BaseName = HostFileName[ NameStartIndex : NameEndIndex ]

NameExtension = csvinput[ 1 ][ 1 ][ 1 : len( csvinput[ 1 ][ 1 ] ) - 1 ]

NewFileName = BaseName + "_" + NameExtension + "_" + time.strftime( "%d_%m_%Y" ) \
    + ".txt"

LogFileName = BaseName + "_" + NameExtension + "_" + time.strftime( "%d_%m_%Y" ) \
    + "_log" + ".txt"

NewFile = open( str( NewFileName ) , "w" )

try:
  LogLevel = int( csvinput[ 0 ][ 5 ] )
except:
  sys.exit( "ERROR!!: Log level can not be cast as an integer!" )

logging.basicConfig( filename = LogFileName , format ="[%(levelname)8s] %(message)s" \
    , filemode = 'w' , level = LogLevel )
logging.debug( "This is the debug level reporting in" )
logging.info( "This is the info level reporting in " )
logging.warning( "This is the warning level reporting in" )
logging.error( "This is the error level reporting in" )
logging.critical( "This is the critical level reporting in" )

# This reads in values of the locations in the array where information
# can be found and assings it to its identifiers

ele = int( csvinput[ 5 ][ 0 ] )
iso = int( csvinput[ 5 ][ 1 ] )
grp = int( csvinput[ 5 ][ 2 ] )
cth = int( csvinput[ 5 ][ 3 ] )
htc = int( csvinput[ 5 ][ 4 ] )
pct = int( csvinput[ 5 ][ 5 ] )
ptt = int( csvinput[ 5 ][ 6 ] )
mof = int( csvinput[ 5 ][ 7 ] )
atf = int( csvinput[ 5 ][ 8 ] )

# This prints out the read in csv file, it should be commented out for
# real runs
#for row in range( len ( csvinput ) ):
#  print csvinput[ row ]

# This extracts the row in cvs input where the actual info begins and
# not header stuff.

StartRow = int( csvinput[ 0 ][ 1 ] )

# This extracts the temperature of the region being written and
# converts it to useful string for input

Temperature = csvinput[ 0 ][ 4 ]
if len( Temperature ) > 3:
  Temp = Temperature[ 0 : 2 ]
else:
  Temp = "0" + Temperature[ 0 : 1 ]

logging.info( "The temperature is " + str( Temperature ) )
logging.info( "The SERPENT tempreature library is " + str( Temp ) )

# This extracts the name of the material being written

material = csvinput[ 0 ][ 2 ][ 1 : len( csvinput[ 0 ][ 2 ] ) - 1 ]
mat = "mat    " + material

logging.info( "The material search pattern is " + str( mat ) )
# This creates the dictionary of lookup values for the salt constituents.
# This is a patch for the original inability to have a mutliple species
# carrier salt.

CarrierComp = {}
for i in range( 1 , int( csvinput[ 3 ][ 0 ] ) * 2 , 2 ):
  CarrierComp[ int( csvinput[ 3 ][ i ] ) ] = float( csvinput[ 3 ][ i + 1 ] ) * \
      ( 1.0 / 100 )

logging.debug( "The CarrierComp is " + str( CarrierComp ) )

# initilizing FloatsInput array, the next 13 lines of code simply copy the csvinput
# array into another array as float values as opposed to strings

FloatsInput=[]
csvinputrows = len( csvinput )
# Total rows in FloatsInput
floatrows = csvinputrows - StartRow
#print " Creating floats array"
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

if LogLevel <= 10:
  logging.debug( "At initilization FloatsInput has the form")
  for row in range( floatrows ):
    logging.debug( FloatsInput[ row ] )

# This is the Free section. Ratio of componenets not given, simply
# max solubilities which are used.

if csvinput[ 0 ][ 0 ] == "Free" or csvinput[ 0 ][ 0 ] == "free" \
    or csvinput[ 0 ][ 0 ] == "FREE":
  logging.info( "Running under the \"Free\" assumption" )
# molcar is the molar percentage of base salt after additions of fuel salt
  molcar = 1
# This simply calculates the molar percentage of base salt
  for column in range( len( FloatsInput[ 0 ] ) ):
    molcar -= FloatsInput[ 0 ][ column ] / 100
  logging.debug( "molcar has the value " + str( molcar ) )
# This converts all weight percentages to atomic percentages by
# looping over a catagory given in weight and doing the appropriate
# math
  for row in range( 1 , floatrows ):
    if FloatsInput[ row ][ ptt ] < 0:
      if FloatsInput[ row ][ grp ] == 1:
        sys.exit("ERROR!!: Carrier constituent fractions are not allowed as \
            weight percents! Please correct to atomic percents as percentages \
            of element type! Yes we know this is buggy but is a result of \
            development occuring in stages")
      componentType = FloatsInput[ row ][ grp ]
      masstotal = 0
      for i in range( 1 , floatrows ):
        if FloatsInput[ i ][ grp ] == componentType:
          masstotal += FloatsInput[ i ][ pct ] / FloatsInput[ i ][ iso ]
      for i in range( 1, floatrows ):
        if FloatsInput[ i ][ grp ] == componentType:
          FloatsInput[ i ][ pct ] = 100 * FloatsInput[ i ][ pct ] / FloatsInput[ i ][ iso ] \
              / masstotal
          FloatsInput[ i ][ ptt ] = 1
# This ends the weight to atom percent converter
# Right below is where the atomic percentage of a carrier componenet is
# adjusted to the molar percentage. This is where the use of the
# dictionary should occur
    if FloatsInput[ row ][ grp ] == 1:
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ pct ] * \
          CarrierComp[ int( FloatsInput[ row ][ ele ] ) ] )
# This is where the mol fraction of the fuel group constituent is
# inserted into the floats array for each group appropriately
    if FloatsInput[ row ][ grp ] > 2:
      FloatsInput[ row ].append( FloatsInput[ 0 ][ int( FloatsInput[ row ][ grp ] ) - 3 ] )
# molsTotal is a way of summing up all the contributions of the molar
# constituents. For example, if U is 24 mol percent of the fuel, and Li
# is 100 percent of the carrier and the carrier is 76 mol percent and
# the other const is F, molsTotal = 24 + 76 (Li) + 76 (F). The trick we
# get into is for the host, say F. We don't have a mols for F, we simply
# calculate them (in the if == 2 section) by the mols of everything
# that uses fluoride. Then we get atomic percentage, in the salt, of
# all components
# Also, right below, is a density calculator is denstity calculation
# is desired
  if LogLevel <= 10:
    logging.debug( "After modification for weight percentage and molar ratios" )
    logging.debug( "FloatsInpput has the value seen below" )
    for row in range( floatrows ):
      logging.debug( FloatsInput [ row ] )
  if float( csvinput[ 0 ][ 3 ] ) < 0:
    logging.debug( "A density calculation request was made")
    density = 0.0
    DensityArray = {}
    for i in range( 1 , int( csvinput[ 4 ][ 0 ] ) * 2 , 2 ):
      DensityArray[ int( csvinput[ 4 ][ i ] ) ] = float( csvinput[ 4 ][ i + 1 ] )
    logging.debug( "DensityArray has the value seen below" )
    logging.debug( DensityArray )
    for i in range( 1 , floatrows ):
      if FloatsInput[ i ][ grp ] != 2:
        density += DensityArray[ int( FloatsInput[ i ][ ele ] ) ] * \
            FloatsInput[ i ][ mof ] * FloatsInput[ i ][ pct ] * ( 1.0 / 10000.0 )
    density = str( density )
  else:
    density = csvinput[ 0 ][ 3 ]
  logging.debug( "density has the value of " + str( density ) )
  molsTotal = 0
  for i in range( 1 , floatrows ):
    if FloatsInput[ i ][ grp ] > 2:
      molsTotal += FloatsInput[ 0 ][ int(FloatsInput[ i ][ grp ] ) - 3 ] * FloatsInput[ i ][ cth ] * \
          FloatsInput[ i ][ pct ] / ( 100 )
    if FloatsInput[ i ][ grp ] == 2:
      SaltTotal = 0
      for j in range( 1 , floatrows ):
        if FloatsInput[ j ][ grp ] != 2:
          molsTotal += FloatsInput[ j ][ htc ] * FloatsInput[ j ][ mof ] * \
              FloatsInput[ i ][ pct ] * FloatsInput[ j ][ pct ] / (100 * 100 )
          SaltTotal += FloatsInput[ j ][ htc ] * FloatsInput[ j ][ mof ] * \
              FloatsInput[ i ][ pct ] * FloatsInput[ j ][ pct ] / (100 * 100 )
      FloatsInput[ i ].append( SaltTotal )
    if FloatsInput[ i ][ grp ] == 1:
      molsTotal += FloatsInput[ i ][ cth ] * FloatsInput[ i ][ pct ] * \
          FloatsInput[ i ][ mof ] / ( 100 )
  for i in range( 1 , floatrows ):
    FloatsInput[ i ].append( FloatsInput[ i ][ mof ] * FloatsInput[ i ][ pct ] \
        * FloatsInput[ i ][ cth ]/ ( molsTotal ) )
  logging.debug( "molsTotal has the value " + str( molsTotal ) )
  if LogLevel <= 10:
    logging.debug( "FloatsInput with atomic ratios is as seen below" )
    for row in range( floatrows ):
      logging.debug( FloatsInput[ row ] )
# This is the preserved seperate solver. I.E. the ratios of the different
# groups to one another are given, as are their max solubilities. A solution
# must be found that maximizes the groups in the salt but preserves their ratio.
# For comments on how sections work, see the above Free solver.

if csvinput[ 0 ][ 0 ] == "Preserved" or csvinput[ 0 ][ 0 ] == "preserved" \
    or csvinput[ 0 ][ 0 ] == "PRESERVED":
  logging.info( "Running under the \"Preserved\" assumption" )
  # initilize ratios array
  ratio = []
  for column in range( len( csvinput[ 2 ] ) ):
    if len ( csvinput[ 2 ][ column ] ) > 0:
      ratio.append( float( csvinput[ 2 ][ column ] ) )
  logging.debug( "The ratio array has value seen below" )
  logging.debug( ratio )
  # initilize multiplier array
  #print " Displaying ratio array"
  #print ratio
  mult = []
# The only thing I will explain is this. What this does,
# is because the total mol fraction of a perserved ratio of
# fuel components is limited by the componenet with the least
# solubility, this finds the minimum multiplier of the ratio
# that will determine the mol percents.
  for column in range( len( ratio ) ):
    mult.append( FloatsInput[ 0 ][ column ] / ratio[ column ] )
  logging.debug( "mult has value seen below" )
  logging.debug( mult )
  multiplier = min( mult )
  logging.debug( "multiplier has the value " + str( multiplier ) )
  for column in range( len( FloatsInput[ 0 ] ) ):
    FloatsInput[ 0 ][ column ] = ratio[ column ] * multiplier
  if LogLevel <= 10:
    logging.debug( "After ratio modification FloatsInpput has value seen below" )
    for row in range( floatrows ):
      logging.debug( FloatsInput[ row ] )
  molcar = 1
  for column in range( len( FloatsInput[ 0 ] ) ):
    molcar -= FloatsInput[ 0 ][ column ] / 100
  logging.debug( "molcar has the value " + str( molcar ) )
  for row in range( 1 , floatrows ):
    if FloatsInput[ row ][ ptt ] < 0:
      if FloatsInput[ row ][ grp ] == 1:
        sys.exit("ERROR!!: Carrier constituent fractions are not allowed as \
            weight percents! Please correct to atomic percents as percentages \
            of element type! Yes we know this is buggy but is a result of \
            development occuring in stages")
      componentType = FloatsInput[ row ][ grp ]
      masstotal = 0
      for i in range( 1 , floatrows ):
        if FloatsInput[ i ][ grp ] == componentType:
          masstotal += FloatsInput[ i ][ pct ] / FloatsInput[ i ][ iso ]
      for i in range( 1, floatrows ):
        if FloatsInput[ i ][ grp ] == componentType:
          FloatsInput[ i ][ pct ] = 100 * FloatsInput[ i ][ pct ] / FloatsInput[ i ][ iso ] \
              / masstotal
          FloatsInput[ i ][ ptt ] = 1
    if FloatsInput[ row ][ grp ] == 1:
      FloatsInput[ row ].append( molcar * FloatsInput[ row ][ pct ] * \
          CarrierComp[ int( FloatsInput[ row ][ ele ] ) ] )
    if FloatsInput[ row ][ grp ] > 2:
      FloatsInput[ row ].append( FloatsInput[ 0 ][ int( FloatsInput[ row ][ grp ] ) - 3 ] )
# This determines if a density calculation is desired and if so
# the caluclation is performed
  if LogLevel <= 10:
    logging.debug( "After weight percentage and molar ratio mods FloatsInput has value")
    for row in range( floatrows ):
      logging.debug( FloatsInput[ row ] )
  if float( csvinput[ 0 ][ 3 ] ) < 0:
    logging.debug( "A density calculation request was made")
    density = 0.0
    DensityArray = {}
    for i in range( 1 , int( csvinput[ 4 ][ 0 ] ) * 2 , 2 ):
      DensityArray[ int( csvinput[ 4 ][ i ] ) ] = float( csvinput[ 4 ][ i + 1 ] )
    logging.debug( "DensityArray has the value seen below" )
    logging.debug( DensityArray)
    for i in range( 1 , floatrows ):
      if FloatsInput[ i ][ grp ] != 2:
        density += DensityArray[ int( FloatsInput[ i ][ ele ] ) ] * \
            FloatsInput[ i ][ mof ] * FloatsInput[ i ][ pct ] * ( 1.0 / 10000.0 )
    density = str( density )
  else:
    density = csvinput[ 0 ][ 3 ]
  logging.debug( "density has the value " + str( density ) )
  molsTotal = 0
  for i in range( 1 , floatrows ):
    if FloatsInput[ i ][ grp ] > 2:
      molsTotal += FloatsInput[ 0 ][ int(FloatsInput[ i ][ grp ] ) - 3 ] * FloatsInput[ i ][ cth ] * \
          FloatsInput[ i ][ pct ] / ( 100 )
    if FloatsInput[ i ][ grp ] == 2:
      SaltTotal = 0
      for j in range( 1 , floatrows ):
        if FloatsInput[ j ][ grp ] != 2:
          molsTotal += FloatsInput[ j ][ htc ] * FloatsInput[ j ][ mof ] * \
              FloatsInput[ i ][ pct ] * FloatsInput[ j ][ pct ] / (100 * 100 )
          SaltTotal += FloatsInput[ j ][ htc ] * FloatsInput[ j ][ mof ] * \
              FloatsInput[ i ][ pct ] * FloatsInput[ j ][ pct ] / (100 * 100 )
      FloatsInput[ i ].append( SaltTotal )
    if FloatsInput[ i ][ grp ] == 1:
      molsTotal += FloatsInput[ i ][ cth ] * FloatsInput[ i ][ pct ] * \
          FloatsInput[ i ][ mof ] / ( 100 )
  for i in range( 1 , floatrows ):
    FloatsInput[ i ].append( FloatsInput[ i ][ mof ] * FloatsInput[ i ][ pct ] \
        * FloatsInput[ i ][ cth ] / ( molsTotal ) )
  logging.debug( "molsTotal has the value " + str( molsTotal ) )
  if LogLevel <= 10:
    logging.debug( "FloatsInput, after atomic ratio calc, has value seen below" )
    for row in range( floatrows ):
      logging.debug( FloatsInput[ row ] )

# This here truncates the floating atomic percentages to 6 decimal palces,
# or 1/10,000 of a percent accuracy
for row in range( 1 , floatrows ):
  FloatsInput[ row ][ atf ] = "%.10f" % ( FloatsInput[ row ][ atf ] / 100.0 )
if LogLevel <= 10:
  logging.debug( "After truncation to strings FloatsInput has the valeu" )
  for row in range( floatrows ):
    logging.debug( FloatsInput[ row ] )


NewFile.write( "% ------ Created on " + time.strftime( "%d-%m-%Y") + " at " + \
    time.strftime( "%H:%M" ) + "\n" )
NewFile.write( "% ------ Comments:" + "\n" )
NewFile.write( "% ------ << \n")
if len( csvinput[ 6 ][ 0 ] ) > 0:
  for i in range( 0 , len( csvinput[ 6 ][ 0 ] ) , 49 ):
    NewFile.write( "% ------ < " + csvinput[ 6 ][ 0 ][ i : i + 49 ] + "\n" )
NewFile.write( "% ------ >> \n")

# This loops through the host file writting out its contents to the new file. It contains an if
# statement to catch the fuel material section and insert the new data

for line in HostFile:
  if line.find( mat ) > -1:
    OldString = line
    Anchor = OldString.find( "tmp" )
    NewString1 = OldString[ 0 : Anchor - 9 ]
    NewString2 = OldString[ Anchor + 6 + len( csvinput[ 0 ][ 4 ] ) : ]
    NewString = NewString1 + "-" + density + "    tmp    " + csvinput[ 0 ][ 4 ] + "    " + \
        NewString2
    NewFile.write( NewString )
    for row in range( 1, floatrows ):
      Z = str( int( FloatsInput[ row ][ ele ] ) )
      #print Z
      A = str( int( FloatsInput[ row ][ iso ] ) )
      #print A
      ModA = tzeros[ 0 : ( 3 - len ( A ) ) ] + A
      Isotope = Z + ModA + "." + Temp + "c"
      #print Isotope
      NewFile.write( "{:<14}{}".format( Isotope , FloatsInput[ row ][ atf ] ) + "\n" )
  else:
    NewFile.write( line )

HostFile.close()

NewFile.close()

logging.info( "Code has finished running succesfully")

logging.shutdown()
exit()

