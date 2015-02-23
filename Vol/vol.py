#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import time as time
import sys as sys
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
Simply create the files above and then execute this program. It will generate
all the desired files.
"""
def Read_Setup():
    """ This function reads in a file named "init_setup.txt". It stores this 
    file as a list object from which the file's contents can be retrieved."""
    input_file = open( "vol_setup.txt" , "r" )
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

def Get_Mat_and_Vol( contents , Sep , Cep ):
    """ This function reads in a SERPENT2 .mvol file and extracts material
    names and volumes, assigning them to a dict with mat names as keys and
    vols as values."""
    Sep()
    logging.debug( "Get_Mat_and_Vol" )
    mat_and_vol_dict = {}
    start_line = contents.index( 'set mvol' ) + 2
    logging.debug( "The start line is: " + str( start_line ) )
    for i in range( start_line , len( contents ) , 1 ):
        string = contents[ i ].split()
        logging.debug( "The string is: " )
        logging.debug( contents[ i ] )
        mat = string.split()[ 0 ]
        vol = float( string.split()[ 2 ] )
        mat_and_vol_dict[ mat ] = vol
    for keys,values in mat_and_vol_dict.items():
        logging.debug( str( keys ) + " : " + str( values ) )
    return( mat_and_vol_dict )

def Insert_Vols( contents , lines , volumes , Sep , Cep ):
    """ This function literally inserts the volume amount into the material
    string"""
    Sep()
    logging.debug( "Insert_Vols" )
    for key in lines.keys():
        old_line = contents[ lines[ key ] ]
        old_line_elements = old_line.split()
        logging.debug( "The initial line is: " )
        logging.debug( contents[ lines[ key ] ] )
        try:
            vol_index = old_line_elements.index('vol')
        except ValueError:
            old_line_elements.append( 'vol' )
            old_line_elements.append( str( volumes[ key ] ) )
        else:
            old_line_elements[ vol_index + 1 ] = str( volumes[ key ] )
        logging.debug( "Inserted volume" + str( volumes[ key ] ) + \
            " for " + str( key ) )
        new_line = "".join( old_line_elements )
        logging.debug( "The new line is: " )
        logging.debug( new_line )
        contents[ lines[ key ] ] = new_line
    return( contents )
            
def Find_Mat_Lines( contents , Sep , Cep ):
    """ This function scans through a file and finds SERPENT material lines
    using regex. It looks for "mat WORD" and then extracts the line that this
    occurs on as well as WORD. These are then paired in a dictionary that is
    the output """
    Sep()
    logging.debug( "Find_Mat_Lines" )
    line_dict = {}
    line_finder = re.compile( r'\bmat\b.*' )
    for i in range( len( contents ) ):
        string = line_finder.match( contents[ i ] )
        if string != None:
           logging.debug( "The matched string is: " )
           logging.debug( string.group() )
           line_dict[ string.group().split()[ 1 ] ] = i
    for keys,values in line_dict.items():
        logging.debug( str( keys ) + " : " + str( values ) )
    return( line_dict )

def Volumize_Files( files_list , Get_Mat_and_Vol , Insert_Vols , Read_Input ,\
    Find_Mat_Lines , Get_Base_Name , options , Sep , Cep ):
    """This function loops through the files list calling the appropriate
    functions to determine the volumes and insert them"""
    Sep()
    logging.debug( "Volumize_Files" )
       for i in range( len( files_list ) ):
           logging.debug( "Reading in file: " + files_list[ i ] )
           host_file = Read_Input( files_list[ i ] , 'string' , Sep )
           destination_name = Get_Base_Name( files_list[ i ] ) + \
            "_vols.txt"
           mat_file_name = files_list[ i ] + ".mvol"
           logging.debug( "Reading in file: " + mat_file_name )
           material_file = Read_Input( mat_file_name , 'string' , Sep )
           mats_and_vols = Get_Mat_and_Vol( material_file , Sep , Cep )
           if 'log_level' in options:
               if options[ 'log_level' ] < 10:
                   Cep()
                   logging.debug( "The material and volume dict is: " )
                   for keys,values in mats_and_vols.items():
                       logging.debug( str( keys ) + " : " + str( values ) )
          lines = Find_Mat_Lines( host_file , Sep , Cep )
          host_file = Insert_Vols( host_file , lines , mats_and_vols , \
            Sep , Cep )
          destination_file = open( destination_name , "w" )
          destination_file.writelines( host_file )
          destination_file.close()
    return() 
                               
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
            file_name + " either not given or not 'string' or not 'float'" )
        logging.debug( "ERROR!!!: Choice of conversion for input from file " + \
            file_name + " either not given or not 'string' or not 'float'" )
        exit()
    logging.debug( "Closing file: " + file_name )
    input_file.close()
    return( file_contents )

# Start the program
print( "\nThe volume program is now running\n" )
setup = Read_Setup()

files_list = Read_Input( setup[ names_list ] , 'raw' , Sep )

try:
    Start_Log( base_name ,  setup[ "log_level" ] )
except:
    Start_Log( base_name , 0 )
    logging.debug( "ERROR!!: < log_level > was not found in vol_setup.txt\n \
        and as such LogLevel was set to 0" )

if 'log_level' in setup:
    if setup[ 'log_level' ] < 10:
        Sep()
        logging.debug( "The input dictionary is: " )
        for keys,values in setup.items():
            logging.debug( str( keys ) + " : " + str( values ) )

Volumize_Files( files_list , Get_Mat_and_Vol , Insert_Vols , Read_Input \
    , Find_Mat_Lines , Get_Base_Name , setup , Sep , Cep )

print( "The volume program has finished\n" )
