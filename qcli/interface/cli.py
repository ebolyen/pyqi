#!/usr/bin/env python

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2013, The QIIME Project"
__credits__ = ["Greg Caporaso", "Daniel McDonald", "Doug Wendel",
                       "Jai Ram Rideout"]
__license__ = "GPL"
__version__ = "0.1.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"

from qcli.interface.core import Interface
from qcli.interface.factory import general_factory
from qcli.exception import IncompetentDeveloperError
from qcli.command.core import Parameter

class CLOption(Parameter):
    def __init__(self, Type, Help, Name, LongName, CLType, CLAction='store',
                 Required=False, Default=None, DefaultDescription=None,
                 ShortName=None):
        self.LongName = LongName
        self.CLType = CLType
        self.CLAction = CLAction
        self.ShortName = ShortName
        
        super(CLOption,self).__init__(Type=Type,Help=Help,Name=Name,Required=Required,Default=Default,DefaultDescription=DefaultDescription)
        
        if LongName != self.Name:
            self.DepWarn = "parameter %s will be renamed %s in QIIME 2.0.0" % (self.LongName, self.Name)
        else:
            self.DepWarn = ""

    def __str__(self):
        return '-%s/--%s' % (self.ShortName, self.LongName)
        
    @classmethod
    def fromParameter(cls, parameter, LongName, CLType, CLAction='store',
                      ShortName=None):
        result = cls(Type=parameter.Type,
                     Help=parameter.Help,
                     Name=parameter.Name,
                     Required=parameter.Required,
                     LongName=LongName,
                     CLType=CLType,
                     CLAction=CLAction,
                     Default=parameter.Default,
                     DefaultDescription=parameter.DefaultDescription,
                     ShortName=ShortName)
        return result

CLTypes = set(['float','int','string','existing_filepath', float, int, str])
CLActions = set(['store','store_true','store_false', 'append'])

class UsageExample(object):
    def __init__(self, ShortDesc=None, LongDesc=None, Ex=None):
        if ShortDesc is None:
            raise IncompetentDeveloperError("No short description provided!")
        if LongDesc is None:
            raise IncompetentDeveloperError("No long description provided!")
        if Ex is None:
            raise IncompetentDeveloperError("No example provided!")

        self.ShortDesc = ShortDesc
        self.LongDesc = LongDesc
        self.Ex = Ex

    def to_tuple(self):
        """Returns (short, long, ex)"""
        return (self.ShortDesc, self.LongDesc, self.Ex)

class ParameterConversion(object):
    def __init__(self, ShortName=None, LongName=None, CLType=None, 
                 CLAction=None):
        if ShortName is None:
            raise IncompetentDeveloperError("No short name provided!")
        if LongName is None:
            raise IncompetentDeveloperError("No long name provided!")
        if CLType not in CLTypes:
            raise IncompetentDeveloperError("Invalid CLType specified!")
        if CLAction is not None and CLAction not in CLActions:
            raise IncompetentDeveloperError("Invalid CLAction specified!")

        self.ShortName = ShortName
        self.LongName = LongName
        self.CLType = CLType
        self.CLAction = CLAction

    def to_dict(self):
        return {'short-name':self.ShortName,
                'long-name':self.LongName,
                'cl-type':self.CLType,
                'cl-action':self.CLAction}

