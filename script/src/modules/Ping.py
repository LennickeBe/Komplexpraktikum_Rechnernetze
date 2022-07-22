"""
    This file contains the wrapper class for the ping command.
    The class follows a certain pattern to work with the measurement core programm.
"""

import subprocess   # running the python3 command
import re           # parsing the output

class PingMeasurement:
    """This class is a wrapper class for the ping command."""
    def __init__(self, target, count=10):
        # the ping command needs a target
        self.target = target

        # count is the number of packets send
        # this should be greater than 0
        if not (type(count) == int):
            raise AssertionError("count argument must be an integer")
        assert(count>0, "count argument must be greater 0")
        self.count = count

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
        found_ping = False
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
            if "ping" in os.listdir(dr):
                found_ping = True

        if not found_bash:
            raise Exception("No bash installation found in $PATH")
        if not found_ping:
            raise Exception("No ping installation found in $PATH")

        # we run the command once to see whether it works or not
        PING_COMMAND = ("ping -c {} {}".format(self.count, self.target)).split(" ")
        test = subprocess.check_output(PING_COMMAND)



    def measure(self):
        """Calling this method starts a measurement."""
        # call ping command 
        PING_COMMAND = ("ping -c {} {}".format(self.count, self.target)).split(" ")
        # check_output returns byte-wise so we decode to str
        output = subprocess.check_output(PING_COMMAND).decode()
        
        # following regex matches the times in the output
        reg = "time=([0-9.]*) ms"
        values = re.findall(reg, output)
        # these are currently integers we want floats
        values = list(map(float, values))

        if len(values) != self.count:
            raise Exception("The number of values does not match the number of measurements.")

        # we calculate the mean value as the result
        result = sum(values) / len(values)

        # we do not need it like 100% exactly so we round
        return round(result, 2)


if __name__=="__main__":
    a = PingMeasurement("8.8.8.8")

    print(a.measure())
