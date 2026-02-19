# ovh-dns-cli

CLI to manage OVH DNS records. Like `cfcli` but for OVH.

## Install

```bash
pip install git+https://github.com/shubs/ovh-dns-cli.git
```

Or locally:

```bash
git clone https://github.com/shubs/ovh-dns-cli.git
cd ovh-dns-cli
pip install -e .
```

## Setup

```bash
ovh-dns setup
```

This will guide you through creating an OVH API app and saving credentials to `~/.ovh.conf`.

Alternatively, set environment variables: `OVH_ENDPOINT`, `OVH_APPLICATION_KEY`, `OVH_APPLICATION_SECRET`, `OVH_CONSUMER_KEY`.

## Usage

```bash
# List all zones
ovh-dns zones

# List records
ovh-dns list example.com
ovh-dns list example.com --type A

# Add record
ovh-dns add example.com www 1.2.3.4
ovh-dns add example.com mail mx.example.com --type CNAME --ttl 300

# Edit record
ovh-dns edit example.com 12345 --target 5.6.7.8

# Remove record
ovh-dns rm example.com www
ovh-dns rm example.com --id 12345

# Export zone
ovh-dns export example.com
```

## License

MIT
