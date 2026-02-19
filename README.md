# ovh-dns-cli

A command-line tool to manage DNS records on [OVH](https://www.ovh.com/) — like [`cfcli`](https://github.com/nicholaskajoh/cfcli) but for OVH.

Built on the [official OVH Python SDK](https://github.com/ovh/python-ovh), with pretty [Rich](https://github.com/Textualize/rich) tables in the terminal.

## Features

- List, add, edit, and delete DNS records from the terminal
- Filter records by type (A, AAAA, CNAME, MX, TXT...)
- Export full zone as BIND-style text
- Interactive setup wizard for OVH API credentials
- Supports all OVH endpoints (EU, CA, US, Kimsufi, SoYouStart)

## Installation

### With pip

```bash
pip install git+https://github.com/shubs/ovh-dns-cli.git
```

### With uv

```bash
uv tool install git+https://github.com/shubs/ovh-dns-cli.git
```

### From source

```bash
git clone https://github.com/shubs/ovh-dns-cli.git
cd ovh-dns-cli
pip install -e .
```

## Authentication

### Option 1: Interactive setup (recommended)

```bash
ovh-dns setup
```

This will:

1. Ask you to create an OVH API application at [eu.api.ovh.com/createApp](https://eu.api.ovh.com/createApp/)
2. Prompt for your Application Key and Secret
3. Generate a Consumer Key with DNS permissions
4. Open a validation URL in your browser
5. Save everything to `~/.ovh.conf`

### Option 2: Manual config file

Create `~/.ovh.conf`:

```ini
[default]
endpoint=ovh-eu

[ovh-eu]
application_key=YOUR_APP_KEY
application_secret=YOUR_APP_SECRET
consumer_key=YOUR_CONSUMER_KEY
```

### Option 3: Environment variables

```bash
export OVH_ENDPOINT=ovh-eu
export OVH_APPLICATION_KEY=YOUR_APP_KEY
export OVH_APPLICATION_SECRET=YOUR_APP_SECRET
export OVH_CONSUMER_KEY=YOUR_CONSUMER_KEY
```

> To create API credentials, go to [eu.api.ovh.com/createApp](https://eu.api.ovh.com/createApp/) (replace `eu` with your region if needed). The Consumer Key can be generated via the `setup` command or through the [OVH token creation page](https://eu.api.ovh.com/createToken/).

## Usage

### List all zones

```bash
ovh-dns zones
```

### List records

```bash
# All records
ovh-dns list example.com

# Filter by type
ovh-dns list example.com --type A
ovh-dns list example.com -t MX
```

### Add a record

```bash
# Add an A record (default type)
ovh-dns add example.com www 1.2.3.4

# Add a CNAME with custom TTL
ovh-dns add example.com blog mysite.netlify.app --type CNAME --ttl 300

# Add an MX record
ovh-dns add example.com "" "10 mx.example.com" --type MX
```

### Edit a record

```bash
# Change the target of record #12345
ovh-dns edit example.com 12345 --target 5.6.7.8

# Change TTL
ovh-dns edit example.com 12345 --ttl 3600

# Change subdomain
ovh-dns edit example.com 12345 --subdomain www2
```

> Find record IDs with `ovh-dns list`.

### Remove records

```bash
# Remove all records for a subdomain (with confirmation prompt)
ovh-dns rm example.com www

# Remove only A records for a subdomain
ovh-dns rm example.com www --type A

# Remove a specific record by ID
ovh-dns rm example.com --id 12345

# Skip confirmation
ovh-dns rm example.com www --yes
```

### Export zone

```bash
# Print BIND-style zone file to stdout
ovh-dns export example.com

# Save to file
ovh-dns export example.com > example.com.zone
```

## Command reference

| Command | Description |
|---------|-------------|
| `ovh-dns zones` | List all DNS zones on the account |
| `ovh-dns list <zone> [--type TYPE]` | List records, optionally filtered by type |
| `ovh-dns add <zone> <sub> <target> [--type TYPE] [--ttl TTL]` | Add a DNS record (default: A) |
| `ovh-dns edit <zone> <id> [--target T] [--ttl N] [--subdomain S]` | Edit a record by ID |
| `ovh-dns rm <zone> <sub> [--type TYPE] [--yes]` | Delete records by subdomain |
| `ovh-dns rm <zone> --id <id> [--yes]` | Delete a record by ID |
| `ovh-dns export <zone>` | Export zone as BIND text |
| `ovh-dns setup` | Interactive credential setup |

## Requirements

- Python 3.9+
- An OVH account with at least one domain

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

[MIT](LICENSE)
