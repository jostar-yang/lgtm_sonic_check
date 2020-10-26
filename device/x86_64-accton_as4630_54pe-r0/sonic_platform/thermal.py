#!/usr/bin/env python

#############################################################################
# Celestica
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import re
import os.path
import sys
import glob

try:
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = []
    SYSFS_PATH = "/sys/bus/i2c/devices"
    SS_CONFIG_PATH = "/usr/share/sonic/device/x86_64-cel_seastone-r0/sensors.conf"

    def __init__(self, thermal_index):
        self.index = thermal_index

        # Add thermal name
        self.THERMAL_NAME_LIST.append("Temp sensor 1")
        self.THERMAL_NAME_LIST.append("Temp sensor 2")
        self.THERMAL_NAME_LIST.append("Temp sensor 3")        

        # Set hwmon path
        i2c_path = {
            0: "14-0048/hwmon/hwmon*/", 
            1: "24-004b/hwmon/hwmon*/", 
            2: "25-004a/hwmon/hwmon*/"
        }.get(self.index, None)
          
        self.hwmon_path = "{}/{}".format(self.SYSFS_PATH, i2c_path)
        print "self.hwmon_path=%s"%self.hwmon_path
        self.ss_key = self.THERMAL_NAME_LIST[self.index]
        self.ss_index = 1

    def __read_txt_file(self, file_path):
        for filename in glob.glob(file_path):
            try:
                with open(filename, 'r') as fd:
                    #data = fd.read()
                    data =fd.readline().rstrip()
                    return data
                    #return data.strip()
            except IOError as e:
                pass

    def __get_temp(self, temp_file):
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        raw_temp = self.__read_txt_file(temp_file_path)
        temp = float(raw_temp)/1000
        #temp = (raw_temp)/1000
        print"temp=%f"%temp        
        return "{:.3f}".format(temp)

    def __set_threshold(self, file_name, temperature):
        temp_file_path = os.path.join(self.hwmon_path, file_name)
        try:
            with open(temp_file_path, 'w') as fd:
                fd.write(str(temperature))
            return True
        except IOError:
            return False

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        temp_file = "temp{}_input".format(self.ss_index)
        return self.__get_temp(temp_file)

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        temp_file = "temp{}_max".format(self.ss_index)
        return self.__get_temp(temp_file)

    def set_high_threshold(self, temperature):
        """
        Sets the high threshold temperature of thermal
        Args :
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125
        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        print("Not supported")
        return False
       #return is_set & file_set

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        return self.THERMAL_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        temp_file = "temp{}_input".format(self.ss_index)
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        return os.path.isfile(temp_file_path)

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if not self.get_presence():
            return False

        fault_file = "temp{}_fault".format(self.ss_index)
        fault_file_path = os.path.join(self.hwmon_path, fault_file)
        if not os.path.isfile(fault_file_path):
            return True

        raw_txt = self.__read_txt_file(fault_file_path)
        return int(raw_txt) == 0


def main(argv):
    print"Start to debug thermal.py"
    my_thermal=Thermal(0)
    print "my_thermal.get_temperature=%s"%my_thermal.get_temperature()
    print "high_threshold=%s"%my_thermal.get_high_threshold()
    my_thermal=Thermal(1)
    print "my_thermal.get_temperature=%s"%my_thermal.get_temperature()
    print "high_threshold=%s"%my_thermal.get_high_threshold()

    my_thermal=Thermal(2)
    print "my_thermal.get_temperature=%s"%my_thermal.get_temperature()
    print "high_threshold=%s"%my_thermal.get_high_threshold()

if __name__ == "__main__":
    main(sys.argv[1:])