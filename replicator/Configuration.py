#    File:    Configuration.py
#    Author:  Marvin Smith
#  
__author__ = 'Marvin Smith'


#  Python Libraries
import argparse, configparser, logging

class Reposync_Config(object):

    #  Name of command
    cmd_name = None


    def __init__(self, cmd_name, cmd_args = None):

        #  Set the command name
        self.cmd_name = cmd_name

        self.cmd_args = cmd_args

    def Build_Command(self, repo_name, repo_sync_directory  ):

        cmd_args = ''
        if self.cmd_args is not None:
            cmd_args = self.cmd_args

        #  Return output
        output = self.cmd_name + ' ' + cmd_args + ' -r ' + repo_name + ' -p ' + repo_sync_directory

        return output

class Configuration(object):

    #  Command-Line Options
    cmd_options = None

    #  Command-Line Parser
    cmd_parser = None

    #  Config-File Options
    cfg_options = None

    #  Global Options
    values = {}

    #  Repo Sync Config Settings
    reposync_config = None


    def __init__(self):


        #  Parse the command-line options
        self.Parse_Command_Line()

        #  Parse the configuration file
        self.Parse_Configuration_File()

        #  Configure Logging
        self.Configure_Logging()


    def Parse_Command_Line(self):

        #  Open the command line
        self.cmd_parser = argparse.ArgumentParser(description='Replicate remote yum repos for offline use.')


        #  Add the configuration file pathname
        self.cmd_parser.add_argument('-c','--config-pathname',
                                 dest='config_pathname',
                                 default='options.cfg',
                                 required=False,
                                 help='Configuration file path.')
        
        #  Build Repo Config
        self.cmd_parser.add_argument('-b','--build-default-repolist',
                                 dest='build_repolist',
                                 default=False,
                                 action='store_true',
                                 help='Flag if you want to construct the repo config file.')

        #  Repo config
        self.cmd_parser.add_argument('-r','--repolist',
                                 dest='repo_config_path',
                                 default='repolist.csv',
                                 required=False,
                                 help='Path to repo config path.')

        #  Do a Dry Run
        self.cmd_parser.add_argument('--dry-run',
                                     dest='dry_run',
                                     default=False,
                                     action='store_true',
                                     help='Print only the shell commands to execute. Do not actually run.')

        #  Parse the auments
        self.cmd_options = self.cmd_parser.parse_args()


    def Parse_Configuration_File(self):

        #  Create config parser
        self.cfg_options = configparser.ConfigParser()

        #  Read file
        self.cfg_options.read(self.cmd_options.config_pathname)

        #  Flag if we want to just build the repolist
        self.values['BUILD_REPOLIST'] = self.cmd_options.build_repolist

        #  Repo config path
        self.values['REPO_CONFIG_PATH'] = self.cmd_options.repo_config_path

        #  Define the Synchronization Directory
        self.values['SYNC_DIRECTORY'] = self.cfg_options.get('general','SYNC_DIRECTORY')

        #  Define the Log Level
        self.values['LOG_LEVEL'] = getattr(logging,self.cfg_options.get('logging','log_level'))


        #  Create reposync config object
        self.reposync_config = Reposync_Config(cmd_name=self.cfg_options.get('general', 'REPO_SYNC_COMMAND'),
                                               cmd_args=self.cfg_options.get('general', 'REPO_SYNC_ARGS'))


    def Configure_Logging(self):

        #  Get the log level
        logging.basicConfig(level=self.values['LOG_LEVEL'])

