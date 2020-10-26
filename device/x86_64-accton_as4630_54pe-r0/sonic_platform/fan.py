#!/usr/bin/env python

#############################################################################
# Celestica
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################

import json
import math
import os.path
import sys

try:
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PSU_FAN_MAX_RPM = 26688

CPLD_I2C_PATH = "/sys/bus/i2c/devices/3-0060/fan_"
PSU_HWMON_I2C_PATH ="/sys/bus/i2c/devices/{}-00{}/"
PSU_I2C_MAPPING = {
    0: {
        "num": 10,
        "addr": "58"
    },
    1: {
        "num": 11,
        "addr": "59"
    },
}


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_tray_index, fan_index=0, is_psu_fan=False, psu_index=0):
        self.fan_index = fan_index
        self.fan_tray_index = fan_tray_index
        self.is_psu_fan = is_psu_fan
        
        # Set hwmon path
        
        
        #    0: "/sys/bus/i2c/drivers/as4630_54pe_cpld/3-0060/", 
        #    1: "24-004b/hwmon/hwmon*/", 
        #    2: "25-004a/hwmon/hwmon*/"
        #}.get(self.index, None)
       
        
        if self.is_psu_fan:
            self.psu_index = psu_index
            self.psu_i2c_num = PSU_I2C_MAPPING[self.psu_index]["num"]
            self.psu_i2c_addr = PSU_I2C_MAPPING[self.psu_index]["addr"]
            self.psu_hwmon_path = PSU_HWMON_I2C_PATH.format(
                self.psu_i2c_num, self.psu_i2c_addr)

        # dx010 fan attributes
        # Two EMC2305s located at i2c-13-4d and i2c-13-2e
        # to control a dual-fan module.
        self.emc2305_chip_mapping = [
            {
                'device': "13-002e",
                'index_map': [2, 1, 4, 5, 3]
            },
            {
                'device': "13-004d",
                'index_map': [2, 4, 5, 3, 1]
            }
        ]
        
        FanBase.__init__(self)

    def __read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return ""

    
    def __write_txt_file(self, file_path, value):
        try:
            with open(file_path, 'w') as fd:
                fd.write(str(value))
        except:
            return False
        return True

    def get_direction(self):
        """
        Retrieves the direction of fan
        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        direction = self.FAN_DIRECTION_EXHAUST

        if not self.is_psu_fan:
            dir_str = "{}{}{}".format(CPLD_I2C_PATH, 'direction_', self.fan_tray_index)
            val=self.__read_txt_file(dir_str)
            if val==0:
                direction=self.FAN_DIRECTION_EXHAUST
            else:
                direction=self.FAN_DIRECTION_INTAKE
        else: #For PSU. YPEB1200AM that is F2B.
            print"self.psu_hwmon_path=%s"%self.psu_hwmon_path
            direction=self.FAN_DIRECTION_EXHAUST
        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
                         
        """
        speed = 0
        if self.is_psu_fan:
            psu_fan_path= "{}{}".format(self.psu_hwmon_path, 'psu_fan1_speed_rpm')
            fan_speed_rpm = self.__read_txt_file(psu_fan_path)
            speed = (int(fan_speed_rpm,10))*100/26688
            if speed > 100:
                speed=100
        elif self.get_presence():            
            speed_path = "{}{}".format(CPLD_I2C_PATH, 'duty_cycle_percentage')
            print"speed_path=%s"%speed_path
            speed=self.__read_txt_file(speed_path)
        return int(speed)
            
    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        Note:
            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use
        """
        raise NotImplementedError

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        #Not supported
        return False

    def set_speed(self, speed):
        """
        Sets the fan speed
        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 0 (off) to 100 (full speed)
        Returns:
            A boolean, True if speed is set successfully, False if not

        """
        
        if not self.is_psu_fan and self.get_presence():            
            speed_path = "{}{}".format(CPLD_I2C_PATH, 'duty_cycle_percentage')            
            return self.__write_txt_file(speed_path, int(speed))

        return False

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        #Not supported
        return False

   
    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        present_path = "{}{}{}".format(CPLD_I2C_PATH, 'present_', self.fan_tray_index+1)
        print "present_str=%s"%present_path
        val=self.__read_txt_file(present_path)
        print"val=%s"%val 

        if not self.is_psu_fan:
            return int(val, 10)
        else:
            return True
        
def main(argv):
    print"Start to debug fan.py"
    
    my_fan=Fan(0, 0 , 0 ,0)
    print "my_fan1 present =%d"%my_fan.get_presence()
    my_fan=Fan(1, 0 , 0 ,0)
    print "my_fan2 present =%d"%my_fan.get_presence()
    my_fan=Fan(2, 0 , 0 ,0)
    print "my_fan3 present =%d"%my_fan.get_presence()
    
    my_fan=Fan(0, 0 , 0 ,0)
    print "my_fan1 speed =%d"%my_fan.get_speed()
    my_fan=Fan(1, 0 , 0 ,0)
    print "my_fan2 speed =%d"%my_fan.get_speed()
    my_fan=Fan(2, 0 , 0 ,0)
    print "my_fan3 speed =%d"%my_fan.get_speed()
    
    my_fan=Fan(0, 0 , 0 ,0)
    my_fan.set_speed(50)
    print "my_fan1 set speed= to 50%"
    
    
    my_fan=Fan(0, 0 , 0 ,0)
    print "my_fan1 dir =%s"%my_fan.get_direction()
    my_fan=Fan(1, 0 , 0 ,0)
    print "my_fan2 dir =%s"%my_fan.get_direction()
    my_fan=Fan(2, 0 , 0 ,0)
    print "my_fan3 dir =%s"%my_fan.get_direction()
    
    
    my_fan=Fan(0, 0, 1 ,0)
    print "my_fan psu1 speed =%d"%my_fan.get_speed()
    my_fan=Fan(1, 0 , 1 ,1)
    print "my_fan psu2 speed =%d"%my_fan.get_speed()
    
    my_fan=Fan(1, 0 , 1 ,0)
    print "my_fan psu1 dir =%s"%my_fan.get_direction()
    my_fan=Fan(2, 0 , 1 ,1)
    print "my_fan psu2 dir =%s"%my_fan.get_direction()
    
    
if __name__ == "__main__":
    main(sys.argv[1:])