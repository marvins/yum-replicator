#!/bin/sh


#--------------------------------#
#-      Global Variables        -#
#--------------------------------#
VERBOSE=0
INTERACTIVE=0
YUM_REPO_LIST=''
YUM_ARCH_LIST=''
REPO_BASE_PATH=''

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
        CMD="reposync -l -r ${YUM_REPO_LIST[$X]} $ARCHVAL -p $REPO_BASE_PATH"

        if [ "$VERBOSE" = '1' ]; then
            echo $CMD
        fi
        if [ "$INTERACTIVE" = '1' ]; then
            echo 'Press any key to start the next repo sync.'
            read ANS
        fi

        #  Fire off command
        $CMD
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

        #  Unknown Option
        *)
            
            #  Otherwise, we have a valid path
            REPO_BASE_PATH=$ARG
            ;;

    esac
done


#  Validate User Priviledges
Validate_User_Priviledges


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


