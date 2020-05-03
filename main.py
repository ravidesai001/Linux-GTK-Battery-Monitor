import gi
import os
import time
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

builder = Gtk.Builder()
builder.add_from_file("interface.glade")

# plans for system screen on time.
# leave application running in the background.
# if status = discharging then start timer.
# label timer as screen on time.
# pause timer when lid is closed


class Timer:

    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def start(self):
        self.start_time = time.time()
        
    def stop(self):
        self.stop_time = time.time()

    @property
    def time_elapsed(self):
        return round(time.time() - self.start_time)


class BatteryMonitor:

    def __init__(self):
        pass
    

    @staticmethod
    def read_battery_stats():
        stats = {}
        path = "/sys/class/power_supply/BAT0/"
        directory = os.fsencode(path)
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                filename = os.fsdecode(file)
                stats[filename] = open(os.path.join(directory, file), "r").read()
        return stats
            
    @staticmethod
    def out_stats():
        fields = builder.get_object("list_box")
        stats = BatteryMonitor.read_battery_stats()
        i = 0
        for stat in stats:
            i+=1
            fields.insert(Gtk.Label(label=stat + stats[stat]), i)


    @staticmethod
    def parse_uevent():
        file_path = "/sys/class/power_supply/BAT0/uevent"
        content_string = open(file_path, "r").read()
        stats = content_string.split("\n")
        return stats
    
    @staticmethod
    def build_list():
        fields = builder.get_object("list_box")
        stats = BatteryMonitor.parse_uevent()
        row = 0
        for statistic in stats:
            row+=1
            fields.insert(Gtk.Label(label=statistic), row)
        

    @staticmethod
    def set_key_stats():
        percentage = builder.get_object("percentage_label")
        discharge = builder.get_object("discharge_label")
        health = builder.get_object("health_label")
        for stat in BatteryMonitor.parse_uevent():
            if stat.startswith("POWER_SUPPLY_CAPACITY="):
                percentage_val = BatteryMonitor.get_value(stat)
            elif stat.startswith("POWER_SUPPLY_VOLTAGE_NOW="):
                voltage_val = int(BatteryMonitor.get_value(stat))/1000000
            elif stat.startswith("POWER_SUPPLY_CURRENT_NOW="):
                current_val = int(BatteryMonitor.get_value(stat))/1000000
            elif stat.startswith("POWER_SUPPLY_CHARGE_FULL="):  
                full_charge_cap = int(BatteryMonitor.get_value(stat))
            elif stat.startswith("POWER_SUPPLY_CHARGE_FULL_DESIGN="):  
                full_charge_design_cap = int(BatteryMonitor.get_value(stat))
            
        percentage.set_text("Battery Percentage: {}%".format(percentage_val))
        discharge.set_text("Discharge Rate: {} W".format(round(voltage_val * current_val, 1)))
        health.set_text("Battery Health: {}%".format(round((full_charge_cap/full_charge_design_cap)*100)))
        
        
    @staticmethod
    # true for open, false for closed
    def lid_open():
        file_path = "/proc/acpi/button/lid/LID0/state"
        content_string = open(file_path, "r").read()
        # if the string contains a 'c' it is closed, otherwise open
        if 'c' in content_string:
            return False
        return True

    @staticmethod
    def discharging():
        stats = BatteryMonitor.parse_uevent()
        for stat in stats:
            if stat.startswith("POWER_SUPPLY_STATUS="):
                status = BatteryMonitor.get_value(stat)
        
        if status == "Discharging":
            return True
        return False

    @staticmethod
    def get_value(string):
        i = 0; start = 0
        for char in string:
            i += 1
            if char == "=":
                start = i
        return string[start:]


global stop_threads
stop_threads = False
# while discharging and the lid is open, let the screen time accumulate every 30 seconds.
# add accumulated time to screen time instance variable.
def calc_screen_time():
    screen_time = 0
    # BatteryMonitor.discharging() and BatteryMonitor.lid_open()
    while not stop_threads:
        if BatteryMonitor.discharging() and BatteryMonitor.lid_open():
            screen_time += 1
            builder.get_object("screen_time").set_text("Screen On Time: {}".format(screen_time))
            time.sleep(1)
            BatteryMonitor.set_key_stats()
        elif BatteryMonitor.discharging() and  not BatteryMonitor.lid_open():
            time.sleep(1)


timer_thread = threading.Thread(target = calc_screen_time)
timer_thread.start()

def quit(self, *args):
    stop_threads = True
    Gtk.main_quit()


# need to modify the gtk main loop to be updating gui components on time interval
handlers = {
    "onDestroy" : quit
}
builder.connect_signals(handlers)
window = builder.get_object("window")
BatteryMonitor.set_key_stats()
BatteryMonitor.build_list()
window.show_all()
Gtk.main()


    