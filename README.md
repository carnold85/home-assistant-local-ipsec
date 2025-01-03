# Local-IPSec: A Custom Home Assistant Component

`local-ipsec` is a custom integration for Home Assistant designed to work with **strongSwan** directly installed on the host. It provides sensors for monitoring IPSec connections and peers, offering detailed information about each connection.

## Features

The `local-ipsec` component creates sensors for each connection/peer, exposing useful information such as:

- **Local Address**: The local IP address of the connection.
- **Remote Address**: The remote IP address of the connection.
- **Local Network**: The local network range associated with the connection.
- **Remote Network**: The remote network range associated with the connection.
- **State**: The current state of the connection.
- **Remote Host**: The remote host name or identifier.
- **Connection Name**: The name of the connection.

## Prerequisites

1. **strongSwan** must be installed and configured properly on the host machine.
2. The `vici` socket (usually located at `/var/run/charon.vici`) must be readable by Home Assistant. Adjust the permissions as follows:
   ```bash
   sudo chown root:hass /var/run/charon.vici
   ```
   Replace `hass` with the appropriate user/group used by your Home Assistant instance.

## Installation

1. Copy the `local-ipsec` integration to your Home Assistant custom components directory:
   ```
   custom_components/local_ipsec/
   ```

2. Ensure strongSwan is configured and running on the host machine.

## Configuration

Enable the `local-ipsec` component by adding the following to your `configuration.yaml` file:

```yaml
# My own IPSec Entities
local_ipsec:
```

No additional configuration is needed. The component will automatically detect active IPSec connections and create corresponding sensors.

## Example Sensor Attributes

Each connection/peer sensor provides the following attributes:

- `Local addr`: The local IP address.
- `Remote addr`: The remote IP address.
- `Local net`: The local network range.
- `Remote net`: The remote network range.
- `State`: The current connection state (e.g., `UP`, `DOWN`).
- `Remote host`: The remote host's identifier.
- `Connection name`: The name of the connection.

## Troubleshooting

- Ensure the `vici` socket is accessible by Home Assistant.
- Check the Home Assistant logs for any error messages related to the `local-ipsec` integration.