__author__ = 'ms6401'


#  Python Libraries
import csv

#  Project Libraries
from .Utilities import Run_Command

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


class Repo_Manager(object):

    #  Repositories
    repos = []

    def __init__(self,options):


        #  Flag if we want to write the repolist
        if options.values['BUILD_REPOLIST'] is True:
            self.Build_Repo_Config( options.values['REPO_CONFIG_PATH'] )
        
        
        #  Get list of repositories
        else:    
            self.repos = self.Load_Repositories( options.values['REPO_CONFIG_PATH'] )


    def Load_Repositories(self, repo_config_path):
        
        #  Create output repo list
        repos = []
        
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
        arch = 'all'
        enabled = False
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
            comps = pline.split()
            
            #  Add the name of the repo
            repos.append(Yum_Repo( comps[0], arch, enabled ))


        #  Create CSV File
        with open( repo_config_path, 'w' ) as csvfile:

            #  Write the header
            csvfile.write('Repo Name,Architecture,Enabled\n')

            #  Write each line
            for repo in repos:
                csvfile.write( repo.name + ',' + str(repo.arch) + ',' + str(repo.enabled) + "\n")

