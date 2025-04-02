from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import resend

# Load .env variables
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
email_from = os.getenv("RESEND_EMAIL_FROM")
default_email_to = os.getenv("RESEND_EMAIL_TO")

mcp = FastMCP("Resend Email Sender")

@mcp.tool()
def send_email(subject: str, html_body: str, to_email: str = None) -> str:
    """
    Send an email using Resend
    
    Args:
    - subject: Email subject line
    - html_body: Email body as HTML
    - to_email: Optional recipient email. Falls back to default from .env
    
    Returns:
    - Success message or error
    """
    try:
        recipient = to_email or default_email_to

        if not subject:
            return "Error: Subject cannot be empty"
        if not html_body:
            return "Error: Email body cannot be empty"
        if not recipient:
            return "Error: No recipient specified"

        response = resend.Emails.send({
            "from": email_from,
            "to": recipient,
            "subject": subject,
            "html": html_body
        })

        return f"Email sent to {recipient}. Response: {response['id']}"
    
    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"

if __name__ == "__main__":
    print("Starting Resend Email MCP Server")
    mcp.run()
