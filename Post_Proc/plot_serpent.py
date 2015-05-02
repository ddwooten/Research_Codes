#!/usr/bin/python
# Creator: Daniel Wooten
# Version 1.0.

import math as math
import logging as logging
import copy as cp
import re as re
import numpy as np
import matplotlib.pyplot as plt
import json as json
# These are custom built python modules containing helpful and necessary
#   functions.
import wooten_common as wc
import post_common as post_common
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
def Make_Plots( data , options ):
    """ This function reads in the plotting command file, titled
        [base_name]_plots_input.json"""
    wc.Sep()
    logging.info( "Read_Plots" )
    input_file = open( wc.Get_Base_Name( options[ "host_name" ] ) + \
        "_plots_input.json" , "r" )
    plot_params = json.load( input_file , object_hook = wc.Decode_Json_Dict )
    wc.Cep()
    logging.debug( "The plot parameters are: " )
    logging.debug( str( plot_params ) )
    wc.Cep()
    for i in range( len( plot_params ) ):
        if plot_params[ i ][ "type" ] == "attribute_burnup":
            Prep_Attribute_Burnup( plot_params[ i ][ "components" ] , \
                data[ "burnup_data" ] )
            Scatter_Plot( plot_params[ i ] , wc.Get_Base_Name( \
                options[ "host_name" ] ) )
        elif plot_params[ i ][ "type" ] == "attribute_burnup_forward_diff":
            Prep_Attribute_Burnup( plot_params[ i ][ "components" ] , \
                data[ "burnup_data" ] )
            Prep_Forward_Difference( plot_params[ i ][ "components" ] )
            Scatter_Plot( plot_params[ i ] , wc.Get_Base_Name( \
                options[ "host_name" ] ) )
        elif plot_params[ i ][ "type" ] == "attribute_burnup_equilibrium":
            Prep_Attribute_Burnup( plot_params[ i ][ "components" ] , \
                data[ "burnup_data" ] )
            Prep_Equilibrium( plot_params[ i ][ "components" ] )
            Scatter_Plot( plot_params[ i ] , wc.Get_Base_Name( \
                options[ "host_name" ] ) )
        elif plot_params[ i ][ "type" ] == "attribute_percent_change":
            Prep_Attribute_Percent_Change( plot_params[ i ][ "components" ] , \
                data[ "burnup_data" ] )
        elif plot_params[ i ][ "type" ] == "k_evolution":
            for key in plot_params[ i ][ "components" ]:
                plot_params[ i ][ "components" ][ key ][ "y_data" ] = \
                    Get_K_Data( plot_params[ i ][ "components" ][ key ] , data )
                plot_params[ i ][ "components" ][ key ][ "x_data" ] = \
                    Get_Time_Range( plot_params[i][ "components" ][ key ],data )
    return

def Prep_Attribute_Burnup( components , burn_data ):
    """ This function, using the information in params, gathers the data to form
    the y_data for the desired plot as well as the x_data """
    wc.Sep()
    logging.info( "Get_Atom_Burnup" )
    for key in components:
        logging.debug( "member is: " + str( key ) )
        y_data = np.zeros( burn_data[ "burn_data" ][ "BU" ].shape[ 0 ] )
        span , x_type = Get_X_Data( components[ key ],burn_data[ "burn_data" ] )
        components[ key ][ "x_data" ] = \
            burn_data[ "burn_data" ][ x_type ][ span[ 0 ] : span[ 1 ] ]
        for item in components[ key ][ "members" ]:
            logging.debug( "Item is: " + str( item ) )
            mat_list = Get_Material_Keys( burn_data[ "burn_data" ] , \
                components[ key ][ "attribute" ] , \
                components[ key ][ "members" ][ item ][ "materials" ] )
            logging.debug( "mat_list is: " + str( mat_list ) )
            isos_list = Get_Isotope_Indicies( burn_data[ "indicies" ] , \
                components[ key ][ "members" ][ item ][ "Z" ] , \
                components[ key ][ "members" ][ item ][ "isotopes" ] )
            logging.debug( "isos_list is: " + str( isos_list ) )
            for mat in mat_list:
                for iso in isos_list: 
                    logging.debug( "The array to be added is: " + \
                        str( np.array( burn_data[ "burn_data" ][mat][iso] ) ) )
                    y_data += np.array(burn_data["burn_data"][mat][iso])[ 0 ]
                    logging.debug( "y_data shape: " + str( y_data.shape ) )
                    logging.debug( "np.array shape: " + \
                        str( np.array( burn_data[ "burn_data" ][mat][iso][0])))
        components[ key ][ "y_data" ] = y_data[ span[ 0 ] : span[ 1 ] ]
    return

