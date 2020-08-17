import configparser
from datetime import datetime
from .somfy import Somfy
import logging

from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_OFF, STATE_ON, CONF_SCAN_INTERVAL

from . import DOMAIN as SOMFY_DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_DEVICE_CLASS = "Safety"
SENSOR_NAME = "somfy_sensor"

SCAN_INTERVAL = timedelta(minutes=1)

def setup_platform(hass, config, add_entities, discovery_info=None):
    #_LOGGER.debug("############# Init sensor #############")
    _LOGGER.info("Setup platform...") 
    #_LOGGER.info(hass)
    #_LOGGER.info(config)
    #_LOGGER.info(add_entities)
    #_LOGGER.info(discovery_info)
    #if discovery_info is None:
    #    return
    
    controller = hass.data[SOMFY_DOMAIN]["controller"]
    #_LOGGER.debug(controller)
    devs = []
    devs.append(SomfySensor(hass, controller))

    add_entities(devs, True)

    _LOGGER.info("Fin setup platform...") 
    
class SomfySensor(Entity):

    def __init__(self, hass, somfy):
        _LOGGER.debug("Init sensor " + SENSOR_NAME)
        self.somfy = somfy
        self._attributes = {}
        self._state = None
        self._available = False
        self._hass = hass
        self._status = ""
        self._name = SENSOR_NAME
        self._device_class = DEFAULT_DEVICE_CLASS
        self._last_updated = None
    
    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
    
    @property
    def last_updated(self):
        return self._last_updated

    @property
    def device_class(self):
        """Return the class of this sensor, from DEVICE_CLASSES."""
        return self._device_class

    def update(self):
        _state_result = None
        #_get_state_counter = 0
        try: 
            self.somfy.login()
            _LOGGER.debug("Logged on Somfy")
        except Exception as inst:
            _LOGGER.debug(type(inst))    # the exception instance
            _LOGGER.debug(inst.args)     # arguments stored in .args
            _LOGGER.debug(inst)
            _LOGGER.debug("Error when trying to log in")
        #while _state_result == None and _get_state_counter < 3:
        try:    
            #_get_state_counter = _get_state_counter+1
            _state_result = self.somfy.get_state()
            _LOGGER.debug("Updated states:")
            _LOGGER.debug(_state_result)
            self._hass.data[SOMFY_DOMAIN]["state"] = _state_result
            #self._hass.data[SOMFY_DOMAIN]["elements"] = _elements
            self._available = True
        except Exception as inst:
            _LOGGER.debug(type(inst))    # the exception instance
            _LOGGER.debug(inst.args)     # arguments stored in .args
            _LOGGER.debug(inst)
            _LOGGER.debug("Error when trying to get state")    


        # try: 
        #     _LOGGER.debug("############# Update sensor #############")
        #     _LOGGER.debug("------------------------- Login Somfy -------------------------")
        #     self.somfy.login()
        #     _state_result = self.somfy.get_state()
        #     _LOGGER.debug("state")
        #     _LOGGER.debug(_state_result)
        #     #_elements = self.somfy.get_elements()
        #     #_LOGGER.debug(_elements)
        #     _LOGGER.debug("------------------------- Logout Somfy -------------------------")
        #     self.somfy.logout()
        #     self._hass.data[SOMFY_DOMAIN]["state"] = _state_result
        #     #self._hass.data[SOMFY_DOMAIN]["elements"] = _elements
        #     self._available = True
        #     _LOGGER.debug(self._hass.data[SOMFY_DOMAIN]["state"])
        #     #_LOGGER.debug(self._hass.data[SOMFY_DOMAIN]["elements"])
        # except:
        #     _LOGGER.debug("Error when trying to log in")
        #     self._state = STATE_OFF

        try:
            self.somfy.logout()
        except Exception as inst:
            _LOGGER.debug(type(inst))    # the exception instance
            _LOGGER.debug(inst.args)     # arguments stored in .args
            _LOGGER.debug(inst)
            _LOGGER.debug("Error when trying to log out !")


        if _state_result:
            _LOGGER.debug("State is full")
            self._state = STATE_ON
            self._last_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        else:
            _LOGGER.debug("No state")
            self._state = STATE_OFF
