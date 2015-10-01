__author__ = 'ms6401'


#  Python Libraries
import csv, os, sys, logging

#  Project Libraries
from .Utilities import Run_Command


def Parse_Repo_Name(input_str):

    #  Check for /
    comps = str(input_str).split('/')

    #  Set the actual repo name
    repo_name = comps[0]

    #  Figure out if the second or third arg is the arch
    return repo_name


def str2bool( str_data ):
    
    if str_data.lower() in ['true','1', 'yes','enable','enabled']:
        return True
    return False


class Yum_Repo(object):

    #  Repo Name
    name = None

    #  Repo Arch
    arch = None

    #  Repo Enabled
    enabled = None

    def __init__(self, name, arch, enabled):
        
        #  Set the name
        self.name = name

        #  Set the architecture
        self.arch = arch

        #  Set the enable flag
        self.enabled = enabled

    def Sync_Repository(self, sync_directory, reposync_config):

        #  Check if the path exists
        if os.path.exists(sync_directory) is False:
            raise Exception('Sync directory does not exist (' + sync_directory + ')')


        #  Create Command to run
        cmd = reposync_config.Build_Command(repo_name=self.name,
                                            repo_sync_directory=sync_directory)

        #  Execute Command
        logging.info('Running: ' + cmd)
        output = Run_Command(cmd)
        logging.info('Result: ' + str(output))



class Repo_Manager(object):

    #  Repositories
    repos = []

    def __init__(self,options):


        #  Flag if we want to write the repolist
        if options.values['BUILD_REPOLIST'] is True:
            self.Build_Repo_Config( options.values['REPO_CONFIG_PATH'] )
        
        
        #  Get list of repositories
        else:    
            self.repos = self.Load_Repositories( options)


    def Load_Repositories(self, options):

        #  Grab the repo config path
        repo_config_path = options.values['REPO_CONFIG_PATH']

        #  Create output repo list
        repos = []

        #  Make sure the config file exists
        if os.path.exists(repo_config_path) is False:
            sys.stderr.write('Unable to file repo configuration file (' + repo_config_path + ')\n')
            options.cmd_parser.print_help()
            sys.exit(-1)


        #  Open the CSV File
        with open( repo_config_path, 'r') as csvfile:
            
            #  Create the csv file parser
            csvreader = csv.DictReader(csvfile)

            #  Parse the entries
            for entry in csvreader:

                #  Get the entries
                name = entry['Repo Name']
                arch = entry['Architecture']
                flag = str2bool(entry['Enabled'])

                #  Add the repo
                repos.append(Yum_Repo(name,arch,flag))


        #  Return the configured repositories
        return repos


    def Build_Repo_Config( self, repo_config_path ):

        
        #  Get list of repos on the system
        cmd_output = Run_Command('yum repolist all')

        
        #  Parse the output of the command
        output = cmd_output[0].split('\n')
        repo_contents = False

        # Define default values
        repos = []

        #  Iterate over lines
        for line in output:
            
            #  Check if we are at the repo listing
            if 'repo id' in line and 'status' in line:
                repo_contents = True
                continue
            
            #  Check if we are at the end of the output
            if 'repolist' in line:
                continue

            # Skip lines until we get to the repo listing
            if repo_contents != True:
                continue
            
            #  Prune the data
            pline = line.strip()
            if len(pline) <= 0:
                continue;

            #  Split
            repo_name = Parse_Repo_Name(pline.split()[0])
            arch = 'all'
            enabled = False

            #  Add the name of the repo
            repos.append(Yum_Repo( repo_name, arch, enabled ))


        #  Create CSV File
        with open( repo_config_path, 'w' ) as csvfile:

            #  Write the header
            csvfile.write('Repo Name,Architecture,Enabled\n')

            #  Write each line
            for repo in repos:
                csvfile.write( repo.name + ',' + str(repo.arch) + ',' + str(repo.enabled) + "\n")