class CLInterface(Interface):
    DisallowPositionalArguments = True
    HelpOnNoArguments = True 
    OptionalInputLine = '[] indicates optional input (order unimportant)'
    RequiredInputLine = '{} indicates required input (order unimportant)'
    
    def __init__(self, **kwargs):
        self.UsageExamples = []
        self.UsageExamples.extend(self._get_usage_examples())
        
        self.ParameterConversionInfo = {
                'verbose':ParameterConversion(ShortName='v',
                                              LongName='verbose',
                                              CLType=None,
                                              CLAction='store_true')
                }

        self.ParameterConversionInfo.update(self._get_param_conv_info())
    
        super(CLInterface, self).__init__(**kwargs)
        
        self.Options.extend(self._get_additional_options())

    def _get_param_conv_info(self):
        raise NotImplementedError("Must define _get_param_conv_info")
    
    def _get_usage_examples(self):
        raise NotImplementedError("Must define _get_usage_examples")
    
    def _get_additional_options(self):
        raise NotImplementedError("Must define _get_additional_options")

    def _the_in_validator(self, in_):
        if not isinstance(in_, list):
            raise IncompetentDeveloperError("The in_ validator is very upset.")

    def _option_factory(self, parameter):
        name = parameter.Name
        if name not in self.ParameterConversionInfo:
            raise IncompetentDeveloperError("YOU IIIIIDDIOT!")

        return CLOption.fromParameter(parameter, 
                     self.ParameterConversionInfo[name]['long-name'],
                     self.ParameterConversionInfo[name]['cl-type'],
                     self.ParameterConversionInfo[name]['short-name'])

    def _input_handler(self, in_, *args, **kwargs):
        """ Constructs the OptionParser object and parses command line arguments
        
            parse_command_line_parameters takes a dict of objects via kwargs which
             it uses to build command line interfaces according to standards 
             developed in the Knight Lab, and enforced in QIIME. The currently 
             supported options are listed below with their default values. If no 
             default is provided, the option is required.
            
            script_description
            script_usage = [("","","")]
            version
            required_options=None
            optional_options=None
            suppress_verbose=False
            disallow_positional_arguments=True
            help_on_no_arguments=True
            optional_input_line = '[] indicates optional input (order unimportant)'
            required_input_line = '{} indicates required input (order unimportant)'
            
           These values can either be passed directly, as:
            parse_command_line_parameters(script_description="My script",\
                                         script_usage=[('Print help','%prog -h','')],\
                                         version=1.0)
                                         
           or they can be passed via a pre-constructed dict, as:
            d = {'script_description':"My script",\
                 'script_usage':[('Print help','%prog -h','')],\
                 'version':1.0}
            parse_command_line_parameters(**d)
        
        """
        # command_line_text will usually be nothing, but can be passed for
        # testing purposes

        # Do we need this? Was used for testing
        #command_line_args = set_parameter('command_line_args',kwargs,None)

        required_opts = [opt for opt in self.Options if opt.Required]
        optional_opts = [opt for opt in self.Options if not opt.Required]
        
        # Build the usage and version strings
        usage = build_usage_lines(required_opts)
        version = 'Version: %prog ' + __version__

        # Instantiate the command line parser object
        parser = OptionParser(usage=usage, version=version)

        # What does this do?
        #parser.exit = set_parameter('exit_func',kwargs,parser.exit)
        
        # If no arguments were provided, print the help string (unless the
        # caller specified not to)

        # Need to figure out what to do with command_line_args
        #if self.HelpOnNoArguments and (not command_line_args) and len(argv) == 1:
        if self.HelpOnNoArguments and len(in_) == 1:
            parser.print_usage()
            return parser.exit(-1)

        # Process the required options
        if required_params:
            # Define an option group so all required options are
            # grouped together, and under a common header
            required = OptionGroup(parser, "REQUIRED options",
                "The following options must be provided under all circumstances.")
            for rp in required_params:
                # if the option doesn't already end with [REQUIRED], 
                # add it.
                if not rp.Help.strip().endswith('[REQUIRED]'):
                    rp.Help += ' [REQUIRED]'

                option = make_option('-' + rp.ShortName, '--' + rp.LongName, type=rp.CLType, help=rp.Help)
                required.add_option(option)
            parser.add_option_group(required)

        # Add the optional options
        for op in optional_params:
            help_text = '%s [default: %s]' % (op.Help, op.DefaultDescription)
            option = make_option('-' + op.ShortName, '--' + op.LongName, type=op.CLType,
                    help=help_text, default=op.Default)
            parser.add_option(option)
        
        # Parse the command line
        # command_line_text will None except in test cases, in which 
        # case sys.argv[1:] will be parsed

        # Need to figure out what to do with command_line_args
        #opts,args = parser.parse_args(command_line_args)
        opts,args = parser.parse_args(in_)
        
        # If positional arguments are not allowed, and any were provided,
        # raise an error.
        if self.DisallowPositionalArguments and len(args) != 0:
            parser.error("Positional argument detected: %s\n" % str(args[0]) +\
             " Be sure all parameters are identified by their option name.\n" +\
             " (e.g.: include the '-i' in '-i INPUT_DIR')")

        # Test that all required options were provided.
        if required_params:
            required_option_ids = [o.dest for o in required.option_list]
            for required_option_id in required_option_ids:
                if getattr(opts,required_option_id) == None:
                    return parser.error('Required option --%s omitted.' \
                                 % required_option_id)
                
        # Return the parser, the options, and the arguments. The parser is returned
        # so users have access to any additional functionality they may want at 
        # this stage -- most commonly, it will be used for doing custom tests of 
        # parameter values.
        return parser, opts, args

    def _output_handler(self, results):
        print results

    def getOutputFilepaths(results, **kwargs):
        mapping = {}

        for k,v in results.items():
            if isinstance(v, FilePath):
                output_fp = str(v)
            else:
                # figure out filepath
                pass

            mapping[k] = output_fp

        return mapping

