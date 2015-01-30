#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import time as time
import sys as sys
import logging as logging
    """ This is the SERPENT Incremental Pitch code. It requires a configuration
    file titled, exactly, "pitches.txt". This file must consist of one column
    of numbers. These numbers are the pitches, in cm, to be used. Additionally
    """

def Read_Setup():
    """ This function reads in a file named "init_setup.txt". It stores this 
    file as a list object from which the file's contents can be retrieved."""
        input_file = open( "init_setup.txt" , "r" )
        setup_file = input_file.readlines()
        setup_file = [ x.rstrip( "\n" ) for x in setup_file ]
        input_file.close()
        return( setup_file )

def Get_Base_Name( file_name ):
    """ This function gets a base name from the host file name """
    end_index = file_name.rfind( "." )
    base_name = file_name[ 0 : end_index ]
    return( base_name )

def Start_Log( base_name , level ): 
    log_file_name = base_name + "_" + time.strftime( "%d_%m_%Y" ) \
        + "_log" + ".txt"

    LogLevel = level 

    logging.basicConfig( filename = log_file_name , format = \
        "[%(levelname)8s] %(message)s" , filemode = 'w' , level = LogLevel )
    logging.debug( "This is the debug level reporting in" )
    logging.info( "This is the info level reporting in " )
    logging.warning( "This is the warning level reporting in" )
    logging.error( "This is the error level reporting in" )
    logging.critical( "This is the critical level reporting in" )

def Cep():
	''' A wrapper to place file seperators in a log file for the
	debug level '''
	logging.debug( "*****************************************************" )
	return()

#Function, refer to docstring for purpose
def Sep():
    '''A wrapper to visually seperate functions in log files'''
    logging.debug( '//////////////////////////////////////////////////////' )
    return()

def Read_Input( file_name , Sep ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list. """
    Sep()
    logging.debug( "Reading in file: " + file_name )
    input_file = open( file_name , "r" )
    file_contents = input_file.readlines()
    logging.debug( "Closing file: " + file_name )
    input_file.close()
    return( file_contents )

def Gen_Pitch_or_Diameter( pd , given , desired , Sep ):
    """ This function generates a list of either diameters or pitches from 
    a list of pitch to diameter ratios depending on which one is additionally
    given"""
    Sep()
    if desired == "diameter":
        output = given / pd
        logging.debug( "The generated diameters are: " )
        logging.debug( output )
    elif desired == "pitch":
        output = given * pd
        logging.debug( "The generated pitches are: " )
        logging.debug( output )
    else:
        print( "ERROR: Choice of pitch or diameter ( given as 'pitch' or \n \
            'diameter' ) was not properly given. Goodbye. " )
        logging.debug( "< desired > in function < Gen_Pitch_or_Diameter > \n \
            was neither 'diameter' nor 'pitch'" )
        exit()
    return( output )

def Gen_Width_List( cladding, Sep ):
    """ This function creates a list of floats for clad widths """
    Sep()
    logging.debug( "The initial cladding array is: ")
    logging.debug( cladding )
    widths = [ float( x ) for x in cladding[ 1 : : 2 ] ]
    logging.debug( "The widths array is: " )
    logging.debug( widths )
    return( widths )

def Gen_Materials_List( cladding, Sep ):
    """ This function creates a list of strings for the materials """
    Sep()
    logging.debug( "The initial cladding array is: " )
    logging.debug( cladding )
    materials = cladding[ 0 : : 2 ]
    logging.debug( "The materials array is: ")
    logging.debug( materials )
    return( materials )


def Gen_Inmost_Radius( widths , diameter , Sep ):
    """ This function generates the inner substance radius """
    Sep()
    logging.debug( "The widths are: " + str( widths ) )
    logging.debug( "The sum of widths is: " + str( sum( widths ) ) ) 
    inner_radius = diameter \ 2.0 - sum( widths )
    logging.debug( "The inner radius is: " + str( inner_radius ) )
    return( inner_radius )

def Gen_Cladding_Radii( widths , inner_radius , Sep , Cep ):
    """ This function generates the outer radii for each clad layer """
    Sep()
    radii = []
    logging.debug( "The widths array is: " + str( widths ) )
    for i in range( len( inner_radius ) ):
        Cep()
        logging.debug( "Inner radius being built is: " + str( \
            inner_radius[ i ] ) )
        width = [ inner_radius ]
        for j in range( len( widths ) - 1 ):
            width.append( width[ j ] + widths[ j ] ) 
        logging.debug( "The build array is: " + str( widths ) ) 
        radii.append( width )
    if LogLevel < 10:
        Cep()
        logging.debug( "The final build array is: " )
        for radius in radii:
            logging.debug( str( radius ) )
    return( radii )

def Surface_Line_Writer( material , radius , lattice , x_pos , y_pos , \
    shape , id_num , Sep ):
    """ This function generates the strings for surfaces, both comment and
    actual """
    Sep()
    comment_string = "% ------ " + material + " Surface"
    surf_string = "surf    " + str( id_num ) + "    " + shape + "    " + \
        str( x_pos ) + "    " + str( y_pos ) + "    " + str( radius )
    if shape != "cyl":
        surf_string = surf_string + "    0.0"
    output = [ comment_string , surf_string ]
    return( output )

def Cell_Line_Writer( material , outer_bound , inner_bound , id_num , \
    uni_num , Sep )
    """ This function writes strings for cells """
    Sep()
    if material == "outside"
        cell_string = "{ 0 }    { 1 }    { 2 }    { 3 }{ 4:>19}{ 5:<6 }".\
            format( "cell" , str( id_num ) , str( uni_num ) , material , \
                str( inner_bound ) , str( outer_bound ) )
    else: 
        cell_string = "{ 0 }    { 1 }    { 2 }    fill { 3 }{ 4:>19}{ 5:<6 }".\
            format( "cell" , str( id_num ) , str( uni_num ) , material , \
                str( inner_bound ) , str( outer_bound ) ) 
    return( cell_string )

def Files_Generator( base_name , materials , radii , host_file , options, \
     Sep , Cep ):
    """ This function generates values to pass to the string writers and then
    inserts these values into the file to be written actually writes the
     contents to file """
    Sep()
    surf_start = host_file.index( "% ------ RSAC\n" )
    cell_start = host_file.index( "% ------ AGC\n" )
    lattice = options[ "la    
     
# Opens, as a file object, the file containing the pitches to be calculated
inputfile = open( "pitches.txt", "r" )

# Extract the name of the file to be modified, i.e., the host
HostFileName = inputfile.readline()

HostFile = open( HostFileName , "r" )

# This is going to be the index where to grab the file name

NameStartIndex = HostFileName.rfind("/") + 1

# This is going to be the index where to chop off the extension

NameEndIndex = HostFileName.rfind(".")

BaseName = HostFileName[ NameStartIndex : NameEndIndex ]

# Loop over the input file and store the pitches
# First, initilize an array to hold the pitches
pitches = []
i = 0
for line in inputfile:
    pitches.append( float( line ) )
    if LogLevel < 10 logging.debug( "The " + str( i ) + "th pitch is " + \
        str( pitches[ i ] ) )
    i += 1


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

material = csvinput[ 0 ][ 2 ][ 0 : len( csvinput[ 0 ][ 2 ] ) ]
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
    NewString2 = OldString[ Anchor + 10 : ]
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

logging.info( "Code has finished running succesfully" )

logging.shutdown()
exit()

