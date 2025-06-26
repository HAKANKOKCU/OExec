import os
import pathlib
import configparser
import subprocess
import readline

workdir = pathlib.Path.home() / ".local/var/OExec"
deviceName = None

# TUI

def tui():
    tuiLoadDevice()
    tuiMainMenu()

def tuiMainMenu():
    print("Options: ")
    print("1: Scan for kernel and ramdisk")
    print("2: Use kernel and ramdisk")
    print("3: Extract boot image and use it")
    bootoption = 4
    boots = getRecentBoots()
    for boot in boots:
        print(str(bootoption) + ": " + boot)
        bootoption += 1
    
    selection = tuiDoSelection()
    if (selection == 1):
        print("Not implemented.")
    elif (selection == 2):
        kernel = tuiDoFileSelection("Kernel: ")
        dtb = tuiDoFileSelection("DTB: ")
        ramdiskType = tuiDoStringSelection(("initrd", "ramdisk"),"Ramdisk type (initrd/ramdisk): ")
        ramdisk = tuiDoFileSelection("Ramdisk: ")
        
        tuiBootMenu(createBootConfig(kernel, ramdiskType, ramdisk, dtb, ""))
    elif (selection == 3):
        name = tuiDoWriteFolderSelection("Save name (Like a directory name): ", workdir / "RecentBoots")
        if (not os.path.exists(workdir / "RecentBoots" / name)):
            os.mkdir(workdir / "RecentBoots" / name)
        bootimage = tuiDoFileSelection("Boot.img file: ")
        r = subprocess.call(("unpackbootimg", "-i", bootimage, "-o", str(workdir / "RecentBoots" / name)))
        if r == 0:
            imgname = os.path.basename(bootimage)
            kernel = str(workdir / "RecentBoots" / name / (imgname + "-kernel"))
            ramdisk = str(workdir / "RecentBoots" / name / (imgname + "-ramdisk"))
            dtb = str(workdir / "RecentBoots" / name / (imgname + "-dt"))
            ba = open(workdir / "RecentBoots" / name / (imgname + "-cmdline"))
            bootargs = ba.read()
            ba.close()
            cfg = createBootConfig(kernel, "ramdisk", ramdisk, dtb, bootargs)
            saveBootConfig(name, cfg)
            tuiBootMenu(cfg)
    elif (selection > 3 and len(boots) >= selection - 3):
        cfg = loadBootConfig(boots[selection - 4])
        if (cfg != None):
            tuiBootMenu(cfg)
    else:
        print("Invalid Selection.")
    tuiMainMenu()

def tuiLoadDevice(): # Load the device if it wasn't loaded for some reasons like user didn't pick or was removed.
    global deviceName
    if (deviceName == None):
        device = input("Type device name (inside DeviceSpecific folder): ")
        getDevice(device)
        if (deviceName == None):
            tuiLoadDevice()
        else:
            d = open(workdir / "device" , "w")
            d.write(device)
            d.close()

def tuiDoSelection(): # Make numeric selection.
    sel = input("Selection: ")
    if (sel.isnumeric()):
        return int(sel)
    else:
        return tuiDoSelection()

def tuiDoStringSelection(l, text):
    sel = input(text)
    if sel in l:
        return sel
    else:
        return tuiDoStringSelection(l, text)

def tuiDoFileSelection(prompt):
    sel = input(prompt)
    if os.path.exists(sel) and os.path.isfile(sel):
        return sel
    else:
        return tuiDoFileSelection(prompt)
    
def tuiDoUniqueFSSelection(prompt, append):
    sel = input(prompt)
    if not os.path.exists(append / sel):
        return sel
    else:
        return tuiDoUniqueFSSelection(prompt, append)

def tuiDoWriteFolderSelection(prompt, append):
    sel = input(prompt)
    if not os.path.exists(append / sel):
        return sel
    elif os.path.isdir(append / sel) and input("Do you want to overwrite (y/[n])? ") == "y":
        return sel
    else:
        return tuiDoWriteFolderSelection(prompt, append)

def tuiBootMenu(config): # Menu after boot is ready.
    kernel = config["bootconfig"]["kernel"]
    ramdiskType = config["bootconfig"]["ramdiskType"]
    ramdisk = config["bootconfig"]["ramdisk"]
    dtb = config["bootconfig"]["dtb"]
    bootargsAppend = config["bootconfig"]["bootargsAppend"]
    action = input("What would you like to do? ([a]rgs, [i]nfo, [s]ave, [b]oot, [e]xit): ")
    loop = True
    if len(action) > 0:
        if (action[0] == "a"):
            bootargsAppendNew = input("boot arguments [" + bootargsAppend + "]: ")
            if (bootargsAppendNew != ""):
                config["bootconfig"]["bootargsAppend"] = bootargsAppendNew
        elif (action[0] == "i"):
            print("Kernel: " + kernel)
            print("Ramdisk type: " + ramdiskType)
            print("Ramdisk: " + ramdisk)
            print("DTB: " + dtb)
            print("Boot arguments append: " + bootargsAppend)
        elif (action[0] == "s"):
            saveConfig = tuiDoWriteFolderSelection("Type the name for the save (like a directory name): ", workdir / "RecentBoots")
            if (saveConfig != ""):
                saveBootConfig(saveConfig, config)
        elif (action[0] == "b"):
            boot(config)
        elif (action[0] == "e"):
            print("Exiting to main menu...")
            loop = False
    if loop:
        tuiBootMenu(config)



