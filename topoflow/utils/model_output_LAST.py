
# Copyright (c) 2001-2013, Scott D. Peckham
#
# Jan 2012      Fixed "print," bug and fixed "dtype" support.
# June 2010     Reorganized & streamlined with "exec", etc.
# October 2009  routines to allow more output file formats)
# August 2009
# January 2009  Converted from IDL.
#
#-------------------------------------------------------------------
#  Functions:
#
#      check_nio()          # test import of Nio package
#      get_nio_type_map()   # map NumPy types to letter codes

#      open_new_gs_file()   # open new grid stack file
#      add_grid()
#      close_gs_file()
#
#      open_new_ts_file()   # open new time series file
#      add_values_at_IDs()
#      add_values()         # placeholder
#      close_ts_file()
#
#      open_new_ps_file()   # open new profile series file
#      add_profiles_at_IDs()
#      add_profiles()
#      close_ps_file()
#
#      open_new_cs_file()   # open new cube stack file
#      add_cube()
#      close_cs_file()
#
#-------------------------------------------------------------------

import numpy
import sys

import file_utils
import ncgs_files
import ncts_files
import ncps_files
import rti_files
import rts_files
import text_ts_files

# import text_ps_files  # (not written yet)

#-------------------------------------------------------------------
def check_nio():

    #---------------------------------------------------
    # Try to import the Nio module from PyNIO package.
    #---------------------------------------------------
    # (1/26/12) Moved this here to avoid printing
    # these messages multiple times.  It should be
    # called at beginning of open_output_files() in
    # each component.
    #---------------------------------------------------
    try:
        import Nio  # (a module in the PyNIO package) 
        print 'Imported Nio version: ' + Nio.__version__
    except:
        python_version = sys.version[:3]
        print ' '
        print 'SORRY, Cannot write netCDF files because'
        print 'the "Nio" package cannot be imported.'
        print ' '
        if (python_version != '2.6'):
            print 'Note that "PyNIO" is only installed for'
            print 'Python version 2.6 on "beach".'
            print 'The current Python version is:', python_version

#   check_nio()
#-------------------------------------------------------------------
def get_nio_type_map():

    #----------------------------------------
    # Possible settings for "nio_type_code"
    #-------------------------------------------
    # nio_type_code = "d"  # (double, Float64)
    # nio_type_code = "f"  # (float,  Float32)
    # nio_type_code = "l"  # (long,   Int64)
    # nio_type_code = "i"  # (int,    Int32)
    # nio_type_code = "h"  # (short,  Int16)
    # nio_type_code = "b"  # (byte,   Int8)
    # nio_type_code = "S1" # (char)
    #---------------------------------------------
    # Only unsigned 8-bit integers are supported
    # in some versions of PyNio. See here:
    #   http://www.pyngl.ucar.edu/User_forum/
    #   Archives/2010/0129.html  (1/26/12)
    # But that is what we want for D8 codes.
    #---------------------------------------------
    nio_type_map = {'float64':'d', 'float32':'f',
                    'int64':'l', 'int32':'i',
                    'int16':'s',
                    'int8':'b',    ## (may not work, 1/26/12)
                    'uint8':'b',   ## (see notes above) 
                    'S|100':'S1'}  ## (check this)                      

    return nio_type_map

