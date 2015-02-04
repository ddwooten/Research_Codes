#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import csv as csvreader
import time as time
import sys as sys
import logging as logging
import copy as cp
""" This is the SERPENT Incremental Pitch code. It requires a configuration
file titled, exactly, "init_setup.txt". This file must consist of one column
of text arragned as
    [ key ]
    [ value ]
    [ key ]
    [ value ]
with no whitespace. Keys are given below with pertinent notes
    [file_name] - name of the SERPENT file to be modified. Surface lines
        will be inserted after the tag "% ------ RSAC" while cell lines
        will be inserted after the tag "% ------ AGC". Id numbering begins
        at 10 and any surface or cell lines already in file will be pushed
        lower in the file.
    [lattice_type] - this is used to name the new files and to give the 
        surface shape for the bounding surface
    [filler_type] - this is the material inside the cladding
    [given_file] - plain text file consisting of one column of numbers
        specifying the measurments for the given parameter ( below )
    [given_type] - either, and exactly "pitch" or "diameter"
    [materials_file] - a plain text file name  with a single column of data
        each even row is a cladding material while each odd is the thickness
        of that material
    [pd_file] - a plain text file name of a single column of numbers denoting
        the p/d ratios
    [outside_type] - the name of the material outside the rod
    [log_level] - the python logger utility logging level. If none is given
        it defaults to 0 but will print much less than if 0 is actually given
Simply create the files above and then execute this program. It will generate
all the desired files.
"""
def Read_Setup():
    """ This function reads in a file named "init_setup.txt". It stores this 
    file as a list object from which the file's contents can be retrieved."""
    input_file = open( "init_setup.txt" , "r" )
    setup_file = input_file.readlines()
    setup_file = [ x.rstrip( "\n" ) for x in setup_file ]
    dictionary = {}
    num_lines = len( setup_file )
    for i in range( 0 , num_lines - 1 , 2 ):
        dictionary[ setup_file[ i ] ] = setup_file[ i + 1 ]
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

def Read_Input( file_name , form , Sep ):
    """ This function reads in a file whose name is given in file_name to the
    function. It's contents are saved in a list and stripped of new lines. 
    They are also converted to floats. """
    Sep()
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

def Gen_Pitch_or_Diameter( pd , given , given_type , options , Sep , Cep ):
    """ This function generates a list of either diameters or pitches from 
    a list of pitch to diameter ratios depending on which one is additionally
    given"""
    Sep()
    geo_instance=[]
    if given_type == "pitch":
        for i in range( len( given ) ):
            for j in range( len( pd ) ):
                geo_instance.append( [ given [ i ] ] )
                geo_instance[ i * len( pd ) + j ].append( \
                     given[ i ] / pd[ j ] )
                logging.debug( "For pitch " + str( given[ i ] ) + \
                " and p/d ratio " + str( pd[ j ] ) + " the diameter is: " )
                logging.debug( str( geo_instance[ i * len( pd ) + j ][ 1 ] ) )
        logging.debug( "There are " + str( len( given ) ) + " pitches \n" + \
            " and there are " + str( len( geo_instance) ) + " geo arrays" )
    elif given_type == "diameter":
        for i in range( len( given ) ):
            for j in range( len( pd ) ):
                Cep()
                geo_instance.append( [ given[ i ] * pd[ j ] , \
                     given[ i ] ] )
            logging.debug( "For diameter " + str( given[ i ] ) + \
                " and p/d raio " + str( pd[ j ] ) + " the pitch is: " )
            logging.debug( str( geo_instance[ i * len( pd ) + j ][ 0 ] ) )
        logging.debug( "There are " + str( len( given ) ) + " diameters \n" + \
            " and there are " + str( len( geo_instance ) ) + " geo arrays" )
    else:
        print( "ERROR: Choice of pitch or diameter ( given as 'pitch' or \n \
            'diameter' ) was not properly given. Goodbye. " )
        logging.debug( "< given_type > in function < Gen_Pitch_or_Diameter >\n\
            was neither 'diameter' nor 'pitch'" )
        exit()  
    if 'log_level' in options: 
        if options[ 'log_level' ] < 10:
            Cep()
            logging.debug( "The geo_instance array is: " ) 
            for i in range( len( geo_instance ) ):
                logging.debug( str( geo_instance[ i ] ) )
    return( geo_instance )

def Gen_Width_List( cladding, Sep ):
    """ This function creates a list of floats for clad widths """
    Sep()
    logging.debug( "The initial cladding array is: ")
    logging.debug( cladding )
    widths = [ float( x ) for x in cladding[ 1 : : 2 ] ]
    logging.debug( "The widths array is: " )
    logging.debug( widths )
    return( widths )

