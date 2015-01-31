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

def Read_Host( file_name , Sep ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list. """
    Sep()
    logging.debug( "Reading in file: " + file_name )
    input_file = open( file_name , "r" )
    file_contents = input_file.readlines()
    logging.debug( "Closing file: " + file_name )
    input_file.close()
    return( file_contents )

def Read_Input( file_name , Sep ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list and stripped of new lines. 
    They are also converted to floats. """
    Sep()
    logging.debug( "Reading in file: " + file_name )
    input_file = open( file_name , "r" )
    file_contents = input_file.readlines()
    file_contents = [ x.rstrip( "\n" ) for x in file_contents ]
    logging.debug( "Closing file: " + file_name )
    input_file.close()
    return( file_contents )

def Gen_Pitch_or_Diameter( pd , given , desired , Sep ):
    """ This function generates a list of either diameters or pitches from 
    a list of pitch to diameter ratios depending on which one is additionally
    given"""
    Sep()
    if desired == "diameter":
        output=[]
        for i in range( len( given ) ):
            diameters=[]
            for j in range( len( pd ) ):
                diameters.append( given[ i ] / pd[ j ] )
            logging.debug( "For pitch " + str( given[ i ] ) + \
                " the diameters are: " )
            logging.debug( str( diameters ) )
            output.append( diameters )
        logging.debug( "There are " + str( len( given ) ) + " pitches \n" + \
            " and there are " + str( len( output ) ) + " diameter arrays" )
    elif desired == "pitch":
        output=[]
        for i in range( len( given ) ):
            pitches=[]
            for j in range( len( pd ) ):
                pitches.append( given[ i ] * pd[ j ] )
            logging.debug( "For diameter " + str( given[ i ] ) + \
                " the pitches are: " )
            logging.debug( str( pitches ) )
            output.append( pitches )
        logging.debug( "There are " + str( len( given ) ) + " diameters \n" + \
            " and there are " + str( len( output ) ) + " pitch arrays" )
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
    inner_radius = diameter / 2.0 - sum( widths )
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
    comment_string = "% ------ " + material + " Surface\n"
    if shape != "cyl":
        surf_string = "surf    " + str( id_num ) + "    " + lattice + "    " + \
            str( x_pos ) + "    " + str( y_pos ) + "    " + str( radius ) + \
                "    0.0\n" 
    else:
        surf_string = "surf    " + str( id_num ) + "    " + shape + "    " + \
            str( x_pos ) + "    " + str( y_pos ) + "    " + str( radius ) + "\n"
    output = [ comment_string , surf_string ]
    return( output )

def Cell_Line_Writer( material , outer_bound , inner_bound , id_num \
        , uni_num , Sep ):
    """ This function writes strings for cells """
    Sep()
    if material == "outside":
        cell_string = "{ 0 }    { 1 }    { 2 }    { 3 }{ 4:>19}{ 5:<6 }\n".\
            format( "cell" , str( id_num ) , str( uni_num ) , material , \
                str( inner_bound ) , str( outer_bound ) )
    else: 
        cell_string = "{ 0 }    { 1 }    { 2 }    fill { 3 }{4:>19}{ 5:<6 }\n".\
            format( "cell" , str( id_num ) , str( uni_num ) , material , \
                str( inner_bound ) , str( outer_bound ) ) 
    return( cell_string )

def Files_Generator( base_name , materials , radii , host_file , options, \
     pitch_array , diameters , Sep , Cep ):
    """ This function generates values to pass to the string writers and then
    inserts these values into the file to be written actually writes the
     contents to file """
    Sep()
    surf_start = host_file.index( "% ------ RSAC\n" )
    logging.debug( "The surf_start index is: " + str( surf_start ) )
    cell_start = host_file.index( "% ------ AGC\n" )
    logging.debug( "The cell_start index is: " + str( cell_start ) )
    lattice = options[ 1 ]
    logging.debug( "The lattice is: " + options[ 1 ] )
    materials = materials.insert( 0 , options[ 2 ] )
    for i in range( len( pitch_array ) ):
        Cep()
        pitch = pitch_array[ i ]
        logging.debug( "The pitch is: " + str( pitch ) )
        for j in range( len( diameters ) ):
            logging.debug( "The inner radius is: " + str( diameters[ j ] ) )
            new_file_list = host_file
            new_name = base_name + "_" + lattice + "_" + str( pitch ) + \
                "P_" + str( diameters[ j ] ) + "D_.txt"
            logging.debug( "The new_name is: " + new_name )
            surface_card = ["\n"]
            cell_card = ["\n"]
# This loop writes out the surfaces for the various materials
            for k in range( len( materials ) ):
                id_num = 11 + k
                new_file_list.insert( surf_start + k , Surface_Line_Writer( \
                    materials[ k ] , radii[ j ][ k ]  , lattice , 0.0 , 0.0 , \
                    "cyl" , id_num , Sep ) )
                new_file_list.insert( cell_start + k , Cell_Line_Writer( \
                   materials[ k ] ,id_num , id_num + 1 * -1 , id_num , 0 \
                   , Sep ) )
# These two function calls write out the final surface and cell lines each
            new_file_list.insert( surf_start + k + 1 , Surface_Line_Writer( \
                "FuelSalt" , pitch  , lattice , 0.0 , 0.0 , lattice , \
                id_num + 1 , Sep ) )
            new_file_list.insert( Cell_Line_Writer( outside , \
                id_num + 1 , id_num + 2 * -1 , id_num + 1 , 0 , Sep ) )
# Here we actually write to file
            destination_file = open( new_name , "w" )
            destination_file.writelines( new_file_list )
            destination_file.close()
    return()

# Start the program
print( "The program is now running\n" )
setup = Read_Setup()

base_name = Get_Base_Name( setup[ 0 ] )

Start_Log( base_name , 0 )

host_file = Read_Host( setup[ 0 ] , Sep )

pitches = Read_Input( "pitches.test" , Sep )

pd = Read_Input( "pd.test" , Sep )

cladding = Read_Input( "cladding.test" , Sep )

diameters = Gen_Pitch_or_Diameter( pd , pitches , "diameter" , Sep )

widths = Gen_Width_List( cladding , Sep )

materials = Gen_Materials_List( cladding , Sep )

inner_radii = Gen_Inmost_Radius( widths , diameters , Sep )

all_radii = Gen_Cladding_Radii( widths , inner_radii , Sep , Cep )

Files_Generator( base_name , materials , all_radii , host_file , setup , \
    pitches , diameters , Sep , Cep )

print( "The program has finished\n" )
