import xml.dom.minidom
import pdb
 
class VmMonitorCfg(object):
	processMap = {}
 	vmname = ""
	profile = ""
	def __init__(self, vmname, processMap, profile, user, password, ip):
		self.vmname = vmname
		self.processMap = processMap
		self.profile = profile
		self.user = user
		self.password = password
		self.ip = ip

	def GetMonitorProcessMap(self):
		return self.processMap;
	def GetVmName(self):
		return self.vmname
	def GetHostInfo(self):
		#pdb.set_trace()
		return dict(username=self.user, password=self.password, ip=self.ip)
	@property
	def Profile(self):
		return self.profile

	@classmethod
	def GetVmMonitorCfgs(cls, fileName):
		dom = xml.dom.minidom.parse(fileName)
		vmCheckCfgList = []
		vms = dom.getElementsByTagName("vm")	
		for vm in vms:
			#profile = "--profile=Linuxcentos5_5x86"
			profile = vm.getElementsByTagName("profile")[0].childNodes[0].data
			user = vm.getElementsByTagName("username")[0].childNodes[0].data
			password = vm.getElementsByTagName("password")[0].childNodes[0].data
			ip = vm.getElementsByTagName("ip")[0].childNodes[0].data

			processes = vm.getElementsByTagName("process")[0]
			pitems = processes.getElementsByTagName("item")

		#	pdb.set_trace()

			pmap = {}
			for p in pitems:
				pname = p.attributes['name'].value
				ploc = p.attributes['path'].value
				paction = p.childNodes[0].data
				pmap[pname] = (paction, ploc);
				#print " "+pname+" "+pmap[pname]
			vname = vm.attributes['name'].value
			print " "+vname+" "+profile	

			cfg = cls(vname, pmap, profile, user, password, ip)
			vmCheckCfgList.append(cfg)	

		return vmCheckCfgList


	
if __name__ == "__main__":
	vmCfgs = VmMonitorCfg.GetVmMonitorCfgs("./vms.cfg")
	
