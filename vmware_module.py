# This file contains all the test realted to vmware application
# It will follow the same convention, all modules must inherit from vmware_base and coantains a main function

import base
import atexit
import ssl
import json
import meta

from vm_tools import tasks
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

#
# Custom exception
#
class ERROR_exception(Exception):
        def __init__(self, msg):
            self.msg = msg

#
# vmware_connect_test module
#

class vmware_connect_test(base.vmware_base):
    description = "testing the connection between local host and vmware host"

    def __init__(self, host, user, password):
        super(vmware_connect_test, self).__init__("vmware_conncet_test", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password

    def main(self):
        
        return_dict = {}
        message = []

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

        except Exception as e:
            print e
            return_dict["success"] = "false"
            meta_dict = meta.meta_header(self.host, self.user, message, ERROR=error.msg)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)

        return_dict["success"] = "true"
        meta_dict = meta.meta_header(self.host, self.user, "ok")
        return_dict["meta"] = meta_dict.main()
        return json.dumps(return_dict)
        
        


#
# vmware_get_vms module
#

class vmware_get_vms(base.vmware_base):
    description = "show all vms on a vmware host"

    def __init__(self, host, user, password, json):
        super(vmware_get_vms, self).__init__("vmware_get_vms", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.json = json

    def print_vm_info(self, virtual_machine):
        """
        Print information for a particular virtual machine or recurse into a
        folder with depth protection
        """
        summary = virtual_machine.summary
        print("Name       : ", summary.config.name)
        print("Template   : ", summary.config.template)
        print("Path       : ", summary.config.vmPathName)
        print("Guest      : ", summary.config.guestFullName)
        print("Instance UUID : ", summary.config.instanceUuid)
        print("Bios UUID     : ", summary.config.uuid)
        annotation = summary.config.annotation
        if annotation:
            print("Annotation : ", annotation)
        print("State      : ", summary.runtime.powerState)
        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            tools_version = summary.guest.toolsStatus
            if tools_version is not None:
                print("VMware-tools: ", tools_version)
            else:
                print("Vmware-tools: None")
            if ip_address:
                print("IP         : ", ip_address)
            else:
                print("IP         : None")
        if summary.runtime.question is not None:
            print("Question  : ", summary.runtime.question.text)
        print("")

    def construct_dict(self, virtual_machine):
        """
        construct part of a json string, it's then concatenated to the VMS dictionary

        """

        summary = virtual_machine.summary
        vm = {}
        vm["Name"] = summary.config.name
        vm["Template"] = summary.config.template
        vm["Path"] = summary.config.vmPathName
        vm["Guest"] = summary.config.guestFullName
        vm["Instance UUID"] = summary.config.instanceUuid
        vm["Bios UUID"] = summary.config.uuid

        if summary.config.annotation:
            vm["Annotation"] = summary.config.annotation

        vm["State"] = summary.runtime.powerState

        if summary.guest.toolsStatus:
            vm["VMware-tools"] = summary.guest.toolsStatus

        if summary.guest.ipAddress:
            vm["IP"] = summary.guest.ipAddress
        else:
            vm["IP"] = None

        if summary.runtime.question is not None:
            vm["Question"] = summary.runtime.question.text

        return vm


    def main(self):
        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            content = service_instance.RetrieveContent()
            container = content.rootFolder  # Starting point to look into
            viewType = [vim.VirtualMachine] # Object types to look for
            recursive = True 
            containerView = content.viewManager.CreateContainerView(
                    container, viewType, recursive)

            children = containerView.view

            return_dict = {}
            return_dict["result"] = []

            for child in children:

                if not self.json:
                    self.print_vm_info(child)

                else:
                    return_dict["result"].append(self.construct_dict(child))


        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            
            if self.json:
                return_dict["success"] = "false"
                message = "oops"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=error.msg)
                return_dict["meta"] = meta_dict.main() 
                return json.dumps(return_dict)
            else:
                return False
        
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, "ok")
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
        

#
# vmware_poweroff_vm module
#

