# MCCDAQ_2048_TC
Tool to run MCCDAQ 2048 to measure and log thermocouple temperatures
Must first install libuldaq for linux https://github.com/mccdaq/uldaq/
Will not run in virtual environment 

channels must match the physical channels that have TCs 

Interval should be set to the number of seconds between measurements

file name is the CSV file name that data will be written to.
if filename is not updated then old data will be overwritten.
Must exit program ( Ctrl + C) to finish program and write data
