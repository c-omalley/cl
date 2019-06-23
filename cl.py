# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# File: cl.py
#
# Process script flags, options, and arguments.
# See https://en.wikipedia.org/wiki/Command-line_interface#Arguments
#
# Here is an example of a script being called from the command line
# in a Windows environment using terminology of this module:
#
# C:> python myscript.py   -r       -f    infile.txt   args for script...
#            -----------   --       --    ----------   ------------------
#             <script>   <flag>  <option>     |           <arguments>
#                                       <option value>
#
# This module also performs automatic glob expasion of script arguments
# for the Windows environment.
#
# Here's an illustration of why globbing is handy. Suppose you need a
# script to perform operations with all the CSVs in a folder:
#
#   C:\Geodata\Garber_Wellington> python csv2gdb.py *.csv
#
# This example only scatches the surface of globbing. Please see
# See https://en.wikipedia.org/wiki/Glob_(programming) for more
# details.
#----------------------------------------------------------------------

import os, sys

# Expose the module's interface
__all__ = ['script', 'folder', 'arguments', 'flag', 'option']

# The script name for utility
folder, script = os.path.split(sys.argv[0])

# Returns a copy of ARGUMENTS on non-Windows systems.
# Returns a glob expanded list of arguments on Windows.
def _glob_expand(arguments):
    if 'win32' in sys.platform:
        # Glob expansion is a rather convienient shorthand.
        # This is the most technichal portion of the module code and
        # is only performed on Windows (because other systems have
        # a "shell" that performs this for you automatically).
        from glob import glob
        glob_expanded_arguments = []
        for arg in arguments:
            # This is a really coarse approach. Basically, try to
            # glob it. If it doesn't glob, treat it as a regular
            # string. This will not catch glob patterns that do not
            # have a match. (I.e. "*.pyc" --> "*.pyc" if there are
            # no matching *.pyc files.)
            globbed = glob(arg)
            if globbed:
                # Glob successfull, add results
                glob_expanded_arguments += glob(arg)
            else:
                # Glob returned nothing, copy argument as-is
                # As stated above, this is less-than-perfect in
                # situations where globbing is intended but does
                # not match anything.
                glob_expanded_arguments += [arg]
        return glob_expanded_arguments
    else:
        return arguments

# Get a copy of the command line. This holds the remaining command line
# arguments after processing options and flags.
arguments = _glob_expand(sys.argv[1:])  # Will be modified!
_original_arguments = arguments.copy()  # For searching, Read-only!

# Grab a flag from the command line. Returns True if the flag is present,
# False if it is not.
def flag(name):
    global arguments
    try:
        _original_arguments.index(name) # ValueError likely
        # Avoid error in case the same flag is asked for more than once
        if name in arguments:
            arguments.remove(name)
        return True
    except ValueError:
        # ValueError: flag not found
        return False

# Grab a script option from the command line and return its value.
#
# If the option is not found, DEFAULT or None will be returned.
#
# If the option is found, but it's corresponding value is missing,
# MISSING or an empty string will be returned.
#
# In this manner, if the requested option is not on the command line
# or the option's value is missing, option() evaluates as False.
#
# Optionally, CONVERT is a conversion function that will be applied
# to the option value (string natively and by default).
def option(name, default=None, missing='', convert=str):
    global arguments
    try:
        i = _original_arguments.index(name) # ValueError likely
        if name in arguments:
            arguments.remove(name)
        value = _original_arguments[i + 1]  # IndexError possible
        if value in arguments:
            arguments.remove(value)
        return convert(value)               # Potential conversion error
    except ValueError:
        # ValueError: Option not found
        return default
    except IndexError:
        # IndexError: Option's argument is missing
        return missing