def Prep_Forward_Difference( components ):
    """ This function takes in components ( objects to graph ) and replaces
        their y_data with the forward difference calculation of the derivative.
        It also approprietly trims the x_data vector to match in length ( i.e.
        one index short as the last won't have a forward differnce ). y_data
        must be of numpy array type as must x_data.
    """
    wc.Sep()
    logging.info( "Prep_Foward_Difference" )
    for key in components:
        for i in range( components[ key ][ "y_data" ].shape[ 0 ] - 1 ):
            components[ key ][ "y_data" ][ i ] = \
                ( float( components[ key ][ "y_data" ][ i + 1 ] ) - \
                float( components[ key ][ "y_data" ][ i ] ) ) / \
                ( float( components[ key ][ "x_data" ][ i + 1 ] ) - \
                float( components[ key ][ "x_data" ][ i ] ) )
        components[ key ][ "y_data" ] = components[ key ][ "y_data" ][ : -1 ]
        components[ key ][ "x_data" ] = components[ key ][ "x_data" ][ : -1 ]
    return

def Prep_Equilibrium( components ):
    """ This function will return the y and x value at which equilibrium
        occurs as defined as equilibrium start being the point for which the
        y value of the next two points does not differ by more than 1%. If this
        does not accur a NaN will be returned. These values will be returned
        as a list of lists
    """
    wc.Sep()
    logging.info( "Get_Equilibrium_Time" )
    for key in components:
        for i in range( components[ key ][ "y_data" ].shape[ 0 ] - 2 ):
            try:
                diff_1 = abs((float(components[ key ][ "y_data" ][ i + 1 ] ) - \
                    float( components[ key ][ "y_data" ][ i ] ) ) / \
                    float( components[ key ][ "y_data" ][ i ] ) )
            except:
                if ( float( components[ key ][ "y_data" ][ i + 1 ] ) - \
                    float( components[ key ][ "y_data" ][ i ] ) ) == 0.0:
                    diff_1 = 0
                else: 
                    diff_1 = float( "inf" )
            try:
                diff_2 = abs((float(components[ key ][ "y_data" ][ i + 2 ] ) - \
                    float( components[ key ][ "y_data" ][ i ] ) ) / \
                    float( components[ key ][ "y_data" ][ i ] ) )
            except:
                if ( float( components[ key ][ "y_data" ][ i + 2 ] ) - \
                    float( components[ key ][ "y_data" ][ i ] ) ) == 0.0:
                    diff_2 = 0
                else: 
                    diff_2 = float( "inf" )
            if diff_1 <= 0.01 and diff_2 <= 0.01:
                components[ key ][ "y_data" ]=components[ key ][ "y_data" ][ i ]
                components[ key ][ "x_data" ]=components[ key ][ "x_data" ][ i ]
                break
            if diff_1 > 0.01 and diff_2 > 0.01 and i == \
                components[ key ][ "y_data" ].shape[ 0 ] - 2:
                components[ key ][ "y_data" ] = None
                components[ key ][ "x_data" ] = None

    return

def Get_X_Data( constituent , burn_data ):
    """ This function returns the correct key for the x_data as well as
        the range if
        asked for. The given range does not need to be exact. The returned
        range will be the smallest range that is inclusive of the desired
        range"""
    wc.Sep()
    logging.info( "Get_X_Data" )
    if "x_type" in constituent:
        if constituent["x_type"] in ( "day" , "days" , "Day" , "Days" , "d" ):
            time_type = "DAYS"
        else:
            time_type = "BU"
    else:
        time_type = "BU"
        constituent[ "x_type" ] = "BU"
    if "x_range" in constituent:
        if len( constituent[ "x_range" ] ) > 1:
            splice = []
            if constituent[ "x_range" ][ 0 ] <= burn_data[ time_type ][ 0 ]:
                splice.append( burn_data[ time_type ][ 0 ] )
            else:
                for i in range( len( burn_data[ time_type ] ) ):
                    if burn_data[time_type][i] == constituent["x_range"][ 0 ]:
                        splice.append( burn_data[ time_type ][ i ] )
                        break
                    if burn_data[time_type][i] > constituent["x_range"][ 0 ]:
                        splice.append( burn_data[ time_type ][ i - 1 ] )
                        break
            if constituent[ "x_range" ][ 1 ] >= burn_data[ time_type ][ -1 ]:
                splice.append( burn_data[ time_type ][ -1 ] )
            else:
                for i in range( len( burn_data[ time_type ] ) ):
                    if burn_data[time_type][i] == constituent["x_range"][ 1 ]:
                        splice.append( burn_data[ time_type ][ i ] )
                        break
                    if burn_data[time_type][i] > constituent["x_range"][ 1 ]:
                        splice.append( burn_data[ time_type ][ i - 1 ] )
                        break
    else:
        splice = [ 0 , len( burn_data[ time_type ] ) - 1 ]
    output = [ splice , time_type ]
    return( output )

