#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, The BiPy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

__author__ = "Daniel McDonald"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Greg Caporaso", "Daniel McDonald", "Doug Wendel",
                       "Jai Ram Rideout"]
__license__ = "BSD"
__version__ = "0.1.0-dev"
__maintainer__ = "Daniel McDonald"
__email__ = "mcdonadt@colorado.edu"

from unittest import TestCase, main
from pyqi.interface.cli import OutputHandler, CLOption, UsageExample, \
        ParameterConversion, CLInterface, cli, clmain
from pyqi.core.exception import IncompetentDeveloperError
from pyqi.core.command import Command, Parameter

class OutputHandlerTests(TestCase):
    def test_init(self):
        # why...
        obj = OutputHandler('a','b')
        self.assertEqual(obj.OptionName, 'a')
        self.assertEqual(obj.Function, 'b')

class CLOptionTests(TestCase):
    def test_init(self):
        obj = CLOption('a','b','c','d',str)
        self.assertEqual(obj.Type, 'a')
        self.assertEqual(obj.Help, 'b')
        self.assertEqual(obj.Name, 'c')
        self.assertEqual(obj.LongName, 'd')
        self.assertEqual(obj.CLType, str)

    def test_str(self):
        obj = CLOption('a','b','c','d',str)
        exp = '--d'
        obs = str(obj)
        self.assertEqual(obs, exp)

        obj = CLOption('a','b','c','d',str, ShortName='e')
        exp = '-e/--d'
        obs = str(obj)
        self.assertEqual(obs, exp)

    def test_fromParameter(self):
        from pyqi.core.command import Parameter
        p = Parameter(Type='a',Help='b',Name='c',Required=False)
        obj = CLOption.fromParameter(p, LongName='d',CLType=str)
        self.assertEqual(obj.Type,'a')
        self.assertEqual(obj.Help,'b')
        self.assertEqual(obj.Name,'c')
        self.assertEqual(obj.Required,False)

class UsageExampleTests(TestCase):
    def test_init(self):
        obj = UsageExample(ShortDesc='a', LongDesc='b', Ex='c')
        self.assertEqual(obj.ShortDesc, 'a')
        self.assertEqual(obj.LongDesc, 'b')
        self.assertEqual(obj.Ex, 'c')

class ParameterConversionTests(TestCase):
    def test_init(self):
        obj = ParameterConversion('a',str,CLAction='store')
        self.assertEqual(obj.LongName, 'a')
        self.assertEqual(obj.CLType, str)
        self.assertEqual(obj.CLAction, 'store')

        self.assertRaises(IncompetentDeveloperError, ParameterConversion, 'a',
                          'not valid')

def oh(key, data, opt_value=None):
    return data * 2

class CLInterfaceTests(TestCase):
    def setUp(self):
        self.interface = fabulous()
    
    def test_init(self):
        self.assertRaises(NotImplementedError, CLInterface)

    def test_option_factory(self):
        obs = self.interface._option_factory(Parameter('a','b','c'))
        self.assertEqual(obs.Type, 'a')
        self.assertEqual(obs.Help, 'b')
        self.assertEqual(obs.Name, 'c')
        self.assertTrue(isinstance(obs, CLOption))

    def test_input_handler(self):
        # note the the argument is --a due to the parameter conversion c->a
        obs = self.interface._input_handler(['--a','foo'])
        self.assertEqual(sorted(obs.items()), [('a', 'foo'),('verbose',False)])

    def test_build_usage_lines(self):
        obs = self.interface._build_usage_lines([])
        self.assertEqual(obs, usage_lines)

    def test_output_handler(self):
        results = {'itsaresult':20} 
        self.interface._output_handler(results)
        self.assertEqual(results, {'itsaresult':40})

class GeneralTests(TestCase):
    def setUp(self):
        self.obj = cli(ghetto, [UsageExample('a','b','c')],
                       {'c':ParameterConversion('a',str)}, [], 
                       {'itsaresult':OutputHandler(OptionName=None,
                                              Function=oh)})

    def test_cli(self):
        # exercise it
        foo = self.obj()

    def test_clmain(self):
        # exercise it
        foo = clmain(self.obj, ['testing', '--a','bar'])
        
class ghetto(Command):
    def _get_parameters(self):
        return [Parameter(str,'b','c')]
    def run(self, **kwargs):
        return {'itsaresult':10}

class fabulous(CLInterface):
    CommandConstructor = ghetto
    def _get_param_conv_info(self):
        return {'c':ParameterConversion('a',str)}
    def _get_usage_examples(self):
        return [UsageExample('a','b','c')]
    def _get_additional_options(self):
        return []
    def _get_output_map(self):
        return {'itsaresult':OutputHandler(OptionName=None,
                                           Function=oh)}
usage_lines = """usage: %prog [options] {}

[] indicates optional input (order unimportant)
{} indicates required input (order unimportant)



Example usage: 
Print help message and exit
 %prog -h

a: b
 c"""
if __name__ == '__main__':
    main()