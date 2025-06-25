# OExec
Just another way of kexec for ARM(Mainly Android) devices.

# Features
* Create boot items, save and load them

## WIP
* Scanning for boot partitions
* Extracting boot.img files and using them. (Couldn't get it working on my device, lmk if you can do this.)

# How to use?
> [!IMPORTANT]  
> This was only tested in postmarketOS.

* Cd to the directory that OExec is in.
* run `python OExec.py`
* The app will explain stuff.

# How to "port" for a device?
* This section is meant for DeviceSpecific folder that doesn't have your device.
* Create a new ini file, name it `manufacturer-codename.ini` (replace them)
* The file should be in this kind of format, example from samsung-goyavewifi:
```ini
[bootargs]
staticbootargs = console=tty0 loglevel=6 mem=1024M init=/init ram=1024M
dynamicbootargs = lcd_id lcd_base wfixnv cordon fgu_init
```
* `staticbootargs` should have arguments that don't change.
* `dynamicbootargs` should have arguments that changes, these should not have value (like `aaa=bbb` to just `aaa` in here) and separated with space.