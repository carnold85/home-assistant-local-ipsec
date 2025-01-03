import logging
from datetime import timedelta

import vici
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(seconds=60)

existing_entities = {}


class IPSecConnectionSensor(Entity):
    def __init__(self, coordinator, connection_name, initial_data):
        # Initial set
        self.coordinator = coordinator
        self._connection_name = connection_name
        self._attributes = initial_data

    @property
    def unique_id(self):
        return self._connection_name

    @property
    def name(self):
        return f"IPSec Connection {self._connection_name}"

    @property
    def state(self):
        # State Online or Offline
        return (
            "Established"
            if self._attributes.get("state", "") == "ESTABLISHED"
            else "Down"
        )

    @property
    def extra_state_attributes(self):
        # Only return spexific values
        return {
            "Local addr": self._attributes.get("local_addr"),
            "Remote addr": self._attributes.get("remote_addr"),
            "Local net": self._attributes.get("local_net"),
            "Remote net": self._attributes.get("remote_net"),
            "State": self._attributes.get("state", ""),
            "Remote host": self._attributes.get("remote_host", ""),
        }

    @property
    def should_poll(self):
        # Should not be polled, we have a coordinator instead
        return False

    async def async_added_to_hass(self):
        # Add an listener for the coordinator for the update
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_on_coordinator_update)
        )

    def async_on_coordinator_update(self):
        # Update was triggered so update data and also wirte update to HA
        self.update_data()
        self.async_write_ha_state()

    def update_data(self):
        # Set the new attributes
        self._attributes = self.coordinator.data.get(self._connection_name, {})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    # Fetcher Function
    async def fetch_from_vici():
        connections = {}
        # Open StrongSwan VICI Session located at /var/run/charon.vici. WARNING must be readable by ha! (e.g. chown root:hass /var/run/charon.vici)
        session = vici.Session()

        # Fetch all connections
        for connection in session.list_conns():
            for name, detail in connection.items():
                connections[name] = {
                    "local_addr": detail.get("local_addrs")[0].decode("utf-8"),
                    "remote_addr": detail.get("remote_addrs")[0].decode("utf-8"),
                    "local_net": detail.get("children")
                    .get(name)
                    .get("local-ts")[0]
                    .decode("utf-8"),
                    "remote_net": detail.get("children")
                    .get(name)
                    .get("remote-ts")[0]
                    .decode("utf-8"),
                }

        # Fetch active. established connections
        for sa in session.list_sas():
            for name, detail in sa.items():
                connections[name].update(
                    {
                        "state": detail.get("state").decode("utf-8"),
                        "remote_host": detail.get("remote-host").decode("utf-8"),
                    }
                )

        return connections

    # The coordinator for all entities. So only on data fetch used to update all entities
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="ipsec_connections",
        update_method=fetch_from_vici,
        update_interval=UPDATE_INTERVAL,
    )

    # Manual trigger
    await coordinator.async_refresh()

    # First inital add - later the update will do the rest
    global existing_entities
    entities = []
    for connection_name, connection_details in coordinator.data.items():
        new_entity = IPSecConnectionSensor(
            coordinator, connection_name, connection_details
        )
        existing_entities[connection_name] = new_entity
        entities.append(new_entity)
    async_add_entities(entities, True)

    # Now we need a function for delete or new entities.
    def coordinator_update():
        global existing_entities

        new_entities = []
        for connection_name, connection_details in coordinator.data.items():
            if connection_name not in existing_entities:
                # New Client forund, create a new entity
                new_entity = IPSecConnectionSensor(
                    coordinator, connection_name, connection_details
                )
                existing_entities[connection_name] = new_entity
                new_entities.append(new_entity)
                _LOGGER.info(f"IPSec connection {connection_name} configured")

        # Add new entities to Home Assistant
        if new_entities:
            async_add_entities(new_entities, True)

        # Remove entities no longer in the data
        for connection_name in list(existing_entities.keys()):
            if connection_name not in coordinator.data:
                # This entity is no longer in the data, remove it
                # entity = existing_entities.pop(connection_name)
                # hass.add_job(entity.async_remove())
                _LOGGER.info(f"IPSec connection {connection_name} deconfigured")

    # Link the coordinator update method
    coordinator.async_add_listener(coordinator_update)