#   get_nio_type_map()
#-------------------------------------------------------------------
def open_new_gs_file(self, file_name, info=None,
                     var_name='X',
                     long_name='Unknown',
                     units_name='None',
                     dtype='float32',
                     time_units='minutes',
                     nx=None, ny=None, dx=None, dy=None):

    #---------------------------
    # Was grid info provided ?
    #---------------------------
    if (info != None):
        info.file_name = file_name
        info.data_type = rti_files.get_rti_data_type( dtype )
        if (nx != None): info.ncols = nx
        if (ny != None): info.nrows = ny
        if (dx != None): info.xres  = dx
        if (dy != None): info.yres  = dy
    else:
        if (nx != None) and (ny != None) and \
           (dx != None) and (dy != None):
            info = rti_files.make_info( file_name, nx, ny, dx, dy )
        else:
            print 'ERROR during open_new_gs_file().'
            print '      Grid info not provided.'
            print ' '
            ## return -1
        
    #---------------------------------
    # Build strings to be used below 
    #---------------------------------
    ncgs_unit_str = "self." + var_name + "_ncgs_unit"
    ncgs_file_str = "self." + var_name + "_ncgs_file"
    gs_file_str   = "self." + var_name + "_gs_file"
    #-------------------
    # For testing only
    #-------------------
    # print 'ncgs_unit_str =', ncgs_unit_str
    # print 'ncgs_file_str =', ncgs_file_str
    # print 'gs_file_str   =', gs_file_str
    # print 'var_name      =', var_name
    # print 'long_name     =', long_name
    # print 'units_name    =', units_name
    # print 'time_units    =', time_units
    # print ' '

    #--------------------------------------------
    # Open new netCDF file to write grid stacks
    # using var_name to build variable names
    #--------------------------------------------
    # Note that "dtype" was not included in the
    # last TopoFlow version (always float32),
    # but Erode needs other types.
    #--------------------------------------------
    try:
        exec( ncgs_file_str + "= file_utils.replace_extension(" +
              gs_file_str + ", '.nc')" )
        exec( ncgs_unit_str + "=" + "ncgs_files.ncgs_file()" )
        exec( ncgs_unit_str + ".open_new_file(" + ncgs_file_str +
              ", self.rti, var_name, long_name, units_name, " +
              "dtype=dtype, " +
              "time_units=time_units)" )
        MAKE_RTS = False
    except:
        print 'ERROR: Unable to open new netCDF file:'
        exec( "print '      '," + ncgs_file_str )
        print ' '
        print 'Will write grid stack in generic RTS format.'
        print ' '
        MAKE_RTS = True

    #-------------------------------------------
    # Always save grid stacks in an RTS file ?
    #--------------------------------------------------
    # Note that if PyNIO is missing, we don't get
    # an exception above and MAKE_RTS is still False.
    #--------------------------------------------------
    MAKE_RTS = True   #####
##    print '#################################'
##    print 'MAKE_RTS =', MAKE_RTS
##    print '#################################'
    
    #---------------------------------
    # Build strings to be used below 
    #---------------------------------
    rts_unit_str = "self." + var_name + "_rts_unit"
    rts_file_str = "self." + var_name + "_rts_file"
    gs_file_str  = "self." + var_name + "_gs_file"

    #------------------------------------------
    # Open new RTS files to write grid stacks
    #------------------------------------------
    if (MAKE_RTS):
        try:
            exec( rts_file_str + "= file_utils.replace_extension(" +
                  gs_file_str + ", '.rts')" )
            exec( rts_unit_str + " = rts_files.rts_file()" )
            exec( rts_unit_str + ".open_new_file(" + rts_file_str +
                  ", self.rti, var_name, " +
                  "dtype=dtype, " +
                  "MAKE_BOV=True)" )
        except:
            print 'ERROR: Unable to open new RTS file:'
            exec( "print '      '," + rts_file_str )
            # exec( "print '      ', self." + var_name + "_rts_file" )
            print ' '
    
#   open_new_gs_file()
#-------------------------------------------------------------------
def add_grid(self, var, var_name, time=None, SILENT=True):
             ## USE_NC=True, USE_RTS=False ):

    #--------------------------------------------------------
    # Note: Each of these "add_grid()" methods must check
    #       to see if var is actually a scalar and, if so,
    #       convert it to a grid by adding a grid of zeros.
    #--------------------------------------------------------
