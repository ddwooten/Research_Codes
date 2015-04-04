#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import os as os
import time as time
import logging as logging
import copy as cp
import re as re

""" This is a collection of commonly used functions in programs created by
    Daniel Wooten. They should be ( and are ) utilized in other programs
    created by Daniel Wooten. This file must be in the current directory of
    execution for these programs or the system path
    Keys are given below with pertinent notes
        [host_file] - name of the SERPENT file that was run. i.e. there should
            be a file in the executing directory titled "host_file_dep.m" for
            burnup runs.
        [log_level] - the python logger utility logging level. If none is given
            it defaults to 0 
        [log_name] - the base name for the log file
"""
def Read_Setup( prefix ):
    """ This function reads in a setup file named "[something]_setup.txt".
        It stores this file as a list object from which the file's contents
        can be retrieved.
        This file must consist of two columns of text arragned as
        [ key ],[ value ]
        [ key ],[ value ]
    """
    with no missing rows though whitespace is tolerated.
    input_file = open( prefix + "_setup.txt" , "r" )
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
