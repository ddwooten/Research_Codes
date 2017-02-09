#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import os as os
import time as time
import logging as logging
import copy as cp
import re as re
import sys
import json

""" This is a collection of commonly used functions in programs created by
    Daniel Wooten. They should be ( and are ) utilized in other programs
    created by Daniel Wooten. This file must be in the current directory of
    execution for these programs or the system path
   This file currently lives in...
   "/usr/lib/pymodules/Python2.7"
"""
def Read_Setup( prefix ):
    """ This function reads in a setup file named "[something]_setup.json".
        Clearly the setup file must be formatted as a json file with a parent
        dictionary. Any stadard json input is accepted.
    """
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

def Read_Json_Setup( selection ):
    """ This function reads in a json formatted setup file. The file
        <<[ selection ]_setup.json>> takes precedence followed by the generic
        <<setup.json>>.
    """
    if os.path.isfile( selection + "_setup.json" ):
        setup_file = open( selection + "_setup.json" , "r" )
    elif os.path.isfile( "setup.json" ):
        setup_file = open( "setup.json" , "r" ) 
    else:
        print( "ERROR!! No setup file found in \n <<<" + os.getcwd() + \
        ">>> \n for Read_Json_Setup. The program will now die. " )
        sys.exit()
    setup = json.load( setup_file , object_hook = Decode_Json_Dict )
    setup_file.close()
    return( setup )

def Read_Json_Data( file_name ):
    """ This function reads in a json formatted data file. 
    """
    if os.path.isfile(file_name):
        setup_file = open( file_name , "r" )
    else:
        print( "ERROR!! File <<<" + file_name + ">>> not found in \n \
            <<<" + os.getcwd() + \
            ">>> \n for Read_Json_Setup. The program will now die.\n" )
        sys.exit()
    setup = json.load( setup_file , object_hook = Decode_Json_Dict )
    setup_file.close()
    return( setup )

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
    return

def Cep():
	''' A wrapper to place file seperators in a log file for the
	debug level '''
	logging.info( "*****************************************************" )
	return

#Function, refer to docstring for purpose
def Sep():
    '''A wrapper to visually seperate functions in log files'''
    logging.info( '//////////////////////////////////////////////////////' )
    return

def Read_Input( file_name , form ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list and stripped of new lines. 
    They are also converted to floats. """
    logging.debug( '//////////////////////////////////////////////////////' )
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

def Decode_List( data , fun ):
    """ These two functions ( Decode_List and Decode_Dict )
    can be used to un-nest nested dicts and lists ( combined )
    while applying "fun" to the items in these dicts and lists ( 
    that are themselves not dicts or lists ). Keys in dicts
    are always converted to ascii strings. """
    output = []
    for item in data:
        if isinstance( item , list ):
            item = Decode_List( item , fun )
        elif isinstance( item , dict ):
            item = Decode_Dict( item , fun )
        else:
            item = fun( item )
        output.append( item )
    return( output )

def Decode_Dict( data , fun ):
    """ These two functions ( Decode_List and Decode_Dict )
    can be used to un-nest nested dicts and lists ( combined )
    while applying "fun" to the items in these dicts and lists ( 
    that are themselves not dicts or lists ). Keys in dicts
    are always converted to ascii strings."""
    output = {}
    for key , value in data.iteritems():
        key = key.encode( 'ascii' )
        if isinstance( value , list ):
            value = Decode_List( value , fun )
        elif isinstance( value , dict ):
            value = Decode_Dict( value, fun )
        else:
            value = fun( value )
        output[ key ] = value
    return( output )

def Decode_Json_List( data ):
    """These two functions can be used with the json module for python as
    an object hook to prevent unicode encoding of strings. Simply pass
    the Decode_Dict function like so
    << a = json.load( file , object_hook = Decode_Dict ) >>
    This will preserve all values but convert strings to ascii strings,
    not unicode. If unicode is desired simply do not pass anything to
    ojbect_hook. This function decodes lists for the json module """
    output = []
    for item in data:
        if isinstance( item , unicode ):
            item = item.encode( 'ascii' )
        elif isinstance( item , list ):
            item = Decode_Json_List( item )
        elif isinstance( item , dict ):
            item = Decode_Json_Dict( item )
        output.append( item )
    return( output )

def Decode_Json_Dict( data ):
    """These two functions can be used with the json module for python as
    an object hook to prevent unicode encoding of strings. Simply pass
    the Decode_Dict function like so
    << a = json.load( file , object_hook = Decode_Dict ) >>
    This will preserve all values but convert strings to ascii strings,
    not unicode. If unicode is desired simply do not pass anything to
    ojbect_hook. This function decodes dicts for the json module """
    output = {}
    for key , value in data.iteritems():
        if isinstance( key , unicode ):
            key = key.encode( 'ascii' )
        # Try to convert key to integer in case integer keys were input as
        # strings
        try:
            key = int(key)
        except ValueError:
            pass
        if isinstance( value , unicode ):
            value = value.encode( 'ascii' )
        elif isinstance( value , list ):
            value = Decode_Json_List( value )
        elif isinstance( value , dict ):
            value = Decode_Json_Dict( value )
        output[ key ] = value
    return( output )

def File_Name_Conditioner( string ):
    """ This function removes any undesirable characters in a file string
        and replaces them with a desired substitute. """
    string = string.replace( " " , "_" )
    string = string.replace( "-" , "_" )
    string = string.replace( "\\" , "_backslash" )
    string = string.replace( "&" , "_and_" )
    string = string.replace( ":" , "_" )
    string = string.replace( "," , "_" )
    string = string.replace( "?" , "_question_mark_" )
    string = string.replace( "!" , "_exclamation_mark_" )
    string = string.replace( "~" , "_tilde_" )
    string = string.replace( "*" , "_asterisk_" )
    string = string.replace( "<" , "_left_arrow_" )
    string = string.replace( ">" , "_right_arrow_" )
    string = string.replace( "^" , "_carrot_" )
    string = string.replace( "$" , "_dollar_sign_" )
    string = string.replace( "/" , "_forward_slash_" )
    return( string )

def Save_Output_As_Json( options , data ):
    """ This function saves given data as a json formated file in the
        current directory
    """
    Sep()
    if "output_save_name" in options:
        output_save_name = options[ "output_save_name" ]
    else:
        output_save_name = Get_Base_Name( options[ "host_file" ] ) + \
            ".txt_dep.json"
    save_file = open( output_save_name , "w" )
    json.dump( data , save_file )
    return 

def Check_Import():
    """ This function simply prints a statment to make sure the import worked"""
    print( "<< wooten_common.py >> imported sucessfully" )
    return