class vmware_poweroff_vm(base.vmware_base):
    description = "power off a vm"

    def __init__(self, host, user, password, json, **search):
        super(vmware_poweroff_vm, self).__init__("vmware_poweroff_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.search = search
        self.json = json

    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            return_dict = {}

            if "uuid" in self.search:
                VM = service_instance.content.searchIndex.FindByUuid(None, self.search["uuid"],
                                                                     True, False)
            elif "ip" in self.search:
                VM = service_instance.content.searchIndex.FindByIp(None, self.search["ip"], True)

            elif "name" in self.search:
                VM = service_instance.content.searchIndex.FindByDnsName(None, self.search["name"],
                                                                        True)
            else:
                raise ERROR_exception("No valid search criteria given")

            if VM is None:
                raise ERROR_exception("Unable to locate VirtualMachine.")

            message = []

            message.append("Found: {0}".format(VM.name))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))
            message.append("Attempting to power off {0}".format(VM.name))

            if not self.json:
                for i in message[0:3]: print i

            TASK = VM.PowerOffVM_Task()
            tasks.wait_for_tasks(service_instance, [TASK])

            message.append("{0}".format(TASK.info.state))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))

            if not self.json:
                for i in message[3:5]: print i
         
        #   exception capture

        except (ERROR_exception,vmodl.MethodFault)   as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
        
   
#
# vmware_poweron_vm module: this module will not accept ipaddress as filter, off machines don't have ip field
#

class vmware_poweron_vm(base.vmware_base):
    description = "power on a vm"

    def __init__(self, host, user, password, json, **search):
        super(vmware_poweron_vm, self).__init__("vmware_poweron_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.search = search
        self.json = json

    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)
            
            return_dict = {}
            message = []

            if "uuid" in self.search:
                VM = service_instance.content.searchIndex.FindByUuid(None, self.search["uuid"],
                                                                     True, False)
            elif "name" in self.search:
                VM = service_instance.content.searchIndex.FindByDnsName(None, self.search["name"],
                                                                        True)
            else:
                raise ERROR_exception("No valid search criteria given")

            if VM is None:
                raise ERROR_exception("Unable to locate VirtualMachine.")

            message.append("Found: {0}".format(VM.name))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))
            message.append("Attempting to power on {0}".format(VM.name))

            if not self.json:
                for i in message[0:3]: print i

            TASK = VM.PowerOnVM_Task()
            tasks.wait_for_tasks(service_instance, [TASK])

            message.append("{0}".format(TASK.info.state))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))

            if not self.json:
                for i in message[3:5]: print i
         
         #   exception capture

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
     
       
#
# vmware_delete_vm module
#
  
class vmware_delete_vm(base.vmware_base):
    description = "delete a vm"

    def __init__(self, host, user, password, json, **search):
        super(vmware_delete_vm, self).__init__("vmware_delete_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.search = search
        self.json = json

    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)
            
            return_dict = {}
            message = []

            if "uuid" in self.search:
                VM = service_instance.content.searchIndex.FindByUuid(None, self.search["uuid"],
                                                                     True, False)
            elif "ip" in self.search:
                VM = service_instance.content.searchIndex.FindByIp(None, self.search["ip"], True)

            elif "name" in self.search:
                VM = service_instance.content.searchIndex.FindByDnsName(None, self.search["name"],
                                                                        True)
            else:
                raise ERROR_exception("No valid search criteria given")

            if VM is None:
                raise ERROR_exception("Unable to locate VirtualMachine.")

            message.append("Found: {0}".format(VM.name))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))

            if not self.json:
                for i in message[0:2]: print i

            if VM.runtime.powerState != "poweredOff":
                message.append("Attempting to power off {0}".format(VM.name))

                TASK = VM.PowerOffVM_Task()
                tasks.wait_for_tasks(service_instance, [TASK])
            
                message.append("{0}".format(TASK.info.state))
                message.append("The current powerState is: {0}".format(VM.runtime.powerState))

                if not self.json:
                    for i in message[-3: -1]: print i

            message.append("Attempting to delete {0}".format(VM.name))
            
            TASK = VM.Destroy_Task()
            tasks.wait_for_tasks(service_instance, [TASK])
            
            message.append("{0}".format(TASK.info.state))
            
            if not self.json:
                for i in message[-2: -1]: print i
            
          #   exception capture

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
        

#
# vmware_reset_vm module: this module reset a vm (hard reset)
#

