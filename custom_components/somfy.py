# -*- coding: utf-8 -*-
#from bs4 import BeautifulSoup
import mechanicalsoup
import configparser
import io
import ssl
import re
import json

class SomfyException(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        return repr(self.value)

class Somfy:
    def __init__(self, url, password, codes):
        ssl._create_default_https_context = ssl._create_unverified_context
        # self.config = config
        self.url = url
        self.id = id
        self.password = password
        self.codes = codes
        self.browser = mechanicalsoup.StatefulBrowser(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36')

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    def login(self, reset_cnx = False):
        login_html = self.browser.open(self.url + "/gb/login.htm")
        login_soup = self.browser.get_current_page()
        self._check_error(login_soup, reset_cnx)
        authentication_code = login_soup.find('form').find('table')

        authentication_code = authentication_code.findAll('tr')[2].find('b').find(text=True)
    
        self.browser.select_form(nr=0)
        self.browser["password"] = self.password
        key = ("key_%s" % authentication_code)
        self.browser["key"] = self.codes[key]

        self.browser.submit_selected()


    def logout(self):
        self.browser.open(self.url + "/logout.htm")

    def set_zone(self,zone):
        self.browser.open(self.url + "/gb/u_pilotage.htm")
        self._check_error(self.browser.get_current_page())
        self.browser.select_form(nr =0)
        self.browser["hidden"] = "hidden"
        submit = self.browser.get_current_page().find("div", {"id": "groupdrive"}).find('input', attrs={"name": zone})
        self.browser.select_form().choose_submit(submit)
        self.browser.submit_selected()

    def set_zone_a(self):
        self.set_zone("btn_zone_on_A")

    def set_zone_b(self):
        self.set_zone("btn_zone_on_B")

    def set_zone_c(self):
        self.set_zone("btn_zone_on_C")

    def set_all_zone(self):
        self.set_zone("btn_zone_on_ABC")

    def unset_all_zone(self):
        self.set_zone("btn_zone_off_ABC")

    def get_state(self):
        state_response = self.browser.open(self.url + "/gb/u_pilotage.htm")
        page_soup = self.browser.get_current_page()
        self._check_error(page_soup)
        result = self.get_general_state(page_soup)
        result.update(self.get_zone_state(page_soup))

        return result

    def get_zone_state(self, state_soup):
        groupstate_soup = state_soup.find("div", {"id": "groupstate"})

        # possible return for each group : alarmoff = / ???
        # Alarm: noalarm or alarm 
        # Armed: alarmon or alarmoff
        def get_zone(zone):
            zone_soup = groupstate_soup.find("div", {"id": "group"+zone}).findAll("div")
            armed_class = zone_soup[0]['class'][0]
            alarm_class = zone_soup[1]['class'][0]
            return { "zone_"+zone+"_armed" : armed_class == "alarmon", "zone_"+zone+"_alarm" : alarm_class != "noalarm" } 

        result = get_zone("a")
        result.update(get_zone("b"))
        result.update(get_zone("c"))

        return result

    def get_general_state(self, state_soup):
        alarmstate_soup = state_soup.find("div", {"id": "alarmstate"}).findAll()

        #print(alarmstate_soup)

        # States based on Home Assistant device classes
        # https://developers.home-assistant.io/docs/core/entity/binary-sensor/
        
        # possible return : pbattery_ok
        # True if battery low
        def get_battery_state():
            return { "battery_low" : alarmstate_soup[3]['class'][0] != "pbattery_ok"}

        # possible return : pcom_ok
        def get_communication_state():
            return { "communication" : alarmstate_soup[4]['class'][0] == "pcom_ok"}

        # possible return : pdoor_ok = door closed, pdoor_nok = dor open
        # True if open
        def get_door_state():
            return { "door" : alarmstate_soup[5]['class'][0] != "pdoor_ok"}

        # possible return : phouse_ok = No alarm, phouse_int = Intrusion
        def get_alarm_state():
            return { "alarm" : alarmstate_soup[6]['class'][0] != "phouse_ok"}

        # possible return : pbox_ok
        def get_material_state():
            return { "material" : alarmstate_soup[7]['class'][0] == "pbox_ok"}

        # possible return : pgsm_5_ok
        def get_gsm_state():
            return { "gsm" : alarmstate_soup[8]['class'][0] == "pgsm_5_ok"}

        # possible return : pcam_serv_off
        def get_camera_state():
            return { "camera" : alarmstate_soup[9]['class'][0] != "pcam_serv_off"}

        result = get_battery_state()
        result.update(get_communication_state())
        result.update(get_door_state())
        result.update(get_alarm_state())
        result.update(get_material_state())
        result.update(get_gsm_state())
        result.update(get_camera_state())

        return result
        
    def _check_error(self, soup, reset_cnx = False):
        if soup.find("div", {"id": "titlebar"}).findAll()[0].find(text=True) == "Error":
            error_code = soup.find('div', {"id": "infobox"}).findAll('b')[0].find(text=True)
            
            if reset_cnx:
              self.browser.select_form(nr =0)
              self.browser.submit_selected()
            
            if '(0x0904)' == error_code:
                raise SomfyException("Nombre d'essais maximum atteint")
            if '(0x1100)' == error_code:
                raise SomfyException("Code errone")
            if '(0x0902)' == error_code:
                raise SomfyException("Session deja ouverte")
            if '(0x0812)' == error_code:
                raise SomfyException("Mauvais login/password")
            if '(0x0903)' == error_code:
                raise SomfyException("Droit d'acces insuffisant")
            else:
                raise SomfyException("Error "+error_code)