# Fix this shit:
class CLCommandParser(object):
    DisallowPositionalArguments = True
    HelpOnNoArguments = True
    OptionalInputLine = '[] indicates optional input (order unimportant)'
    RequiredInputLine = '{} indicates required input (order unimportant)'

    def __init__(self):
        if len(self.UsageExamples) < 1:
            raise IncompetentDeveloperError("How the fuck do I use this "
                                            "command?")

    def getOutputFilepaths(results, **kwargs):
        raise NotImplementedError("All subclasses must implement "
                                  "getOutputFilepaths.")

def build_usage_lines(required_params, usage_examples, optional_input_line, 
                      required_input_line, long_description):
    """ Build the usage string from components """
    line1 = 'usage: %prog [options] ' + '{%s}' %\
     ' '.join(['%s %s' % (str(rp),rp.Name.upper())\
               for rp in required_params])
    
    formatted_usage_examples = []
    for title, description, command in usage_examples:
        title = title.strip(':').strip()
        description = description.strip(':').strip()
        command = command.strip()
        if title:
            formatted_usage_examples.append('%s: %s\n %s' %\
             (title,description,command))
        else:
            formatted_usage_examples.append('%s\n %s' % (description,command))
    
    formatted_usage_examples = '\n\n'.join(formatted_usage_examples)
    
    lines = (line1,
             '', # Blank line
             optional_input_line,
             required_input_line,
             '', # Blank line
             long_description,
             '', # Blank line
             'Example usage: ',\
             'Print help message and exit',
             ' %prog -h\n',
             formatted_usage_examples)
    
    return '\n'.join(lines)

def cli(command_constructor, usage_examples, param_conversions, added_options):
    """Command line interface factory
    
    command_constructor - a subclass of ``Command``
    usage_examples - usage examples for using ``command_constructor`` on via a
        command line interface.
    param_conversions - necessary conversion information to converting
        parameters to options.
    added_options - any additional options that are not defined by the 
        ``command_constructor``.
    """
    return general_factory(command_constructor, usage_examples, param_conversions,
                           added_options, CLInterface)

def clmain(cmd_constructor, local_argv):
    logger = logger_constructor()
    cmd = cmd_constructor()
    try:
        result = cmd(local_argv[1:])
    except Exception, e:
        # Possibly do *something*
        raise e
    #else:
    #    output_mapping = cmd.getOutputFilepaths(result, kwargs)
#
#        for k, v in result.items():
#            v.write(output_mapping[k])
#
    return 0

# def argv_to_kwargs(cmd, argv):
#     pass