# Normal functions

def getDevice(device):
    global deviceName
    if device == None: # Load the last device.
        if os.path.exists(workdir / "device"):
            d = open(workdir / "device")
            device = d.read()
            d.close()
    if device == None: # If none, deviceName is already normally None. So we just return.
        return
    if os.path.exists("./DeviceSpecific/" + device + ".ini"):
        deviceName = device

def getRecentBoots():
    bootspath = workdir / "RecentBoots"
    if not os.path.exists(bootspath):
        os.mkdir(bootspath)
    boots = [f for f in os.listdir(bootspath) if os.path.isdir(os.path.join(bootspath, f))]
    return boots

def createBootConfig(kernel, ramdiskType, ramdisk, dtb, bootargsAppend): # Create boot config from parameters.
    config = configparser.ConfigParser()
    config["bootconfig"] = {}
    config["bootconfig"]["kernel"] = kernel
    config["bootconfig"]["ramdiskType"] = ramdiskType
    config["bootconfig"]["ramdisk"] = ramdisk
    config["bootconfig"]["dtb"] = dtb
    config["bootconfig"]["bootargsAppend"] = bootargsAppend
    return config
    
def saveBootConfig(configname, config):
    if (not os.path.exists(workdir / "RecentBoots" / configname)):
        os.mkdir(workdir / "RecentBoots" / configname)
    savefile = open(workdir / "RecentBoots" / configname / "config.ini", 'w')
    config.write(savefile)

def loadBootConfig(configname):
    if (os.path.exists(workdir / "RecentBoots" / configname)):
        config = configparser.ConfigParser()
        config.read(workdir / "RecentBoots" / configname / "config.ini")
        # Execute the function that was given as parameter.
        return config
    return None

def boot(config):
    kernel = config["bootconfig"]["kernel"]
    ramdiskType = config["bootconfig"]["ramdiskType"]
    ramdisk = config["bootconfig"]["ramdisk"]
    dtb = config["bootconfig"]["dtb"]
    bootargsAppend = config["bootconfig"]["bootargsAppend"]

    global deviceName
    config = configparser.ConfigParser()
    config.read("./DeviceSpecific/" + deviceName + ".ini") # getDevice already checks if this exists.
    bootargs = config["commandline"]["staticbootargs"] + " " # Add space to end as dynamic/appends will be put after this.
    
    dynamicbootargs = config["commandline"]["dynamicbootargs"].split(" ")
    # We read /proc/cmdline to get the "dynamic" ones that can change.
    pcmdline = open("/proc/cmdline") 
    cmdline = pcmdline.read()[:-1] # have to remove newline...
    pcmdline.close()
    # Split by space to split arguments.
    args = cmdline.split(" ")
    for dba in args:
        arg = dba.split("=") # split with = to get name/value
        if arg[0] in dynamicbootargs:
            bootargs += dba.replace("\n","") + " " # add as argument.
    # Add appends
    bootargs += bootargsAppend
    kexeccmd = ("-d", "-l", kernel, "--dtb=%s" % dtb)
    if ramdiskType == "initrd":
        kexeccmd += ("--initrd=%s" % ramdisk,)
    elif ramdiskType == "ramdisk":
        kexeccmd += ("--ramdisk=%s" % ramdisk,)
    
    if (config["boot"]["bootmode"] == "forceBeforeArguments"):
        kexeccmd += ("-f",) # Force the kexec because it would cause problems on some devices.
    
    bootargs = bootargs.replace("\\","\\\\")
    if (config["commandline"]["cmdmode"] == "append"):
        kexeccmd += ("--append=%s" % bootargs,)
    elif (config["commandline"]["cmdmode"] == "cmdline"):
        kexeccmd += ("--command-line=%s" % bootargs,)
    
    print(kexeccmd) # Print for debug
    # Execute
    r = subprocess.call(("sudo", "kexec") + kexeccmd)
    if (r == 0 and config["boot"]["bootmode"] == "normal"):
        subprocess.call(("sudo", "kexec", "-e"))
    # If it didn't fail, this wouldn't have a way to exit back. So, ignoring.

# Start
# TODO: Improve this...
if not os.path.exists(pathlib.Path.home() / ".local/"):
    os.mkdir(pathlib.Path.home() / ".local/")
if not os.path.exists(pathlib.Path.home() / ".local/var/"):
    os.mkdir(pathlib.Path.home() / ".local/var/")
if not os.path.exists(workdir):
    os.mkdir(workdir)

getDevice(None) # Load the last device.
print("Welcome to OExec!")
# Start the Terminal UI. Idea: Add another UI types. Maybe QT/GTK?
tui()