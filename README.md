# Cycle Submit

The cycle_submit tool allows you to push Condor jobs to a CycleServer meta-scheduler instance from the command line. It provides all the same features and capabilities of the Submit Job GUI in CycleServer from the command line, in a format that's easily integrated in to your scripts.

It also serves as an example of how to use CycleServer's RESTful job submission API.

## Options

* -d | --description -- description for the submission
* -u | --username -- user name to use for authentication
* -p | --password -- password to use for authentication
* -g | --group -- group name for the submission
* --poolid -- pool ID to use for the submission
* --host -- hostname and port where CycleServer is listening
* -v | --version -- print version information and exit

## Description

The cycle_submit tool uses the CycleServer RESTful job submission API to place Condor jobs in to CycleServer's meta-scheduler for distribution to Condor scheduler daemons. It provides the same facilities for job submission as CycleServer's built-in GUI submission page (Jobs -> Submit Jobs in the CycleServer menu).

In most cases, if you opt not to supply information using the command line options, cycle_submit will let CycleServer assume the defaults for the user. The only exception to this is the --pool option and the pool ID. If you omit the --pool option, cycle_submit will use the first pool in the list of pools the user is authorized to submit to. This may not be the pool with the lowest ID and there's no garuntee it's the same every time you call cycle_submit.

Future enhancements to cycle_submit include validating the group name and providing the user with a list of valid pool and group options when the user does not supply one with a command line option.

If the submission succeeds, cycle_submit exits with status code 0 and prints the submission ID of the new submission to stdout. If the submission fails, cycle_submit exits with a non-zero status code and prints some hopefully helpful error information to stderr.

## Examples

my.sub: A simple submission file that runs sleep jobs on Linux machi

	universe = vanilla
	executable = /bin/sleep
	arguments = "5m"
	requirements = OpSys == "Linux" && Arch != UNDEFINED && Memory > 1 && Disk > 1
	should_transfer_files = yes
	transfer_executable = false
	when_to_transfer_output = on_exit
	leave_in_queue = false
	notification = never
	queue 1

Example 1: A simple submission requiring user interaction

	cycle_submit.py my.sub

Example 2: A completely unattended submission

	cycle_submit.py --username foo --password bar --pool 1 --group research my.sub

Example 3: A remote submission to a CycleServer on another machine

	cycle_submit.py --host cycleserver.mydomain.com:8080 my.sub
	
## See Also

* [Condor][condor] - high throughput computing from the University of Wisconsin
* [curl][] - a command line tool for transferring data with URL syntax

## Copyright

Copyright (C) 2007-2012, Cycle Computing, LLC.

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.  You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0.txt>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

[cycleserver]:http://www.cyclecomputing.com/cycleserver/overview
[condor]:http://www.uwisc.cs.edu/condor
[curl]:http://curl.haxx.se/