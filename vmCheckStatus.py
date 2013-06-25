#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111

from threading import Thread
import vmrsConfig

 class VmCheckStatus(object):
		
	def __init__(self):
		self.state = kvm.RUNNING	
		self.missingProcesses = []
		self.isSystemCallHooked = False
		self.isRootKitScanned = False
		self.zombieProcesses= []
		self.profileValid = True
	@property
	def ProfileValid(self):
		return self.profileValid
	@ProfileValid.setter
	def ProfileValid(self, value):
		self.profileValid = value

	@property
	def MissingProcesses(self):
		return self.missingProcesses

	@MissingProcesses.setter
	def MissingProcesses(self, value):
		self.missingProcesses= value
	@property
	def SystemCallHooked(self):
		return self.isSystemCallHooked 

	@SystemCallHooked.setter
	def SystemCallHooked(self, value):
		self.isSystemCallHooked= value

	@property
	def RootKitScanned(self):
		return	self.isRootKitScanned 

	@RootKitScanned.setter
	def RootKitScanned(self, value):
		self.isRootKitScanned= value
	@property
	def ZombieProcesses(self):
		return self.zombieProcesses 

	@ZombieProcesses.setter
	def ZombieProcesses(self, value):
		self.zombieProcesses= value
	@property
	def VmState(self):	 
		return self.state
	 
	@VmState.setter
	def VmState(self, value):
		self.state= value
	def ToString(self):
		msg = "Vm state:\t"+self.VmState+"\n" ;
		if not self.ProfileValid:
			msg=msg+"Profile is not valid\n"
		msg=msg+"System call hooked: %s \n"%(str(self.SystemCallHooked)) 
		msg=msg+"RootKitScanned: %s \n"%(str(self.RootKitScanned))
		msg=msg+"ZombieProcesses:\t"
		for z in self.ZombieProcesses :
			msg=msg+z+"\t"
		msg= msg+"\n"
		msg=msg+"MissingProcesses:\t"
		for m in self.MissingProcesses:
			msg=msg+m+"\t"
		msg= msg+"\n"

		return msg	
			
