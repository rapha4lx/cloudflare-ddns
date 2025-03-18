# Cloudflare DDNS

## Overview
This project is a Dynamic DNS (DDNS) client that updates your Cloudflare DNS records automatically. It allows you to keep your domain's DNS records up-to-date with your current IP address, which is useful if you have a dynamic IP address from your ISP.

## Features
- Automatically updates Cloudflare DNS records with your current IP address.
- Support for IPv4.
- Support for IPv6.
- Simple configuration file for easy setup.
- Support for Discord WebHook for logs.

## Requirements
- Python 3.x
- `requests` library (install with `pip install requests`)
- `python-dotenv` library (install with `pip install python-dotenv`)

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/rapha4lx/cloudflare-ddns.git
    cd cloudflare-ddns
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Edit the `.env` file with your details:
    ```sh
    nano .env
    ```

2. Add your Cloudflare API token, zone ID, and DNS record details to the `.env` file.

## Usage
Add the DDNS client to crontab to run every 5 minutes:
```sh
*/5 * * * * python3 ~/cloudflare-ddns/main.py
```