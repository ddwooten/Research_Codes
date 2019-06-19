#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import logging as logging
import copy as cp
import re as re
import numpy as np
# These import statements bring in custom modules
import wooten_common as wc

""" This is the SERPENT post processor. It requires a configuration
    file titled, exactly, "post_setup.txt". 
    This file must consist of two columns of text arragned as
    [ key ],[ value ]
    [ key ],[ value ]
    with no missing rows though whitespace is tolerated.
    Keys are given below with pertinent notes
        [host_file] - name of the SERPENT file that was run. i.e. there should
            be a file in the executing directory titled "host_file_dep.m" for
            burnup runs.
        [log_level] - the python logger utility logging level. If none is given
            it defaults to 0 
        [log_name] - the base name for the log file
        [process_burn] - yes/no to process burnup data
"""
def Read_Burn_File( base_name, options):
    """ This function reads in a SERPENT2 ( Aufiero and later mod ) burnup file
        and stores data as lists inside of a dictionary """
    
# Logging output 

    wc.Sep()

    logging.debug( "Read_Burn_File" )

    burn_data = {} 

    nuclide_indicies = {}
    
# Read in the data file

    raw_burn_data = wc.Read_Input( base_name + "_dep.m" , "string" )

# Strip the quotes at the beginning and end of every line

    raw_burn_data = [ x.strip( " " ) for x in raw_burn_data ]

# Generate a stored list of all the materials in the data file

    materials_list = Get_Materials_List( raw_burn_data , options )

# Logging output

    wc.Cep()

# Patterns to look for in the data file that identify and seperate
# data of interest

    index_pattern = re.compile( r'i(\d*)\s*=\s*(\d*)' )

    bu_pattern = re.compile( r'(BU)\s=' )

    day_pattern = re.compile( r'(DAYS)\s=' )

    mat_pattern = re.compile( r'MAT\S*' )

    tot_pattern = re.compile( r'TOT\S*' )

    vector_pattern = re.compile( r'\];$' )

    name_pattern = re.compile( r'_(\S*?)_' )

# Initiate some counters

    i = 0

    vectors = 0

# Loop through the read in data

    while ( i < len( raw_burn_data ) ):

# Process the next line

        line = raw_burn_data[ i ]

# Logging information

        logging.debug( "The iterator is on: " + str( i ) )

        logging.debug( "The line being processed is: " )

        if len( line ) > 41:

            logging.debug( line[ : 20 ] + "..." + line[ -20 : ] )

        else:

            logging.debug( line )
        
# These are regex search matches in the line. .match only matches at the
# beginning of a line. .search searches the whole line.

        index_match = index_pattern.match( line )

        bu_match = bu_pattern.match( line )
       
        day_match = day_pattern.match( line )
      
        mat_match = mat_pattern.match( line )
     
        tot_match = tot_pattern.match( line )
    
        vector_match = vector_pattern.search( line )
   
        if index_match:
  
            logging.info( "Index match!" )

# Get the indices of all the nuclides. This is needed later

            nuclide_indicies = Get_Nuclide_Indicies( line ,\
                nuclide_indicies )

            i += 1 

        elif bu_match:

            vectors += 1

            logging.info( "BU match!" )

            if vector_match:

# You found the BU vector which holds the burnup points in units of MWD/Kg
# Save this is a list to a dict key with the name BU

                burn_data[ bu_match.group(1) ] = Parse_Matlab_Vector( \
                    line )

                i += 1 

            else:

# Get the start and end line for the Matlab style matrix 

                start , i = Get_Matlab_Matrix( raw_burn_data , i )

# Save the matlab matrix as a numpy matrix in the dictionary

                burn_data[ bu_match.group(1) ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )

        elif day_match:

            vectors += 1

            logging.info( "Day match!" )

# Save the day vector

            if vector_match:

                burn_data[ day_match.group(1) ] = Parse_Matlab_Vector(\
                    line )

                i += 1

            else:

# Get the start and end of the Matlab matrix

                start , i = Get_Matlab_Matrix( raw_burn_data , i )

