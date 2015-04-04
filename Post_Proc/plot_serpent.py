#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import os as os
import time as time
import logging as logging
import copy as cp
import re as re
import wooten_common as wc
import post_common as pc

""" This is the SERPENT plotter. It requires a configuration
    file titled, exactly, "plot_setup.txt". 
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
"""

def Nuclide_Dictionaries():
    """ This function reads in nuclide ZAIs and names from a static file,
    "nuclide_ids.txt" and creates a dictionary of name:ZAI and ZAI:name """
    wc.Sep()
    logging.debug( "Nuclide_Dictionaries" )
    nuclide_file = wc.Read_Input( "nuclide_ids.txt" , "string" )
    dictionary_0 = {}
    dictionary_1 = {}
    for i in range( len( nuclide_file ) ):
        line = nuclide_file[ i ].split( ':' )
        dictionary_0[ line[ 0 ] ] = line[ 1 ]
        dictionary_1[ line[ 1 ] ] = line[ 0 ]
    output_list = [ dictionary_0 , dictionary_1 ]
    return( output_list )

def Plot_Main():
    """ This function runs the program if it is called as an import """
    setup = wc.Read_Setup( "plot" )

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

    d_list = Nuclide_Dictionaries()
    d_file = open( "d1.test" , "w" )
    e_file = open( "d2.test" , "w" )
    for key in d_list[ 0 ].keys():
        string = str( key ) + " : " + str( d_list[ 0 ][ key ] ) + " \n"
        d_file.write( string )
    for key in d_list[ 1 ].keys():
        string = str( key ) + " : " + str( d_list[ 0 ][ key ] ) + " \n"
        e_file.write( string )
    d_file.close()
    e_file.close()
    return( output )

print( "Begining the Plotting program" )

Plot_Main()

print( "Ending the Plotting program" )
