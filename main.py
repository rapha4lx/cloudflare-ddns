
import socket
import requests
import os
from dotenv import load_dotenv
import json


def force_ipv4():
    socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

def get_ipv4(urls_env:str):
    if not urls_env:
        return
    urls_env = urls_env.split(',')
    for url in urls_env:
        print(url)
        try:
            response = requests.get(url)
        except requests.RequestException as e:
            print(e)
            return None
        
        if response.status_code != 200:
            print("Error: request fail")
            return None
        
        body = response.text.splitlines()
        if len(body) > 1:
            for line in body:
                if line.startswith('ip='):
                    return line.split('=')[1]
        return response.text.strip()

def get_cloudflare_infos():
    email_env = os.getenv('CLOUDFLARE_EMAIL')
    zone_identifier_env = os.getenv('CLOUDFLARE_ZONE_IDENTIFIER')
    record_name_env = os.getenv('CLOUDFLARE_RECORD_NAME')
    auth_method_env = os.getenv('CLOUDFLARE_AUTH_METHOD')
    if auth_method_env == "global":
        auth_header = "X-Auth-Key"
    elif auth_method_env == "token":
        auth_header = "Authorization: Bearer"
    else:
        exit()  
    api_key_env = os.getenv('CLOUDFLARE_API_KEY')
    ttl_env = os.getenv('TTL')
    proxy_env = os.getenv('PROXY')
    site_name_env = os.getenv('SITENAME')
    discord_webhook_env = os.getenv('DISCORD_WEBHOOK')
    urls_env = os.getenv('URL_GET_IPV4')
    return email_env, zone_identifier_env, record_name_env, auth_method_env, auth_header, api_key_env, ttl_env, proxy_env, site_name_env, discord_webhook_env, urls_env

def get_records(zone_identifier, record_name, auth_email, auth_header, auth_key): 
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_identifier}/dns_records?type=A&name={record_name}"

    headers = {
        "X-Auth-Email": auth_email,
        auth_header: auth_key, 
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
    except requests.RequestException as e:
        print(e)
        exit()
    
    if response.status_code != 200:
        print("Error: request fail")

    print(response.text)

force_ipv4()
load_dotenv()

email_env, zone_identifier_env, record_name_env, \
    auth_method_env, auth_header, api_key_env, ttl_env, \
    proxy_env, site_name_env, discord_webhook_env, \
    urls_env = get_cloudflare_infos()

ipv4 = get_ipv4(urls_env)
print(ipv4)

record_ipv4 = get_records(zone_identifier_env, record_name_env, email_env, auth_header, api_key_env)




