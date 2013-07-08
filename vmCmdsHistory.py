#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111

class VmCmdsHistory(object):
	@property
	def RestartVMNum(self):
		return self.restartVMNum
	@RestartVMNum.setter
	def RestartVMNum(self, value):
		self.restartVMNum=value
	@property
	def RestoreVMNum(self):
		return self.restoreVMNum

	@RestoreVMNum.setter
	def RestoreVMNum(self, value):
		self.restoreVMNum=value
	def __init__(self):
		self.restartVMNum = 0
		self.restoreVMNum = 0
		self.rpmap = {}

	def Clear(self):
		self.restartVMNum = 0
		self.restoreVMNum = 0
		self._ClearRestartProcess(True)

	def _ClearRestartProcess(self, clearCount=True):
		for(k, v) in sorted(self.rpmap.items()):
			self.rpmap[k] = 0

	def AddRestartProcess(self, pname):
		if pname not in self.rpmap:
			self.rpmap[pname] = 1 # use two tuple, second is used to record action nums	
		else :
			self.rpmap[pname] =self.rpmap[pname]+1 

		return self.rpmap[pname]
	def ToString(self):
		msg = "VmCmdHistory:\t"
		msg = msg+"Restore VM num: %s\t Restart VM num: %s\t" %(self.RestoreVMNum, self.RestartVMNum)

		msg = msg+"Processed restarted:"
		for (pname, count) in sorted(self.rpmap.items()):
			msg=msg+pname+"\t"+str(count)	
		msg = msg+"\n"

		return msg
