# Project Feeder
## An open source pet feeder project

This repository is a collection of all the files used in this project.

## The image file hosting went down, so here is a summary of what you need to do to get it working:
1) Get a clean Rapsbian image running on your pi, and make sure you're able to run an Apache server / MySQL server localy. 

	>Easy way to connect to your Pi is using an ethernet cable straight to your pc and using the APIPA-range. After doing this you can connect to the address 169.254.10.1 over SSH

2)	Move the files to their location.
	- **Frontend:** RPi Code/www &rightarrow; /var/
	- **Backend:** RPI Code/project &rightarrow; /home/pi/ (or custom user)
3) Connect to the database through MySql-Workbench
	
	>Use the same APIPA-address: 169.254.10.1
	
4) Load the sql-database by running the dump-file on it **[thisRepo/Database-export/feederdb_dump.sql]**
5) Make sure the config file is correctly configured:**[RPi Code/project/config.py]**
  
	```python
	[connector_python]
	user = <Configured user>
	host = 127.0.0.1	#This is the ip for localhost and shouldn't be changed if ran localy
	port = 3306		    #Shouldn't be changed except if you changed the port for some reason
	password = mysql	#Here the password you've chosen for the database
	database = feederdb	#Here the name of the database

	[application_config]
	driver = 'SQL Server'
	```
6) Autorun the service on boot **[RPi Code/project/config.py]**
> There are a lot of ways to do this, find something that works for you.

Everything else for building this project can be found here:
https://www.instructables.com/Project-Feeder/

## Chrome extension (optional)
I've also implemented a chrome extension, this is in no way mandatory to let it work but is a nice to have.
To get it to work on your system you just load the folder <b>Feeder extension</b> in Chrome developper mode.
