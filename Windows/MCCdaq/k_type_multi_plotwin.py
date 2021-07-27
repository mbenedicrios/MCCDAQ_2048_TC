#!/usr/bin/env python
#must first install InstaCal from http://www.mccdaq.com/Software-Downloads.aspx
#Github for MCC daq https://github.com/mccdaq
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
from __future__ import absolute_import, division, print_function
from time import sleep
#from builtins import *
from os import system
from sys import stdout
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.shape_base import block
import csv

from mcculw.enums import InfoType, BoardInfo, AiChanType, TcType, TempScale, TInOptions
from mcculw import ul
from mcculw.device_info import DaqDeviceInfo

################################################
#Settings
################################################
#Physical channels on the MCCDAQ that have TCs installed
channels=[0,1,2,3,5,6]
#How long to wait between measurements in seconds
interval_seconds=1
#Name of the file that will be saved in the same directory as the program
file_name='doors on fans side 1 labelling'

def run_example(channels=channels,interval=interval_seconds):
    """
    Configures MCC DAQ and prints list of channel readings from K type TCs
    Keyword arguments:
    channels -- list of channels to read    
    """
    device_to_show = "USB-2408"
    board_num = 0

    # Verify board is Board 0 in InstaCal.  If not, show message...
    print("Looking for Board 0 in InstaCal to be {0} series...".format(device_to_show))

    try:
        # Get the devices name...
        board_name = ul.get_board_name(board_num)
        # Get the devices name...
        board_name = ul.get_board_name(board_num)

    except Exception as e:
        if ul.ErrorCode(1):
            # No board at that number throws error
            print("\nNo board found at Board 0.")
            print(e)
            return

    else:
        if device_to_show in board_name:
            # Board 0 is the desired device...
            print("{0} found as Board number {1}.\n".format(board_name, board_num))
            ul.flash_led(board_num)

        else:
            # Board 0 is NOT desired device...
            print("\nNo {0} series found as Board 0. Please run InstaCal.".format(device_to_show))
            return



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
    plt.xlabel('time [s]')
    plt.ylabel('temperature [F]')
    plt.title('TC measurements')
    #plt.legend()

    #Configure all of the channels to read tcs
    for channel in channels:
        config_channel(board_num,channel)
    
    try:
        while True:
            try:
                print('Please enter CTRL + C to terminate the process\n')
                #Retrieve temperature readings and save them in a list
                temp_list = poll_channels(board_num,channels)
                #Append measurements to previous readings
                final_temp_list.append(temp_list)
                temp_list_simple.append(temp_list)
                #append a new time 
                time_list.append(i_time*interval_seconds)
                #plot temps
                print('plotting')
                fig.clear()
                print('length of measures = {}'.format(len(temp_list_simple)))
                for i in range(len(temp_list)):
                    plt.plot(time_list,[pt[i] for pt in temp_list_simple],label = 'channel {}'.format(channels[i]))
                #plt.show()
                plt.legend()
                fig.canvas.draw()
                fig.canvas.flush_events()
                #print('plotted')
                #increment time counter
                i_time+=1
                #Wait for specified interval before making another reading
                sleep(interval)
            except Exception as e:
                print('\n', e)
                break

    except KeyboardInterrupt:
        pass


    with open('{}.csv'.format(file_name),'w') as f: 
        writer = csv.writer(f)
        writer.writerows(final_temp_list)

"""
def reset_cursor():
    stdout.write('\033[1;1H')
"""

def config_channel(board_num,channel_number=0):
    """
    Configures MCC DAQ channels to read as TCs
    Keyword arguments:
    channel_number -- number of analog channel on MCC DAQ
    """
    channel = channel_number
    ul.set_config(
        InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
        AiChanType.TC)
    # Set thermocouple type to type J
    ul.set_config(
        InfoType.BOARDINFO, board_num, channel, BoardInfo.CHANTCTYPE,
        TcType.J)
    # Set the temperature scale to Fahrenheit
    ul.set_config(
        InfoType.BOARDINFO, board_num, channel, BoardInfo.TEMPSCALE,
        TempScale.FAHRENHEIT)
    # Set data rate to 60Hz
    ul.set_config(
        InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 60)


def poll_channels(board_num,channel_numbers):
    """
    Poll MCC DAQ channels to read TC temperature
    Keyword arguments:
    channel_numbers -- list of channel numbers to poll
    """
    #Initiate an empty list to store temperature readings
    temp_list=[]

    for channel in channel_numbers:
        #Config channels
        options=TInOptions.NOFILTER
        #Read indivdiual channels
        value_temperature = ul.t_in(board_num, channel, TempScale.FAHRENHEIT, options)
        #Append temperatures to the list
        temp_list.append(value_temperature)
        #Print out channels and temperatures
        #print("Channel {:d} \n  {:.3f} Degrees.".format(channel_numbers, temp_list))
    temp_list=[int(a) for a in temp_list]
    print(str(channel_numbers)[1:-1])
    print(str(temp_list)[1:-1])
    return(temp_list)




if __name__ == '__main__':
    run_example()