##    ncgs_unit_str = "self." + var_name + "_ncgs_unit"
##    exec( ncgs_unit_str + ".add_grid( var, var_name, time )")
    
    ## if (USE_NC):
    try:
        ncgs_unit_str = "self." + var_name + "_ncgs_unit"
        exec( ncgs_unit_str + ".add_grid( var, var_name, time )")
    except:
        if not(SILENT):
            print 'ERROR: Unable to add grid to netCDF file.'

    ## if (USE_RTS):
    try:
        rts_unit_str = "self." + var_name + "_rts_unit"
        exec( rts_unit_str + ".add_grid( var )" )
    except:
        pass
        ## print 'ERROR: Unable to add grid to RTS file.'

#   add_grid()
#-------------------------------------------------------------------
def close_gs_file(self, var_name): 

    try:
        exec( "self." + var_name + "_ncgs_unit.close()" )
    except:
        pass

    try:
        exec( "self." + var_name + "_rts_unit.close()" )
    except:
        pass
    
#   close_gs_file()
#-------------------------------------------------------------------
#-------------------------------------------------------------------
def open_new_ts_file(self, file_name, IDs, ####
                     var_name='X',
                     long_name='Unknown',
                     units_name='None',
                     dtype='float32',
                     time_units='minutes'):

    #----------------------------------
    # Build lists for var_names, etc.
    #----------------------------------
    n_IDs = numpy.size(IDs[0])
    var_names   = []
    long_names  = []
    units_names = []
    rows        = IDs[0]
    cols        = IDs[1]
    for k in xrange(n_IDs):
        #----------------------------------------
        # Construct var_name of form:  Q[24,32]
        # or, if necessary, Q_24_32
        #----------------------------------------
        row_str  = '_' + str(rows[k])
        col_str  = '_' + str(cols[k])
        #------------------------------------------------
        # Must match with ncts_files.add_values_add_IDs
        #------------------------------------------------
##        row_str = '[' + str(rows[k]) + ','
##        col_str = str(cols[k]) + ']'            
        vname = var_name + row_str + col_str
        var_names.append( vname )
        long_names.append( long_name )
        units_names.append( units_name )
    
    #--------------------------------------------
    # Open new netCDF file to write time series
    # using var_name to build variable names
    #--------------------------------------------
    try:
        ncts_unit_str = "self." + var_name + "_ncts_unit"
        ncts_file_str = "self." + var_name + "_ncts_file"
        ts_file_str   = "self." + var_name + "_ts_file"
        exec( ncts_file_str + "= file_utils.replace_extension(" +
              ts_file_str + ", '.nc')" )
        exec( ncts_unit_str + "=" + "ncts_files.ncts_file()" )
        exec( ncts_unit_str + ".open_new_file(" + ncts_file_str +
              ", var_names, long_names, units_names," +
              "dtype=dtype, " +  ## (11/5/13)
              "time_units=time_units)" )
        MAKE_TTS = False
    except:
        print 'ERROR: Unable to open new netCDF file:'
        exec( "print '      ', self." + var_name + "_ncts_file" )
        print ' '
        print 'Will write time series to multi-column text file.'
        print ' '
        MAKE_TTS = True

    #-------------------------------------------
    # Always save time series in a text file ?
    #-------------------------------------------
    MAKE_TTS = True   ###########
    
    #------------------------------------------
    # Open new text file to write time series
    #------------------------------------------
    if (MAKE_TTS):
        try:
			tts_unit_str = "self." + var_name + "_tts_unit"
			tts_file_str = "self." + var_name + "_tts_file"
			ts_file_str  = "self." + var_name + "_ts_file"
			exec( tts_file_str + "= file_utils.replace_extension(" +
				  ts_file_str + ", '.txt')" )
			exec( tts_unit_str + " = text_ts_files.ts_file()" )
			exec( tts_unit_str + ".open_new_file(" + tts_file_str +
				  ", var_names, " +
				  "dtype=dtype, " +  ## (11/5/13)
				  "time_units=time_units)" )
        except:
            print 'ERROR: Unable to open new text file:'
            exec( "print '      ', self." + var_name + "_tts_file" )
            print ' '
    
