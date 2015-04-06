#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import math as math
import logging as logging
import copy as cp
import re as re
import numpy as np
# These are custom built python modules containing helpful and necessary
#   functions.
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
    logging.Info( "Nuclide_Dictionaries" )
    nuclide_file = wc.Read_Input( "nuclide_ids.txt" , "string" )
    dictionary_0 = {}
    dictionary_1 = {}
    for i in range( len( nuclide_file ) ):
        line = nuclide_file[ i ].split( ':' )
        dictionary_0[ line[ 0 ] ] = line[ 1 ]
        dictionary_1[ line[ 1 ] ] = line[ 0 ]
    output_list = [ dictionary_0 , dictionary_1 ]
    return( output_list )

def List_To_Array( data ):
    """ This function takes in classic python lists ( or a dictionary of lists )
        and nested lists ( matricies ) and converts them to numpy arrays. """
    wc.Sep()
    logging.info( "List_To_Array" )
    if isinstance( data , dict ):
        for key in data.keys():
            data[ key ] = np.array( data[ key ] )
    elif isinstance( data , list ):
        data = np.array( data )
    else:
        print( "ERROR!!!: Data passed to < List_To_Array > was not either \n \
            of type < list > or < dict >." )
        logging.critical( "ERROR!!!: Data passed to < List_To_Array > was \n \
            not either of type < list > or < dict >." )
        exit()
    return( data )

def Get_Element_Data( matrix , nuclide_indicies , Z ):
    """ This function collapses isotopic burn vectors into a given
        elemental burn vector """
    wc.Sep()
    logging.Info( "Get_Element_Data" )
    logging.debug( "Z is: " + str( Z ) )
    vector = np.zeros( matrix.shape[ 1 ] )
    for key in nuclide_indicies.keys()
        cur_Z = int( math.floor( float( key ) / 1000.0 ) )
        if Z == cur_Z:
            logging.debug( "Isotope is: " + str( key ) )
            logging.debug( "End value before addition: " + \
                str( vector[ -1  ] ) )
            logging.debug( "Value being added: " + \
                str( matrix[ nuclide_indicies[ key ] : -1 ] ) )
            vector = vector + matrix[ nuclide_indicies[ key ] 
            logging.debug( "End value after addition: " + \
                str( vector[ -1 ] ) )
    return( vector ) 

def Matrix_Or_Vector( target ):
    """ This function determines if target is a list of values or a list
        of lists and returns a list of equal dimension, empty """
        wc.Sep()
        logging.info( "Matrix_Or_Vector" )
        if isinstance( target[ 0 ] , list ):
            beast = "matrix"
            rows = len( target )
            columns = len( target[ 0 ] )
            output = [ 0.0 ] * rows
            output = [ [ 0.0 ] * columns for x in output ]
        else:
            beast = "vector"
            columns = len( target )
            output = [ 0.0 ] * columns 
        send = [ beast , output ]
        return( send )

def Gather_Materials( dictionary , attribute , materials ):
    """ This function gathers burn data across a given list of materials
        or accross all materials ( mimics TOT in earlier SERPENT files ).
    """
    wc.Sep()
    logging.info( "Gather_Materials" )
# This little chunk here is to determine if we have a vector or a matrix
# and builds the appropriate data storage
    pattern = re.compile( "\\S*_" + attribute )
    for key in dictionary.keys():
        match = pattern.match( key )
        if match:
            beast , output = Matrix_Or_Vector( dictionary[ key ] )
            break
# This handles if you want all materials
    for key in dictionary.keys():
        match = pattern.match( key )
        if isinstance( materials , list ):
            for elemement in materials:
                match = None
                pattern = re.compile( "\\S*_" + element + \
                    "_" + attribute )
                match = pattern.match( key )
                if match:
                    break
        if match:
            if beast == "matrix":
                output = [ map( sum , zip( *t ) ) for t in \
                    zip( output , dictionary[ key ] ) ] 
            else:
                output = map( lambda x , y : x + y , output , \
                    dictionary[ key ] )
    return( output )

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
    return

print( "Begining the Plotting program" )

Plot_Main()

print( "Ending the Plotting program" )
