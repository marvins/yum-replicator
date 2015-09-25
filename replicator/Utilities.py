__author__ = 'ms6401'

#  Python Libraries
import subprocess

def Run_Command(cmd):

    #  Create subprocess object
    p = subprocess.Popen( cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    
    # Output data
    sout = ''
    serr = ''

    #  Get all output
    while True:

        #  Get the next set of output
        outline = p.stdout.readline()
        errline = p.stderr.readline()

        if not outline and not errline:
            break
        elif outline:
            sout += outline.decode('utf-8')
        elif errline:
            serr += errline.decode('utf-8')
        

    return sout, serr

