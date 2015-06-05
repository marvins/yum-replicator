#!/bin/sh


#--------------------------------#
#-      Global Variables        -#
#--------------------------------#
VERBOSE=0
INTERACTIVE=0
YUM_REPO_LIST=''
YUM_ARCH_LIST=''
REPO_BASE_PATH=''
GENERATE_YUM_CONF=0
TEMP_DIR='tmp'
REPOSYNC_GPG='-g'
REPOSYNC_NEWEST='-n'

#-------------------------------------#
#-      Print Usage Instruction      -#
#-------------------------------------#
Usage()
{

    #  Print usage line
    echo "usage: $0 [options] <repo-base-path>"

    #  Print help
    echo ''
    echo '  -h | --help         : Print usage instructions and exit.'
    echo '  -v | --verbose      : Generate verbose output.'
    echo '  -i | --interactive  : Provide interactive output with confirmation required between steps.'
    echo '  -g | --generate     : Generate yum *.repo files to adding to your yum.conf.d path.'
    
    #  Print the repo-base-path
    echo ''
    echo '   <repo-base-path>   : Path to where repositories will be synced against.'
    echo ''

    # Exit
    exit 0
}


#--------------------------------------#
#-      Print Configuration Data      -#
#--------------------------------------#
Print_Configuration()
{
    

    #  Print header
    echo "$0 : Yum Repository Synchronization Utility"
    echo ''
    echo "   REPO_BASE_PATH=$REPO_BASE_PATH"
    echo ''
    printf "%-60s  %-08s\n"  "Repository" "Architecture"
    for ((X=1;X<=${#YUM_REPO_LIST[@]};X++)); do
        
        printf "%-60s  %-08s\n"  "${YUM_REPO_LIST[$X]}"  "${YUM_ARCH_LIST[$X]}"
    done


}

#--------------------------------------------------#
#-      Validate User has Proper Priviledges      -#
#--------------------------------------------------#
Validate_User_Priviledges()
{
    
    #  Check that user is root
    if [ ! "`whoami`" = 'root' ]; then
        echo 'error: User must be root.' 
        exit
    fi

}


#-------------------------------------------------------#
#-      Validate the proper software is installed      -#
#-------------------------------------------------------#
Validate_Required_Software()
{
    #  Make sure createrepo is installed
    command -v createrepo >/dev/null 2>&1 || { 
        echo >&2 "error: 'createrepo' is required but not installed."
        Usage
    }

}

#----------------------------------------#
#-      Validate the repo base path     -#
#----------------------------------------#
Validate_Repo_Base_Path()
{

    #  Check if the repo base path was provided
    if [ "$REPO_BASE_PATH" = '' ]; then
        echo "Must provide path to where to sync repositories."
        Usage
    fi


    #  Check if the repo base path exists
    if [ ! -d "$REPO_BASE_PATH" ]; then
    
        #  If interactive, ask if the user wants to create the directory
        if [ "$INTERACTIVE" = '1' ]; then
            echo -n "$REPO_BASE_PATH does not exist. Would you like to create path? (y/n - default): "
            read CREATE_PATH

            #  Check for a match
            if [[ "$CREATE_PATH" =~ [y|Y].* ]]; then
                if [ "$VERBOSE" = '1' ]; then
                    echo 'Creating path.'
                fi
                mkdir -p $REPO_BASE_PATH

            # If no match, then abort
            else
                if [ "$VERBOSE" = '1' ]; then
                    echo 'Cancelled.'
                fi
                exit
            fi

        #  Otherwise, just create
        else
            mkdir -p $REPO_BASE_PATH
        fi
    fi

}


#----------------------------------------------#
#-      Get the List of Yum Repositories      -#
#----------------------------------------------#
Get_Yum_Repo_List()
{

    #  Run yum
    TEMP_REPO_LIST=`yum repolist | awk -f subscripts/yum-repolist-parser.awk`

    #  Iterate over list, splitting
    for TEMPLINE in $TEMP_REPO_LIST; do
        
        #  Get the repo name
        REPO_NAME="`echo $TEMPLINE | awk -F \",\" '{print $1}'`" 
        YUM_REPO_LIST="$YUM_REPO_LIST $REPO_NAME"

        #  Get the architecture
        ARCH_NAME="`echo $TEMPLINE | awk -F \",\" '{print $2}'`"
        YUM_ARCH_LIST="$YUM_ARCH_LIST $ARCH_NAME"
        

    done
    
    #  Convert to arrays
    IFS=' ' read -a YUM_REPO_LIST <<< "$YUM_REPO_LIST"
    IFS=' ' read -a YUM_ARCH_LIST <<< "$YUM_ARCH_LIST"

}


#--------------------------------------------------#
#-         Generate Yum Repo Configuration        -#
#--------------------------------------------------#
Generate_Yum_Repo_Config()
{
    #  Grab the repo name
    REPO_NAME="$1-local"

    #  Create tmp directory
    mkdir -p ${TEMP_DIR}

    #  Create temp file
    TEMP_REPO_PATH="${TEMP_DIR}/$REPO_NAME.repo"
    cp templates/template.repo "$TEMP_REPO_PATH"
    
    #  Set the Name
    sed -i "s/__REPONAME__/$REPO_NAME/g" -i $TEMP_REPO_PATH
    
    #  Set the Path
    REPO_FILEDIR="`echo \"file://$REPO_BASE_PATH/$REPO_NAME\" | sed 's/\//\\\\\\//g'`"
    sed -i "s/__REPO_PATH__/$REPO_FILEDIR/g" -i $TEMP_REPO_PATH
    
}


#--------------------------------------------------#
#-         Update the Yum Repo Definitions        -#
#--------------------------------------------------#
Update_Repo_Definitions()
{
    #  Get the current repo
    CURRENT_REPO=$1

    #  Navigate to new repo
    pushd $REPO_BASE_PATH/$CURRENT_REPO

    #  Run Create Repo
    createrepo 

    #   Return
    popd

}


#-------------------------------------------------#
#-          Process the Repository List          -#
#-------------------------------------------------#
Process_Repositories()
{

    # Iterate over list
    for ((X=1;X<=${#YUM_REPO_LIST[@]};X++)); do
        
        #  Set the arch
        ARCHVAL="--arch=${YUM_ARCH_LIST[$X]}"
        if [ "${YUM_ARCH_LIST[$X]}" = '__NULL__' ]; then
            ARCHVAL=''
        fi

        #  Create reposync command
        CMD="reposync ${REPOSYNC_GPG} ${REPOSYNC_NEWEST} -l -r ${YUM_REPO_LIST[$X]} $ARCHVAL -p $REPO_BASE_PATH"

        if [ "$VERBOSE" = '1' ]; then
            echo $CMD
        fi
        Generate_Yum_Repo_Config "${YUM_REPO_LIST[$X]}"
        if [ "$INTERACTIVE" = '1' ]; then
            echo 'Press any key to start the next repo sync.'
            read ANS
        fi

        #  Fire off command
        $CMD

        #  Generate the yum conf file
        if [ "$GENERATE_YUM_CONF" = '1' ]; then
            Generate_Yum_Repo_Config "${YUM_REPO_LIST[$X]}"
        fi
        

        #  Update the repo
        Update_Repo_Definitions ${YUM_REPO_LIST[$X]}

    done

}

#-----------------------------#
#-       Main Function       -#
#-----------------------------#

#  Iterate over command-line arguments
for ARG in "$@"; do
    case $ARG in

        #  Check usage instructions
        -h|--help)
            Usage
            ;;
        
        #  Print with verbose output
        -v|--verbose)
            VERBOSE=1
            ;;

        #  Print Interactive output
        -i|--interactive)
            VERBOSE=1
            INTERACTIVE=1
            ;;

        #  Generate
        -g|--generate)
            GENERATE_YUM_CONF=1
            ;;

        #  Unknown Option
        *)
            
            #  Otherwise, we have a valid path
            REPO_BASE_PATH=$ARG
            ;;

    esac
done


#  Validate User Priviledges
Validate_User_Priviledges


#   Check required software
Validate_Required_Software

# Check the yum list
Get_Yum_Repo_List


#  Print the information if verbose
if [ "$VERBOSE" = '1' ]; then
    Print_Configuration
fi


#  Validate Repo Base Path
Validate_Repo_Base_Path


#  Start iterating over repo paths
Process_Repositories


