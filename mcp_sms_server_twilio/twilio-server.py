# twilio-server.py
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# Get Twilio credentials and phone numbers from environment variables
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phone_from = os.getenv('TWILIO_PHONE_FROM')
default_phone_to = os.getenv('TWILIO_PHONE_TO')

# Initialize Twilio client with account SID and auth token
client = Client(account_sid, auth_token)

mcp = FastMCP("Twilio SMS Sender")

@mcp.tool()
def send_sms(message: str, to_phone: str = None) -> str:
    """
    Send an SMS message using Twilio
    
    Args:
    - message: The text message to send
    - to_phone: Optional phone number to send to. If not provided, uses default TWILIO_PHONE_TO
    
    Returns:
    - Success message with message SID or error details
    """
    try:
        # Use default phone number if not provided
        send_to = to_phone or default_phone_to
        
        # Validate input
        if not message:
            return "Error: Message cannot be empty"
        
        if not send_to:
            return "Error: No phone number specified"
        
        # Send message using Twilio
        message_obj = client.messages.create(
            body=message,
            from_=phone_from,
            to=send_to
        )
        
        return f"Message sent successfully to {send_to}. SID: {message_obj.sid}"
    
    except Exception as e:
        return f"Failed to send message. Error: {str(e)}"

@mcp.tool()
def validate_phone_number(phone_number: str) -> str:
    """
    Validate a phone number format
    
    Args:
    - phone_number: Phone number to validate
    
    Returns:
    - Validation result
    """
    try:
        # Simple validation - you might want to use a more robust library like `phonenumbers`
        if not phone_number:
            return "Error: Phone number cannot be empty"
        
        # Basic format check (modify as needed)
        if not (phone_number.startswith('+') and len(phone_number) > 10):
            return "Error: Invalid phone number format. Must start with '+' and include country code"
        
        return f"Phone number {phone_number} appears to be valid"
    
    except Exception as e:
        return f"Validation error: {str(e)}"

if __name__ == "__main__":
    print("Starting Twilio SMS MCP Server")
    mcp.run()