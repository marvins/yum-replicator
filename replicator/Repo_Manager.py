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
    
    #  Remove Leading !
    repo_name = repo_name.strip('!')

    #  Figure out if the second or third arg is the arch
    return repo_name

def Parse_Repo_Enable_State(input_str):

    comp = input_str.lower()

    #  Check for Disable/Enable
    if 'enabled' in comp:
        return True
    else:
        return False


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

        logging.debug('Building Repo Def. Name: ' + str(name) + ', Arch: ' + str(arch) + ', Enabled: ' + str(enabled))

        #  Set the name
        self.name = name

        #  Set the architecture
        self.arch = arch

        #  Set the enable flag
        self.enabled = enabled

    def Sync_Repository(self, sync_directory,
                        reposync_config,
                        dry_run = False,
                        gen_run_script_options = {},
                        skip_reposync = False ):


        #  Check if the path is root-relative
        abs_path = sync_directory
        if os.path.isabs(sync_directory) is False:

            #  If so, then make it absolute
            abs_path = os.path.abspath(sync_directory)

        #  Check if the path exists
        if os.path.exists(abs_path) is False:
            raise Exception('Sync directory does not exist (' + abs_path + ')')


        #  Create Command to run
        cmd = reposync_config.Build_Command(repo_name=self.name,
                                            repo_sync_directory=abs_path)

        #  Execute Command
        logging.info('Running: \n' + cmd)
        if dry_run is False and skip_reposync is False:
            output = Run_Command(cmd)
            logging.info('Result: ' + str(output))


        #  Add to the run script
        if self.enabled == True:
            if gen_run_script_options['ENABLED'] == True:
                with open(gen_run_script_options['PATH'], 'a') as fout:
                    fout.write(cmd + '\n')


    def Write_Spec(self, fout, base_url ):

        #  Create text
        output  = '[' + str(self.name) + ']\n'
        output += 'baseurl=file://' + base_url + '\n'

        fout.write(output)

    def ToString(self):
        
        output  = "Repo Name: " + self.name + ', Arch: ' + self.arch + ', Enabled: ' + str(self.enabled)
        return output


class Repo_Manager(object):

    #  Repositories
    repos = []

    def __init__(self,options):


        #  Flag if we want to write the repolist
        if options.values['BUILD_REPOLIST'] is True:
            self.Build_Repo_Config( options.values['REPO_CONFIG_PATH'],
                                    options.values['REPO_CONFIG_FORMAT'],
                                    options.values['REPO_ACTIVATE_ENABLED_REPOS'])

        
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


        #  Print the Loaded Repos
        for repo in repos:
            print('Found Repository: ' + repo.ToString())

        #  Return the configured repositories
        return repos


    def Build_Repo_Config( self, repo_config_path,
                                 repo_config_format,
                                 activate_enabled_repos ):

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
                continue


            #  Split
            repo_name = Parse_Repo_Name(pline.split()[0])
            arch = 'all'
            enabled_state = Parse_Repo_Enable_State( pline.split()[1])
            enabled = False

            if (enabled_state == True) and (activate_enabled_repos == True):
                enabled = True

            #  Add the name of the repo
            repos.append(Yum_Repo( repo_name, arch, enabled ))


        #  Create CSV File
        with open( repo_config_path, 'w' ) as csvfile:

            #  Write the header
            csvfile.write('Repo Name,Architecture,Enabled\n')

            #  Write each line
            for repo in repos:
                csvfile.write( repo.name + ',' + str(repo.arch) + ',' + str(repo.enabled) + "\n")

    def Write_Repo_Spec(self, options):


        #  Create the output file
        base_url = options.values['SYNC_DIRECTORY']

        #  Check if the path is root-relative
        abs_path = base_url
        if os.path.isabs(base_url) is False:
            #  If so, then make it absolute
            abs_path = os.path.abspath(base_url)

        output_path = abs_path + '/composite.repo'
        
        with open( output_path, 'w') as fout:
            for repo in self.repos:
                
                repo.Write_Spec(fout, abs_path)
                fout.write('\n')


        