# Save the matlab matrix as a numpy matrix in the dict
 
                burn_data[ day_match.group(1) ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )

        elif mat_match or tot_match:

            vectors += 1

            logging.info( "Data match!" )

            if mat_match:

# Get the name of the material which was matched

                field_name = mat_match.group()

            else:

# Save the name of the total attribute which was matched

                field_name = tot_match.group() 

            logging.info( "Data is: " + field_name )

            if vector_match:

# Save the vector to the dict

                burn_data[ field_name ] = Parse_Matlab_Vector(\
                    line )

                i += 1

            else:

# Get the start and end line for the Matlab Matrix

                start , i = Get_Matlab_Matrix( raw_burn_data , i )

# Save the Matlab matrix as a numpy matrix

                burn_data[ field_name ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )

        else:

            i += 1

    logging.info( "The number of vectors is: " + str( vectors ) )

    output = { 'burn_data' :  burn_data ,
        'indicies' : nuclide_indicies , 
        'materials' :  materials_list
        }

    return( output )

def Get_Matlab_Matrix( contents , counter ):
    """ This function searches through a serpent dep file and extracts
        the currently selected matlab style matrix ( composing several lines
        of the file ) returning this matrix as a list """

    wc.Sep()

    logging.debug( "Get_Matlab_Matrix" )

# Save the start point of the MatLab matrix

    start = cp.deepcopy( counter )

# Look for the end pattern of a matlab matrix ( which is always more than one
# line which is how we differentiate a matrix from a vector )

    pattern = re.compile( r'\];' )

    match = None

# Keep moving through the file until you find the end of the matrix

    while ( match is None ):

        counter += 1

        logging.debug( "The line is: " )

        if len( contents[ counter ] ) > 41:

            logging.debug( contents[ counter ][ : 20 ] + "..." + \
                contents[ counter ][ -20 : ] )

        else:

            logging.debug( contents[ counter ] )

        match = pattern.search( contents[ counter ] )

        logging.debug( "The match is: " + str( match ) )

# You found the end of the matrix, return its start and end points

    output = [ start , counter ]

    return( output ) 

def Parse_Matlab_Matrix( begin , end , contents ):
    """ This function extracts numerical data from a matlab matrix and returns
        a numpy matrix of the data"""
    
    wc.Sep()
   
    logging.debug( "Parse_Matlab_Matrix" )
  
    output = list() 

# Move through the lines that Get_Matlab_Matrix provided
 
    for i in range( begin + 1 , end ):

        line = contents[ i ].split( " " )

# Many times comments are left at the end of lines beginning with %. Find this
# percent and ignore contents following it
        
        try:
       
            index = line.index( "%" )
# If there is not comment, just skip this step
               
        except:
     
            pass
   
# If there is a comment, cut the line at the comment
       
        else:

            line = line[ : index ]
  
        logging.debug( "The line is: " )
 
        if len( str( line ) ) > 41:

            logging.debug( str( line[ : 3 ] ) + "..." + str( line[ -3 : ] ) )

        else:

            logging.debug( str( line ) )

        line = [ float( x ) for x in line ]

# Append the new row of the matrix to the matrix
 
        output.append( line )

# Save the list of lists, as a numpy matrix

    output = np.matrix( output )

    return( output )

def Parse_Matlab_Vector( line ):
    """ This function extracts the numerical data from a matlab vector format
        and returns a numpy vector """

    wc.Sep()

    logging.debug( "Parse_Matlab_Vector" )

# Extract the vector from the given line with this pattern

    pattern = re.compile( r'\[.*?\]' )

# Actually extract the vector and stip it of brackets and the white space
# after them

    string = pattern.search( line ).group()[ 1 : -1 ].strip( " " )

    logging.debug( "The string is: " )

    if len( string ) > 41:

        logging.debug( string[ : 20 ] + "..." + string[ -20 : ] )

    else:

        logging.debug( string )

# Split the string into a list of elements by the white space between numbers

    nums = string.split( " " )

