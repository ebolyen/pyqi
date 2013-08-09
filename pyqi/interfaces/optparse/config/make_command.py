#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, The BiPy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

__author__ = "Daniel McDonald"
__copyright__ = "Copyright 2013, The pyqi project"
__credits__ = ["Daniel McDonald", "Greg Caporaso", "Doug Wendel",
               "Jai Ram Rideout"]
__license__ = "BSD"
__version__ = "0.1.0-dev"
__maintainer__ = "Daniel McDonald"
__email__ = "mcdonadt@colorado.edu"

from pyqi.core.interfaces.optparse import (OptparseOption,
                                           OptparseResult,
                                           OptparseUsageExample)
from pyqi.core.interfaces.optparse.output_handler import write_string
from pyqi.commands.make_command import CommandConstructor

usage_examples = [
    OptparseUsageExample(ShortDesc="Basic Command",
                         LongDesc="Create a basic Command with appropriate attribution",
                         Ex='%prog -n example -a "some author" -c "Copyright 2013, The pyqi project" -e "foo@bar.com" -l BSD --command-version "0.1" --credits "someone else","and another person" -o example.py')
]

inputs = [
    OptparseOption(Parameter=CommandConstructor.Parameters['name'],
                   ShortName='n'),
    OptparseOption(Parameter=CommandConstructor.Parameters['email'],
                   ShortName='e'),
    OptparseOption(Parameter=CommandConstructor.Parameters['author'],
                   ShortName='a'),
    OptparseOption(Parameter=CommandConstructor.Parameters['license'],
                   ShortName='l'),
    OptparseOption(Parameter=CommandConstructor.Parameters['copyright'],
                   ShortName='c'),
    OptparseOption(Parameter=CommandConstructor.Parameters['command_version']),
    OptparseOption(Parameter=CommandConstructor.Parameters['credits']),
    OptparseOption(Parameter=None,
                   InputType='new_filepath',
                   ShortName='o',
                   Name='output-fp',
                   Required=True,
                   Help='output filepath to store generated Python code')
]

outputs = [
    OptparseResult(ResultKey='result',
                   OutputHandler=write_string,
                   OptionName='output-fp')
]
