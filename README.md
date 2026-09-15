# Elora Vision Desktop
Desktop app for the Elora Vision project (receiver module only)

## Installing
`pip install -r requirements.txt`


#### Ubuntu Users:

if you are getting error complaining that `tkinter` in not installed on Ubuntu, run the below line of code to install it on your Ubuntu machine.

`sudo apt-get install python3-tk`


`python main.py`


serial.serialutil.SerialException: [Errno 13] could not open port /dev/ttyACM0: [Errno 13] Permission denied: '/dev/ttyACM0'

sudo chmod 666 /dev/ttyACM0




