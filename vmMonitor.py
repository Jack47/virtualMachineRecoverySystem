#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111
from threading import Thread
import pdb
import sys
import kvm
import unix
import logging
from vmInspection import VmInspection

class VmMonitor(object):
	vmcfgs = {}
	vmInspection = VmInspection() 
	kvm_host = kvm.KVM(unix.Local())
	
	#self.vmProcessMap = {}

	def __init__(self, vmcfgs):
		
		kvm_vms = self.kvm_host.vms

		for vmcfg in vmcfgs:
			vmname = vmcfg.GetVmName()
			if  vmname not in kvm_vms :
				logging.warning(vmname+" is not available!")
				vmcfgs.remove(vmname)
			else:
				self.vmcfgs[vmname] = vmcfg

	def Execute(self):
		vmstatus = {}

		for(vmname, vmcfg) in sorted(self.vmcfgs.items()): 
			status = VmCheckStatus()
			logging.info("Checking VM: "+vmname)
			state = self.kvm_host.state(vmname) 
			
			if state != kvm.RUNNING:
				logging.warning(vmname +" is in status "+state) 
				status.VmState = state
				vmstatus[vmname] = status
				continue
			try:
				mplist = self.CheckVMMissingProcesses(vmname)
				status.MissingProcesses = mplist;
				status.IsSystemCallHooked = self.CheckVMSystemCall(vmname )
				status.ZombieProcesses = self.CheckZombieProcesses(vmname)
			except exceptions.AddrSpaceError, e:
				logging.exception(vmcfg.GetVmName()+" profile is not valid")
				
				status.ProfileValid = False
			except Exception, e:
				logging.exception(e)
			
			vmstatus[vmname] = status
		return vmstatus
	def CheckVMSystemCall(self, vmname):
		logging.info("\t Checking System call")		
		return self.vmInspection.IsSystemCallHooked(vmname, self.vmcfgs[vmname].Profile)

	def CheckZombieProcesses(self, vmname):
	#	self.vmInspection.DumpProcess(vmname, "sshd", self.vmcfgs[vmname].Profile)
		return []

	def CheckVMMissingProcesses(self, vmname):
		logging.info("\t Checking VM missing Processes")		
		vmMissingProcess = []
		vmpList = self.GetVMProcessName(vmname)				
		pmap = self.vmcfgs[vmname].GetMonitorProcessMap()	
		monitorPlist = []
		for(k,v) in sorted(pmap.items()):
			monitorPlist.append(k)

		for p in monitorPlist:
			if not p in vmpList:
				vmMissingProcess.append(p)

		return vmMissingProcess 
	def GetVMProcesses(self, vmname):
		vmProcesses = self.vmInspection.GetProcesses(vmname, self.vmcfgs[vmname].Profile)

		return vmProcesses
	def GetVMProcessName(self, vmname):
		return self.vmInspection.GetProcessName(vmname, self.vmcfgs[vmname].Profile)

