# OExec
Just another UI way of kexec for ARM(Mainly Android) devices.

# Features
* TUI
* Create boot items, save and load them

## WIP
* Scanning for boot partitions
* Extracting boot.img files and using them. (Couldn't get it working on my device, let me know if you can do this.)

# How to use?
> [!IMPORTANT]  
> This was only tested in postmarketOS and armv7 architecture.
> 
> This is currently a "Works on my device" project.

* Install `kexec-tools` and optionally `unpackbootimg`
* Cd to the directory that OExec is in.
* run `python OExec.py`
* The app will explain stuff.

# How to "port" for a device?
* This section is meant for DeviceSpecific folder that doesn't have your device.
* Create a new ini file, name it `manufacturer-codename.ini` (replace them)
* The file should be in this kind of format, example from `samsung-goyavewifi`:
```ini
[commandline]
staticbootargs = console=tty0 loglevel=6 mem=1024M init=/init ram=1024M
dynamicbootargs = lcd_id lcd_base wfixnv wruntimenv cordon fgu_init
cmdmode = cmdline
[boot]
bootmode = normal
```
* `staticbootargs` should have arguments that don't change. Make sure that they don't crash the device.
* `dynamicbootargs` should have arguments that changes, these should not have value (like `aaa=bbb` to just `aaa` in here) and separated with space. Make sure that they don't crash the device. If you are unsure if they change or not, feel free to just put them to dynamicbootargs. They might change on other devices.
* `cmdmode` should be `cmdline` or `append`. Choose which one works best.
* `bootmode` should be `forceBeforeArguments` or `normal`. Choose which one works best. Feel free to open a issue for other cases so I can add them. (Yes, for some reason changing the order does help...)