#   open_new_ts_file()
#-------------------------------------------------------------------
def add_values_at_IDs(self, time_min, var, var_name, IDs):

##    ncts_unit_str = "self." + var_name + "_ncts_unit"   
##    exec( ncts_unit_str + ".add_values_at_IDs( time_min, var, var_name, IDs )")
              
    try:
        ncts_unit_str = "self." + var_name + "_ncts_unit"   
        exec( ncts_unit_str + ".add_values_at_IDs( time_min, var, var_name, IDs )")
    except:
        pass
        #------------------------------------------------
        # Don't want to print this every time.
        # Could use "self.SAVE_CDF = False" to disable.
        #------------------------------------------------
        # print 'ERROR: Unable to add values to netCDF file.'

    try:
        tts_unit_str = "self." + var_name + "_tts_unit"
        exec( tts_unit_str + ".add_values_at_IDs( time_min, var, IDs )" )
    except:
        pass
        #------------------------------------------------
        # Don't want to print this every time.
        # Could use "self.SAVE_CDF = False" to disable.
        #------------------------------------------------
        # print 'ERROR: Unable to add values to text file.'
    

#   add_values_at_IDs()
#-------------------------------------------------------------------
##def add_values(self, prefix, values, var_names, time_min):
##
##    try:
##        ncts_unit_str = "self." + prefix + "_ncts_unit"   
##        exec( ncts_unit_str + ".add_values( time_min, values, var_names )")
##    except:
##        print 'ERROR: Unable to add values to netCDF file.'
##
##    try:
##        tts_unit_str = "self." + prefix + "_tts_unit"
##        exec( tts_unit_str + ".add_values( time_min, values )" )
##    except:
##        print 'ERROR: Unable to add values to text file.'
##    
##
###   add_values()
#-------------------------------------------------------------------
def close_ts_file(self, var_name):

    try:
        exec( "self." + var_name + "_ncts_unit.close()" )
    except:
        pass

    try:
        exec( "self." + var_name + "_tts_unit.close()" )
    except:
        pass

#   close_ts_file()
#-------------------------------------------------------------------
#-------------------------------------------------------------------
def open_new_ps_file(self, file_name, IDs, ####
                     z_values=numpy.arange(10),
                     z_units='m',
                     var_name='X',
                     long_name='Unknown',
                     units_name='None',
                     dtype='float32',
                     time_units='minutes'):

    #----------------------------------
    # Build lists for var_names, etc.
    #----------------------------------
    n_IDs = numpy.size(IDs[0])
    var_names   = []
    long_names  = []
    units_names = []
    rows        = IDs[0]
    cols        = IDs[1]
    for k in xrange(n_IDs):
        #----------------------------------------
        # Construct var_name of form:  Q[24,32]
        # or, if necessary, Q_24_32
        #----------------------------------------
        row_str  = '_' + str(rows[k])
        col_str  = '_' + str(cols[k])
        #--------------------------------------------------
        # Must match with ncps_files.add_profiles_add_IDs
        #--------------------------------------------------
##        row_str = '[' + str(rows[k]) + ','
##        col_str = str(cols[k]) + ']'

        vname = var_name + row_str + col_str
        var_names.append( vname )
        long_names.append( long_name )
        units_names.append( units_name )
    
    #--------------------------------------------
    # Open new netCDF file to write time series
    # using var_name to build variable names
    #--------------------------------------------
    try:
        ncps_unit_str = "self." + var_name + "_ncps_unit"
        ncps_file_str = "self." + var_name + "_ncps_file"
        ps_file_str   = "self." + var_name + "_ps_file"
        exec( ncps_file_str + "= file_utils.replace_extension(" +
              ps_file_str + ", '.nc')" )
        exec( ncps_unit_str + "=" + "ncps_files.ncps_file()" )
        exec( ncps_unit_str + ".open_new_file(" + ncps_file_str +
              ", z_values, z_units" +
              ", var_names, long_names, units_names," +
              "dtype=dtype, " +  ## (11/5/13)
              "time_units=time_units)" )
        MAKE_TPS = False
    except:
        # pass
        print 'ERROR: Unable to open new netCDF file:'
        exec( "print '      ', self." + var_name + "_ncps_file" )
        print ' '
