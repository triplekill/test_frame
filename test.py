#################################################################################################################
# command template for testing vmware modules
#################################################################################################################
import vmware_module
import statseeker_module
import local_module
import remote_module
import json

auto_iso_gen = statseeker_module.auto_iso_gen("em0", "10.2.26.155", "255.255.255.0","10.2.26.254", "qa-vm-auto@statseeker.com", "10.1.5.2", "$6$4thfn1RHRHr6mrYA$mz0JES4qk6mxIDx9cUWmttDcnIhN.Svv7/4M3D6OPgA8pNGeEDTKmqoJf6bGepHaMA8lyLnIvlioLf3AyWpRq/", "/home/hang/test_frame/install_conf/installerconfig_mod_5x", "/home/hang/Desktop/build/statseeker_5.0.0_install_64bit.iso",  "auto_test.iso")
test_upload = vmware_module.vmware_datastore_upload("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "auto_test.iso", "datastore2-qa", "auto_install.iso")
test_get = vmware_module.vmware_get_vms("10.2.1.50", "hgu@SS.local", "hguSS!234", False)
test_poweron = vmware_module.vmware_poweron_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, name="qa-vm-auto")
#test_poweroff = vmware_module.vmware_poweroff_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, name="qa-vm-create_test_1")
test_delete = vmware_module.vmware_delete_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, name="qa-vm-auto")
#test_reset = vmware_module.vmware_reset_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, name="qa-vm-create_test_1")
#test_reboot = vmware_module.vmware_soft_reboot_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, name="qa-vm-create_test_1")
list_datastore = vmware_module.vmware_list_datastore_info("10.2.1.50", "hgu@SS.local", "hguSS!234", True)
#clone_vm = vmware_module.vmware_clone_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-test15x", "qa-vm-test142", resource_pool="QA-RP1", power_on=False)
create_vm = vmware_module.vmware_create_vm("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-auto", "datastore2-qa", memoryMB=4096, numCPUs=2)
add_disk = vmware_module.vmware_add_disk("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-auto", "Thick", 400)
add_test_nic = vmware_module.vmware_add_nic("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-auto", "TEST_QA")
#add_ha_nic = vmware_module.vmware_add_nic("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-test146", "HA")
add_cdrom = vmware_module.vmware_add_cdrom("10.2.1.50", "hgu@SS.local", "hguSS!234", True, "qa-vm-auto", "cdrom_test", iso="[datastore2-qa] auto_install.iso")
test_licence = statseeker_module.licence("10.2.26.155", "77284604-3779060166", "statseeker", "qa")
wait_for_ping = local_module.ping_test("10.2.26.155", "600")
wait_for_ssh = remote_module.ssh_check("statseeker@10.2.26.155", "qa")
test_add_route = remote_module.add_route("10.2.26.155", "qa", True, route="10.138.0.0/16", gateway="10.2.26.100")
test_add_scan_range = statseeker_module.add_scan_range("10.2.26.155", "statseeker", "qa", "10.100.0.0/16", "10.120.0.0/16", "10.121.0.0/16")
run_command = remote_module.run_command("10.2.26.155", "statseeker", "qa", "echo lala","nim-discover -R")
test_add_scan_range = statseeker_module.add_scan_range("10.2.26.155", "statseeker", "qa", "10.100.0.0/16", "10.120.0.0/16", "10.121.0.0/16")
test_add_community = statseeker_module.add_community("10.2.26.155", "statseeker", "qa", "public", "private", "lala")
#print(test_poweroff.main())
print (test_get.main())
#print (test_reboot.main())
#print (list_datastore.main())
#print (clone_vm.main())
#print (test_reset.main())
#print (test_poweroff.main())

#print(test_delete.main())
#print(auto_iso_gen.main())
#print(test_upload.main())
#print(create_vm.main())
#print(add_disk.main())
#print(add_test_nic.main())
#print(add_cdrom.main())
#print(test_poweron.main())
#print(wait_for_ssh.main())
#print(wait_for_ping.main())
#print(test_licence.main())
#print(test_add_route.main())
#print test_add_scan_range.main()
#print(run_command.main())
#print(test_add_community.main())






def suc_ext(result):
    print result
    s = json.loads(result)["success"]
    if s == "True":
        return True
    else:
        return False

#suc_ext(test_delete.main()):
#if suc_ext(auto_iso_gen.main()):
#    if suc_ext(test_upload.main()):
#        if suc_ext(create_vm.main()):
#            if suc_ext(add_disk.main()):
#                if suc_ext(add_test_nic.main()):
#                    if suc_ext(add_cdrom.main()):
#                        if suc_ext(test_poweron.main()):
#                            if suc_ext(wait_for_ssh.main()):
#                                 suc_ext(test_licence.main())           


#################################################################################################################



