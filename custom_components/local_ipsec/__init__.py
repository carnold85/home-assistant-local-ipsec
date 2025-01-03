from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import load_platform

DOMAIN = "local_ipsec"


def setup(hass: HomeAssistant, config):
    load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
