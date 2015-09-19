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

    #  Iterate over repositories, syncing


if __name__ == '__main__':
    Main()

