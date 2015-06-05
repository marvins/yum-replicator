#Yum-Replicator#

Simple utility for replicating all registered repositories 
of a particular system to a hard drive.

### Tested Systems ###
- RHEL 6
- RHEL 7
- Fedora 21


## Features ###

###Synchronization of Yum Repos###
This script will fetch all repositories you have available in yum.  It will then
fetch any new repos and delete the old, unsupported repos.

###Generation of New Yum Repo Files###
Given the `-g` argument, the script will create and deploy the required .repo files 
needed for users to copy to their yum.repos.d directory.  Basically it just sets the repo name and path to the one specified.  Since remote users may have a different mount point or network configuration, you will have to adjust accordingly for now. 

###Management and Update of the RPM repo data###
This tool requires the `createrepo` tool installed.  This will enable you to build the RPM database and subsequently update it for any new changes cause by reposync.