class vmware_reset_vm(base.vmware_base):
    description = "hard reset a vm"

    def __init__(self, host, user, password, json, **search):
        super(vmware_reset_vm, self).__init__("vmware_reset_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.json = json
        self.search = search

    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            return_dict = {}
            message = []

            if "uuid" in self.search:
                VM = service_instance.content.searchIndex.FindByUuid(None, self.search["uuid"],
                                                                     True, False)
            elif "ip" in self.search:
                VM = service_instance.content.searchIndex.FindByIp(None, self.search["ip"], True)

            elif "name" in self.search:
                VM = service_instance.content.searchIndex.FindByDnsName(None, self.search["name"],
                                                                        True)
            else:
                raise ERROR_exception("No valid search criteria given")

            if VM is None:
                raise ERROR_exception("Unable to locate VirtualMachine.")

            message.append("Found: {0}".format(VM.name))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))
            message.append("Attempting to reset {0}".format(VM.name))
            TASK = VM.ResetVM_Task()
            tasks.wait_for_tasks(service_instance, [TASK])
            message.append("{0}".format(TASK.info.state))

            if not self.json:
                for i in message: 
                    print i

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
        

#
# vmware_soft_reboot_vm module: this module send target vm a  reboot signal(no gurantee for a reboot though)
#

