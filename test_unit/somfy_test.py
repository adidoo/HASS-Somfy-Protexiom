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

    def login(self):
        login_html = self.browser.open(self.url + "/gb/login.htm")
        login_soup = self.browser.get_current_page()
        self._check_error(login_soup)
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

        # possible return for each group : alarmoff / ???
        def get_zone(zone):
            zone_soup = groupstate_soup.find("div", {"id": "group"+zone}).findAll("div")
            armed_class = zone_soup[0]['class'][0]
            alarm_class = zone_soup[1]['class'][0]
            return { "zone_"+zone : { "armed" : armed_class == "alarmon", "alarm" : alarm_class != "noalarm" } } 
        def get_zone_a():
            return { "zone_a" : groupstate_soup.find("div", {"id": "groupa"}).find()['class'][0] }

        def get_zone_b():
            return { "zone_b" : groupstate_soup.find("div", {"id": "groupb"}).find()['class'][0] }

        def get_zone_c():
            return { "zone_c" : groupstate_soup.find("div", {"id": "groupc"}).find()['class'][0] }

        result = get_zone("a")
        result.update(get_zone("b"))
        result.update(get_zone("c"))

        return result

    def get_general_state(self, state_soup):
        alarmstate_soup = state_soup.find("div", {"id": "alarmstate"}).findAll()

        #print(alarmstate_soup)

        # possible return : pbattery_ok
        def get_battery_state():
            return { "battery" : alarmstate_soup[3]['class'][0] == "pbattery_ok"}

        # possible return : pcom_ok
        def get_communication_state():
            return { "communication" : alarmstate_soup[4]['class'][0] == "pcom_ok"}

        # possible return : pdoor_ok
        def get_door_state():
            return { "door" : alarmstate_soup[5]['class'][0] == "pdoor_ok"}

        # possible return : phouse_ok
        def get_alarm_state():
            return { "alarm" : alarmstate_soup[6]['class'][0] == "phouse_ok"}

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

    # def get_elements(self):
        # page_response = self.browser.open(self.url + "/gb/u_listelmt.htm")
        # page_soup = self.browser.get_current_page()
        # self._check_error(page_soup)
        
        # result = page_soup.find("div", {"id": "itemlist"})
        
        # extract_elements = re.compile('var\sitem_type\s+=\s(.*);\nvar\sitem_label\s+=\s(.*);\nvar\sitem_pause\s+=\s(.*);\nvar\selt_name\s+=\s(.*);\nvar\selt_code\s+=\s(.*);\nvar\selt_pile\s+=\s(.*);\nvar\selt_as\s+=\s(.*);\nvar\selt_maison\s+=\s(.*);\nvar\selt_onde\s+=\s(.*);\nvar\selt_porte\s+=\s(.*);\nvar\selt_zone\s+=\s(.*);', re.IGNORECASE).search(str(result))
               
        # item_type = json.loads(extract_elements.group(1))
        # item_label = json.loads(extract_elements.group(2))
        # item_pause = json.loads(extract_elements.group(3))
        # elt_name = json.loads(extract_elements.group(4))
        # elt_code = json.loads(extract_elements.group(5)) 
        # elt_pile = json.loads(extract_elements.group(6))
        # elt_as = json.loads(extract_elements.group(7))
        # elt_maison = json.loads(extract_elements.group(8))
        # elt_onde = json.loads(extract_elements.group(9))
        # elt_porte = json.loads(extract_elements.group(10))
        # elt_zone = json.loads(extract_elements.group(11))

        # elements = {}
        # for x in range(len(elt_code)):
            # elements[elt_code[x]]  = { 
                # "item_type" : item_type[x], 
                # "item_label" : item_label[x], 
                # "item_pause" : item_pause[x],
                # "elt_name" : elt_name[x],
                # "elt_pile" : elt_pile[x],
                # "elt_as" : elt_as[x],
                # "elt_maison" : elt_maison[x],
                # "elt_onde" : elt_onde[x],
                # "elt_porte" : elt_porte[x],
                # "elt_zone" : elt_zone[x]
            # }

        # return  elements

    def _check_error(self, soup):
        if soup.find("div", {"id": "titlebar"}).findAll()[0].find(text=True) == "Error":
            error_code = soup.find('div', {"id": "infobox"}).findAll('b')[0].find(text=True)
            
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

if __name__ == '__main__':
    url = "https://my_alarm_url"
    password = "XXXX"
    codes={
        "key_A1":"XXXX",
        "key_A2":"XXXX",
        "key_A3":"XXXX",
        "key_A4":"XXXX",
        "key_A5":"XXXX",
        "key_B1":"XXXX",
        "key_B2":"XXXX",
        "key_B3":"XXXX",
        "key_B4":"XXXX",
        "key_B5":"XXXX",
        "key_C1":"XXXX",
        "key_C2":"XXXX",
        "key_C3":"XXXX",
        "key_C4":"XXXX",
        "key_C5":"XXXX",
        "key_D1":"XXXX",
        "key_D2":"XXXX",
        "key_D3":"XXXX",
        "key_D4":"XXXX",
        "key_D5":"XXXX",
        "key_E1":"XXXX",
        "key_E2":"XXXX",
        "key_E3":"XXXX",
        "key_E4":"XXXX",
        "key_E5":"XXXX",
        "key_F1":"XXXX",
        "key_F2":"XXXX",
        "key_F3":"XXXX",
        "key_F4":"XXXX",
        "key_F5":"XXXX"
    }
    somfy = Somfy(url, password, codes)
    somfy.login()
    print("Login succeed")
    print("Get status")
    print(somfy.get_state())

    #print("Set zone B")
    #somfy.set_zone_b()
    #print("Get status")
    #print(somfy.get_state())
    #print("Unset all zone")
    #somfy.unset_all_zone()
    #print("Get status")
    #print(somfy.get_state())
    
    # Not updated
    #print("Get elements")
    #print(somfy.get_elements())

    somfy.logout()
    print("Logged out")
