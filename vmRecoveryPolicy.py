#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111
from threading import Thread
import pdb
import sys
from vmMonitorCfg import VmMonitorCfg
from vmCmdsHistory import VmCmdsHistory

class VmRecoveryPolicy(object):
	VM_RESTART_LIMIT = 1
	VM_RESTORE_LIMIT = 2
	PROCESS_RESTART_LIMIT = 2
	
	def __init__(self, vmcfgs):
		self.cfgsDict = {}
		self.vmStatusHistoryDict = {}	

		for cfg in vmcfgs:
			self.cfgsDict[cfg.GetVmName()] = cfg
			self.vmStatusHistoryDict[cfg.GetVmName()] = VmCmdsHistory() 
	def _RestartVM(self, vmCmdHistory, cmd):
		vmCmdHistory.RestartVMNum= vmCmdHistory.RestartVMNum+1
		if(vmCmdHistory.RestartVMNum > self.VM_RESTART_LIMIT):
			logging.warning("Restarted Vm continous %s times but in vain, need restore snapshot" %(vmCmdHistory.RestartVMNum))
			#vmCmdHistory.RestartVM = 0
			self._RestoreSnapShot(vmCmdHistory, cmd)
		else : 
			cmd.SetRestartVM()

	def _RestoreSnapShot(self, vmCmdHistory, cmd):
		vmCmdHistory.RestoreVMNum= vmCmdHistory.RestoreVMNum+1 
		if(vmCmdHistory.RestoreVMNum> self.VM_RESTORE_LIMIT):
			logging.warning("Restored vm continous %s times but in vain." %(vmCmdHistory.RestoreVMNum))
		cmd.SetRestoreSnapShot()
	def _RestartProcess(self, vmCmdHistory, pname, location, cmd):
			
		count = vmCmdHistory.AddRestartProcess( pname)
		if(count> self.PROCESS_RESTART_LIMIT):
			logging.warning("Restarted process continuous %s times but in valid."%(count-1))
			self._RestartVM(vmCmdHistory, cmd)	
			#vmCmdHistory.Clear()
		else :
			cmd.AddRestartProcess(location)
				
	def _StartVM(self, vmCmdHistory, cmd):
		
		cmd.SetStartVM()
	def Execute(self, validVmStatusDict):
		cmdsDict = {}

		for(vm, cmdHistory) in sorted(self.vmStatusHistoryDict.items()):
				logging.info(vm+" "+cmdHistory.ToString())

		for (vm, status) in sorted(validVmStatusDict.items()):
			cfg = self.cfgsDict[vm]

			cmd = MonitorCmd(vm, cfg.GetHostInfo())	
			if status.ProfileValid :
				if status.VmState == kvm.SHUTOFF :
					self._StartVM(self.vmStatusHistoryDict[vm], cmd)	
				elif(status.SystemCallHooked or status.RootKitScanned):
					self._RestoreSnapShot(self.vmStatusHistoryDict[vm],cmd)
				elif(len(status.ZombieProcesses) !=0):
					self._RestartVM(self.vmStatusHistoryDict[vm],cmd)
				elif(len(status.MissingProcesses) !=0):
					#pdb.set_trace()	
					self.ProcessMissingProcess(vm, status.MissingProcesses, cmd)
				else : 
					self.vmStatusHistoryDict[vm].Clear()
							

			cmdsDict[vm] = cmd	

		return cmdsDict
	def ProcessMissingProcess(self, vmname, missingProcessList, cmd):
		cfg = self.cfgsDict[vmname]
		monitorProcessMap = cfg.GetMonitorProcessMap()
		logging.info(monitorProcessMap)	
		logging.info(missingProcessList)	
		for p in missingProcessList:
			self._ProcessActionStr(vmname, p, monitorProcessMap[p], cmd)			

	def _ProcessActionStr(self, vmname, pname, info, vmCmd):

		logging.info(pname+" is stopped, need ["+info[0])
		if info[0].strip() == "restartP":
			self._RestartProcess(self.vmStatusHistoryDict[vmname], pname, info[1], vmCmd)

		elif info[0].strip() == "restoreV":
			self._RestoreSnapShot(self.vmStatusHistoryDict[vmname], vmCmd)

		elif info[0].strip() == "restartV":
			self._RestartVM(self.vmStatusHistoryDict[vmname], vmCmd)	
		else :
			logging.error("Unknowing info")

