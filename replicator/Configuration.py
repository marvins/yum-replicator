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
        output = self.cmd_name + ' ' + cmd_args + ' -r ' + repo_name + ' ' + repo_sync_directory

        return output

class Configuration(object):


    def __init__(self):

        #  Initialize Default Values
        self.Set_Defaults()

        #  Parse the command-line options
        self.Parse_Command_Line()

        #  Parse the configuration file
        self.Parse_Configuration_File()

        #  Configure Logging
        self.Configure_Logging()

    def Set_Defaults(self):

        #  Command-Line Options
        self.cmd_options = None

        #  Command-Line Parser
        self.cmd_parser = None

        #  Config-File Options
        self.cfg_options = None

        #  Global Options
        self.values = {}
        self.values['REPO_SPEC'] = {'WRITE_REPO_SPEC_FILES'    : False,
                                    'WRITE_REPO_COMPOSITE_SPEC': False }

        #  Repo Sync Config Settings
        reposync_config = None


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
                                 default=None,
                                 required=False,
                                 help='Path to repo config path.')

        self.cmd_parser.add_argument('-rf','--repolist-format',
                                     dest='repo_config_format',
                                     default=None,
                                     required=False,
                                     choices=['csv'],
                                     help='Type of Repo Config Format')

        #  Do a Dry Run
        self.cmd_parser.add_argument('--dry-run',
                                     dest='dry_run',
                                     default=False,
                                     action='store_true',
                                     help='Print only the shell commands to execute. Do not actually run.')

        #  Skip repository sync step
        self.cmd_parser.add_argument('--skip-reposync','-rs',
                                     dest='skip_reposync',
                                     default=False,
                                     action='store_true',
                                     help='Skip the repository sync step (reposync cmd)')

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
        self.values['REPO_CONFIG_PATH'] = self.cfg_options.get('repo-config','REPO_CONFIG_PATH')
        if self.cmd_options.repo_config_path is not None:
            self.values['REPO_CONFIG_PATH'] = self.cmd_options.repo_config_path

        #  Repo Config Format
        self.values['REPO_CONFIG_FORMAT'] = self.cfg_options.get('repo-config','REPO_CONFIG_FORMAT')
        if self.cmd_options.repo_config_format is not None:
            self.values['REPO_CONFIG_FORMAT'] = self.cmd_options.repo_config_format

        self.values['REPO_ACTIVATE_ENABLED_REPOS'] = self.cfg_options.getboolean('repo-config','ACTIVATE_ENABLED_REPOS')


        #  Define the Synchronization Directory
        self.values['SYNC_DIRECTORY'] = self.cfg_options.get('general','SYNC_DIRECTORY')


        #  Define the Log Level
        self.values['LOG_LEVEL'] = getattr(logging,self.cfg_options.get('logging','log_level'))


        #  Create reposync config object
        self.reposync_config = Reposync_Config(cmd_name=self.cfg_options.get('general', 'REPO_SYNC_COMMAND'),
                                               cmd_args=self.cfg_options.get('general', 'REPO_SYNC_ARGS'))

        #  Repo Spec Settings
        if self.cfg_options.has_option('repo-spec', 'WRITE_REPO_SPEC_FILES'):
            self.values['REPO_SPEC']['WRITE_REPO_SPEC_FILES'] = self.cfg_options.getboolean('repo-spec','WRITE_REPO_SPEC_FILES')
        if self.cfg_options.has_option('repo-spec', 'WRITE_REPO_COMPOSITE_SPEC'):
            self.values['REPO_SPEC']['WRITE_REPO_COMPOSITE_SPEC'] = self.cfg_options.getboolean('repo-spec','WRITE_REPO_COMPOSITE_SPEC')


    def Configure_Logging(self):

        #  Get the log level
        logging.basicConfig(level=self.values['LOG_LEVEL'])