def Gen_Materials_List( cladding , filler , outside_mat , Sep ):
    """ This function creates a list of strings for the materials """
    Sep()
    logging.debug( "The initial cladding array is: " )
    logging.debug( cladding )
    logging.debug( "The filler is: " + filler )
    logging.debug( "The outside_mat is " + outside_mat )
    materials = [ filler ]
    materials = materials + cladding[ 0 : : 2 ]
    materials.append( outside_mat )
    logging.debug( "The materials array is: ")
    logging.debug( str( materials ) )
    return( materials )


def Gen_Inmost_Radius( widths , geo_instance , options , Sep , Cep ):
    """ This function generates the inner substance radius """
    Sep()
    logging.debug( "The widths are: " + str( widths ) )
    thickness = sum( widths )
    logging.debug( "The sum of widths is: " + str( thickness ) )
    Cep()
    for i in range( len( geo_instance ) ): 
        geo_instance[ i ].append( [ geo_instance[ i ][ 1 ] / 2.0 - \
            thickness ] )
        logging.debug( "The inner radius for diameter " + \
            str( geo_instance[ i ][ 1 ] ) + " is: " + \
            str( geo_instance[ i ][ 2 ] ) )
    return( geo_instance )

def Gen_Cladding_Radii( widths , geo_instance , options , Sep , Cep ):
    """ This function generates the outer radii for each clad layer """
    Sep()
    logging.debug( "The widths array is: " + str( widths ) )
    for i in range( len( geo_instance ) ):
        Cep()
        logging.debug( "Inner radius being built is: " + str( \
            geo_instance[ i ][ 2 ] ) )
        for j in range( len( widths ) ):
            geo_instance[ i ][ 2 ].append( widths[ j ] + \
                sum( geo_instance[ i ][ 2 ] ) ) 
        logging.debug( "The build array is: " + str( geo_instance[ i ][ 2 ] ) ) 
    if 'log_level' in options: 
        if options[ 'log_level' ] < 10:
            Cep()
            logging.debug( "The final build array is: " )
            for i in range( len( geo_instance ) ):
                logging.debug( str( geo_instance[ i ] ) )
    return( geo_instance )

def Surface_Line_Writer( material , radius , x_pos , y_pos , \
    shape , id_num , Sep , Cep ):
    """ This function generates the strings for surfaces, both comment and
    actual """
    Cep()
    comment_string = "% ------ " + material + " Surface\n"
    if shape != "cyl":
        surf_string = "surf    " + str( id_num ) + "    " + shape + "    " + \
            str( x_pos ) + "    " + str( y_pos ) + "    " + str( radius ) + \
                "    0.0\n" 
    else:
        surf_string = "surf    " + str( id_num ) + "    " + shape + "    " + \
            str( x_pos ) + "    " + str( y_pos ) + "    " + str( radius ) + "\n"
    output = [ comment_string , surf_string ]
    logging.debug( "The surf strings are: " )
    logging.debug( output[ 0 ].rstrip( "\n" ) )
    logging.debug( output[ 1 ].rstrip( "\n" ) )
    return( output )

def Cell_Line_Writer( material , inner_bound , outer_bound , id_num \
        , uni_num , index , Sep , Cep ):
    """ This function writes strings for cells """
    Cep()
    if material == "outside":
        cell_string = "{0:<8} {1:<6} {2:<6} {3:<20} {4:<4}\n"\
            .format( "cell" , str( id_num ) , str( uni_num ) , material , \
                str( inner_bound ) , str( outer_bound ) )
    elif index < 1:
# This indicates it is the first cell and as such has no inner_bound
# We only use inner bound because that index number becomes the outer_bound
        cell_string = "{0:<8} {1:<6} {2:<6} fill {3:<27}     {4:<4}\n"\
            .format("cell" , str( id_num ) , str( uni_num ) , str( material ), \
                str( outer_bound ) )
    else: 
        cell_string = "{0:<8} {1:<6} {2:<6} fill {3:<15} {4:<4}\
            {5:<4}\n"\
            .format( "cell" , str( id_num ) , str( uni_num ) , \
                str( material ) , str( inner_bound ) , str( outer_bound ) ) 
    output = [ cell_string ]
    logging.debug( "The cell string is: " )
    logging.debug( output[ 0 ].rstrip( "\n" ) )
    return( output )

def Gen_New_File_Name( geo_array_seg , base_name , options , Sep , Cep ):
    """ This function generates the new file name """
    Sep()
    logging.debug( "The pitch being developed is: " + \
        str( geo_array_seg[ 0 ] ) )
    logging.debug( "The diameter being developed is: " + \
        str( geo_array_seg[ 1 ] ) )
    d_string = str( geo_array_seg[ 1 ] )[ : 6 ] if \
        len( str( geo_array_seg[ 1 ] ) ) > 7 else str( geo_array_seg[ 1 ] )
    new_name = base_name + "_" + str( options[ "lattice_type" ] ) + \
    "_" + str( geo_array_seg[ 0 ] ) + "_P_" + d_string + \
         "_D_.test"
    logging.debug( "The new_name is: " + new_name )
    return( new_name )

