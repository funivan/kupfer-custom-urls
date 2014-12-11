# -*- coding: UTF-8 -*-
from __future__ import with_statement

__kupfer_name__ = _("Custom urls")
__kupfer_sources__ = ("CustomUrlSource", )
__description__ = _("Navigate to custom urls from list")
__version__ = "0.0.1"
__author__ = "Ivan Scherbak <dev@funivan.com>"

import gtk

import os.path
import subprocess
import re


from kupfer import config
from kupfer import plugin_support

from kupfer.obj import objects
from kupfer.obj.base import Source
from kupfer.obj.helplib import FilesystemWatchMixin

from kupfer.objects import UrlLeaf, Leaf, Source

CONFIG_FILENAME = 'custom_urls.cfg'

'''
Allow user to define own urls.
Example of configuration file (default file located in ~/.config/kupfer/custom_urls.cfg'):

blog = http://funivan.com
admin = http://localhost/admin
test = http://test


'''

__kupfer_settings__ = plugin_support.PluginSettings(
    {
        "key": "change_file_location",
        "label": _("Change file location"),
        "type": bool,
        "value": False,
    },
    {
        "key" : "path_to_file",
        "label": _("Path to custom config files ( delimiter ; )"),
        "type": str,
        "value": "",
    },
)




class CustomUrlSource (Source, FilesystemWatchMixin):
    appleaf_content_id = "custom-url"

    def __init__(self):
        Source.__init__(self, name=_('CustomUrlSource'))
        self.loaded = False
        self.items = []
        __kupfer_settings__.connect("plugin-setting-changed", self._refresh_settings);

    def _refresh_settings(self, settings, key, value):
        self.loaded = False

    def is_dynamic(self):
        return True;
    
    def get_items(self):
        
        self.output_debug("Items")
        if self.loaded: 
            self.output_debug('load from cache')
            return self.items

        filesToLoad=[]

        if __kupfer_settings__["change_file_location"]: 
            filesConfig = __kupfer_settings__["path_to_file"]
            filesToLoad = filesConfig.split(';')
        else:
            filesToLoad.append(config.get_config_file(CONFIG_FILENAME))
            

        self.items = []

        for filePath in filesToLoad:
            if not os.path.isfile(filePath):
                self.output_debug('File does not exist', filePath)
                continue
            
            self.output_debug('loading sources', filePath)        
            ins = open( filePath, "r" )
            
            for line in ins:
                matchObj = re.match( r'([^=]+)=(.*)$', line.strip(), re.M|re.I)
                if matchObj:
                    self.items.append(UrlLeaf(matchObj.group(2).strip(), matchObj.group(1).strip()))

            ins.close()   

        self.output_debug(self.items);
        self.output_debug('mark_for_update');
        self.loaded = True
        return self.items
        
        
    def get_description(self):
        return _(__description__)

    def get_gicon(self):
        return self.get_leaf_repr() and self.get_leaf_repr().get_gicon()
    
    def get_icon_name(self):
        return "web-browser"

    def provides(self):
        yield UrlLeaf
