#!/usr/bin/env python

#############################################################################
# Celestica
#
# Component contains an implementation of SONiC Platform Base API and
# provides the components firmware management function
#
#############################################################################
import sys, getopt
import json
import os.path
import shutil
import shlex
import subprocess

try:
    from sonic_platform_base.component_base import ComponentBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

CPLD_ADDR_MAPPING = {
    "CPLD": "3-0060",
}
SYSFS_PATH = "/sys/bus/i2c/devices/"
BIOS_VERSION_PATH = "/sys/class/dmi/id/bios_version"
COMPONENT_NAME_LIST = ["CPLD", "BIOS"]
COMPONENT_DES_LIST = ["CPLD","Basic Input/Output System"]


class Component(ComponentBase):
    """Platform-specific Component class"""

    DEVICE_TYPE = "component"

    def __init__(self, component_index):
        ComponentBase.__init__(self)
        self.index = component_index
        self.name = self.get_name()

    def __run_command(self, command):
        # Run bash command and print output to stdout
        try:
            process = subprocess.Popen(
                shlex.split(command), stdout=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
            rc = process.poll()
            if rc != 0:
                return False
        except:
            return False
        return True

    def __get_bios_version(self):
        # Retrieves the BIOS firmware version
        try:
            with open(BIOS_VERSION_PATH, 'r') as fd:
                bios_version = fd.read()
                return bios_version.strip()
        except Exception as e:
            return None

    def get_sysfs_value(self, addr, name):
        # Retrieves the cpld register value
        #cmd = "echo {1} > {0}; cat {0}".format(SYSFS_PATH, addr)
        cmd = "cat {0}{1}/{2}".format(SYSFS_PATH, addr, name)
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        print "raw_data=%s"%raw_data
        if err is not '':
            return None
        return raw_data.strip()

    def __get_cpld_version(self):
        # Retrieves the CPLD firmware version
        cpld_version = dict()
        for cpld_name in CPLD_ADDR_MAPPING:
            try:
                cpld_addr = CPLD_ADDR_MAPPING[cpld_name]
                cpld_version_raw=self.get_sysfs_value(cpld_addr, "version")
                print "cpld_version_raw=%s"%cpld_version_raw
                #cpld_version_raw = self.get_register_value(cpld_addr)
                #cpld_version_str = "{}.{}".format(int(cpld_version_raw[2], 16), int(
                #    cpld_version_raw[3], 16)) if cpld_version_raw is not None else 'None'
                cpld_version[cpld_name] = "{}".format(int(cpld_version_raw,16))
            except Exception as e:
                cpld_version[cpld_name] = 'None'
        
        print"cpld_version=%s"%cpld_version
        return cpld_version

    def get_name(self):
        """
        Retrieves the name of the component
         Returns:
            A string containing the name of the component
        """
        return COMPONENT_NAME_LIST[self.index]

    def get_description(self):
        """
        Retrieves the description of the component
            Returns:
            A string containing the description of the component
        """
        return COMPONENT_DES_LIST[self.index]

    def get_firmware_version(self):
        """
        Retrieves the firmware version of module
        Returns:
            string: The firmware versions of the module
        """
        fw_version = None

        if self.name == "BIOS":
            fw_version = self.__get_bios_version()
        elif "CPLD" in self.name:
            cpld_version = self.__get_cpld_version()
            fw_version = cpld_version.get(self.name)

        return fw_version

    def install_firmware(self, image_path):
        """
        Install firmware to module
        Args:
            image_path: A string, path to firmware image
        Returns:
            A boolean, True if install successfully, False if not
        """
        if not os.path.isfile(image_path):
            return False
 
        if self.name == "BIOS":
            print "Not supported"
            return False
 
        return self.__run_command(install_command)


def main(argv):
    print"Start to debug"
    com=Component(0)
    #print "cpld=%s"%com._Component__get_cpld_version()
    #com.name="BIOS"
    com.name="CPLD"
    print"vernios=%s"%com.get_firmware_version()
    
if __name__ == "__main__":
    main(sys.argv[1:])
        