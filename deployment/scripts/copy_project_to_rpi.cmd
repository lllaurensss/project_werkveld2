@echo off
set "LOCAL_FOLDER_PATH=C:\pers_project\proj_werkveld_2"
set "PI_USER=envirosense"
set "PI_ADDRESS=192.168.0.210"
set "DESTINATION_PATH=/home/envirosense/sensor_app/"

scp -r "%LOCAL_FOLDER_PATH%" %PI_USER%@%PI_ADDRESS%:%DESTINATION_PATH%
