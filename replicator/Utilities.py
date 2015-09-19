__author__ = 'ms6401'

#  Python Libraries
import subprocess

def Run_Command(cmd):

    #  Create subprocess object
    p = subprocess.Popen( cmd,
                          stdout=subprocess.STDOUT,
                          stderr=subprocess.PIPE)

    #  Run
    try:
        sout, serr = p.communicate()

    except TimeoutExpired:
        p.kill()
        sout, serr = p.communicate()

    return sout, serr