# Strip any comments that may be in this line which would always be at the end

    try:
 
        index = nums.index( "%" )
 
    except:
 
        pass
 
    else:

        nums = nums[ : index - 1 ]

    logging.debug( "The generated list is: " )
 
    if len( str( nums ) ) > 41:

        logging.debug( str( nums[  : 5 ] ) + "..." + str( nums[ -5 : ] ) )

    else:
 
        logging.debug( str( nums ) )

# Convert the string elements in the list to numbers
 
    nums = [ float( x ) for x in nums ]

# Save them as a numpy array 

    nums = np.array( nums )

    return( nums )

def Get_Nuclide_Indicies( string , index_dict ):
    """ This function reads through the burn file to get the matrix rows of
        each nuclide ( the index in matricies where it's info can be found ) """

    wc.Sep()

    logging.debug( "Get_Nuclide_Indicies" )

    logging.debug( "The string being analyzed is:" )

    logging.debug( string )

# This pattern finds the nuclide indices

    pattern = re.compile( r'i(\d*)\s*=\s*(\d*)' )

# Actually look for the pattern

    match = pattern.match( string )

    if match:

# If a nuclide indice was found save it in a dict

        index_dict[ int( match.group( 1 ) ) ] = int( match.group( 2 ) ) - 1

    logging.debug( "The key value pair generated is: " )

    logging.debug( match.group( 1 ) + " : " + match.group( 2 ) ) 

    return( index_dict )

def Get_Materials_List( contents , options ):
    """ This function generates a list of all the materials in the burn file"""

    wc.Sep()

    logging.debug( "Get_Materials_List" )

    materials = []

# This pattern will find material names in the data file

    pattern = re.compile(r'MAT_(\S*?)_VOLUME')

# Search the entire file

    for i in range( len( contents ) ):
        
        match = pattern.match( contents[ i ] )

        if match:

# If a material was found, append it to the list

            materials.append( match.group( 1 ) )

    logging.debug( "The materials found in the burnup file are: " )

    if 'log_level' in options:

        if options[ 'log_level' ] < 10:

            for i in range( len( materials ) ):

                logging.debug( str( materials[ i ] ) )

    return( materials )

def Report_Output( output , file_name ):
    """ This function is a debugging function to test the parse functions """

    wc.Sep()
    
    logging.debug( "Report_Output" )
   
    destination = open( file_name , "w" )

# Print all the information found 

    for key in output.keys():

        destination.write( "********************************************* \n" )

        destination.write( str( key ) + ": \n" )

        if isinstance( output[ key ] , list ):

            for i in range( len( output[ key ] ) ):

                string = str( output[ key ][ i ] ) + "\n"

                if len( string ) > 41:

                    destination.write( string[ : 20 ] + "..." + \

                        string[ -20 : ] )

                else:

                    destination.write( string )

        else:

            string = str( output[ key ] ) + "\n"

            if len( string ) > 41:

                destination.write( string[ : 20 ] + "..." + string[ -20 : ] )

            else:

                destination.write( string )

    destination.write( "********************************************* \n" )

    destination.write( "END!!" )

    destination.close()

    return

# Start the program

def Post_Main():
    """ This function runs the program if it is called as an import """

# Read the setup file, setup is a dict of user inputs

    setup = wc.Read_Setup( "post" )

# Try to start a log file

    try:

        wc.Start_Log( setup[ 'log_name' ] ,  setup[ "log_level" ] )

    except:

        wc.Start_Log( 'post_error' , 0 )

        logging.debug( "ERROR!!: < log_level > or < log_name > was not \n \
            found in post_setup.txt and as such LogLevel was set to 0 \n \
            and the base name to 'post_error' " )

    if 'log_level' in setup:

        if setup[ 'log_level' ] < 10:

            wc.Sep()
 
            logging.debug( "The input dictionary is: " )

            for keys,values in setup.items():

                logging.debug( str( keys ) + " : " + str( values ) )

# Storage container for all output

    output = {}

    if 'process_burn' in setup:

        if setup[ 'process_burn' ] == "yes" or "Yes" or "YES" or "y" or "Y": 

            burnup_data = Read_Burn_File( setup[ "host_file" ] , setup )

            output[ 'burnup_data' ] = burnup_data

    Report_Output( burnup_data , "report.test" )

    return( output )