class vmware_soft_reboot_vm(base.vmware_base):
    description = "send vm a soft reboot signal"

    def __init__(self, host, user, password, json, **search):
        super(vmware_soft_reboot_vm, self).__init__("vmware_soft_reboot_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.search = search
        self.json = json

    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            return_dict = {}
            message = []

            if "uuid" in self.search:
                VM = service_instance.content.searchIndex.FindByUuid(None, self.search["uuid"],
                                                                     True, False)
            elif "ip" in self.search:
                VM = service_instance.content.searchIndex.FindByIp(None, self.search["ip"], True)

            elif "name" in self.search:
                VM = service_instance.content.searchIndex.FindByDnsName(None, self.search["name"],
                                                                        True)
            else:
                raise ERROR_exception("No valid search criteria given")

            if VM is None:
                raise ERROR_exception("Unable to locate VirtualMachine.")

                       
            message.append("Found: {0}".format(VM.name))
            message.append("The current powerState is: {0}".format(VM.runtime.powerState))
            message.append("Attempting to reboot {0}".format(VM.name))

            TASK = VM.RebootGuest()
            tasks.wait_for_tasks(service_instance, [TASK])
            
            if not self.json: 
                for i in message: 
                    print i

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True
        
        
#
#  wmare_list_datastore_info module: still haven't decide whether I want json output yet (definitely)
#

class vmware_list_datastore_info(base.vmware_base):
    description = "list datastore informations"

    def __init__(self, host, user, password, json):
        super(vmware_list_datastore_info, self).__init__("vmware_list_datastore_info", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.json = json

    def sizeof_fmt(self, num):
        """
        Returns the human readable version of a file size

        :param num:
        :return:
        """
        for item in ['bytes', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, item)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')


    def print_fs(self, host_fs):
        """
        Prints the host file system volume info

        :param host_fs:
        :return:
        """
        print("{}\t{}\t".format("Datastore:     ", host_fs.volume.name))
        print("{}\t{}\t".format("UUID:          ", host_fs.volume.uuid))
        print("{}\t{}\t".format("Capacity:      ", self.sizeof_fmt(
            host_fs.volume.capacity)))
        print("{}\t{}\t".format("VMFS Version:  ", host_fs.volume.version))


    def main(self):

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            message = []
            return_dict = {}

            if not service_instance:
                print("could not connect ot the host with given credentials")
                return False

            content = service_instance.RetrieveContent()

            objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
            esxi_hosts = objview.view
            objview.Destroy()

            datastores = {}

            for esxi_host in esxi_hosts:
                if not self.json:
                    print("{}\t{}\t\n".format("ESXi Host:    ", esxi_host.name))

                # All Filesystems on ESXi host
                storage_system = esxi_host.configManager.storageSystem
                host_file_sys_vol_mount_info = \
                    storage_system.fileSystemVolumeInfo.mountInfo

                datastore_dict = {}
                # Map all filesystems
                for host_mount_info in host_file_sys_vol_mount_info:
                    # Extract only VMFS volumes
                    if host_mount_info.volume.type == "VMFS":

                        extents = host_mount_info.volume.extent
                        if not self.json:
                            self.print_fs(host_mount_info)
                        else:
                            datastore_details = {
                                'uuid': host_mount_info.volume.uuid,
                                'capacity': host_mount_info.volume.capacity,
                                'vmfs_version': host_mount_info.volume.version,
                                'local': host_mount_info.volume.local,
                                'ssd': host_mount_info.volume.ssd
                            }

                        extent_arr = []
                        extent_count = 0
                        for extent in extents:
                            if not self.json:
                                print("{}\t{}\t".format(
                                    "Extent[" + str(extent_count) + "]:",
                                    extent.diskName))
                                extent_count += 1
                            else:
                                # create an array of the devices backing the given
                                # datastore
                                extent_arr.append(extent.diskName)
                                # add the extent array to the datastore info
                                datastore_details['extents'] = extent_arr
                                # associate datastore details with datastore name
                                datastore_dict[host_mount_info.volume.name] = \
                                    datastore_details
                        if not self.json:
                            print

                # associate ESXi host with the datastore it sees
                datastores[esxi_host.name] = datastore_dict

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            return_dict["result"] = datastores
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True


#
# vmware_clone_vm: this modue is designed to clone an existing vm (how is ip address and uuid resolved?)
# clone a vm is okay, but not permitted to power it up, duplicated ip maybe, need to modify
#

class vmware_clone_vm(base.vmware_base):
    description = "this modue is designed to clone an existing vm (how is ip address and uuid resolved?)"

    def __init__(self, host, user, password, json, vm_name, template, **select):
        super(vmware_clone_vm, self).__init__("vmware_clone_vm", "6.0.0")
       
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        
        self.host = host
        self.user = user
        self.password = password
        self.json = json
        self.vm_name = vm_name
        self.template = template
        self.select = select

        elective = ["datacenter_name", "vm_folder", "datastore_name", "cluster_name", "resource_pool",
                    "power_on"]

        for var in elective:
            if var in select:
                setattr(self, var, self.select[var])
            else:
                setattr(self, var, None)


    def get_obj(self, content, vimtype, name):
        """
        Return an object by name, if name is None the
        first found object is returned
        """
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True)
        for c in container.view:
            if name:
                if c.name == name:
                    obj = c
                    break
            else:
                obj = c
                break

        return obj


    def clone_vm(
            self, content, template, vm_name, service_instance,
            datacenter_name, vm_folder, datastore_name,
            cluster_name, resource_pool, power_on):
        """
        Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
        cluster_name, resource_pool, and power_on are all optional.
        """

        # if none git the first one
        datacenter = self.get_obj(content, [vim.Datacenter], datacenter_name)

        if vm_folder:
            destfolder = self.get_obj(content, [vim.Folder], vm_folder)
        else:
            destfolder = datacenter.vmFolder

        if datastore_name:
            datastore = self.get_obj(content, [vim.Datastore], datastore_name)
        else:
            datastore = self.get_obj(
                content, [vim.Datastore], template.datastore[0].info.name)

        # if None, get the first one
        cluster = self.get_obj(content, [vim.ClusterComputeResource], cluster_name)

        if resource_pool:
            resource_pool = self.get_obj(content, [vim.ResourcePool], resource_pool)
        else:
            resource_pool = cluster.resourcePool

        # set customspec
        # guest NIC settings, i.e. "adapter map"
        adaptermaps=[]
        guest_map = vim.vm.customization.AdapterMapping()
        guest_map.adapter = vim.vm.customization.IPSettings()
        guest_map.adapter.ip = vim.vm.customization.FixedIp()
        guest_map.adapter.ip.ipAddress = "10.2.26.158"
        guest_map.adapter.subnetMask = "255.255.255.0"
        adaptermaps.append(guest_map)
        
        # Hostname settings only supports windows and linux bloody hell!
        ident = vim.vm.customization.LinuxPrep()
        ident.domain = "statseeker.com"
        ident.hostName = vim.vm.customization.FixedName()
        ident.hostName.name = vm_name

        # DNS settings
        globalip = vim.vm.customization.GlobalIPSettings()
        globalip.dnsServerList = "10.1.5.2"
        globalip.dnsSuffixList = "statseeker.com"

        customspec = vim.vm.customization.Specification()
        customspec.nicSettingMap = adaptermaps
        customspec.identity = ident
        customspec.globalIPSettings = globalip

        # set relospec
        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = resource_pool

        # set clonespec, note custom spec is required to change ip and domain name
        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = power_on
        clonespec.template = False
        #clonespec.config = vmconf

        #customization of freebsd vms are not supported in vmware as for now, power_on stays false
        #when cloning from vm instead of template
        #clonespec.customization = customspec 
        
        print "cloning VM..."

        TASK = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)

        tasks.wait_for_tasks(service_instance, [TASK])

    
    def main(self):

        return_dict = {}
        message = []

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            content = service_instance.RetrieveContent()
            # template is not a template, it should be able to be a vm as well, fingers crossed
            # is this name the dns name or vm name (need to find out)
            template = self.get_obj(content, [vim.VirtualMachine], self.template)

            if template:
                message.append("Found vm template: " + self.template)
                self.clone_vm(content, template, self.vm_name, service_instance, self.datacenter_name,
                        self.vm_folder, self.datastore_name, self.cluster_name, self.resource_pool,
                        self.power_on)
                       
            else:
                raise ERROR_exception("Can't find specified template")

        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True



