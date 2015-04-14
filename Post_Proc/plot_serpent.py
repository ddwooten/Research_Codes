#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import math as math
import logging as logging
import copy as cp
import re as re
import numpy as np
import matplotlib.pyplot as plt
# These are custom built python modules containing helpful and necessary
#   functions.
import wooten_common as wc
import post_common as post_common
import decode as decode
import nuclide_ids as nid

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
   Additionally a plotting parameters file is required for plotting. This file
   should be titled "[host_file]_plots_input.json" as it is formatted as a
   json file. The primary container is a list, inside this list are
   dictionaries ( in json jargon "objects" ), inside of these dictionaries
   are parameters for the plots; i.e. each dictionary inside the list
   represents a plot. A sample is given below. For atom_burnup plots each
   componenet will become a line on the plot while each entry in members is
   summed up to create the component it is hosted in. Additionally,
   matplotlib has its own implemention of the TeX engine and TeX style strings
   may be provided for any string argument given for display on a plot, most
   notably titles and axis labels. The ability to use LaTeX explicitly with
   all of its packages is also an option but requires advanced configuration.
   <<<
    [
        {
            "type" : "atom burnup",
            "components" : { 
                "fuel" : {
                    "y_range" : [
                        0.0,
                        10.5
                        ],
                    "members" : { 
                        "U-235" : { 
                            "element" : "U",
                            "Z" : 92,
                            "isotopes" : [
                                235,
                                238
                            ],
                            "materials" : [
                                "all"
                            ]
                        },
                        "Pu-239" : {
                            "element" : "Pu",
                            "Z" : 94,
                            "isotopes" : [
                                "all"
                            ],
                            "materials" : [
                                "fuel",
                                "blanket"
                            ]
                        }
                    },
                    "marker" : "o",
                    "label" : "fuel",
                    "color" : "g",
                    "size" : 20
                }
            },
            "x_label" : "Days",
            "y_label" : "atoms/$cm^3$",
            "title" : "Fuel Atom Density in atoms/cc Over Time in days",
            "legend_loc" : "upper right"
        }
    ]
    >>>
   Additionally the program "post_process.py" will be called, this program
   has its own configuration file and requirements. Please see that file for
   explanation.