def Get_Isotope_Indicies( nuclide_indicies , Z , isotopes ):
    """ This function collapses isotopic burn vectors into a given
        elemental burn vector """
    wc.Sep()
    logging.info( "Get_Isotope_Indicies" )
    logging.debug( "Z is: " + str( Z ) )
    logging.debug( "Isotopes requested are: " )
    logging.debug( str( isotopes ) )
    nuclide_list = list()
    if str( isotopes[ 0 ] ) in ( "All" , "ALL" , "all" ):
        logging.debug( "Isotopes for " + str( Z ) + " are ALL" )
        for key in nuclide_indicies:
            cur_Z = int( math.floor( float( key ) / 10000.0 ) )
            if Z == cur_Z:
                logging.debug( "Isotope is: " + str( key ) )
                nuclide_list.append( nuclide_indicies[ key ] )
    else:
        logging.debug( "Specific Isotopes are requested, they are: " )
        logging.debug( str( isotopes ) )
        for item in isotopes:
            if str( item )[ -1 ] == "m":
                A = str( item )[ : -1 ].zfill( 3 ) + '1'
                nuclide_list.append(nuclide_indicies[int(str(Z)+str(A))])
            else:
                A = str( item ).zfill( 3 ) + '0'
                nuclide_list.append(nuclide_indicies[int(str(Z)+str(A))])
    logging.debug( "The nuclide_list is: " )
    logging.debug( str( nuclide_list ) )
    return( nuclide_list ) 

def Get_Material_Keys( data , attribute , materials ):
    """ This function gathers burn data across a given list of materials
        or accross all materials ( mimics TOT in earlier SERPENT files ).
    """
    wc.Sep()
    logging.info( "Gather_Materials" )
    logging.debug( "The materials are: " )
    logging.debug( str( materials ) )
    logging.debug( "The attribute is:'" + str( attribute ) + "'" )
    pattern = re.compile( r'\S*_' + attribute )
    material_keys = list() 
    for key in data:
        if materials[ 0 ] not in ( "all" , "All" , "ALL" ):
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
        if match:
            material_keys.append( key )
    logging.debug( "The material_keys list is: " )
    logging.debug( str( material_keys ) )
    return( material_keys )

def Calculate_Percent_Change( vector ):
    """ This function simply gets the percent change between an aspect's
        first value and its last """
    wc.Sep()
    logging.info( "Get_Percent_Difference" )
    diff = ( float( vector[ -1 ] ) - float( vector[ 0 ] ) ) * 100.0 / \
        float( vector[ 0 ] )
    return( diff )

def Get_Auto_Scale( params , data_type ):
    """ This function scans through params[ components ][ key ][ data_type ]
        and pulls the max and min from data_type against all keys. It then
        increments and decrements, respectively, by 10% of the range and
        returns this list
    """
    wc.Sep()
    logging.info( "Get_Auto_Scale" )
    overall_min = float( "inf" ) 
    overall_max = None
    for key in params[ "components" ]:
        cur_min = np.amin( params[ "components" ][ key ][ data_type ] )
        cur_max = np.amax( params[ "components" ][ key ][ data_type ] )
        if cur_min < overall_min:
            overall_min = cp.deepcopy( cur_min )
        if cur_max > overall_max:
            overall_max = cp.deepcopy( cur_max )
    rng = overall_max - overall_min
    overall_min = overall_min - 0.1 * rng
    overall_max = overall_max + 0.1 * rng
    output = [ overall_min , overall_max ]
    return( output )

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
        axes1.set_title( "Percentage Diff Plot " )
    if "y_label" in params:
        axes1.set_ylabel( params[ "y_label" ] )
    else:
        axes1.set_ylabel( "y axis" )
    if "x_label" in params:
        axes1.set_xlabel( params[ "x_label" ] )
    else:
        axes1.set_xlabel( "x axis" )
    if "legend_loc" in params:
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

