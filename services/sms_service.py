import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SMSService:
    """Service for sending SMS messages to patients."""
    
    def __init__(self):
        """Initialize the SMS service with Twilio credentials."""
        # Get Twilio credentials from environment variables
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio client
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
            # Check if message exceeds Twilio's character limit
            max_length = 1500  # Using 1500 to be safe (Twilio's limit is 1600)
            
            # If message is too long, split it into multiple parts
            if len(message_body) > max_length:
                message_sids = []
                
                # Split the message into parts
                parts = self._split_message(message_body, max_length)
                
                # Send each part
                for i, part in enumerate(parts):
                    # Add part number if there are multiple parts
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
                # Send as a single message
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.phone_number,
                    to=to_number
                )
                return [message.sid]
        except Exception as e:
            print(f"Error sending SMS: {e}")
            raise  # Re-raise the exception to handle it in the calling code
    
    def _split_message(self, message, max_length):
        """Split a long message into multiple parts.
        
        Args:
            message: The message to split
            max_length: Maximum length of each part
            
        Returns:
            list: A list of message parts
        """
        # If the message is short enough, return it as is
        if len(message) <= max_length:
            return [message]
        
        parts = []
        
        # Try to split at paragraph breaks first
        paragraphs = message.split('\n\n')
        current_part = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit, start a new part
            if len(current_part) + len(paragraph) + 2 > max_length:
                if current_part:
                    parts.append(current_part.strip())
                current_part = paragraph
            else:
                if current_part:
                    current_part += "\n\n" + paragraph
                else:
                    current_part = paragraph
        
        # Add the last part
        if current_part:
            parts.append(current_part.strip())
        
        # If any part is still too long, split it at sentence boundaries
        final_parts = []
        for part in parts:
            if len(part) <= max_length:
                final_parts.append(part)
            else:
                # Split at sentence boundaries
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
                
                # Add the last part
                if current_part:
                    final_parts.append(current_part.strip())
        
        # If any part is STILL too long, just split it at the character limit
        result = []
        for part in final_parts:
            if len(part) <= max_length:
                result.append(part)
            else:
                # Split at character limit
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
        # Basic validation - should start with + and country code
        # For a production app, you'd want more robust validation
        return phone_number and phone_number.startswith('+') and len(phone_number) >= 10
