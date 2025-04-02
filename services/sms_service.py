import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SMSService:
    """Service for sending SMS messages to patients."""
    
    def __init__(self):
        """Initialize the SMS service with Twilio credentials."""
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not account_sid or not auth_token or not self.phone_number:
            raise ValueError("Twilio credentials not found in environment variables.")
        
        self.client = Client(account_sid, auth_token)
    
    def send_message(self, to_number, message_body):
        """Send an SMS message to a patient.
        
        Args:
            to_number: The patient's phone number (should include country code)
            message_body: The content of the SMS message
            
        Returns:
            list: A list of message SIDs if successful, empty list otherwise
        """
        try:
            max_length = 1500  
            
            # If message is too long, split it into multiple parts
            if len(message_body) > max_length:
                message_sids = []
                
                parts = self._split_message(message_body, max_length)
                
                for i, part in enumerate(parts):
                    if len(parts) > 1:
                        part_header = f"(Part {i+1}/{len(parts)}) "
                        part = part_header + part
                    
                    message = self.client.messages.create(
                        body=part,
                        from_=self.phone_number,
                        to=to_number
                    )
                    message_sids.append(message.sid)
                
                return message_sids
            else:
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.phone_number,
                    to=to_number
                )
                return [message.sid]
        except Exception as e:
            print(f"Error sending SMS: {e}")
            raise  
    
    def _split_message(self, message, max_length):
        """Split a long message into multiple parts.
        
        Args:
            message: The message to split
            max_length: Maximum length of each part
            
        Returns:
            list: A list of message parts
        """
        if len(message) <= max_length:
            return [message]
        
        parts = []
        
        paragraphs = message.split('\n\n')
        current_part = ""
        
        for paragraph in paragraphs:
            if len(current_part) + len(paragraph) + 2 > max_length:
                if current_part:
                    parts.append(current_part.strip())
                current_part = paragraph
            else:
                if current_part:
                    current_part += "\n\n" + paragraph
                else:
                    current_part = paragraph
        
        if current_part:
            parts.append(current_part.strip())
        
        final_parts = []
        for part in parts:
            if len(part) <= max_length:
                final_parts.append(part)
            else:
                sentences = part.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
                current_part = ""
                
                for sentence in sentences:
                    if len(current_part) + len(sentence) + 1 > max_length:
                        if current_part:
                            final_parts.append(current_part.strip())
                        current_part = sentence
                    else:
                        if current_part:
                            current_part += " " + sentence
                        else:
                            current_part = sentence
                
                if current_part:
                    final_parts.append(current_part.strip())
        
        result = []
        for part in final_parts:
            if len(part) <= max_length:
                result.append(part)
            else:
                for i in range(0, len(part), max_length):
                    result.append(part[i:i+max_length])
        
        return result
    
    def validate_phone_number(self, phone_number):
        """Validate that a phone number is in the correct format.
        
        Args:
            phone_number: The phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return phone_number and phone_number.startswith('+') and len(phone_number) >= 10