def Print_Values( params , base_name ):
    """ This function prints to file the x and y data given in params
    """
    wc.Sep()
    logging.info( "Print_Values" )
    out_matrix = list()
    if "title" in params:
        if "save_name" not in params:
            file_name = base_name + "_" + params[ "title" ] + \
               "_" + ".eps" 
            file_name = wc.File_Name_Conditioner( file_name )
    else:
        if "save_name" not in params:
            file_name = base_name + "_" + params[ "type" ] + \
               "_" + str( np.random.randint( 100 , size = 1 ) ) + ".eps" 
            file_name = wc.File_Name_Conditioner( file_name )
    if "save_name" in params:
        file_name = base_name + "_" + params[ "save_name" ] + "_"  + ".eps" 
    for key in params[ "componets" ]:
        out_matrix.append( [ params[ "components" ][ key ][ "x_data" ] , \
            params[ "components" ][ key ][ "y_data" ] ] )
    out_file = open( file_name , "w" )
    np.savetxt( out_file , np.matrix( out_matrix ) )
    out_file.close()
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
            mark = params[ "components"][ key ][ "marker" ]
        else:
             mark = 'o'
        if "label" in params[ "components" ][ key ]:
            name = params[ "components" ][ key ][ "label" ]
        else:
             name = str( key )
        axes1.scatter( params[ "components" ][ key ][ "x_data" ] , \
            params[ "components" ][ key ][ "y_data" ] , s = size , c = color , \
            marker = mark , label = name )
    if "title" in params:
        axes1.set_title( params[ 'title' ] )
        if "save_name" not in params:
            fig_name = base_name + "_" + params[ "title" ] + \
               "_" + ".eps" 
            fig_name = wc.File_Name_Conditioner( fig_name )
    else:
        axes1.set_title( 'Scatter Plot of y( x )' )
        if "save_name" not in params:
            fig_name = base_name + "_" + params[ "type" ] + \
               "_" + str( np.random.randint( 100 , size = 1 ) ) + ".eps" 
            fig_name = wc.File_Name_Conditioner( fig_name )
    if "y_label" in params:
        axes1.set_ylabel( params[ 'y_label' ] )
    else:
        axes1.set_ylabel( 'y axis' )
    if "y_auto_scale" in params:
        if params[ "y_auto_scale" ] in ( "yes" , "Yes" , "y" , "YES" , ):
            y_min , y_max = Get_Auto_Scale( params , "y_data" )
            axes1.set_ylim( bottom = y_min )
            axes1.set_ylim( top = y_max )
    if "y_min" in params:
        axes1.set_ylim( bottom = params[ "y_min" ] )
    if "y_max" in params:
        axes1.set_ylim( top = params[ "y_max" ] )
    if "x_label" in params:
        axes1.set_xlabel( params[ 'x_label' ] )
    else:
        axes1.set_xlabel( 'x axis' )
    if "x_auto_scale" in params:
        if params[ "x_auto_scale" ] in ( "yes" , "Yes" , "y" , "YES" , ):
            x_min , x_max = Get_Auto_Scale( params , "x_data" )
            axes1.set_xlim( left = x_min )
            axes1.set_xlim( right = x_max )
    if "x_min" in params:
        axes1.set_xlim( left = params[ "x_min" ] )
    if "x_max" in params:
        axes1.set_xlim( right = params[ "x_max" ] )
    if "legend_loc" in params:
        if params[ "legend_loc" ] == "off right":
            plt.legend( loc = "upper left" , bbox_to_anchor = ( 1 , 1 ) )
        else:
            plt.legend( loc = params[ 'legend_loc' ] )
    else:
        plt.legend( loc = 'upper right' )
    if "save_name" in params:
        fig_name = base_name + "_" + params[ "save_name" ] + "_"  + ".eps" 
    fig_file = open( fig_name , "w" )
    plt.savefig( fig_name , format = 'eps' , dpi = 1000 , bbox_inches = \
        "tight" )
    plt.cla()
    fig_file.close()
    return

def Plot_Main():
    """ This function runs the program if it is called as an import """
    print( "REading setup! \n" )
    setup = wc.Read_Setup( "plot" )
    print( "Right before the try statement!" )
    try:
        print( "Trying to open plot log file! \n " )
        wc.Start_Log( setup[ 'log_name' ] ,  setup[ "log_level" ] )
    except:
        print( "Failed to open plot log file in try statement\n" )
        wc.Start_Log( 'plot_error' , 0 )
        logging.debug( "ERROR!!: < log_level > or < log_name > was not \n \
            found in plot_setup.txt and as such LogLevel was set to 0 \n \
            and the base name to 'plot_error' " )

    if 'log_level' in setup:
        if setup[ 'log_level' ] < 10:
            wc.Sep()
            logging.debug( "The input dictionary is: " )
            for keys,values in setup.items():
                logging.debug( str( keys ) + " : " + str( values ) )
    print( "Calling post processor!\n " )
    data = post_common.Post_Main()
    print( "Making plots!\n " )
    Make_Plots( data , setup )

    return

print( "Beginning the plotting program \n " )

Plot_Main()

print( "Ending the plotting program \n " )
