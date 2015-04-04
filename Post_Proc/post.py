#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import time as time
import logging as logging
import copy as cp
import re as re

""" This is the SERPENT volume writter code. It requires a configuration
file titled, exactly, "vol_setup.txt". This file must consist of two columns
of text arragned as
    [ key ],[ value ]
    [ key ],[ value ]
with no missing rows though whitespace is tolerated.
Keys are given below with pertinent notes
    [names_list] - name of the txt file containing a list of files to be
        modified
    [log_level] - the python logger utility logging level. If none is given
        it defaults to 0 but will print much less than if 0 is actually given
    [log_name] - the base name for the log file
Simply create the files above and then execute this program. It will generate
all the desired files.
"""
def Read_Setup():
    """ This function reads in a file named "post_setup.txt". It stores this 
    file as a list object from which the file's contents can be retrieved."""
    input_file = open( "post_setup.txt" , "r" )
    setup_file = input_file.readlines()
    setup_file = [ x.rstrip( "\n" ) for x in setup_file ]
    dictionary = {}
    num_lines = len( setup_file )
    for i in range( num_lines ):
        line = setup_file[ i ].split( ',' )
        dictionary[ line[ 0 ] ] = line[ 1 ]
    if 'log_level' in dictionary.keys():
        dictionary[ 'log_level' ] = int( dictionary[ 'log_level' ] )
    input_file.close()
    return( dictionary )

def Nuclide_Dictionaries( Sep , Cep ):
    """ This function reads in nuclide ZAIs and names from a static file,
    "nuclide_ids.txt" and creates a dictionary of name:ZAI and ZAI:name """
    Sep()
    logging.debug( "Nuclide_Dictionaries" )
    input_file = open( "nuclide_ids.txt" , "r" )
    setup_file = input_file.readlines()
    setup_file = [ x.rstrip( "\n" ) for x in setup_file ]
    dictionary_0 = {}
    dictionary_1 = {}
    num_lines = len( setup_file )
    for i in range( num_lines ):
        line = setup_file[ i ].split( ':' )
        dictionary_0[ line[ 0 ] ] = line[ 1 ]
        dictionary_1[ line[ 1 ] ] = line[ 0 ]
    input_file.close()
    output_list = [ dictionary_0 , dictionary_1 ]
    return( output_list )

def Read_Burn_File( base_name, options , Read_Input , Get_Materials_List , \
    Get_Nuclide_Indicies , Sep , Cep ):
    """ This function reads in a SERPENT2 ( Aufiero and later mod ) burnup file
        and stores data as lists inside of a general list """
    Sep()
    logging.debug( "Read_Burn_File" )
    burn_data = {} 
    nuclide_indicies = {}
    raw_burn_data = Read_Input( base_name + "_dep.m" , "string" , Sep )
    materials_list = Get_Materials_List( raw_burn_data , options , Sep , Cep )
    Cep()
    index_pattern = re.compile( r'i(\d*) = (\d*)' )
    bu_pattern = re.compile( r'BU' )
    day_pattern = re.compile( r'DAYS' )
    mat_pattern = re.compile( r'MAT\S*?' )
    tot_pattern = re.compile( r'TOT\S*?' )
    name_pattern = re.compile( r'\S*?' )
    i = 0
    while ( i < len( raw_burn_data ) + 1 ):
        line = raw_burn_data[ i ]
        logging.debug( "The line being processed is: " )
        try:
            logging.debug( line[ : 20 ] + "..." + line[ -20 : ] )
        except:
            logging.debug( line )
        index_match = index_pattern.match( line )
        bu_match = bu_pattern.match( line )
        day_match = day_pattern.match( line )
        mat_match = mat_pattern.match( line )
        tot_match = tot_pattern.match( line )
        if index_match:
            logging.debug( "Index match!" )
            nuclide_indicies = Get_Nuclide_Indicies( line ,\
                nuclide_indicies ,Sep, Cep )
            i += 1 
        elif bu_match:
            logging.debug( "BU match!" )
            burn_data[ bu_match.group() ] = Parse_Matlab_Vector( \
                line , Sep , Cep )
            i += 1 
        elif day_match:
            logging.debug( "Day match!" )
            burn_data[ day_match.group() ] = Parse_Matlab_Vector(\
                line , Sep , Cep )
            i += 1
        elif mat_match or tot_match:
            logging.debug( "Data match!" )
            field_name =  name_pattern.match( line ).group()
            logging.debug( "The field name is: " + field_name )
            start , i = Get_Matlab_Matrix( raw_burn_data , i , Sep , Cep )
            burn_data[ field_name ] = Parse_Matlab_Matrix( \
                start, i , raw_burn_data , Sep , Cep )
        else:
            i += 1
    output = [ burn_data , nuclide_indicies , materials_list ]
    return( output )

def Get_Matlab_Matrix( contents , counter , Sep , Cep ):
    """ This function searches through a serpent dep file and extracts
        the currently selected matlab style matrix ( composing several lines
        of the file ) returning this matrix as a list """
    Sep()
    logging.debug( "Get_Matlab_Matrix" )
    start = cp.deepcopy( counter )
    pattern = re.compile( r'\];' )
    match = None
    while ( match is None ):
        logging.debug( "The line is: " )
        try:
            logging.debug( contents[ counter ][ : 20 ] + "..." + \
                contents[ counter ][ -20 : ] )
        except:
            logging.debug( contents[ counter ] )
        match = pattern.match( contents[ counter ] )
        logging.debug( "The match is: " + str( match ) )
        end = counter
        counter += 1
    output = [ start , counter ]
    return( output ) 

