#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111

import sys
if sys.version_info < (2, 6, 0):
    sys.stderr.write("Volatility requires python version 2.6, please upgrade your python installation.")
    sys.exit(1)

try:
    import psyco #pylint: disable-msg=W0611,F0401
except ImportError:
    pass

if False:
    # Include a fake import for things like pyinstaller to hit
    # since this is a dependency of the malware plugins
    import yara

import textwrap
import volatility.conf as conf
import os
import logging
import pdb
#config = conf.ConfObject()
# must be put before  registry
import volatility.constants as constants

profile_path="/root/csd/virtualMachineRecoverySystem/vol-profile/"
argv = ['main.py','--plugins='+profile_path] 
argvt = sys.argv  
sys.argv = argv
import volatility.registry as registry
sys.argv = argvt

import volatility.exceptions as exceptions
import volatility.obj as obj
import volatility.debug as debug

import volatility.addrspace as addrspace
import volatility.commands as commands
import volatility.scan as scan

class VmInspection(object):
		
	def IsSystemCallHooked(self, vmname, profile):
	   self.profile = profile
	   data = self._CheckSystemCall( vmname)
	   for ( table_name, i, call_addr, hooked) in data:
		if hooked != 0:
			return True
	   return False

	def _CheckSystemCall(self, vmname):
	   return self._ExecuteCommand(vmname, "linux_check_syscall")
	   
	def GetProcessName(self, vmname, profile):
	   self.profile = profile
	   data = self._ExecuteCommand(vmname, "linux_pslist")
	   list = []
	   for task in data:
		list.append(str(task.comm))
	   return list
		
	def GetProcesses(self, vmname, profile):
	   logging.info(profile)
	   self.profile = profile
	   self.vmprocessMap[vmname] = self._ExecuteCommand(vmname, "linux_pslist")
	   logging.info(self.vmprocessMap[vmname])
	   return self.vmprocessMap[vmname] 

	def DumpProcess(self, vmname, pname, profile):
	   self.profile = profile
	   outfile = "./tmp/"+pname+".2"
	   if not os.path.exists("./tmp"):
		os.makedirs("./tmp")
 
	   self._ExecuteCommand(vmname, "linux_dump_proc_map",pname, outfile )

	def _ExecuteCommand(self, vmname, command, pname = None, outfile=None):
	    location = " -l vmi://"+vmname;
	    profile = " --profile "+self.profile 
	    #argv = self.plugin+profile+location+" ";
	    argv = profile+location+" ";
	   # pdb.set_trace()
	    if pname :
		argv+="-n "+pname+" "
	    if outfile :
		argv+="-O "+outfile+" "
	    argv+=command
 	    #pdb.set_trace()
	    self.config.parse_options_from_string(argv, False)
	    module  = self._GetModule(self.config)
	    return self._ExecuteModule(module, argv)

	def _GetModule(self, config):
		for m in config.args:
			if m in self.cmds.keys():
			    module = m
			    return module 

		if not module:
		#config.parse_options()
			debug.error("You must specify something to do (try -h)")
		
		
	def _ExecuteModule(self, module, argv):
		    if not module:			
			debug.error("You must specify something to do (try -h)")
		    try:
			if module in self.cmds.keys():
			    command = self.cmds[module](self.config)
			    ## Register the help cb from the command itself
			    #self.config.set_help_hook(obj.Curry(command_help, command))
			    #config.parse_options()
			    self.config.parse_options_from_string(argv)
			    #pdb.set_trace()

			    if not self.config.LOCATION:
				debug.error("Please specify a location (-l) or filename (-f)")

			    data = command.execute_call()
			    return data
			    #for task in data:
			#	print str(task.comm)+"\t"+str(task.pid)
		    except exceptions.AddrSpaceError, e:
		   	print e
#		    except (exceptions.VolatilityException,exceptions.AddrSpaceError) as e:
			#print e

	def __init__(self):	

	    # Get the version information on every output from the beginning
	    # Exceptionally useful for debugging/telling people what's going on
	    #sys.stderr.write("Volatile Systems Volatility Framework {0}\n".format(constants.VERSION))
	    #sys.stderr.flush()
	    self.config = conf.ConfObject()
	    self.cmds = {}
	    self.profile = "--profile=Linuxcentos5_5x86"
	    self.vmprocessMap = {}

	    self.config.add_option("INFO", default = None, action = "store_true",
			  cache_invalidator = False,
			  help = "Print information about all registered objects")

	    # Setup the debugging format
	    debug.setup()
	    # Load up modules in case they set config options
	    registry.PluginImporter()

	    ## Register all register_options for the various classes
	    registry.register_global_options(self.config, addrspace.BaseAddressSpace)
	    registry.register_global_options(self.config, commands.Command)

	# Reset the logging level now we know whether debug is set or not
	    debug.setup(self.config.DEBUG)
	    
	    #pdb.set_trace()
	    
	    ## Try to find the first thing that looks like a module name
	    self.cmds = registry.get_plugin_classes(commands.Command, lower = True)
