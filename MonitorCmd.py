#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111
from threading import Thread
import kvm
import unix
import vmrsConfig
 
class MonitorCmd(object):
	USE_VM_CMD_TO_REBOOT_SHUTDOWN = True
	def __init__(self, vmname, hostinfo):
		self.vmname = vmname	
		self.user = hostinfo['username'] 
		self.password= hostinfo['password'] 
		self.ip = hostinfo['ip'] 
		self.isRestoreSnapShot = False
		self.isRestartVM = False
		self.isStartVM =False 
		self.restartCmds = []
		self.kvm_host = kvm.KVM(unix.Local())
	def AddRestartProcess(self, plocation):
		self.restartCmds.append(plocation)	

	def SetRestoreSnapShot(self):
		self.isRestoreSnapShot = True
	
	def SetRestartVM(self):
		self.isRestartVM = True
	def SetStartVM(self):
		self.isStartVM = True	
	def Execute(self):
		#pdb.set_trace()
		if	self.isStartVM :
			try:
				t = Thread(target=self._StartVM(), args=())
				t.daemon = THREAD_DAEMON_MOD
				t.start()
			except Exception, errtxt:
				logging.error(errtxt)

		elif self.isRestoreSnapShot:
			try:
				t = Thread(target=self._RestoreVM(), args=())
				t.daemon = THREAD_DAEMON_MOD
				t.start()
			except Exception, errtxt:
				logging.error(errtxt)
						
		elif self.isRestartVM:
			try:
				t = Thread(target=self._RestartVM(), args=())
				t.daemon = THREAD_DAEMON_MOD
				t.start()
			except Exception, errtxt:
				logging.error(errtxt)
		elif len(self.restartCmds)>0 :
			try:
				t = Thread(target=self._RestartProcesses, args=())
				t.daemon = THREAD_DAEMON_MOD
				t.start()
			except Exception, errtxt:
				logging.error(errtxt)
		else :
			logging.info("\tNo actions need")
	def _RestartVM(self):
		logging.info("\tRestarting vm")
		if self.USE_VM_CMD_TO_REBOOT_SHUTDOWN:
			msg = self.vmname
			cmds = ["reboot"]
			self.ExecuteCMDInVm(msg, cmds, self.ip, self.user, self.password)
		else:
			r = self.kvm_host.reboot(self.vmname)			
			logging.info("Result:\t"+r[1])
	def _StartVM(self):
		logging.info("\tStarting vm")
		r = self.kvm_host.start(self.vmname)			
		logging.info("Result:\t")
		logging.info(r)

	def _RestoreVM(self):
		logging.info("\tRestoreing from snapshot "+self.vmname)
		if self.kvm_host.state(self.vmname) == kvm.RUNNING :
			logging.info("\tShutdownning "+self.vmname)
			if self.USE_VM_CMD_TO_REBOOT_SHUTDOWN:
				cmds = ["shutdown -h now"] # incase centos enter into single user mode
				msg = "\tShutdownning "+self.vmname
				self.ExecuteCMDInVm(msg, cmds, self.ip, self.user, self.password)
				logging.info("must sleep to wait shutdown")
				time.sleep(70)
			else:
				r = self.kvm_host.stop(self.vmname, timeout=60)

			logging.info(self.vmname+" Shutdowned ")

		r = self.kvm_host.restore(self.vmname, '/usr/saves/'+self.vmname)			
		logging.info("Result:\t")
		logging.info(r)
	def _RestartProcesses(self):
		msg = self.vmname+" Restarting process:\t" 

		self.ExecuteCMDInVm(msg, self.restartCmds, self.ip, self.user, self.password)

	def ExecuteCMDInVm(self, msg, cmds,ip, usr,pwd ):
		h = unix.Remote()
		h.connect(ip,username=usr, password=pwd)
		logging.info("ExecuteCMDInVm")
		for v in cmds:
			#pdb.set_trace()
			r = h.execute(v)	
			logging.info(r)
			logging.info(msg+"\t"+v+"\t"+str(r[0]))
	def ToString(self):
		msg="VmMonitor\t"
		if self.isRestoreSnapShot:
			msg=msg+"RestoreSnapShot";					
		elif self.isRestartVM:
			msg=msg+"Restart VM"
		elif len(self.restartCmds)>0 :
			msg=msg+"Executeing Cmd:\t"
			for p in self.restartCmds:
				msg=msg+p+"\t"
		else :
			msg="No actions need"
		msg=msg+"\n"
	
		return msg
