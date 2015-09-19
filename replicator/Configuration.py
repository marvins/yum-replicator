__author__ = 'ms6401'


#  Python Libraries
import argparse, configparser

class Configuration(object):

    #  Command-Line Options
    cmd_options = None

    #  Config-File Options
    cfg_options = None

    #  Global Options
    values = {}


    def __init__(self):


        #  Parse the command-line options
        self.Parse_Command_Line()

        #  Parse the configuration file
        self.Parse_Configuration_File()


    def Parse_Command_Line(self):

        #  Open the command line
        cmd_options = argparse.ArgumentParser(description='Replicate remote yum repos for offline use.')


        #  Add the configuration file pathname
        cmd_options.add_argument('-c','--config-pathname',
                                 dest='config_pathname',
                                 default='options.cfg',
                                 required=False,
                                 help='Configuration file path.')


        #  Parse the auments
        self.cmd_options = cmd_options.parse_args()


    def Parse_Configuration_File(self):

        #  Create config parser
        self.cfg_options = configparser.ConfigParser()

        #  Read file
        self.cfg_options.read(self.cmd_options.config_pathname)
