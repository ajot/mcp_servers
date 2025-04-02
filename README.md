# MCP Servers Collection

This repository contains a collection of MCP (Model Control Protocol) servers designed to work seamlessly with Cursor IDE. Each server provides a specific service that you can access by initiating a chat with your LLM in Cursor. Here’s a quick overview:

- **SQLite Database Server:** Manage and query SQLite databases.
- **Twilio SMS Server:** Send SMS messages and validate phone numbers using Twilio.
- **Resend Email Server:** Send emails via the Resend service.
- **DigitalOcean Function Deployer:** Deploy Python functions to DigitalOcean.

## Cursor Setup

Before you start, configure your MCP servers in Cursor by creating or updating the `~/.cursor/mcp.json` file. Below is an example configuration:

```json
{
  "mcpServers": {
    "sqlite-server": {
      "command": "/path/to/mcp_servers/mcp_sqlite_server/venv/bin/python",
      "args": [
        "/path/to/mcp_servers/mcp_sqlite_server/sqlite-server.py",
        "--db-path",
        "/path/to/your/users.db"
      ]
    },
    "send-sms-twilio": {
      "command": "/path/to/mcp_servers/mcp_sms_server_twilio/venv/bin/python",
      "args": [
        "/path/to/mcp_servers/mcp_sms_server_twilio/twilio-server.py"
      ]
    },
    "send-email-resend": {
      "command": "/path/to/mcp_servers/mcp_email_server_resend/venv/bin/python",
      "args": [
        "/path/to/mcp_servers/mcp_email_server_resend/resend-server.py"
      ]
    },
    "do-function-deployer": {
      "command": "/path/to/mcp_servers/mcp_deploy_function_server_digitalocean/venv/bin/python",
      "args": [
        "/path/to/mcp_servers/mcp_deploy_function_server_digitalocean/do_function_deployer.py"
      ]
    }
  }
}
```

**Remember to:**
- Replace `/path/to/` with your actual project paths.
- Create virtual environments for each server. The command in `mcp.json` points directly to the Python executable in that virtual environment, ensuring MCP has access to all the required dependencies.
- Each server includes its own `requirements.txt` file, which makes it easy to install just the dependencies you need. (If you prefer, you can combine all dependencies into one file and use a single virtual environment for all servers.)

## Available Servers

### 1. SQLite Database Server
**Location:** `mcp_sqlite_server/`

**Setup Instructions:**
1. Navigate to the server directory:
   ```bash
   cd mcp_sqlite_server
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies from its own `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

**How It Works:**  
With this server, you can now initiate a chat with your LLM within Cursor and ask it to interact with your SQLite database. For example, you might say:  
- *"LLM, fetch all users where age is over 25."*  
- *"LLM, connect to the database and show me the users table."*  
These requests are converted into MCP calls that query your SQLite database.

---

### 2. Twilio SMS Server
**Location:** `mcp_sms_server_twilio/`

**Setup Instructions:**
1. Navigate to the server directory:
   ```bash
   cd mcp_sms_server_twilio
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies using the server’s own `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

**Environment Variables:**  
Create a `.env` file with your Twilio credentials:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_FROM=your_twilio_phone
TWILIO_PHONE_TO=default_recipient_phone
```

**How It Works:**  
This server lets you send SMS messages and validate phone numbers through LLM interactions in Cursor. You might say:  
- *"LLM, send an SMS saying 'Hello from MCP!'"*  
- *"LLM, can you check if the phone number +1234567890 is valid?"*  
These requests are translated into MCP calls that trigger the Twilio SMS server.

---

### 3. Resend Email Server
**Location:** `mcp_email_server_resend/`

**Setup Instructions:**
1. Navigate to the server directory:
   ```bash
   cd mcp_email_server_resend
   ```
2. Set up and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies using its own `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

**Environment Variables:**  
Create a `.env` file with:
```
RESEND_API_KEY=your_resend_api_key
RESEND_EMAIL_FROM=your_verified_email
RESEND_EMAIL_TO=default_recipient_email
```

**How It Works:**  
With this server, you can instruct your LLM in Cursor to send emails. For example, you might say:  
- *"LLM, send an email with the subject 'Hello from MCP' and body 'This is a test email.'"*  
The LLM converts your request into an MCP call to trigger the email server.

---

### 4. DigitalOcean Function Deployer
**Location:** `mcp_deploy_function_server_digitalocean/`

**Prerequisites:**
- Install the `doctl` CLI.
- Authenticate using `doctl auth init`.

**Setup Instructions:**
1. Navigate to the directory:
   ```bash
   cd mcp_deploy_function_server_digitalocean
   ```
2. Set up and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies from the server’s `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

**How It Works:**  
This server helps you deploy Python functions to DigitalOcean. You can interact with your LLM in Cursor to deploy functions. For instance, you might say:  
- *"LLM, deploy my function from path/to/your/function.py in the 'my-app' namespace."*  
- *"LLM, deploy a function with dependencies numpy and pandas to region nyc1."*  
The LLM translates these commands into MCP calls to handle the deployment.

---

## Running the Servers

While Cursor will start the servers automatically based on your configuration, you can also test them manually:

1. Open the terminal and navigate to the server’s directory.
2. Activate the corresponding virtual environment.
3. Run the server:
   ```bash
   python server-file.py
   ```
   For example:
   - `python sqlite-server.py` for the SQLite server.
   - `python twilio-server.py` for the Twilio SMS server.
   - `python resend-server.py` for the Resend email server.
   - `python do_function_deployer.py` for the DigitalOcean function deployer.

---

## Best Practices

- **Virtual Environments & Dependencies:**  
  Each server includes its own `requirements.txt` file, making it easy to install just the dependencies you need. The command in `mcp.json` points to the Python executable within that server’s virtual environment, ensuring MCP has access to all the necessary libraries. If you prefer, you can combine dependencies into one file and use a single virtual environment for all servers, but the individual approach is recommended for better isolation.

- **Environment Variables:**  
  Keep your sensitive data in a `.env` file and avoid committing it to your repository.

- **Testing:**  
  Always test your connections before using these servers in a production environment.

- **Absolute Paths:**  
  Ensure that all paths in `~/.cursor/mcp.json` are correct and absolute.

---

## Error Handling

Each server includes error handling to return clear, descriptive messages if something goes wrong. In Cursor, you can catch exceptions and inspect error messages to resolve any issues quickly.

---

## Contributing

Contributions are welcome! Feel free to:
- Add new MCP servers.
- Enhance existing features.
- Improve the documentation.

---

## License

MIT License – use this project in your own projects without any restrictions.