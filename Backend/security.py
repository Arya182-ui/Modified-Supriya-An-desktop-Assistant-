# Enhanced Security System for Supriya Assistant
# Provides authentication, authorization, and security logging

import hashlib
import json
import os
import datetime
import getpass
from cryptography.fernet import Fernet
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

class SecuritySystem:
    def __init__(self):
        self.security_dir = "Data/Security"
        self.auth_file = f"{self.security_dir}/auth.json"
        self.log_file = f"{self.security_dir}/security.log"
        self.key_file = f"{self.security_dir}/master.key"
        
        # Create security directory if it doesn't exist
        os.makedirs(self.security_dir, exist_ok=True)
        
        # Initialize encryption key
        self.cipher_suite = self._init_encryption()
        
        # Initialize authentication system
        self._init_auth_system()
        
        # Security levels for different operations
        self.security_levels = {
            "shutdown": "high",
            "reboot": "high", 
            "file_delete": "medium",
            "system_config": "high",
            "email_access": "medium",
            "social_media": "medium",
            "financial": "high"
        }
    
    def _init_encryption(self):
        """Initialize encryption system"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
        
        return Fernet(key)
    
    def _init_auth_system(self):
        """Initialize authentication system"""
        if not os.path.exists(self.auth_file):
            # Create default admin user
            default_password = getpass.getpass("Set master password for security system: ")
            self.create_user("admin", default_password, "high")
    
    def create_user(self, username, password, security_level="medium"):
        """Create a new user with hashed password"""
        users = self._load_users()
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        users[username] = {
            "password_hash": password_hash,
            "security_level": security_level,
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users(users)
        self.log_action(f"User created: {username}")
    
    def authenticate(self, username=None, password=None):
        """Authenticate user"""
        if not username:
            username = input("Username: ")
        if not password:
            password = getpass.getpass("Password: ")
        
        users = self._load_users()
        
        if username in users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if users[username]["password_hash"] == password_hash:
                users[username]["last_login"] = datetime.datetime.now().isoformat()
                self._save_users(users)
                self.log_action(f"Successful authentication: {username}")
                return True
        
        self.log_action(f"Failed authentication attempt: {username}")
        return False
    
    def requires_auth(self, operation):
        """Check if operation requires authentication"""
        return operation in self.security_levels
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher_suite.encrypt(data)
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()
    
    def log_action(self, action):
        """Log security actions"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - {action}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def _load_users(self):
        """Load user data"""
        if os.path.exists(self.auth_file):
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self, users):
        """Save user data"""
        with open(self.auth_file, 'w') as f:
            json.dump(users, f, indent=4)
    
    def get_security_logs(self, lines=50):
        """Get recent security logs"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
                return logs[-lines:] if len(logs) > lines else logs
        return []
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        if self.authenticate(username, old_password):
            users = self._load_users()
            users[username]["password_hash"] = hashlib.sha256(new_password.encode()).hexdigest()
            self._save_users(users)
            self.log_action(f"Password changed for user: {username}")
            return True
        return False