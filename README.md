
  
## Disclaimer

Ce composant pour home assistant permet de controler une alarme Protexiom (2017) de Somfy.

Il s'agit d'une mise à jour du projet de Pschittt initialement développé pour l'alarme Somfy Protexiom 600 version 2009 : 
https://github.com/Pschittt/HASS-Somfy-Protexiom

La classe Somfy a été modifiée pour fonctionner avec la version 2017 des alarmes Somfy Protexiom 600.
La libraire Mechanize à également été remplacé par MechanicalSoup car non disponible sur hassos.

Ce "custom component" a été développé pour mes besoins personnels. En aucun cas, il n'y est lié à Somfy.

## Compatibilité
Ce composant a été testé uniquement avec l'alarme **Somfy Protexiom 600 version 2017**

## Installation

 1. Installer [Home Assistant](https://www.home-assistant.io/)
 2. Créer un répertoire `custom_components` dans le répertoire config de Home Assistant
 
 La structure de Home Assistant devrait être ainsi :

    .homeassistant/
    |-- custom_components/
    |   |-- protexiom/
    |       |-- __init__.py
    |       |-- sensor.py
    |       |-- binary_sensor.py
    |       |-- alarm_control_panel.py
    |       |-- const.py
    |       |-- manifest.json
    |       |-- somfy.py

 3. Ajouter la configuration suivante dans votre fichier `config/configuration.yaml`

```yaml
protexiom:  
  url: !secret protexiom_url
  password: !secret protexiom_password
  codes:
    key_A1: !secret protexiom_key_A1
    key_A2: !secret protexiom_key_A2
    key_A3: !secret protexiom_key_A3
    key_A4: !secret protexiom_key_A4
    key_A5: !secret protexiom_key_A5
    key_B1: !secret protexiom_key_B1
    key_B2: !secret protexiom_key_B2
    key_B3: !secret protexiom_key_B3
    key_B4: !secret protexiom_key_B4
    key_B5: !secret protexiom_key_B5
    key_C1: !secret protexiom_key_C1
    key_C2: !secret protexiom_key_C2
    key_C3: !secret protexiom_key_C3
    key_C4: !secret protexiom_key_C4
    key_C5: !secret protexiom_key_C5
    key_D1: !secret protexiom_key_D1
    key_D2: !secret protexiom_key_D2
    key_D3: !secret protexiom_key_D3
    key_D4: !secret protexiom_key_D4
    key_D5: !secret protexiom_key_D5
    key_E1: !secret protexiom_key_E1
    key_E2: !secret protexiom_key_E2
    key_E3: !secret protexiom_key_E3
    key_E4: !secret protexiom_key_E4
    key_E5: !secret protexiom_key_E5
    key_F1: !secret protexiom_key_F1
    key_F2: !secret protexiom_key_F2
    key_F3: !secret protexiom_key_F3
    key_F4: !secret protexiom_key_F4
    key_F5: !secret protexiom_key_F5
```

## Fonctionnement du composant
`Sensor.py` permet de récupérer via le script `Somfy.py` :
 - L'état général de l'alarme
 - L'état des différents éléments (Pas encore mis à niveau pour fonctionner avec cette version)
Et les stockent dans l'objet Hass.

`Binary_sensor.py` permet de récupérer l'ensemble des états (ON/OFF) des éléments issus de `sensor.py`

`alarm_control_panel.py` permet d'activer ou de désactiver l'alarme via Hass.

> Le custom_component est configuré pour récupérer les états toutes les **minutes.**

## Exemple automation
Editer le fichier `config/automations.yaml`
Alerte en cas de changement d'état de l'alarme (activation/désactivation).
```yaml
- alias: Changement etat alarme
  trigger:
    - platform: state
      entity_id: 
      - binary_sensor.protexiom_general_zone_a
      - binary_sensor.protexiom_general_zone_b
      - binary_sensor.protexiom_general_zone_c
  action:
    - service: notify.mobile_app_iphone
      data_template:
        message: >
          {% if is_state(trigger.to_state.state, 'off') %}
          Alarme activée
          {% else %}
          Alarme désactivée
          {% endif %}
```
