"""
    This file contains the wrapper class for the iperf command.
    The class follows a certain pattern to work with the measurement core programm.

    The iperf command returns network throughput.
    This requires iperf -s to run at the ip given with target on the port.
"""

import subprocess   # running the python3 command
import re           # parsing the output

class IperfMeasurement:
    """This class is a wrapper class for the iperf command."""
    def __init__(self, target, time=5, interval=0, port=5001, via=None, loss=None):
        self.target = target
        self.time = time
        if interval==0:
            self.interval = time
        else:
            self.interval = interval
        self.port = port
        self.via = via

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
        found_iperf = False
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
            # aswell as for iperf
            if "iperf" in os.listdir(dr):
                found_iperf = True

        if not found_bash:
            raise Exception("No bash installation found in $PATH")
        if not found_iperf:
            raise Exception("No free installation found in $PATH")

        # we check whether we find the server
        cmd = ("iperf -c {} -t 1 -i 1 -p {}".format(self.target, self.port)).split(" ")
        output = subprocess.check_output(cmd).decode()
        if "tcp connect failed" in output:
            raise Exception("Could not reach the iperf server at {}.".format(self.target))
        if "Bandwidth" not in output:
            print("Test run of iperf resulted in:\n{}".format(output))
            raise Exception("Server is probably not running at {}.".format(self.target))

                    
    def measure(self):
        """Calling this method starts a measurement."""
        # call iperf command 
        # -c IP where iperf -s is running
        # -t time in seconds to transmit for
        # -i pause in seconds between periodic bandwidth reports
        # -f M force output in MBytes
        # -p port the server listens
        IPERF_COMMAND = (("iperf -c {} -t {} -i {} -f M -p {}").format(self.target, self.time, self.interval, self.port)).split(" ")
        # check_output returns byte-wise so we decode to str
        output = subprocess.check_output(IPERF_COMMAND).decode()
        
        # we are interested in the overall bandwidth  in the last line
        res = output.split("\n")[-2]

        # following regex extracts the Bandwidth value from this line
        reg = "[\s\S]?([0-9\.]*) MBytes\/sec"

        result = float(re.findall(reg, res)[0])

        return round(result, 2)

if __name__=="__main__":
    a = IperfMeasurement(target="172.18.0.6", time=5, interval=1)
    print(a.measure())
