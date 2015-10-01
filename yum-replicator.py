#!/usr/bin/env python3
#
#    File:    yum-replicator.py
#    Author:  Marvin Smith
#    Date:    9/19/2015
#
#    Purpose: Replicate Yum Repos
#
__author__ = 'Marvin Smith'


#  Project Libraries
from replicator.Configuration import Configuration
from replicator.Repo_Manager import Repo_Manager

# -------------------------------- #
# -        Main Function         - #
# -------------------------------- #
def Main():

    #  Load the configuration
    options = Configuration()

    #  Create repository manager
    repo_manager = Repo_Manager(options=options)

    #  If we only want to build the repolist, then exit
    if options.values['BUILD_REPOLIST'] is True:
        return

    #  Iterate over repositories, syncing
    for repo in repo_manager.repos:

        #  Sync the repo
        repo.Sync_Repository(options.values['SYNC_DIRECTORY'],
                             options.reposync_config)

if __name__ == '__main__':
    Main()

