#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import os as os
import time as time
import logging as logging
import copy as cp
import re as re
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
"""

def Nuclide_Dictionaries():
    """ This function reads in nuclide ZAIs and names from a static file,
    "nuclide_ids.txt" and creates a dictionary of name:ZAI and ZAI:name """
    wc.Sep()
    logging.debug( "Nuclide_Dictionaries" )
    nuclide_file = wc.Read_Input( "nuclide_ids.txt" , "r" )
    dictionary_0 = {}
    dictionary_1 = {}
    for i in range( len( nuclide_file ) ):
        line = setup_file[ i ].split( ':' )
        dictionary_0[ line[ 0 ] ] = line[ 1 ]
        dictionary_1[ line[ 1 ] ] = line[ 0 ]
    input_file.close()
    output_list = [ dictionary_0 , dictionary_1 ]
    return( output_list )

def Read_Burn_File( base_name, options , Get_Materials_List , \
    Get_Nuclide_Indicies ):
    """ This function reads in a SERPENT2 ( Aufiero and later mod ) burnup file
        and stores data as lists inside of a dictionary """
    wc.Sep()
    logging.debug( "Read_Burn_File" )
    burn_data = {} 
    nuclide_indicies = {}
    raw_burn_data = wc.Read_Input( base_name + "_dep.m" , "string" )
    raw_burn_data = [ x.strip( " " ) for x in raw_burn_data ]
    materials_list = Get_Materials_List( raw_burn_data , options )
    wc.Cep()
    index_pattern = re.compile( r'i(\d*) = (\d*)' )
    bu_pattern = re.compile( r'BU' )
    day_pattern = re.compile( r'DAYS' )
    mat_pattern = re.compile( r'MAT\S*' )
    tot_pattern = re.compile( r'TOT\S*' )
    vector_pattern = re.compile( r'\];$' )
    name_pattern = re.compile( r'_(\S*?)_' )
    i = 0
    vectors = 0
    while ( i < len( raw_burn_data ) ):
        line = raw_burn_data[ i ]
        logging.debug( "The iterator is on: " + str( i ) )
        logging.debug( "The line being processed is: " )
        if len( line ) > 41:
            logging.debug( line[ : 20 ] + "..." + line[ -20 : ] )
        else:
            logging.debug( line )
        index_match = index_pattern.match( line )
        bu_match = bu_pattern.match( line )
        day_match = day_pattern.match( line )
        mat_match = mat_pattern.match( line )
        tot_match = tot_pattern.match( line )
        vector_match = vector_pattern.search( line )
        if index_match:
            logging.info( "Index match!" )
            nuclide_indicies = Get_Nuclide_Indicies( line ,\
                nuclide_indicies )
            i += 1 
        elif bu_match:
            vectors += 1
            logging.info( "BU match!" )
            if vector_match:
                burn_data[ bu_match.group() ] = Parse_Matlab_Vector( \
                    line )
                i += 1 
            else:
                start , i = Get_Matlab_Matrix( raw_burn_data , i )
                burn_data[ bu_match.group() ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )
        elif day_match:
            vectors += 1
            logging.info( "Day match!" )
            if vector_match:
                burn_data[ day_match.group() ] = Parse_Matlab_Vector(\
                    line )
                i += 1
            else:
                start , i = Get_Matlab_Matrix( raw_burn_data , i )
                burn_data[ day_match.group() ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )
        elif mat_match or tot_match:
            vectors += 1
            logging.info( "Data match!" )
            if mat_match:
                field_name = mat_match.group()
            else:
                field_name = tot_match.group() 
            logging.info( "Data is: " + field_name )
            if vector_match:
                burn_data[ field_name ] = Parse_Matlab_Vector(\
                    line )
                i += 1
            else:
                start , i = Get_Matlab_Matrix( raw_burn_data , i )
                burn_data[ field_name ] = Parse_Matlab_Matrix( \
                    start, i , raw_burn_data )
        else:
            i += 1
    logging.info( "The number of vectors is: " + str( vectors ) )
    output = [ burn_data , nuclide_indicies , materials_list ]
    return( output )

def Get_Matlab_Matrix( contents , counter ):
    """ This function searches through a serpent dep file and extracts
        the currently selected matlab style matrix ( composing several lines
        of the file ) returning this matrix as a list """
    wc.Sep()
    logging.debug( "Get_Matlab_Matrix" )
    start = cp.deepcopy( counter )
    pattern = re.compile( r'\];' )
    match = None
    while ( match is None ):
        logging.debug( "The line is: " )
        if len( contents[ counter ] ) > 41:
            logging.debug( contents[ counter ][ : 20 ] + "..." + \
                contents[ counter ][ -20 : ] )
        else:
            logging.debug( contents[ counter ] )
        match = pattern.match( contents[ counter ] )
        logging.debug( "The match is: " + str( match ) )
        end = counter
        counter += 1
    output = [ start , counter ]
    return( output ) 

def Parse_Matlab_Matrix( begin , end , contents ):
    """ This function extracts numerical data from a matlab matrix and returns
        a nested list of the data"""
    wc.Sep()
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
        if len( str( line ) ) > 41:
            logging.debug( str( line[ : 3 ] ) + "..." + str( line[ -3 : ] ) )
        else:
            logging.debug( str( line ) )
        output.append( line )
    return( output )

def Parse_Matlab_Vector( line ):
    """ This function extracts the numerical data from a matlab vector format
        and returns a list """
    wc.Sep()
    logging.debug( "Parse_Matlab_Vector" )
    pattern = re.compile( r'\[.*?\]' )
    string = pattern.search( line ).group()[ 1 : -1 ].strip( " " )
    logging.debug( "The string is: " )
    if len( string ) > 41:
        logging.debug( string[ : 20 ] + "..." + string[ -20 : ] )
    else:
        logging.debug( string )
    nums = string.split( " " )
    logging.debug( "The generated list is: " )
    if len( str( nums ) ) > 41:
        logging.debug( str( nums[  : 5 ] ) + "..." + str( nums[ -5 : ] ) )
    else:
        logging.debug( str( nums ) )
    return( nums )

def Get_Nuclide_Indicies( string , index_dict ):
    """ This function reads through the burn file to get the matrix rows of
        each nuclide ( the index in matricies where it's info can be found ) """
    wc.Sep()
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

def Get_Materials_List( contents , options ):
    """ This function generates a list of all the materials in the burn file"""
    wc.Sep()
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
    wc.Sep()
    logging.debug( "Report_Output" )
    destination = open( file_name , "w" )
    for key in output.keys():
        destination.write( "********************************************* \n" )
        destination.write( str( key ) + ": \n" )
        if isinstance( output[ key ][ 0 ] , list ):
            for i in range( len( output[ key ] ) ):
                string = str( output[ key ][ i ] )
                if len( string ) > 41:
                    destination.write( string[ : 20 ] + "..." + \
                        string[ -20 : ] )
                else:
                    destination.write( string )
        else:
            string = str( output[ key ] )
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
    setup = wc.Read_Setup( "post" )

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

    if os.path.isfile( setup[ "host_file" ] + "_dep.m" ): 
        output = Read_Burn_File( setup[ "host_file" ] , setup , \
                    Get_Materials_List , Get_Nuclide_Indicies )
    return( output )
