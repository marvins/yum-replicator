__author__ = 'ms6401'

#  Python Libraries
import subprocess, logging

def Run_Command(cmd):

    logging.debug('Running Command: ' + str(cmd))

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
        outline, errline = p.communicate()

        if not outline and not errline:
            break
        elif outline:
            sout += outline.decode('utf-8')
            logging.debug(outline.decode('utf-8'))

        elif errline:
            serr += errline.decode('utf-8')
            logging.debug(errline.decode('utf-8'))

    return sout, serr

