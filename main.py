#!/usr/bin/python
#  -*- mode: python; -*-

#pylint: disable-msg=C0111
import BaseHTTPServer
import sys
import pdb
import logging
import signal
import unix
import kvm
import volatility.debug as debug
from vmRecoverySystem import VmRecoverySystem
from threading import Thread
import logging
import volatility.exceptions as exceptions
 
def sigint_handler(signal, frame):
        print "program SIGINT Interrupted"
	sys.exit(0)

HOST_NAME = ''
PORT_NUMBER = 8009
vmRecoverySystem = VmRecoverySystem()

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		self.log_message("Command: %s Path: %s Headers: %r" %(self.command, self.path, self.headers.items()))
		if(self.path[:7]=="/pslist"):
			vmname = self.path[8:]	
			self.sendPsList( vmname)
	def sendPsList(self, vmname):
			
			plist = []
			
			kvm_host = kvm.KVM(unix.Local())
			kvm_vms = kvm_host.vms
			if not vmname in kvm_vms or kvm_host.state(vmname)!=kvm.RUNNING:
				del plist[:]
				logging.info(vmname+"not valid")
			else:
				try:
					data = vmRecoverySystem.Monitor.GetVMProcesses(vmname)
					for task in data:
						plist.append(str(task.pid)+" "+str(task.comm))
				except exceptions.AddrSpaceError, e:
					logging.exception(e)
					logging.info(vmname+" profile not valid")		
				except Exception, e:
					logging.exception(e)
			logging.info("Send plist:"+';'.join(plist))
			self.sendPage("text/html", ';'.join(plist))
	def sendPage(self, type, body):
		self.send_response(200)
		self.send_header("Content-type", type)
		self.send_header("Content-length", str(len(body)) )
		self.end_headers()
		self.wfile.write(body)
def httpd():
	server_class = BaseHTTPServer.HTTPServer
	#pdb.set_trace()
	
	Httpd = server_class((HOST_NAME, PORT_NUMBER), Handler)
	try:
		logging.info("Http service started")
		Httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	logging.info("Http service end!")
	httpd.server_close()
def initLogger():
    for h in logging.getLogger().handlers:
	    logging.getLogger().removeHandler(h)

    logFormatter = logging.Formatter("%(asctime)s - %(threadName)s - [%(levelname)-5.5s] %(message)s")
    fileHandler = logging.FileHandler("./{0}.log".format('csdvmm'), mode='w')
    fileHandler.setFormatter(logFormatter)
    logging.getLogger().addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logging.getLogger().addHandler(consoleHandler)
    
    logging.getLogger().setLevel(logging.INFO)

    #logging.basicConfig(level=logging.INFO, filename='csdvmm.log')
    
	
if __name__ == "__main__":
    #config.add_help_hook(list_plugins)
    #pdb.set_trace()

    initLogger() 
    signal.signal(signal.SIGINT, sigint_handler)
    logging.info('Starting program')

    try:
	f = Thread(target=httpd, args=())	
	f.daemon = True
	f.start()
	
	vmRecoverySystem.Execute_forever() 
#pdb.set_trace()	
    except Exception, ex:
        #if config.DEBUG:
            debug.post_mortem()
	    logging.exception(ex)
        #else:
        #    raise
    except KeyboardInterrupt:
        print "Interrupted"
	sys.exit(0)