##        print 'Will write profile series to text file.'
##        print ' '
##        MAKE_TPS = True

    #-------------------------------------------
    # Always save time series in a text file ?
    #-------------------------------------------
    ## MAKE_TPS = True   ###########
    
    #------------------------------------------
    # Open new text file to write time series
    #------------------------------------------
##    if (MAKE_TPS):
##        try:
##            tps_unit_str = "self." + var_name + "_tps_unit"
##            tps_file_str = "self." + var_name + "_tps_file"
##            ps_file_str  = "self." + var_name + "_ps_file"
##            exec( tps_file_str + "= file_utils.replace_extension(" +
##                  ps_file_str + ", '.txt')" )
##            exec( tps_unit_str + " = text_ps_files.ps_file()" )
##            exec( tps_unit_str + ".open_new_file(" + tps_file_str +
##                  ", var_names, " +
##                  "dtype=dtype, " +
##                  "time_units=time_units)" )
##        except:
##            print 'ERROR: Unable to open new text file:'
##            exec( "print '      ', self." + var_name + "_tps_file" )
##            print ' '
    
#   open_new_ps_file()
#-------------------------------------------------------------------
def add_profiles_at_IDs(self, var, var_name, IDs, time_min):

    ncps_unit_str = "self." + var_name + "_ncps_unit"   
    exec( ncps_unit_str + ".add_profiles_at_IDs( var, var_name, IDs, time_min )")
        
##    try:
##        ncps_unit_str = "self." + var_name + "_ncps_unit"   
##        exec( ncps_unit_str + ".add_profiles_at_IDs( var, var_name, IDs, time_min )")
##    except:
##        print 'ERROR: Unable to add profiles to netCDF file.'

##    try:
##        tps_unit_str = "self." + var_name + "_tps_unit"
##        exec( tps_unit_str + ".add_profiles_at_IDs( var, IDs, time_min )" )
##    except:
##        print 'ERROR: Unable to add profiles to text file.'
    

#   add_profiles_at_IDs()
#-------------------------------------------------------------------
##def add_profiles(self, prefix, values, var_names, time_min):
##
##    try:
##        ncps_unit_str = "self." + prefix + "_ncps_unit"   
##        exec( ncps_unit_str + ".add_profiles( values, var_names, time_min )")
##    except:
##        print 'ERROR: Unable to add profiles to netCDF file.'
##
##    try:
##        tps_unit_str = "self." + prefix + "_tps_unit"
##        exec( tps_unit_str + ".add_profiles( values, time_min )" )
##    except:
##        print 'ERROR: Unable to add profiles to text file.'
##    
##
###   add_profiles()
#-------------------------------------------------------------------
def close_ps_file(self, var_name):

    try:
        exec( "self." + var_name + "_ncps_unit.close()" )
    except:
        pass

##    try:
##        exec( "self." + var_name + "_tps_unit.close()" )
##    except:
##        pass

