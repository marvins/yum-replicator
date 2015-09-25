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
        
        #  Build Repo Config
        cmd_options.add_argument('-b','--build-default-repolist',
                                 dest='build_repolist',
                                 default=False,
                                 action='store_true',
                                 help='Flag if you want to construct the repo config file.')

        #  Repo config
        cmd_options.add_argument('-r','--repolist',
                                 dest='repo_config_path',
                                 default='repolist.csv',
                                 required=False,
                                 help='Path to repo config path.')

        #  Parse the auments
        self.cmd_options = cmd_options.parse_args()


    def Parse_Configuration_File(self):

        #  Create config parser
        self.cfg_options = configparser.ConfigParser()

        #  Read file
        self.cfg_options.read(self.cmd_options.config_pathname)

        #  Flag if we want to just build the repolist
        self.values['BUILD_REPOLIST'] = self.cmd_options.build_repolist

        #  Repo config path
        self.values['REPO_CONFIG_PATH'] = self.cmd_options.repo_config_path


