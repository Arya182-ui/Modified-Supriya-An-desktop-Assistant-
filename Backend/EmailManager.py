# Advanced Email Management System
# Provides comprehensive email operations including reading, sending, and organizing

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import datetime
from dotenv import dotenv_values
import re
from Backend.security import SecuritySystem

env_vars = dotenv_values(".env")

@dataclass
class EmailConfig:
    email_address: str
    password: str
    smtp_server: str
    smtp_port: int
    imap_server: str
    imap_port: int

@dataclass
class EmailMessage:
    subject: str
    sender: str
    recipient: str
    body: str
    date: str
    message_id: str = None
    attachments: List[str] = None
    is_read: bool = False
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []

class EmailManager:
    def __init__(self):
        self.security = SecuritySystem()
        self.config_file = "Data/Email/config.json"
        self.drafts_file = "Data/Email/drafts.json"
        self.templates_file = "Data/Email/templates.json"
        
        # Create email directory
        os.makedirs("Data/Email", exist_ok=True)
        
        # Load email configurations
        self.email_configs = self._load_email_configs()
        self.drafts = self._load_drafts()
        self.templates = self._load_templates()
        
        # Default templates
        if not self.templates:
            self._create_default_templates()
    
    def add_email_account(self, name: str, email_address: str, password: str, 
                         smtp_server: str, smtp_port: int, imap_server: str, imap_port: int):
        """Add a new email account configuration"""
        if not self.security.authenticate():
            print("🔒 Authentication required to add email account")
            return False
        
        # Encrypt the password
        encrypted_password = self.security.encrypt_data(password)
        
        config = {
            "email_address": email_address,
            "password": encrypted_password.decode(),
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "imap_server": imap_server,
            "imap_port": imap_port
        }
        
        self.email_configs[name] = config
        self._save_email_configs()
        
        self.security.log_action(f"Email account added: {name}")
        print(f"✅ Email account '{name}' added successfully")
        return True
    
    def send_email(self, account_name: str, to_email: str, subject: str, 
                   body: str, attachments: List[str] = None, cc: List[str] = None, 
                   bcc: List[str] = None, template: str = None):
        """Send an email"""
        if account_name not in self.email_configs:
            print(f"❌ Email account '{account_name}' not found")
            return False
        
        try:
            config = self.email_configs[account_name]
            
            # Decrypt password
            encrypted_password = config["password"].encode()
            password = self.security.decrypt_data(encrypted_password)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config["email_address"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Apply template if specified
            if template and template in self.templates:
                body = self.templates[template]["body"].format(content=body)
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["email_address"], password)
            
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.sendmail(config["email_address"], recipients, msg.as_string())
            server.quit()
            
            self.security.log_action(f"Email sent to {to_email} from {account_name}")
            print(f"📧 Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def read_emails(self, account_name: str, folder: str = "INBOX", 
                   limit: int = 10, unread_only: bool = False) -> List[EmailMessage]:
        """Read emails from specified account and folder"""
        if account_name not in self.email_configs:
            print(f"❌ Email account '{account_name}' not found")
            return []
        
        try:
            config = self.email_configs[account_name]
            
            # Decrypt password
            encrypted_password = config["password"].encode()
            password = self.security.decrypt_data(encrypted_password)
            
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
            mail.login(config["email_address"], password)
            mail.select(folder)
            
            # Search for emails
            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, messages = mail.search(None, search_criteria)
            
            if status != "OK":
                print("❌ Failed to search emails")
                return []
            
            email_messages = []
            message_ids = messages[0].split()[-limit:]  # Get latest emails
            
            for msg_id in reversed(message_ids):  # Reverse to get newest first
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                
                if status == "OK":
                    email_msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract email details
                    subject = email_msg.get("Subject", "No Subject")
                    sender = email_msg.get("From", "Unknown Sender")
                    recipient = email_msg.get("To", "")
                    date = email_msg.get("Date", "")
                    
                    # Get email body
                    body = self._extract_email_body(email_msg)
                    
                    # Check if read
                    status, flags = mail.fetch(msg_id, "(FLAGS)")
                    is_read = b'\\Seen' in flags[0] if flags else False
                    
                    email_message = EmailMessage(
                        subject=subject,
                        sender=sender,
                        recipient=recipient,
                        body=body,
                        date=date,
                        message_id=msg_id.decode(),
                        is_read=is_read
                    )
                    
                    email_messages.append(email_message)
            
            mail.logout()
            
            self.security.log_action(f"Read {len(email_messages)} emails from {account_name}")
            return email_messages
            
        except Exception as e:
            print(f"❌ Failed to read emails: {e}")
            return []
    
    def search_emails(self, account_name: str, query: str, folder: str = "INBOX") -> List[EmailMessage]:
        """Search emails by subject or sender"""
        emails = self.read_emails(account_name, folder, limit=100)
        
        query = query.lower()
        results = []
        
        for email_msg in emails:
            if (query in email_msg.subject.lower() or 
                query in email_msg.sender.lower() or
                query in email_msg.body.lower()):
                results.append(email_msg)
        
        return results
    
    def mark_as_read(self, account_name: str, message_id: str, folder: str = "INBOX"):
        """Mark an email as read"""
        try:
            config = self.email_configs[account_name]
            encrypted_password = config["password"].encode()
            password = self.security.decrypt_data(encrypted_password)
            
            mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
            mail.login(config["email_address"], password)
            mail.select(folder)
            
            mail.store(message_id, '+FLAGS', '\\Seen')
            mail.logout()
            
            print(f"✅ Email marked as read")
            return True
            
        except Exception as e:
            print(f"❌ Failed to mark email as read: {e}")
            return False
    
    def delete_email(self, account_name: str, message_id: str, folder: str = "INBOX"):
        """Delete an email"""
        try:
            config = self.email_configs[account_name]
            encrypted_password = config["password"].encode()
            password = self.security.decrypt_data(encrypted_password)
            
            mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
            mail.login(config["email_address"], password)
            mail.select(folder)
            
            mail.store(message_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            mail.logout()
            
            self.security.log_action(f"Email deleted from {account_name}")
            print(f"🗑️ Email deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete email: {e}")
            return False
    
    def save_draft(self, subject: str, to_email: str, body: str, 
                   attachments: List[str] = None) -> str:
        """Save email as draft"""
        draft_id = str(len(self.drafts) + 1)
        
        draft = {
            "id": draft_id,
            "subject": subject,
            "to_email": to_email,
            "body": body,
            "attachments": attachments or [],
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.drafts[draft_id] = draft
        self._save_drafts()
        
        print(f"💾 Draft saved with ID: {draft_id}")
        return draft_id
    
    def send_draft(self, account_name: str, draft_id: str):
        """Send a saved draft"""
        if draft_id not in self.drafts:
            print(f"❌ Draft with ID '{draft_id}' not found")
            return False
        
        draft = self.drafts[draft_id]
        
        success = self.send_email(
            account_name=account_name,
            to_email=draft["to_email"],
            subject=draft["subject"],
            body=draft["body"],
            attachments=draft["attachments"]
        )
        
        if success:
            # Remove draft after sending
            del self.drafts[draft_id]
            self._save_drafts()
        
        return success
    
    def create_template(self, name: str, subject_template: str, body_template: str):
        """Create an email template"""
        template = {
            "subject": subject_template,
            "body": body_template,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.templates[name] = template
        self._save_templates()
        
        print(f"📄 Email template '{name}' created")
    
    def get_email_statistics(self, account_name: str) -> Dict:
        """Get email statistics for an account"""
        try:
            inbox_emails = self.read_emails(account_name, "INBOX", limit=100)
            sent_emails = self.read_emails(account_name, "SENT", limit=100)
            
            unread_count = len([e for e in inbox_emails if not e.is_read])
            
            return {
                "total_inbox": len(inbox_emails),
                "unread_count": unread_count,
                "sent_count": len(sent_emails),
                "drafts_count": len(self.drafts),
                "templates_count": len(self.templates)
            }
            
        except Exception as e:
            print(f"❌ Failed to get email statistics: {e}")
            return {}
    
    def _extract_email_body(self, email_msg):
        """Extract plain text body from email message"""
        body = ""
        
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        continue
        else:
            try:
                body = email_msg.get_payload(decode=True).decode()
            except:
                body = str(email_msg.get_payload())
        
        return body[:1000]  # Limit body length
    
    def _create_default_templates(self):
        """Create default email templates"""
        templates = {
            "meeting_request": {
                "subject": "Meeting Request - {meeting_topic}",
                "body": """Dear {recipient_name},

I hope this email finds you well. I would like to schedule a meeting with you to discuss {meeting_topic}.

{content}

Please let me know your availability for the coming week.

Best regards,
{sender_name}"""
            },
            "follow_up": {
                "subject": "Follow-up: {original_subject}",
                "body": """Hello {recipient_name},

I wanted to follow up on our previous conversation regarding {topic}.

{content}

Looking forward to your response.

Best regards,
{sender_name}"""
            },
            "thank_you": {
                "subject": "Thank you - {occasion}",
                "body": """Dear {recipient_name},

Thank you for {content}.

I truly appreciate your time and effort.

Best regards,
{sender_name}"""
            }
        }
        
        for name, template in templates.items():
            self.templates[name] = template
        
        self._save_templates()
    
    def _load_email_configs(self) -> Dict:
        """Load email configurations from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_email_configs(self):
        """Save email configurations to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.email_configs, f, indent=4)
    
    def _load_drafts(self) -> Dict:
        """Load email drafts from file"""
        if os.path.exists(self.drafts_file):
            with open(self.drafts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_drafts(self):
        """Save email drafts to file"""
        with open(self.drafts_file, 'w', encoding='utf-8') as f:
            json.dump(self.drafts, f, indent=4, ensure_ascii=False)
    
    def _load_templates(self) -> Dict:
        """Load email templates from file"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_templates(self):
        """Save email templates to file"""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=4, ensure_ascii=False)

# Global email manager instance
email_manager = EmailManager()

# Voice command functions for email management
def read_emails_voice(command: str):
    """Read emails from voice command"""
    # Parse command like "read my emails" or "check unread emails"
    account_name = "default"  # You might want to extract account name from command
    
    if "unread" in command:
        emails = email_manager.read_emails(account_name, unread_only=True, limit=5)
        if not emails:
            return "You have no unread emails"
        
        result = f"You have {len(emails)} unread emails:\n"
        for i, email_msg in enumerate(emails, 1):
            result += f"{i}. From: {email_msg.sender}\n"
            result += f"   Subject: {email_msg.subject}\n"
            
    else:
        emails = email_manager.read_emails(account_name, limit=5)
        if not emails:
            return "No emails found"
        
        result = f"Latest {len(emails)} emails:\n"
        for i, email_msg in enumerate(emails, 1):
            result += f"{i}. From: {email_msg.sender}\n"
            result += f"   Subject: {email_msg.subject}\n"
    
    return result

def send_email_voice(command: str):
    """Send email from voice command"""
    # This would typically integrate with a form or dialog
    # For now, provide instructions
    return "To send an email, please use the email interface or provide recipient, subject, and message details"

def email_summary_voice(command: str):
    """Get email summary from voice command"""
    account_name = "default"
    stats = email_manager.get_email_statistics(account_name)
    
    if not stats:
        return "Unable to retrieve email statistics"
    
    return (f"Email Summary:\n"
            f"Total inbox emails: {stats.get('total_inbox', 0)}\n"
            f"Unread emails: {stats.get('unread_count', 0)}\n"
            f"Sent emails: {stats.get('sent_count', 0)}\n"
            f"Draft emails: {stats.get('drafts_count', 0)}")

# Common email providers configurations
EMAIL_PROVIDERS = {
    "gmail": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_server": "imap.gmail.com",
        "imap_port": 993
    },
    "outlook": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "imap_server": "outlook.office365.com",
        "imap_port": 993
    },
    "yahoo": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "imap_server": "imap.mail.yahoo.com",
        "imap_port": 993
    }
}