"""
def Make_Plots( data , base_name ):
    """ This function reads in the plotting command file, titled
        [base_name]_plots_input.json"""
    wc.Sep()
    logging.info( "Read_Plots" )
    input_file = open( base_name + "_plots_input.json" , "r" )
    plot_params = json.load( input_file , object_hook = decode.Decode_Dict )
    for i in range( len( plot_params ) ):
        if plot_params[ i ][ "type" ] = "atom_burnup":
            Prep_Atom_Burnup( plot_params[ i ][ "components" ] , \
                data[ "burnup_data" ] )
            Plot_Atom_Burnup( plot_params[ i ] )
        elif plot_params[ i ][ "type" ] = "atom_percent_change":
            for key in plot_params[ i ][ "components" ]:
                plot_params[ i ][ "components" ][ key ][ "p_change" ] = \
                    Get_Percentage_Change( \
                    plot_params[ i ][ "components" ][ key ] , data )
        elif plot_params[ i ][ "type" ] = "k_evolution":
            for key in plot_params[ i ][ "components" ]:
                plot_params[ i ][ "components" ][ key ][ "y_data" ] = \
                    Get_K_Data( plot_params[ i ][ "components" ][ key ] , data )
                plot_params[ i ][ "components" ][ key ][ "x_data" ] = \
                    Get_Time_Range( plot_params[i][ "components" ][ key ],data )
    return

def Prep_Atom_Burnup( components , burn_data ):
    """ This function, using the information in params, gathers the data to form
    the y_data for the desired plot as well as the x_data """
    wc.Sep()
    logging.info( "Get_Atom_Burnup" )
    for key in componenets:
        y_data = np.zeros( len( burn_data[ "burn_data" ][ "BU" ] ) )
        span , x_type = Get_X_Info( components[ key ],burn_data[ "burn_data" ] )
        components[key]["x_data"] = burn_data[time_type][span[0],span[1]]
        Check_X_Label( components[ key ] , x_type ) 
        for item in components[ key ][ "members" ]:
            mat_list = Get_Material_Keys( burn_data[ "burn_data" ] , "ADENS" , \
                components[ key ][ item ][ "materials" ] )
            isos_list = Get_Isotope_Indicies( burn_data[ "indicies" ] , \
                components[ key ][ item ][ "Z" ] , \
                components[ key ][ item ][ "isotopes" ] ):
            for mat in mat_list:
                for iso in isos_list: 
                    y_data += burn_data[ "burn_data" ][ mat ][ iso ]
        components[ key ][ "y_data" ] = y_data[ span[ 0 ] : span[ 1 ] ]

def Check_X_Label( constituent , time_type ):
    """ This function"""
def Get_X_Data( constituent , burn_data ):
    """ This function returns the correct key for the x_data as well as
        the range if
        asked for. The given range does not need to be exact. The returned
        range will be the smallest range that is inclusive of the desired
        range"""
    wc.Sep()
    logging.info( "Get_X_Data" )
    if "x_type" in constituent:
        if constituent[ "x_type" ] == "day" or "days" or "Day" or "Days" or "d":
            time_type = "DAYS"
    else:
        time_type = "BU"
        constituent[ "x_type" ] = "BU"
    if "x_range" in constituent:
        if len( constituent[ "x_range" ] ) > 1:
            splice = []
            for i in range( len( burn_data[ time_type ] ) ):
                if burn_data[time_type][i] == constituent["x_range "][ 0 ]:
                    splice.append( burn_data[ time_type ][ i ] )
                    break
                if burn_data[time_type][i] > constituent["x_range "][ 0 ]:
                    splice.append( burn_data[ time_type ][ i - 1 ] )
                    break
            for i in range( len( burn_data[ time_type ] ) ):
                if burn_data[time_type][i] == constituent["x_range "][ 1 ]:
                    splice.append( burn_data[ time_type ][ i ] )
                    break
                if burn_data[time_type][i] > constituent["x_range "][ 1 ]:
                    splice.append( burn_data[ time_type ][ i - 1 ] )
                    break
    else:
        splice = [ 0 , len( burn_data[ time_type ] ) - 1 ]
    output = [ splice , time_type ]
    return( output )
                        
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

def Get_Isotope_Indicies( nuclide_indicies , Z , isotopes ):
    """ This function collapses isotopic burn vectors into a given
        elemental burn vector """
    wc.Sep()
    logging.Info( "Get_Isotope_Indicies" )
    logging.debug( "Z is: " + str( Z ) )
    nuclide_list = []
    if isinstance( isotopes[ 0 ] , str ):
        for key in nuclide_indicies:
            cur_Z = int( math.floor( float( key ) / 1000.0 ) )
            if Z == cur_Z:
                logging.debug( "Isotope is: " + str( key ) )
                nuclide_list.append( nuclide_indicies[ key ] )
    else:
        for item in isotopes:
            A = str( item ).zfill( 3 )
            nuclide_list.append(nuclide_indicies[ int( str( Z ) + str( A ) ) )])
    return( nuclide_list ) 

def Get_Material_Keys( data , attribute , materials ):
    """ This function gathers burn data across a given list of materials
        or accross all materials ( mimics TOT in earlier SERPENT files ).
    """
    wc.Sep()
    logging.info( "Gather_Materials" )
    logging.debug( "The materials are: " )
    logging.debug( str( materials ) )
    pattern = re.compile( r'\S*_' + attribute )
    material_keys = []
    for key in data:
        if materials[ 0 ] != "all" or "All" or "ALL":
            for mat in materials:
                match = None
                pattern = re.compile( r"\S*_" + mat + \
                    "_" + attribute )
                match = pattern.match( key )
                if match:
                    logging.debug( "The match is: " + match.group() ) 
                    break
        else:
            match = pattern.match( key )
            logging.debug( "The match is: " + match.group() ) 
        if match:
            material_keys.append( key )
    return( material_keys )

def Calculate_Percent_Change( vector ):
    """ This function simply gets the percent change between an aspect's
        first value and its last """
        wc.Sep()
        logging.info( "Get_Percent_Difference" )
        diff = ( float( vector[ -1 ] ) - float( vector[ 0 ] ) ) * 100.0 / \
            float( vector[ 0 ] )
        return( diff )

def Percentage_Change_Plot( params , base_name ):
    """ This function creates a vertical bar graph of the percentage change
        of values passed in with x_data and given labels in labels. params
        contain optional plotting options. """
    wc.Sep()
    logging.info( "Percentage_Change_Plot" )
    fig = plt.figure()
    axes1 = fig.add_subplot( 111 )
    bar_list = []
    legend_list = []
    names_list = []
    bar_number = 0
    for key in params[ "components" ]:
        if "width" in params[ "components" ][ key ]:
            width = float( params[ "components"][ key ][ "width" ] )
        else:
            width = 0.35
        if "color" in params[ "components" ][ key ]:
            color = params[ "components" ][ key ][ "color" ]
        else:
             color = 'b'
        bar_list.append( axes1.bar( bar_number , \
            params[ "components" ][ key ][ "p_change" ] , \
                width , c = color ) )
        legend_list.append( bar_list[ bar_number ][ 0 ] )
        if "label" in params:
            names_list.append( params[ "components" ][ key ][ "label" ] )
        else:
            names_list.append( str( key ) )
# This simply creates a legend for our plot
    ax.legend( legend_list , names_list )
    if "title" in params:
        axes1.set_title( params[ "title" ] )
    else:
        axes1.set_title( "Scatter Plot of y( x )" )
    if "y_label" in params:
        axes1.set_ylabel( params[ "y_label" ] )
    else:
        axes1.set_ylabel( "y axis" )
    if "x_label" in params:
        axes1.set_xlabel( params[ "x_label" ] )
    else:
        axes1.set_xlabel( "x axis" )
    if "legend_loc" params:
        plt.legend( loc = params[ "legend_loc" ] )
    else:
        plt.legen( loc = "upper right" )
    if "title" in params:
        plt.savefig( base_name + "_" + params[ 'title' ] + ".eps" , \
            format = 'eps' , dpi = 1000 )
    else:
        plt.savefig( base_name + "_bar_" + str( np.random.randint( 100 , \
            size = 1 ) ) + ".eps" , format = 'eps' , dpi = 1000 )
    plt.cla()
    return

def Scatter_Plot( params , base_name ):
    """ This function plots a dict of lists from params against a list of
        y_data while params contains additional optional plotting
        parameters """
    wc.Sep()
    logging.info( "Scatter_Plot" )
    fig = plt.figure()
    axes1 = fig.add_subplot( 111 )
    for key in params[ "components" ]:
        if "size" in params[ "components" ][ key ]:
            size = params[ "components" ][ key ][ "size" ]
        else:
             size = 20
        if "color" in params[ "components" ][ key ]:
            color = params[ "components" ][ key ][ "color" ]
        else:
             color = 'b'
        if "marker" in params[ "components" ][ key ]:
            mark = params[ 'marker' ][ i ]
        else:
             mark = 'o'
        if "label" in params[ "components" ][ key ]:
            name = params[ "components" ][ key ][ 'label' ]
        else:
             name = str( key )
        axes1.scatter( params[ "components" ][ key ][ "x_data" ] , \
            params[ "components" ][ key ][ "y_data" ] , s = size , c = color , \
            marker = mark , label = name )
    if 'title' in params:
        axes1.set_title( params[ 'title' ] )
    else:
        axes1.set_title( 'Scatter Plot of y( x )' )
    if 'y_label' in params:
        axes1.set_ylabel( params[ 'y_label' ] )
    else:
        axes1.set_ylabel( 'y axis' )
    if 'x_label' in params:
        axes1.set_xlabel( params[ 'x_label' ] )
    else:
        axes1.set_xlabel( 'x axis' )
    if 'legend_loc' in params:
        plt.legend( loc = params[ 'legend_loc' ] )
    else:
        plt.legend( loc = 'upper right' )
    if 'title' in params:
        plt.savefig( base_name + "_" + params[ 'title' ] + ".eps" , \
            format = 'eps' , dpi = 1000 )
    else:
        plt.savefig( base_name + "_" + params[ "type" ] + "_" + \
            str( np.random.randint( 100 , \
            size = 1 ) ) + ".eps" , format = 'eps' , dpi = 1000 )
    plt.cla()
    return
    
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