def Insert_Lines( host_file , insert_start , offset , add_lines , Sep , Cep ):
    """ This function takes a list of the host file's lines, host_file ,
    and a list of lines to be added, add_lines, and inserts these lines
    into the file starting at insert_start and updating the file's offset """
    Sep()
    logging.debug( "The initial offset is: " + str( offset ) )
    for i in range( len( add_lines ) ):
        host_file.insert( insert_start + offset , add_lines[ i ] )
        offset += 1 
    output = [ host_file , offset ]
    return( output )

def Files_Generator( base_name , materials , host_file , options , \
     geo_array , Gen_New_File_Name , Insert_Lines , Sep , Cep ):
    """ This function generates values to pass to the string writers and then
    inserts these values into the file to be written actually writes the
     contents to file """
    Sep()
    surf_start = host_file.index( "% ------ RSAC\n" ) + 1
    logging.debug( "The surf_start index is: " + str( surf_start ) )
    cell_start = host_file.index( "% ------ AGC\n" ) + 1
    logging.debug( "The cell_start index is: " + str( cell_start ) )
    lattice = options[ "lattice_type" ]
    logging.debug( "The lattice is: " + options[ 'lattice_type' ] )
    for i in range( len( geo_array ) ):
        Cep()
        new_name = Gen_New_File_Name( geo_array[ i ] , base_name , options , \
            Sep , Cep )
        new_file_list = cp.deepcopy( host_file )
# This variable tracks the number of inserted lines
        offset = 0
        surface_strings = []
        cell_strings = []
        Sep()
        logging.debug( "The area to be written to: " )
        for m in range( surf_start - 10 , cell_start + 10 , 1 ):
            logging.debug( new_file_list[ m ].rstrip("\n" ) )
        Sep()
# This loop generates the list of strings to be added. This list is a list of 
# lists where each list holds the strings and the starting index for them
# to be placed in the new file
        for k in range( len( materials ) - 1 ):
            surface_strings = surface_strings + Surface_Line_Writer( \
                materials[ k ] , geo_array[ i ][ 2 ][ k ]  , \
                0.0 , 0.0 , "cyl" , k + 10 , Sep , Cep ) 
            cell_strings = cell_strings + Cell_Line_Writer( \
               materials[ k ] , k + 9 , ( k + 10 ) * -1 , k + 10 , 0 \
               , k , Sep , Cep ) 
# These two function calls write out the final surface and cell lines each
        surface_strings = surface_strings + Surface_Line_Writer( \
            options[ 'outside_type' ] , geo_array[ i ][ 0 ] ,  0.0 , 0.0 , \
            lattice , k + 11 , Sep , Cep ) 
        cell_strings = cell_strings + Cell_Line_Writer( "outside" , k + 10 , \
            ( k + 11 ) * -1 , k + 11 , 0 , k + 1 , Sep , Cep ) 
# Here we insert the lines we have created into the new_file_list
        new_file_list , offset = Insert_Lines( new_file_list , surf_start , \
            offset , surface_strings , Sep , Cep )
        new_file_list , offset = Insert_Lines( new_file_list , cell_start , \
            offset , cell_strings , Sep , Cep )
# Here we actually write to file
        destination_file = open( new_name , "w" )
        destination_file.writelines( new_file_list )
        destination_file.close()
    return()

# Start the program
print( "\nThe program is now running\n" )
setup = Read_Setup()

base_name = Get_Base_Name( setup[ "file_name" ] )

try:
    Start_Log( base_name ,  setup[ "log_level" ] )
except:
    Start_Log( base_name , 0 )
    logging.debug( "ERROR!!: < log_level > was not found in init_setup.txt\n \
        and as such LogLevel was set to 0" )

if 'log_level' in setup:
    if setup[ 'log_level' ] < 10:
        Sep()
        logging.debug( "The input dictionary is: " )
        for keys,values in setup.items():
            logging.debug( str( keys ) + " : " + str( values ) )

host_file = Read_Input( setup[ "file_name" ] , 'raw' , Sep )
    
given = Read_Input( setup[ "given_file" ] , 'float' , Sep )

pd = Read_Input( setup[ "pd_file" ] , 'float' , Sep )

cladding = Read_Input( setup[ "materials_file" ] , 'string' , Sep )

generated = Gen_Pitch_or_Diameter( pd , given , setup[ "given_type" ] , \
    setup , Sep , Cep )

widths = Gen_Width_List( cladding , Sep )

materials = Gen_Materials_List( cladding , setup[ "filler_type" ] , \
    setup[ "outside_type" ] , Sep )

generated = Gen_Inmost_Radius( widths , generated , setup , Sep , Cep )

generated = Gen_Cladding_Radii( widths , generated , setup , Sep , Cep )

Files_Generator( base_name , materials , host_file , setup , generated , \
    Gen_New_File_Name , Insert_Lines , Sep , Cep )

print( "The program has finished\n" )
