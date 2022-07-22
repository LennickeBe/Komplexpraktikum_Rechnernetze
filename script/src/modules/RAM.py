"""
    This file contains the wrapper class for the free command.
    The class follows a certain pattern to work with the measurement core programm.

    The free command returns the ram and swap usage.
    
"""

import subprocess   # running the python3 command
import re           # parsing the output

class RAMMeasurement:
    """This class is a wrapper class for the free command."""
    def __init__(self):
        # we make sure the measurement is possible
        self._check()


    def _check(self):
        """This method is called when the class is initialized to prevent
           errors later on when calling the measurement method.
        """
        # check is bash and ping installed/in $PATH
        import os
        # default is "no installation found
        found_bash = False
        found_free = False
        # $PATH contains directories split with :
        # in these directories are executable binaries 
        for dr in os.environ['PATH'].split(":"):
            # looks like there are paths in there which do not exists
            # we check this first
            if not os.path.isdir(dr):
                break
            # we look for bash in each of the directories
            if "bash" in os.listdir(dr):
                found_bash = True
            # aswell as for ping
            if "free" in os.listdir(dr):
                found_ping = True

        if not found_bash:
            raise Exception("No bash installation found in $PATH")
        if not found_ping:
            raise Exception("No free installation found in $PATH")



    def measure(self):
        """Calling this method starts a measurement."""
        # call free command 
        FREE_COMMAND = ("free").split(" ")
        # check_output returns byte-wise so we decode to str
        output = subprocess.check_output(FREE_COMMAND).decode()

        # now we parse the output
        # subprocess does not well with PIPES in the command string
        # so we use the subprocess.PIPE to "store" the output
        free_out = subprocess.Popen(["free"], stdout=subprocess.PIPE)
        # this returns a line which contains the memory values for the RAM
        grep_out = subprocess.check_output(["grep", "Mem:"], stdin=free_out.stdout)
        # Mem: total used free shared buff/cache available
        # this currently is in bytes not as a string so we convert
        grep_out = "".join(chr(x) for x in grep_out)

        # now we parse it
        reg = "Mem:[\s]*([0-9]*)[\s]*([0-9]*)[\s\S]*"
        # we just want the first one (its only one anyway and we drop
        # [] here allready
        value_tuple, = re.findall(reg, grep_out)

        # first value is the total ram space
        # second is the currently used space
        # we are interessted how many percent are used
        result = (int(value_tuple[1])/int(value_tuple[0])) * 100

        return round(result, 2)


if __name__=="__main__":
    a = RAMMeasurement("8.8.8.8")

    print(a.measure())
