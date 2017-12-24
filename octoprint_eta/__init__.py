# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.util import RepeatedTimer
import time

class DisplayETAPlugin(octoprint.plugin.ProgressPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        self.eta_string = "-"
        self.eta_strftime = "%H:%M:%S"
        self.timer = RepeatedTimer(15.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)

    def fromTimer(self):
        self.eta_string = self.calculate_ETA()
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
        
    def calculate_ETA(self):
        currentData = self._printer.get_current_data()
        if not currentData["progress"]["printTimeLeft"]:
            return "-"
        current_time = time.localtime(time.time())
        finish_time = time.localtime(time.time() + currentData["progress"]["printTimeLeft"])
        strtime = time.strftime(self.eta_strftime, finish_time)
        strdate = ""
        if finish_time.tm_mday > current_time.tm_mday:
            if finish_time.tm_mday == current_time.tm_mday + 1:
                strdate = " Tomorrow"
            else:
                strdate = " Day %s" % finish_time.tm_mday
        return strtime + strdate
            
        
        
    def on_print_progress(self,storage, path, progress):
        self.eta_string = self.calculate_ETA()
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
    def on_event(self,event, payload):
        if event.startswith('Print'):
            if event not in {"PrintStarted","PrintResumed"}:
                self.eta_string="-"
                self.timer.cancel()
            else:
                self.eta_string = self.calculate_ETA()
                self.timer.cancel()
                self.timer = RepeatedTimer(10.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)
                self.timer.start()
            self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
            
    def get_assets(self):
        return {
            "js": ["js/displayeta.js"]
        } 


    def get_update_information(self):
        return {
            "display-eta":dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="pablogventura",
                repo="Octoprint-ETA",

                pip="https://github.com/pablogventura/Octoprint-ETA/archive/{target}.zip"
                )
            }

__plugin_name__ = "Display ETA"
__plugin_identifier = "display-eta"
__plugin_version__ = "1.0.1"
__plugin_description__ = "Show finish time (ETA time) for current print."
__plugin_implementation__ = DisplayETAPlugin()

__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}