#
# vmware_create_vm: this module creates a new vm 
#

class vmware_create_vm(base.vmware_base):
    description="This module is used to create new vm"

    def __init__(self, host, user, password, json, vm_name, datastore, **settings):
        super(vmware_create_vm, self).__init__("vmware_create_vm", "6.0.0")
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.verify_mode = ssl.CERT_NONE
        self.host = host
        self.user = user
        self.password = password
        self.json = json
        self.vm_name = vm_name
        self.datastore = datastore
        self.settings = settings

    def create_dummy_vm(self, param):
        datastore_path = '[' + datastore +']' + param["vm_name"]

        #minimim VM shells
        vmx_file = vim.vm.FileInfo(logDirectory=None,
                               snapshotDirectory=None,
                               suspendDirectory=None,
                               vmPathName=datastore_path)
        
        config = Vim.vm.ConfigSpec(**param)
        config = vim.vm.ConfigSpec(name=vm_name, memoryMB=128, numCPUs=1,
                               files=vmx_file, guestId='dosGuest',
                               version='vmx-07')

        print "Creating VM {}...".format(vm_name)
        task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
        tasks.wait_for_tasks(service_instance, [task])


    def main(self):
        
        return_dict = {}
        message = []

        try:
            service_instance = connect.SmartConnect(host=self.host ,user=self.user,
                    pwd=self.password, port=443, sslContext=self.context)

            atexit.register(connect.Disconnect, service_instance)

            content = service_instance.RetrieveContent()

            datacenter = content.rootFolder.childEntity[0]
            vm_folder = datacenter.vmFolder
            hosts = datacenter.hostFolder.childEntity
            resource_pool = hosts[0].resourcePool


            # define datastore file path
            datastore_path = '[' + self.datastore +']' + self.vm_name

            #creating parameter dictionary
            param = {}
            param["name"] = self.vm_name
            param["files"] = vim.vm.FileInfo(logDirectory=None,
                                 snapshotDirectory=None,
                                 suspendDirectory=None,
                                 vmPathName=datastore_path)
            
            # default setting
            param["memoryMB"] = 1024
            param["numCPUs"] = 1
            param["guestId"] = "freebsd64Guest"
            param["version"] = "vmx-07"
            
            # overwrite and append to default setting by "self.settings"
            for setting in self.settings:
                param[setting] = self.settings[setting]
            
            # Set config spec
            config = vim.vm.ConfigSpec(**param)

            # print "Creating VM {}...".format(vm_name)
            task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
            tasks.wait_for_tasks(service_instance, [task])

            # use some of the params as a returned result, excluding files though
            del param["files"]
            return_dict["result"] = param
        
        except (ERROR_exception,vmodl.MethodFault) as e:

            if self.json:
                return_dict["success"] = "false"
                meta_dict = meta.meta_header(self.host, self.user, message, ERROR=e.msg)
                return_dict["meta"] = meta_dict.main()
                return json.dumps(return_dict)
            else:
                print e.msg
                return False
            
        if self.json:
            return_dict["success"] = "true"
            meta_dict = meta.meta_header(self.host, self.user, message)
            return_dict["meta"] = meta_dict.main()
            return json.dumps(return_dict)
        else:
            return True






