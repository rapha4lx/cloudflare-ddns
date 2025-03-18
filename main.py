
import socket
import requests
import os
from dotenv import load_dotenv
import json

from logging import Logger
from logs import setup_logger

class Cloudflare:
    def __init__(self):
        load_dotenv()

        self.logger = setup_logger()

        self.email = os.getenv('CLOUDFLARE_EMAIL')
        self.zone_identifier = os.getenv('CLOUDFLARE_ZONE_IDENTIFIER')

        self.record_name_ipv4 = None
        self.auth_method_ipv4 = None
        self.auth_header_ipv4 = None
        self.api_key_ipv4 = None
        self.ttl_ipv4 = None
        self.proxy_ipv4 = None
        self.sitename_ipv4 = None
        self.home_ipv4 = None
        self.record_ipv4 = None
        self.record_id_ipv4 = None
        self.discord_webhook_ipv4 = os.getenv('DISCORD_WEBHOOK_IPV4')
        self.urls_ipv4 = os.getenv('URL_GET_IPV4')


        self.record_name_ipv6 = None
        self.auth_method_ipv6 = None
        self.auth_header_ipv6 = None
        self.api_key_ipv6 = None
        self.ttl_ipv6 = None
        self.proxy_ipv6 = None
        self.sitename_ipv6 = None
        self.home_ipv6 = None
        self.record_ipv6 = None
        self.record_id_ipv6 = None
        self.discord_webhook_ipv6 = os.getenv('DISCORD_WEBHOOK_IPV6')
        self.urls_ipv6 = os.getenv('URL_GET_IPV6')

        self.force_ipv4()
        if self.get_ipv4() and self.get_cloudflare_infos_ipv4() and self.get_record_ipv4():
            if self.home_ipv4 != self.record_ipv4:
                self.send_discord_webhook(self.discord_webhook_ipv4, f"🏠local_ipv4: {self.home_ipv4} >> 🌎record_ipv4: {self.record_ipv4}")
                self.set_record_ipv4()

            self.logger.info(f"🏠local_ipv4: {self.home_ipv4} >> 🌎record_ipv4: {self.record_ipv4}")

        self.force_ipv6()
        if self.get_ipv6() and self.get_cloudflare_infos_ipv6() and self.get_record_ipv6():
            if self.home_ipv6 != self.record_ipv6:
                self.force_ipv4()
                self.send_discord_webhook(self.discord_webhook_ipv6, f"🏠local_ipv6: {self.home_ipv6} >> 🌎record_ipv6: {self.record_ipv6}")
                self.set_record_ipv6()

            self.logger.info(f"🏠local_ipv6: {self.home_ipv6} >> 🌎record_ipv6: {self.record_ipv6}")

    @staticmethod
    def force_ipv4():
        socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

    @staticmethod
    def force_ipv6():
        socket.getaddrinfo = lambda *args: [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

    def get_ipv4(self) -> bool:
        if not self.urls_ipv4:
            return False
        urls_env = self.urls_ipv4.split(',')
        for url in urls_env:
            try:
                response = requests.get(url)
            except requests.RequestException as e:
                self.logger.error(e)
                self.send_discord_webhook(self.discord_webhook_ipv4, e)
                return False
            
            if response.status_code != 200:
                self.logger.error(f"{response.status_code} >> {response.text}")
                return False
            
            body = response.text.splitlines()
            if len(body) > 1:
                for line in body:
                    if line.startswith('ip='):
                        self.home_ipv4 = line.split('=')[1]
                        return True
            self.home_ipv4 = response.text.strip()
            return True

    def get_ipv6(self) -> bool:
        if not self.urls_ipv6:
            return False
        urls_env = self.urls_ipv6.split(',')
        for url in urls_env:
            try:
                response = requests.get(url)
            except requests.RequestException as e:
                self.logger.error(e)
                self.send_discord_webhook(self.discord_webhook_ipv6, e)
                return False
            
            if response.status_code != 200:
                self.logger.error(f"{response.status_code} >> {response.text}")
                return False
            
            body = response.text.splitlines()
            if len(body) > 1:
                for line in body:
                    if line.startswith('ip='):
                        self.home_ipv6 = line.split('=')[1]
                        return True
            self.home_ipv6 = response.text.strip()
            return True

    def get_cloudflare_infos_ipv4(self) -> bool:
        required_env_vars = [
        'CLOUDFLARE_RECORD_NAME_IPV4',
        'CLOUDFLARE_AUTH_METHOD_IPV4',
        'CLOUDFLARE_API_KEY_IPV4',
        'TTL_IPV4',
        'PROXY_IPV4',
        'SITENAME_IPV4'
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            msg = f"This variables is empty: {', '.join(missing_vars)}"
            self.logger.warning(msg)
            if self.discord_webhook_ipv4:
                self.send_discord_webhook(msg)
            return False

        self.record_name_ipv4 = os.getenv('CLOUDFLARE_RECORD_NAME_IPV4')
        self.auth_method_ipv4 = os.getenv('CLOUDFLARE_AUTH_METHOD_IPV4')
        if self.auth_method_ipv4 == "global":
            self.auth_header_ipv4 = "X-Auth-Key"
        elif self.auth_method_ipv4 == "token":
            self.auth_header_ipv4 = "Authorization: Bearer"
        self.api_key_ipv4 = os.getenv('CLOUDFLARE_API_KEY_IPV4')
        self.ttl_ipv4 = os.getenv('TTL_IPV4')
        self.proxy_ipv4 = os.getenv('PROXY_IPV4')
        self.sitename_ipv4 = os.getenv('SITENAME_IPV4')
        self.discord_webhook_ipv4 = os.getenv('DISCORD_WEBHOOK_IPV4')
        return True

    def get_cloudflare_infos_ipv6(self) -> bool:
        required_env_vars = [
        'CLOUDFLARE_RECORD_NAME_IPV6',
        'CLOUDFLARE_AUTH_METHOD_IPV6',
        'CLOUDFLARE_API_KEY_IPV6',
        'TTL_IPV6',
        'PROXY_IPV6',
        'SITENAME_IPV6'
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            msg = f"This variables is empty: {', '.join(missing_vars)}"
            self.logger.warning(msg)
            if self.discord_webhook_ipv6:
                self.send_discord_webhook(self.discord_webhook_ipv6, msg)
            return False

        self.record_name_ipv6 = os.getenv('CLOUDFLARE_RECORD_NAME_IPV6')
        self.auth_method_ipv6 = os.getenv('CLOUDFLARE_AUTH_METHOD_IPV6')
        if self.auth_method_ipv6 == "global":
            self.auth_header_ipv6 = "X-Auth-Key"
        elif self.auth_method_ipv6 == "token":
            self.auth_header_ipv6 = "Authorization: Bearer"
        self.api_key_ipv6 = os.getenv('CLOUDFLARE_API_KEY_IPV6')
        self.ttl_ipv6 = os.getenv('TTL_IPV6')
        self.proxy_ipv6 = os.getenv('PROXY_IPV6')
        self.sitename_ipv6 = os.getenv('SITENAME_IPV6')
        self.discord_webhook_ipv6 = os.getenv('DISCORD_WEBHOOK_IPV6')
        return True

    def get_record_ipv4(self) -> bool:
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_identifier}/dns_records?type=A&name={self.record_name_ipv4}"

        headers = {
            "X-Auth-Email": self.email,
            self.auth_header_ipv4: self.api_key_ipv4, 
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
        except requests.RequestException as e:
            self.logger.error(e)
            self.send_discord_webhook(self.discord_webhook_ipv4, e)
            return False
        
        if response.status_code != 200:
            self.logger.error(f"{response.status_code} >> {response.text}")
            return False

        json_text = json.loads(response.text)
        self.record_ipv4 = json_text['result'][0]['content']
        self.record_id_ipv4 = json_text['result'][0]['id']
        return True

    def set_record_ipv4(self):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_identifier}/dns_records/{self.record_id_ipv4}"

        headers = {
            "X-Auth-Email": self.email,
            self.auth_header_ipv4: self.api_key_ipv4, 
            "Content-Type": "application/json"
        }

        data = {
            "name": self.record_name_ipv4,
            "type": "A",
            "content": self.home_ipv4,
            "ttl": 3600,
            "proxied": False
        }
        
        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
        except requests.RequestException as e:
            self.logger.error(e)
            self.send_discord_webhook(self.discord_webhook_ipv4, e)
    
    def get_record_ipv6(self) -> bool: 
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_identifier}/dns_records?type=AAAA&name={self.record_name_ipv6}"

        headers = {
            "X-Auth-Email": self.email,
            self.auth_header_ipv6: self.api_key_ipv6,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
        except requests.RequestException as e:
            self.logger.error(e)
            self.send_discord_webhook(self.discord_webhook_ipv6, e)
            return False
        
        if response.status_code != 200:
            self.logger.error(f"{response.status_code} >> {response.text}")
            return False

        json_text = json.loads(response.text)
        self.record_ipv6 = json_text['result'][0]['content']
        self.record_id_ipv6 = json_text['result'][0]['id']
        return True

    def set_record_ipv6(self):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_identifier}/dns_records/{self.record_id_ipv6}"

        headers = {
            "X-Auth-Email": self.email,
            self.auth_header_ipv6: self.api_key_ipv6, 
            "Content-Type": "application/json"
        }

        data = {
            "name": self.record_name_ipv6,
            "type": "AAAA",
            "content": self.home_ipv6,
            "ttl": 3600,
            "proxied": False
        }
        
        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
        except requests.RequestException as e:
            self.logger.error(e)
            self.send_discord_webhook(self.discord_webhook_ipv6, e)

    def send_discord_webhook(self, webhook, msg):
        if not webhook:
            return

        payload = {
            "content": msg
        }
        try:
            response = requests.post(webhook, data=json.dumps(payload, indent=4),
                                    headers={"Content-Type": "application/json"})
        except requests.RequestException as e:
            print(e)
        
        if response.status_code != 204:
            print("Error: fail send webhook")
            return
        
Cloudflare()

