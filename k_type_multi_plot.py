#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Must first install libuldaq for linux https://github.com/mccdaq/uldaq/
#Will not run in virtual environment 

"""
File:                       USB2408_t_in.py

Library Call Demonstrated:  ai_device.t_in().

Purpose:                    Setup and read from an analog input, one sample at a time.

Demonstration:              How to configure and read temperature value from device.

Other Library Calls:        daq_device.flash_LED()
                            ai_config.set_chan_type()
                            ai_config.set_chan_data_rate()
                            ai_config.set_chan_tc_type()
                            ai_config.set_chan_otd_mode()

Special Requirements:       Connect a thermocouple to CH0H and CH0L terminals
                            of the USB-2408 series.


"""
from __future__ import print_function
from time import sleep
from os import system
from sys import stdout
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.shape_base import block

from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType,
                   AiInputMode, OtdMode, AiChanType, TcType, TempScale, TempUnit, TInFlag)
import csv



################################################
#Settings
################################################
#Physical channels on the MCCDAQ that have TCs installed
channels=[0,1,2,3,5,6]
#How long to wait between measurements in seconds
interval_seconds=1
#Name of the file that will be saved in the same directory as the program
file_name='test_temps'

def run_example(channels=channels,interval=interval_seconds):
    """
    Configures MCC DAQ and prints list of channel readings from K type TCs
    Keyword arguments:
    channels -- list of channels to read    
    """
    device_to_show = "USB-2408"
    board_num = 0
    board_found = False
    daq_device = None

    descriptor_index = 0
    descriptor = 0
    interface_type = InterfaceType.USB

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            raise Exception('Error: No DAQ devices found')

        print('Found', number_of_devices, 'DAQ device(s):')
        for i in range(number_of_devices):
            board_name = devices[i].product_name
            if device_to_show in board_name:
                print("{0} found, assigned Board number {1}.\n".format(board_name, board_num))
                print('  ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')
                board_found = True

                # Create the DAQ device object associated with the specified descriptor index.
                daq_device = DaqDevice(devices[descriptor_index])

                # Establish a connection to the DAQ device.
                descriptor = daq_device.get_descriptor()
                print('\nConnecting to', descriptor.dev_string, '- please wait...')
                daq_device.connect()
                daq_device.flash_led(5)

        if not board_found:
            raise Exception('Error:  No {0} found.\n'.format(device_to_show))

        daq_device.get_config()
        ai_device = daq_device.get_ai_device()
        ai_info = ai_device.get_info()  # not used but left for user
        ai_config = ai_device.get_config()

        #Set the board variables
        input_mode = AiInputMode.DIFFERENTIAL
        scale = TempScale.FAHRENHEIT
        t_in_flag = TInFlag.DEFAULT

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Function demonstrated: ai_device.t_in()')
        print('    Input mode: ', input_mode.name)
        print('    Scale: ', scale.name)
        print('Please enter CTRL + C to terminate the process\n')

        try:
            input('\nHit ENTER to continue\n')
        except (NameError, SyntaxError):
            pass

        system('clear')

        #Initialize a list of channels
        final_temp_list = [['channel {}'.format(channel) for channel in channels]]
        temp_list_simple=[]
        #Initialize a list of measurement times
        time_list = []
        #Initialize a time incremental counter
        i_time=0
        #Initialize a plot
        fig=plt.gcf()
        fig.show()
        fig.canvas.draw()
        plt.legend()
        try:
            while True:
                try:
                    reset_cursor()
                    #Retrieve temperature readings and save them in a list
                    temp_list = poll_channels(ai_config,ai_device,scale,t_in_flag,channels)
                    #Append measurements to previous readings
                    final_temp_list.append(temp_list)
                    temp_list_simple.append(temp_list)
                    #append a new time 
                    time_list.append(i_time*interval_seconds)
                    #plot temps
                    fig.clear()
                    print('length of measures = {}'.format(len(temp_list_simple)))
                    #Add legend with channel names
                    for i in range(len(temp_list)):
                        plt.plot(time_list,[pt[i] for pt in temp_list_simple],label = 'channel {}'.format(channels[i]))
                    plt.xlabel('time [s]')
                    plt.ylabel('temperature [F]')
                    plt.title('TC measurements')
                    plt.legend()
                    #update and show plot
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    #print('plotted')
                    #increment time counter
                    i_time+=1
                    #Wait for specified interval before making another reading
                    sleep(interval)
                except (ValueError, NameError, SyntaxError):
                    break

        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        #Release device on termination
        if daq_device:
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()
        #Save final csv file
        with open('{}.csv'.format(file_name),'w') as f: 
            writer = csv.writer(f)
            writer.writerows(final_temp_list)


def reset_cursor():
    stdout.write('\033[1;1H')

def config_channel(ai_config,channel_number=0):
    """
    Configures MCC DAQ channels to read as TCs
    Keyword arguments:
    channel_number -- number of analog channel on MCC DAQ
    """
    channel = channel_number
    ai_config.set_chan_type(channel, AiChanType.TC)
    ai_config.set_chan_data_rate(channel, 60)
    ai_config.set_chan_tc_type(channel, TcType.K)
    ai_config.set_chan_otd_mode(channel, OtdMode.ENABLED)

def poll_channel(ai_config, ai_device,scale,t_in_flag,channel_number=0):
    """
    Poll MCC DAQ channels to read TC temperature
    Keyword arguments:
    channel_number -- number of analog channel on MCC DAQ
    channel number to be configed    
    """
    channel = channel_number
    value_temperature = ai_device.t_in(channel, scale, t_in_flag)
    print("Channel {:d}:  {:.3f} Degrees.".format(channel, value_temperature))

def poll_channels(ai_config,ai_device,scale,t_in_flag,channel_numbers):
    """
    Poll MCC DAQ channels to read TC temperature
    Keyword arguments:
    channel_numbers -- list of channel numbers to poll
    """
    #Initiate an empty list to store temperature readings
    temp_list=[]

    for channel in channel_numbers:
        #Config channels
        config_channel(ai_config,channel)
        #Read indivdiual channels
        value_temperature = ai_device.t_in(channel, scale, t_in_flag)
        #Append temperatures to the list
        temp_list.append(value_temperature)
        #Print out channels and temperatures
        #print("Channel {:d} \n  {:.3f} Degrees.".format(channel_numbers, temp_list))
    temp_list=[int(a) for a in temp_list]
    print(str(channel_numbers)[1:-1])
    print(str(temp_list)[1:-1])
    return(temp_list)

def set_up_plot(data):
    fig = plt.figure()

    for p in range(50):
        p=3
        updated_x=x+p
        updated_y=np.cos(x)
        plt.plot(updated_x,updated_y)
        plt.draw()  
        x=updated_x
        y=updated_y
        plt.pause(0.2)
        fig.clear()



if __name__ == '__main__':
    run_example()