#   close_ps_file()
#-------------------------------------------------------------------    
#-------------------------------------------------------------------
def open_new_cs_file(self, file_name, info=None,
                     var_name='X',
                     long_name='Unknown',
                     units_name='None',
                     dtype='float32',
                     time_units='minutes',
                     nx=None, ny=None, dx=None, dy=None):

    #---------------------------
    # Was grid info provided ?
    #---------------------------
    if (info != None):
        info.file_name = file_name
        info.data_type = rti_files.get_rti_data_type( dtype )
        if (nx != None): info.ncols = nx
        if (ny != None): info.nrows = ny
        if (dx != None): info.xres  = dx
        if (dy != None): info.yres  = dy
    else:
        if (nx != None) and (ny != None) and \
           (dx != None) and (dy != None):
            info = rti_files.make_info( file_name, nx, ny, dx, dy )
        else:
            print 'ERROR during open_new_cs_file().'
            print '      Grid info not provided.'
            print ' '
            ## return -1
        
    #--------------------------------------------
    # Open new netCDF file to write curbe stacks
    # using var_name to build variable names
    #--------------------------------------------
    try:
        nccs_unit_str = "self." + var_name + "_nccs_unit"
        nccs_file_str = "self." + var_name + "_nccs_file"
        cs_file_str   = "self." + var_name + "_cs_file"
            
        exec( nccs_file_str + "= file_utils.replace_extension(" +
              cs_file_str + ", '.nc')" )
        exec( nccs_unit_str + "=" + "nccs_files.nccs_file()" )
        exec( nccs_unit_str + ".open_new_file(" + nccs_file_str +
              ", self.rti, var_name, long_name, units_name, " +
              "dtype=dtype, " +  ## (11/5/13)
              "time_units=time_units)" )
        MAKE_RT3 = False
    except:
        print 'ERROR: Unable to open new netCDF file:'
        exec( "print '      ', self." + var_name + "_nccs_file" )
        print ' '
        print 'Will write cube stack in generic RT3 format.'
        print ' '
        MAKE_RT3 = True

    #-------------------------------------------
    # Always save cube stacks in an RT3 file ?
    #-------------------------------------------
    # MAKE_RT3 = True   #####
    
    #------------------------------------------
    # Open new RTS files to write grid stacks
    #------------------------------------------
##    if (MAKE_RT3):
##        try:
##            rt3_unit_str = "self." + var_name + "_rt3_unit"
##            rt3_file_str = "self." + var_name + "_rt3_file"
##            cs_file_str  = "self." + var_name + "_cs_file"
##            
##            exec( rt3_file_str + "= file_utils.replace_extension(" +
##                  cs_file_str + ", '.rt3')" )
##            exec( rt3_unit_str + " = rt3_files.rt3_file()" )
##            exec( rt3_unit_str + ".open_new_file(" + rt3_file_str +
##                  ", self.rti, var_name, " +
##                  "dtype=dtype, " +
##                  "MAKE_BOV=True)" )
##        except:
##            print 'ERROR: Unable to open new RT3 file:'
##            exec( "print '      ', self." + var_name + "_rt3_file" )
##            print ' '
    
#   open_new_gs_file()
#-------------------------------------------------------------------
def add_cube(self, var, var_name, time=None):
             ## USE_NC=True, USE_RT3=False ):

    #--------------------------------------------------------
    # Note: Each of these "add_cube()" methods must check
    #       to see if var is actually a scalar and, if so,
    #       convert it to a grid by adding a grid of zeros.
    #--------------------------------------------------------
##    nccs_unit_str = "self." + var_name + "_nccs_unit"
##    exec( nccs_unit_str + ".add_cube( var, var_name, time )")
    
    ## if (USE_NC):
    try:
        nccs_unit_str = "self." + var_name + "_nccs_unit"
        exec( nccs_unit_str + ".add_grid( var, var_name, time )")
    except:
        pass
        #------------------------------------------------
        # Don't want to print this every time.
        # Could use "self.SAVE_CDF = False" to disable.
        #------------------------------------------------
        # print 'ERROR: Unable to add cube to netCDF file.'

    ## if (USE_RT3):
    try:
        rt3_unit_str = "self." + var_name + "_rt3_unit"
        exec( rt3_unit_str + ".add_cube( var )" )
    except:
        pass
        ## print 'ERROR: Unable to add cube to RT3 file.'

#   add_cube()
#-------------------------------------------------------------------
def close_cs_file(self, var_name): 

    try:
        exec( "self." + var_name + "_nccs_unit.close()" )
    except:
        pass

    try:
        exec( "self." + var_name + "_rt3_unit.close()" )
    except:
        pass
    
#   close_cs_file()
#-------------------------------------------------------------------

