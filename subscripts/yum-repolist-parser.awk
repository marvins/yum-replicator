BEGIN{
    pattern = "repo id" 
}
{
    # Skip the repolist pattern
    if( match($0,"repolist") ){

    }
    
    # Validate the pattern has been found
    else if( flag1 > 0 ){ 

        #  Split the line by spaces to get the repo
        split($0, array, " ")

        #  Split line by / to get the architecture
        split(array[1], repo_info, "/")
        arch_name="__NULL__"

        # Check if x86_64
        if( match(repo_info[2], "x86_64") ){
            arch_name="x86_64"
        }

        #  Check if i686
        if( match(repo_info[2], "i686") ){
            arch_name="i686"
        }

        #  Print the line
        print repo_info[1] "," arch_name
    }
    if( $0 ~ pattern ) 
        flag1++
}

