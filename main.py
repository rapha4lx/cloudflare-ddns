
import socket
import requests
import os
from dotenv import load_dotenv
import json

from logging import Logger
from logs import setup_logger

def force_ipv4():
    socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

def get_ipv4(logger: Logger, urls_env:str, discord_webhook):
    if not urls_env:
        return
    urls_env = urls_env.split(',')
    for url in urls_env:
        try:
            response = requests.get(url)
        except requests.RequestException as e:
            logger.error(e)
            send_discord_webhook(logger, discord_webhook, e)
            return None
        
        if response.status_code != 200:
            logger.error(f"{response.status_code} >> {response.text}")
            return None
        
        body = response.text.splitlines()
        if len(body) > 1:
            for line in body:
                if line.startswith('ip='):
                    return line.split('=')[1]
        return response.text.strip()

def get_cloudflare_infos(logger: Logger):
    required_env_vars = [
    'CLOUDFLARE_EMAIL',
    'CLOUDFLARE_ZONE_IDENTIFIER',
    'CLOUDFLARE_RECORD_NAME',
    'CLOUDFLARE_AUTH_METHOD',
    'CLOUDFLARE_API_KEY',
    'TTL',
    'PROXY',
    'SITENAME',
    'URL_GET_IPV4'
    ]

    discord_webhook_env = os.getenv('DISCORD_WEBHOOK')

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        msg = f"This variables is empty: {', '.join(missing_vars)}"
        logger.warning(msg)
        if discord_webhook_env:
            send_discord_webhook(logger, discord_webhook_env, msg)
        exit()

    email_env = os.getenv('CLOUDFLARE_EMAIL')
    zone_identifier_env = os.getenv('CLOUDFLARE_ZONE_IDENTIFIER')
    record_name_env = os.getenv('CLOUDFLARE_RECORD_NAME')
    auth_method_env = os.getenv('CLOUDFLARE_AUTH_METHOD')
    if auth_method_env == "global":
        auth_header = "X-Auth-Key"
    elif auth_method_env == "token":
        auth_header = "Authorization: Bearer"
    api_key_env = os.getenv('CLOUDFLARE_API_KEY')
    ttl_env = os.getenv('TTL')
    proxy_env = os.getenv('PROXY')
    site_name_env = os.getenv('SITENAME')
    urls_env = os.getenv('URL_GET_IPV4')

    return email_env, zone_identifier_env, record_name_env, auth_method_env, auth_header, api_key_env, ttl_env, proxy_env, site_name_env, discord_webhook_env, urls_env

def get_record(logger: Logger, discord_webhook, zone_identifier, record_name, auth_email, auth_header, auth_key): 
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_identifier}/dns_records?type=A&name={record_name}"

    headers = {
        "X-Auth-Email": auth_email,
        auth_header: auth_key, 
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
    except requests.RequestException as e:
        logger.error(e)
        send_discord_webhook(logger, discord_webhook, e)
        exit()
    
    if response.status_code != 200:
        logger.error(f"{response.status_code} >> {response.text}")
        exit()

    json_text = json.loads(response.text)
    return json_text['result'][0]['content']

def send_discord_webhook(logger, discord_webhook, msg):
    if not discord_webhook:
        return

    payload = {
        "content": msg
    }
    try:
        response = requests.post(discord_webhook, data=json.dumps(payload, indent=4),
                                 headers={"Content-Type": "application/json"})
    except requests.RequestException as e:
        print(e)
    
    if response.status_code != 204:
        print("Error: fail send webhook")
        return
    

force_ipv4()
load_dotenv()

logger = setup_logger()

email_env, zone_identifier_env, record_name_env, \
    auth_method_env, auth_header, api_key_env, ttl_env, \
    proxy_env, site_name_env, discord_webhook_env, \
    urls_env = get_cloudflare_infos(logger)

ipv4 = get_ipv4(logger, urls_env, discord_webhook_env)

record_ipv4 = get_record(logger, discord_webhook_env, zone_identifier_env, record_name_env, email_env, auth_header, api_key_env)

if ipv4 != record_ipv4:
    send_discord_webhook(logger, discord_webhook_env, f"🏠local_ipv4: {ipv4} >> 🌎record_ipv4: {record_ipv4}")

logger.info(f"🏠local_ipv4: {ipv4} >> 🌎record_ipv4: {record_ipv4}")