def Parse_Matlab_Matrix( begin , end , contents , Sep , Cep ):
    """ This function extracts numerical data from a matlab matrix and returns
        a nested list of the data"""
    Sep()
    logging.debug( "Parse_Matlab_Matrix" )
    output = []
    for i in range( begin + 1 , end ):
        line = contents[ i ].split( " " )
        try:
            index = line.index( "%" )
        except:
            pass
        else:
            line = line[ : index - 1 ]
        logging.debug( "The line is: " )
        try:
            logging.debug( str( line[ : 3 ] ) + "..." + str( line[ -3 : ] ) )
        except:
            logging.debug( str( line ) )
        output.append( line )
    return( output )

def Parse_Matlab_Vector( line , Sep , Cep ):
    """ This function extracts the numerical data from a matlab vector format
        and returns a list """
    Sep()
    logging.debug( "Parse_Matlab_Vector" )
    pattern = re.compile( r'\[.*?\]' )
    string = pattern.search( line ).group()[ 1 : -1 ].strip( " " )
    logging.debug( "The string is: " )
    try:
        logging.debug( string[ : 20 ] + "..." + string[ -20 : ] )
    except:
        logging.debug( string )
    nums = string.split( " " )
    logging.debug( "The generated list is: " )
    try:
        logging.debug( str( nums[  : 5 ] ) + "..." + str( nums[ -5 : ] ) )
    except:
        logging.debug( str( nums ) )
    return( nums )

def Get_Nuclide_Indicies( string , index_dict , Sep , Cep ):
    """ This function reads through the burn file to get the matrix rows of
        each nuclide ( the index in matricies where it's info can be found ) """
    Sep()
    logging.debug( "Get_Nuclide_Indicies" )
    logging.debug( "The string being analyzed is:" )
    logging.debug( string )
    pattern = re.compile( r'i(\d*) = (\d*)' )
    match = pattern.match( string )
    if index_match:
        index_dict[ int( match.group( 1 ) ) ] = int( match.group( 2 ) )
    logging.debug( "The key value pair generated is: " )
    logging.debug( match.group( 1 ) + " : " + match.group( 2 ) ) 
    return( index_dict )

def Get_Materials_List( contents , options , Sep , Cep ):
    """ This function generates a list of all the materials in the burn file"""
    Sep()
    logging.debug( "Get_Materials_List" )
    materials = []
    pattern = re.compile(r'MAT_(\S*?)_VOLUME')
    for i in range( len( contents ) ):
        match = pattern.match( contents[ i ] )
        if match:
            materials.append( match.group( 1 ) )
    logging.debug( "The materials found in the burnup file are: " )
    if 'log_level' in options:
        if options[ 'log_level' ] < 10:
            for i in range( len( materials ) ):
                logging.debug( str( materials[ i ] ) )
    return( materials )

def Report_Output( output , file_name ):
    """ This function is a debugging function to test the parse functions """
    Sep()
    logging.debug( "Report_Output" )
    destination = open( file_name , "w" )
    for key in output.keys():
        destination.writeline( str( key ) + ": \n" )
        destination.writelines( ouput[ key ] )
    destination.writeline( "********************************************* \n" )
    destination.writeline( "END!!" )
    destination.close()

def Get_Base_Name( file_name ):
    """ This function gets a base name from the host file name """
    end_index = file_name.rfind( "." )
    base_name = file_name[ 0 : end_index ]
    return( base_name )

def Start_Log( base_name , level ): 
    log_file_name = "Log_" + base_name + "_" + time.strftime( "%d_%m_%Y" ) \
        + ".log"

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

def Read_Input( file_name , form , Sep ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list and stripped of new lines. 
    They are also converted to floats. """
    Sep()
    logging.debug( "Read_Input" )
    logging.debug( "Reading in file: " + file_name )
    input_file = open( file_name , "r" )
    file_contents = input_file.readlines()
    if form == 'string':
        file_contents = [ x.rstrip( "\n" ) for x in file_contents ]
    elif form == 'float':
        file_contents = [ float( x ) for x in file_contents ]
    elif form == 'raw':
        pass
    else:
        print( "ERROR!!!: Choice of conversion for input from file " + \
            file_name + " either not given or not 'string','raw', or 'float'" )
        logging.debug( "ERROR!!!: Choice of conversion for input from file " + \
            file_name + " either not given or not 'string', 'raw', or 'float'" )
        exit()
    logging.debug( "Closing file: " + file_name )
    input_file.close()
    return( file_contents )

# Start the program
print( "\nThe post processing program is now running\n" )

setup = Read_Setup()

try:
    Start_Log( setup[ 'log_name' ] ,  setup[ "log_level" ] )
except:
    Start_Log( 'post_error' , 0 )
    logging.debug( "ERROR!!: < log_level > or < log_name > was not found in \n \
        post_setup.txt and as such LogLevel was set to 0 and the base name \n \
        to 'post_error' " )

if 'log_level' in setup:
    if setup[ 'log_level' ] < 10:
        Sep()
        logging.debug( "The input dictionary is: " )
        for keys,values in setup.items():
            logging.debug( str( keys ) + " : " + str( values ) )

output = Read_Burn_File( "2MWd.txt" , setup , Read_Input, Get_Materials_List , \
                Get_Nuclide_Indicies , Sep , Cep )

Report_Output( output , "report.test" )

print( "The post processing program has finished\n" )
