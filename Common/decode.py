#!/usr/bin/python

""" These two functions can be used with the json module for python as
    an object hook to prevent unicode encoding of strings. Simply pass
    the Decode_Dict function like so
    << a = json.load( file , object_hook = Decode_Dict ) >>
    This will preserve all values but convert strings to ascii strings,
    not unicode. If unicode is desired simply do not pass anything to
    ojbect_hook.
    This function will live here and in /usr/lib/pymodules/python2.7
     """

def Decode_List( data ):
    """ This function decodes lists for the json module """
    output = []
    for item in data:
        if isinstance( item , unicode ):
            item = item.encode( 'ascii' )
        elif isinstance( item , list ):
            item = Decode_List( item )
        elif isinstance( item , dict ):
            item = Decode_Dict( item )
        output.append( item )
    return( output )

def Decode_Dict( data ):
    """ This function decodes dicts for the json module """
    output = {}
    for key , value in data.iteritems():
        if isinstance( key , unicode ):
            key = key.encode( 'ascii' )
        if isinstance( value , unicode ):
            value = value.encode( 'ascii' )
        elif isinstance( value , list ):
            value = Decode_List( value )
        elif isinstance( value , dict ):
            value = Decode_Dict( value )
        output[ key ] = value
    return( output )
