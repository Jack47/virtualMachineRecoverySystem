#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111

from threading import Thread
from vmMonitorCfg import VmMonitorCfg
from vmMonitor import VmMonitor
from vmRecoveryPolicy import VmRecoveryPolicy
import logging
import time

class VmRecoverySystem(object):
	
	def __init__(self):
		self.vmcfgs = VmMonitorCfg.GetVmMonitorCfgs("./vms.cfg")
		self.vmMonitor = VmMonitor(self.vmcfgs);
		self.vmRecoveryPolicy = VmRecoveryPolicy(self.vmcfgs)
	@property
	def Monitor(self):
		return self.vmMonitor	

	def Execute_forever(self):
	
		while True:
			#validVmStatusDict = self.vmMonitor.Execute()
			
			#for(vm, vmStatus) in sorted(validVmStatusDict.items()):
			#	logging.info("Vm checked status:"+vm+"\n"+vmStatus.ToString())

			#monitorCmds = self.vmRecoveryPolicy.Execute(validVmStatusDict)

			#for(vm, cmd) in sorted(monitorCmds.items()):
			#	logging.info("Vm cmd:"+vm+"\n"+cmd.ToString())

			#for (vmname, cmd) in sorted(monitorCmds.items()):
			#	cmd.Execute()	
			logging.info("sleep 70")
			time.sleep(70)
			
