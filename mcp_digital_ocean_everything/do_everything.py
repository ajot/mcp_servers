# do_app_platform.py
import os
import json
import httpx
from typing import List, Dict, Optional, Any, Union
from urllib.parse import urljoin
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context, Image

# Load environment variables from .env file
load_dotenv()

# Create MCP server instance
mcp = FastMCP("DigitalOcean App Platform")

# Constants
BASE_URL = "https://api.digitalocean.com/v2/"
# Get API token from environment variable
API_TOKEN = os.getenv("DO_API_TOKEN")
if not API_TOKEN:
    print("Warning: DO_API_TOKEN environment variable not set. API calls will fail.")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# Helper function for API requests
async def do_request(
    method: str, 
    endpoint: str, 
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make a request to DigitalOcean API"""
    url = urljoin(BASE_URL, endpoint)
    
    if not API_TOKEN:
        return {"error": "API token not configured. Set DO_API_TOKEN in your .env file."}
    
    async with httpx.AsyncClient() as client:
        if method.lower() == "get":
            response = await client.get(url, headers=HEADERS, params=params)
        elif method.lower() == "post":
            response = await client.post(url, headers=HEADERS, json=data)
        elif method.lower() == "put":
            response = await client.put(url, headers=HEADERS, json=data)
        elif method.lower() == "delete":
            response = await client.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        if response.status_code >= 400:
            return {"error": f"API Error: {response.status_code}", "details": response.text}
        
        return response.json()

# App Platform Resources
@mcp.resource("apps://list")
async def list_apps_resource() -> str:
    """Get list of all apps in your DigitalOcean account"""
    response = await do_request("get", "apps")
    apps = response.get("apps", [])
    formatted_apps = json.dumps(apps, indent=2)
    return f"# DigitalOcean Apps\n\n{formatted_apps}"

@mcp.resource("app://{app_id}")
async def get_app_details(app_id: str) -> str:
    """Get detailed information about a specific app"""
    response = await do_request("get", f"apps/{app_id}")
    app_details = json.dumps(response, indent=2)
    return f"# App Details: {app_id}\n\n{app_details}"

@mcp.resource("app://{app_id}/deployments")
async def get_app_deployments(app_id: str) -> str:
    """Get deployments for a specific app"""
    response = await do_request("get", f"apps/{app_id}/deployments")
    deployments = response.get("deployments", [])
    formatted_deployments = json.dumps(deployments, indent=2)
    return f"# Deployments for App: {app_id}\n\n{formatted_deployments}"

@mcp.resource("functions://list")
async def list_functions_resource() -> str:
    """Get list of all functions in your DigitalOcean account"""
    # Note: This is an approximation as functions are part of apps in DigitalOcean
    response = await do_request("get", "apps")
    
    functions = []
    for app in response.get("apps", []):
        app_id = app.get("id")
        app_details = await do_request("get", f"apps/{app_id}")
        
        for component in app_details.get("spec", {}).get("functions", []):
            functions.append({
                "app_id": app_id,
                "name": component.get("name"),
                "source_dir": component.get("source_dir"),
                "github": component.get("github", {}),
                "routes": component.get("routes", [])
            })
    
    formatted_functions = json.dumps(functions, indent=2)
    return f"# DigitalOcean Functions\n\n{formatted_functions}"

# PostgreSQL Database Resources
@mcp.resource("databases://list")
async def list_databases_resource() -> str:
    """Get list of all PostgreSQL databases in your DigitalOcean account"""
    response = await do_request("get", "databases?type=pg")
    databases = response.get("databases", [])
    formatted_databases = json.dumps(databases, indent=2)
    return f"# DigitalOcean PostgreSQL Databases\n\n{formatted_databases}"

@mcp.resource("database://{db_id}")
async def get_database_details(db_id: str) -> str:
    """Get detailed information about a specific PostgreSQL database"""
    response = await do_request("get", f"databases/{db_id}")
    db_details = json.dumps(response, indent=2)
    return f"# Database Details: {db_id}\n\n{db_details}"

@mcp.resource("database://{db_id}/users")
async def get_database_users(db_id: str) -> str:
    """Get users for a specific PostgreSQL database"""
    response = await do_request("get", f"databases/{db_id}/users")
    users = response.get("users", [])
    formatted_users = json.dumps(users, indent=2)
    return f"# Users for Database: {db_id}\n\n{formatted_users}"

@mcp.resource("database://{db_id}/pools")
async def get_database_connection_pools(db_id: str) -> str:
    """Get connection pools for a specific PostgreSQL database"""
    response = await do_request("get", f"databases/{db_id}/pools")
    pools = response.get("pools", [])
    formatted_pools = json.dumps(pools, indent=2)
    return f"# Connection Pools for Database: {db_id}\n\n{formatted_pools}"

# App Platform Tools
@mcp.tool()
async def get_apps() -> str:
    """Get a list of all apps in your DigitalOcean account"""
    response = await do_request("get", "apps")
    
    if "error" in response:
        return f"Error getting apps: {response['error']}"
    
    apps = response.get("apps", [])
    
    if not apps:
        return "No apps found in your DigitalOcean account."
    
    result = "# Your DigitalOcean Apps\n\n"
    for app in apps:
        result += f"- **{app.get('spec', {}).get('name')}** (ID: `{app.get('id')}`)\n"
        result += f"  - Region: {app.get('region', {}).get('name', 'Unknown')}\n"
        result += f"  - Created: {app.get('created_at', 'Unknown')}\n"
        result += f"  - Updated: {app.get('updated_at', 'Unknown')}\n"
        result += f"  - Default Ingress: {app.get('default_ingress', 'None')}\n\n"
    
    return result

@mcp.tool()
async def get_app_details(app_id: str) -> str:
    """Get detailed information about a specific app"""
    response = await do_request("get", f"apps/{app_id}")
    
    if "error" in response:
        return f"Error getting app details: {response['error']}"
    
    spec = response.get("spec", {})
    result = f"# App: {spec.get('name')}\n\n"
    result += f"- **ID**: `{app_id}`\n"
    result += f"- **Region**: {response.get('region', {}).get('name', 'Unknown')}\n"
    result += f"- **Created**: {response.get('created_at', 'Unknown')}\n"
    result += f"- **Updated**: {response.get('updated_at', 'Unknown')}\n"
    result += f"- **Tier**: {spec.get('tier', 'Unknown')}\n\n"
    
    # Add components information
    components = []
    components.extend(spec.get("services", []))
    components.extend(spec.get("static_sites", []))
    components.extend(spec.get("functions", []))
    components.extend(spec.get("workers", []))
    components.extend(spec.get("jobs", []))
    components.extend(spec.get("databases", []))
    
    if components:
        result += "## Components\n\n"
        for component in components:
            component_type = next((t for t in ["service", "static_site", "function", "worker", "job", "database"] 
                                 if t in component), "unknown")
            result += f"- **{component.get('name')}** (Type: {component_type})\n"
            if "github" in component:
                github = component.get("github", {})
                result += f"  - Source: GitHub - Repo: {github.get('repo')}, Branch: {github.get('branch', 'main')}\n"
            if "source_dir" in component:
                result += f"  - Source Directory: {component.get('source_dir')}\n"
            if "routes" in component:
                result += f"  - Routes: {', '.join(component.get('routes', []))}\n"
            result += "\n"
    
    return result

@mcp.tool()
async def get_deployments(app_id: str) -> str:
    """Get deployments for a specific app"""
    response = await do_request("get", f"apps/{app_id}/deployments")
    
    if "error" in response:
        return f"Error getting deployments: {response['error']}"
    
    deployments = response.get("deployments", [])
    
    if not deployments:
        return f"No deployments found for app {app_id}."
    
    result = f"# Deployments for App: {app_id}\n\n"
    for deployment in deployments:
        result += f"- **Deployment ID**: `{deployment.get('id')}`\n"
        result += f"  - Created: {deployment.get('created_at', 'Unknown')}\n"
        result += f"  - Phase: {deployment.get('phase', 'Unknown')}\n"
        result += f"  - Progress: {deployment.get('progress', {}).get('success_steps', 0)}/{deployment.get('progress', {}).get('total_steps', 0)}\n"
        result += f"  - Cause: {deployment.get('cause', 'Unknown')}\n\n"
    
    return result

@mcp.tool()
async def create_app(
    name: str,
    region: str = "nyc",
    tier: str = "basic",
    repo_url: Optional[str] = None,
    branch: str = "main",
    source_dir: Optional[str] = None
) -> str:
    """Create a new app on DigitalOcean App Platform"""
    # Build app spec
    spec = {
        "name": name,
        "region": region,
        "tier": tier
    }
    
    # Add GitHub source if provided
    if repo_url:
        if "github.com" in repo_url:
            # Extract owner/repo from URL
            parts = repo_url.split("github.com/")
            if len(parts) > 1:
                repo_path = parts[1].strip("/")
                if repo_path.endswith(".git"):
                    repo_path = repo_path[:-4]
                
                spec["services"] = [
                    {
                        "name": f"{name}-service",
                        "github": {
                            "repo": repo_path,
                            "branch": branch
                        }
                    }
                ]
                
                if source_dir:
                    spec["services"][0]["source_dir"] = source_dir
    
    # Create app request
    response = await do_request("post", "apps", {"spec": spec})
    
    if "error" in response:
        return f"Error creating app: {response['error']}"
    
    app_id = response.get("app", {}).get("id", "Unknown")
    app_name = response.get("app", {}).get("spec", {}).get("name", "Unknown")
    
    return f"Successfully created app '{app_name}' with ID: {app_id}"

@mcp.tool()
async def deploy_app(app_id: str) -> str:
    """Create a new deployment for an existing app"""
    response = await do_request("post", f"apps/{app_id}/deployments")
    
    if "error" in response:
        return f"Error creating deployment: {response['error']}"
    
    deployment_id = response.get("deployment", {}).get("id", "Unknown")
    
    return f"Successfully created deployment with ID: {deployment_id} for app {app_id}"

@mcp.tool()
async def add_function(
    app_id: str,
    function_name: str,
    repo_url: str,
    branch: str = "main",
    source_dir: str = "/",
    routes: List[str] = None
) -> str:
    """Add a serverless function to an existing app"""
    # Get the current app spec
    app_response = await do_request("get", f"apps/{app_id}")
    
    if "error" in app_response:
        return f"Error getting app details: {app_response['error']}"
    
    app_spec = app_response.get("spec", {})
    
    # Extract repo owner/name from URL
    if "github.com" in repo_url:
        parts = repo_url.split("github.com/")
        if len(parts) > 1:
            repo_path = parts[1].strip("/")
            if repo_path.endswith(".git"):
                repo_path = repo_path[:-4]
            
            # Create function component
            function_spec = {
                "name": function_name,
                "github": {
                    "repo": repo_path,
                    "branch": branch
                },
                "source_dir": source_dir
            }
            
            if routes:
                function_spec["routes"] = routes
            
            # Add function to app spec
            if "functions" not in app_spec:
                app_spec["functions"] = []
            
            app_spec["functions"].append(function_spec)
            
            # Update app with new spec
            update_response = await do_request("put", f"apps/{app_id}", {"spec": app_spec})
            
            if "error" in update_response:
                return f"Error updating app with new function: {update_response['error']}"
            
            return f"Successfully added function '{function_name}' to app {app_id}. Deploy the app to apply changes."
    
    return "Error: Invalid repository URL format. Expected GitHub URL."

@mcp.tool()
async def delete_app(app_id: str) -> str:
    """Delete an app from DigitalOcean App Platform"""
    response = await do_request("delete", f"apps/{app_id}")
    
    if response == {} or response == None:  # DELETE usually returns empty on success
        return f"Successfully deleted app {app_id}"
    elif "error" in response:
        return f"Error deleting app: {response['error']}"
    else:
        return f"Unknown response from deletion request: {response}"

@mcp.tool()
async def get_app_metrics(app_id: str, metrics_type: str = "cpu") -> str:
    """Get metrics for a specific app (cpu, memory, bandwidth)"""
    valid_types = ["cpu", "memory", "bandwidth"]
    
    if metrics_type.lower() not in valid_types:
        return f"Invalid metrics type. Must be one of: {', '.join(valid_types)}"
    
    # Get app to check if it exists
    app_response = await do_request("get", f"apps/{app_id}")
    
    if "error" in app_response:
        return f"Error getting app details: {app_response['error']}"
    
    # For this example, we'll return a simplified response
    # In a real implementation, you would query DO's metrics endpoints
    metrics = {
        "cpu": "CPU usage data would appear here. DigitalOcean provides this data through their monitoring API.",
        "memory": "Memory usage data would appear here. DigitalOcean provides this data through their monitoring API.",
        "bandwidth": "Bandwidth usage data would appear here. DigitalOcean provides this data through their monitoring API."
    }
    
    return f"# {metrics_type.upper()} Metrics for App {app_id}\n\n{metrics[metrics_type.lower()]}"

# PostgreSQL Database Tools
@mcp.tool()
async def get_databases() -> str:
    """Get a list of all PostgreSQL databases in your DigitalOcean account"""
    response = await do_request("get", "databases?type=pg")
    
    if "error" in response:
        return f"Error getting databases: {response['error']}"
    
    databases = response.get("databases", [])
    
    if not databases:
        return "No PostgreSQL databases found in your DigitalOcean account."
    
    result = "# Your DigitalOcean PostgreSQL Databases\n\n"
    for db in databases:
        result += f"- **{db.get('name')}** (ID: `{db.get('id')}`)\n"
        result += f"  - Region: {db.get('region', 'Unknown')}\n"
        result += f"  - Created: {db.get('created_at', 'Unknown')}\n"
        result += f"  - Status: {db.get('status', 'Unknown')}\n"
        result += f"  - Version: {db.get('version', 'Unknown')}\n"
        result += f"  - Size: {db.get('size', 'Unknown')}\n"
        result += f"  - Connection URI: {db.get('connection', {}).get('uri', 'Unknown')}\n\n"
    
    return result

@mcp.tool()
async def get_database_details(db_id: str) -> str:
    """Get detailed information about a specific PostgreSQL database"""
    response = await do_request("get", f"databases/{db_id}")
    
    if "error" in response:
        return f"Error getting database details: {response['error']}"
    
    db = response.get("database", {})
    
    result = f"# Database: {db.get('name')}\n\n"
    result += f"- **ID**: `{db_id}`\n"
    result += f"- **Region**: {db.get('region', 'Unknown')}\n"
    result += f"- **Created**: {db.get('created_at', 'Unknown')}\n"
    result += f"- **Status**: {db.get('status', 'Unknown')}\n"
    result += f"- **Version**: {db.get('version', 'Unknown')}\n"
    result += f"- **Size**: {db.get('size', 'Unknown')}\n"
    result += f"- **Num Nodes**: {db.get('num_nodes', 'Unknown')}\n\n"
    
    # Connection details
    conn = db.get('connection', {})
    private_conn = db.get('private_connection', {})
    
    result += "## Connection Details\n\n"
    result += f"- **Public Connection**\n"
    result += f"  - Host: {conn.get('host', 'Unknown')}\n"
    result += f"  - Port: {conn.get('port', 'Unknown')}\n"
    result += f"  - Database: {conn.get('database', 'Unknown')}\n"
    result += f"  - URI: {conn.get('uri', 'Unknown')}\n\n"
    
    result += f"- **Private Connection**\n"
    result += f"  - Host: {private_conn.get('host', 'Unknown')}\n"
    result += f"  - Port: {private_conn.get('port', 'Unknown')}\n"
    result += f"  - Database: {private_conn.get('database', 'Unknown')}\n"
    result += f"  - URI: {private_conn.get('uri', 'Unknown')}\n\n"
    
    # Database users
    users_response = await do_request("get", f"databases/{db_id}/users")
    
    if "error" not in users_response:
        users = users_response.get("users", [])
        result += "## Database Users\n\n"
        for user in users:
            result += f"- **{user.get('name')}**\n"
            result += f"  - Role: {user.get('role', 'Normal')}\n"
            # Note: We don't show passwords for security reasons
    
    return result

@mcp.tool()
async def create_database(
    name: str,
    region: str = "nyc",
    size: str = "db-s-1vcpu-1gb",
    version: str = "15",
    num_nodes: int = 1
) -> str:
    """Create a new PostgreSQL database cluster on DigitalOcean"""
    data = {
        "name": name,
        "engine": "pg",
        "version": version,
        "region": region,
        "size": size,
        "num_nodes": num_nodes
    }
    
    response = await do_request("post", "databases", data)
    
    if "error" in response:
        return f"Error creating database: {response['error']}"
    
    db = response.get("database", {})
    db_id = db.get("id", "Unknown")
    db_name = db.get("name", "Unknown")
    
    return f"Successfully created PostgreSQL database '{db_name}' with ID: {db_id}. Status: {db.get('status', 'Unknown')}"

@mcp.tool()
async def delete_database(db_id: str) -> str:
    """Delete a PostgreSQL database from DigitalOcean"""
    response = await do_request("delete", f"databases/{db_id}")
    
    if response == {} or response is None:  # DELETE usually returns empty on success
        return f"Successfully deleted database {db_id}"
    elif "error" in response:
        return f"Error deleting database: {response['error']}"
    else:
        return f"Unknown response from deletion request: {response}"

@mcp.tool()
async def create_database_user(db_id: str, username: str) -> str:
    """Create a new user for a PostgreSQL database"""
    data = {
        "name": username
    }
    
    response = await do_request("post", f"databases/{db_id}/users", data)
    
    if "error" in response:
        return f"Error creating database user: {response['error']}"
    
    user = response.get("user", {})
    password = user.get("password", "")
    
    # Return details including the password - in a real application,
    # you'd likely want a more secure way to provide this information
    return f"""Successfully created database user '{username}' for database {db_id}.
    
Important: Save these credentials securely. The password will not be shown again.

- Username: {username}
- Password: {password}
- Connection string: postgresql://{username}:{password}@{user.get('host', 'Unknown')}:{user.get('port', 'Unknown')}/{user.get('database', 'Unknown')}
    """

@mcp.tool()
async def reset_database_user_password(db_id: str, username: str) -> str:
    """Reset password for a PostgreSQL database user"""
    response = await do_request("post", f"databases/{db_id}/users/{username}/reset_auth")
    
    if "error" in response:
        return f"Error resetting password: {response['error']}"
    
    user = response.get("user", {})
    password = user.get("password", "")
    
    # Return new credentials
    return f"""Successfully reset password for database user '{username}' on database {db_id}.
    
Important: Save these credentials securely. The password will not be shown again.

- Username: {username}
- New Password: {password}
- Connection string: postgresql://{username}:{password}@{user.get('host', 'Unknown')}:{user.get('port', 'Unknown')}/{user.get('database', 'Unknown')}
    """

@mcp.tool()
async def create_connection_pool(
    db_id: str, 
    name: str, 
    mode: str = "transaction", 
    size: int = 10, 
    db: str = "defaultdb", 
    user: str = "doadmin"
) -> str:
    """Create a new connection pool for a PostgreSQL database
    
    Args:
        db_id: Database ID
        name: Pool name
        mode: Pool mode (transaction, session, statement)
        size: Pool size (number of connections)
        db: Database name
        user: Database user
    """
    # Validate mode
    valid_modes = ["transaction", "session", "statement"]
    if mode not in valid_modes:
        return f"Error: mode must be one of {', '.join(valid_modes)}"
    
    data = {
        "name": name,
        "mode": mode,
        "size": size,
        "db": db,
        "user": user
    }
    
    response = await do_request("post", f"databases/{db_id}/pools", data)
    
    if "error" in response:
        return f"Error creating connection pool: {response['error']}"
    
    pool = response.get("pool", {})
    
    return f"""Successfully created connection pool '{name}' for database {db_id}.

Pool Details:
- Name: {name}
- Mode: {mode}
- Size: {size}
- Database: {db}
- User: {user}
- Connection string: {pool.get('connection_uri', 'Unknown')}
    """

@mcp.tool()
async def get_database_metrics(db_id: str, metrics_type: str = "cpu") -> str:
    """Get metrics for a specific database (cpu, memory, disk, connections)"""
    valid_types = ["cpu", "memory", "disk", "connections"]
    
    if metrics_type.lower() not in valid_types:
        return f"Invalid metrics type. Must be one of: {', '.join(valid_types)}"
    
    # Get database to check if it exists
    db_response = await do_request("get", f"databases/{db_id}")
    
    if "error" in db_response:
        return f"Error getting database details: {db_response['error']}"
    
    # For this example, we'll return a simplified response
    # In a real implementation, you would query DO's metrics endpoints
    metrics = {
        "cpu": "CPU usage data would appear here. DigitalOcean provides this data through their monitoring API.",
        "memory": "Memory usage data would appear here. DigitalOcean provides this data through their monitoring API.",
        "disk": "Disk usage data would appear here. DigitalOcean provides this data through their monitoring API.",
        "connections": "Connection count data would appear here. DigitalOcean provides this data through their monitoring API."
    }
    
    return f"# {metrics_type.upper()} Metrics for Database {db_id}\n\n{metrics[metrics_type.lower()]}"

@mcp.tool()
async def connect_app_to_database(app_id: str, db_id: str) -> str:
    """Connect an app to a PostgreSQL database by adding a database component to the app"""
    # First, get app details
    app_response = await do_request("get", f"apps/{app_id}")
    
    if "error" in app_response:
        return f"Error getting app details: {app_response['error']}"
    
    # Then get database details
    db_response = await do_request("get", f"databases/{db_id}")
    
    if "error" in db_response:
        return f"Error getting database details: {db_response['error']}"
    
    app_spec = app_response.get("spec", {})
    db = db_response.get("database", {})
    
    # Get cluster UUID from the database
    cluster_uuid = db.get("id", "")
    
    # Add database to app spec
    if "databases" not in app_spec:
        app_spec["databases"] = []
    
    # Check if this database is already connected
    for existing_db in app_spec.get("databases", []):
        if existing_db.get("cluster_id") == cluster_uuid:
            return f"Database {db_id} is already connected to app {app_id}."
    
    # Add the database connection
    app_spec["databases"].append({
        "name": f"{db.get('name', 'db')}-connection",
        "cluster_id": cluster_uuid,
        "production": True
    })
    
    # Update the app with the new spec
    update_response = await do_request("put", f"apps/{app_id}", {"spec": app_spec})
    
    if "error" in update_response:
        return f"Error connecting database to app: {update_response['error']}"
    
    return f"""Successfully connected database '{db.get('name')}' to app {app_id}.
    
The database will be accessible to your app as an environment variable.
After deploying your app, you can access the database using the connection string from the DATABASE_URL environment variable.
"""

# App Platform Prompts
@mcp.prompt()
def create_app_prompt() -> str:
    """Template for creating a new DigitalOcean app"""
    return """
I need to create a new application on DigitalOcean App Platform with the following details:

- Name: [Application Name]
- Region: [Region Code, e.g., nyc, ams, sfo]
- Tier: [basic/professional/enterprise]
- Repository URL: [GitHub Repository URL]
- Branch: [Git Branch]
- Source Directory: [Source Directory Path]

Please help me create this application using the DigitalOcean API.
"""

@mcp.prompt()
def add_function_prompt() -> str:
    """Template for adding a serverless function to an app"""
    return """
I want to add a serverless function to my DigitalOcean app with these details:

- App ID: [Existing App ID]
- Function Name: [Function Name]
- Repository URL: [GitHub Repository URL]
- Branch: [Git Branch]
- Source Directory: [Function Source Directory]
- Routes: [List of HTTP routes, e.g., "/api/function"]

Please help me add this function to my app.
"""

# PostgreSQL Database Prompts
@mcp.prompt()
def create_database_prompt() -> str:
    """Template for creating a new DigitalOcean PostgreSQL database"""
    return """
I need to create a new PostgreSQL database on DigitalOcean with the following details:

- Name: [Database Name]
- Region: [Region Code, e.g., nyc, ams, sfo]
- Size: [Size slug, e.g., db-s-1vcpu-1gb, db-s-2vcpu-4gb]
- Version: [PostgreSQL version, e.g., 15, 14, 13]
- Number of Nodes: [1 for basic, 2+ for high availability]

Please help me create this database using the DigitalOcean API.
"""

@mcp.prompt()
def connect_app_database_prompt() -> str:
    """Template for connecting an app to a PostgreSQL database"""
    return """
I want to connect my DigitalOcean App Platform application to a PostgreSQL database:

- App ID: [Existing App ID]
- Database ID: [Existing Database ID]
- Database Name: [Database Name to Use]
- Database User: [User to Connect With]

Please help me set up this database connection for my application.
"""

# Add these billing-related resources and tools to your existing do_app_platform.py file

# Billing Resources
@mcp.resource("billing://summary")
async def get_billing_summary_resource() -> str:
    """Get a summary of the current billing period"""
    response = await do_request("get", "customers/my/balance")
    balance_info = response.get("account_balance", {})
    
    # Also get billing history
    history_response = await do_request("get", "customers/my/billing_history")
    billing_history = history_response.get("billing_history", [])
    
    # Format as JSON for resource viewing
    result = {
        "account_balance": balance_info,
        "recent_billing_history": billing_history[:10] if billing_history else []
    }
    
    formatted_result = json.dumps(result, indent=2)
    return f"# DigitalOcean Billing Summary\n\n{formatted_result}"

@mcp.resource("billing://history")
async def get_billing_history_resource() -> str:
    """Get detailed billing history"""
    response = await do_request("get", "customers/my/billing_history")
    billing_history = response.get("billing_history", [])
    formatted_history = json.dumps(billing_history, indent=2)
    return f"# DigitalOcean Billing History\n\n{formatted_history}"

@mcp.resource("billing://invoices")
async def get_invoices_resource() -> str:
    """Get list of invoices"""
    response = await do_request("get", "customers/my/invoices")
    invoices = response.get("invoices", [])
    formatted_invoices = json.dumps(invoices, indent=2)
    return f"# DigitalOcean Invoices\n\n{formatted_invoices}"

# Billing Tools
@mcp.tool()
async def get_account_balance() -> str:
    """Get the current account balance information"""
    response = await do_request("get", "customers/my/balance")
    
    if "error" in response:
        return f"Error getting account balance: {response['error']}"
    
    balance_info = response.get("account_balance", {})
    
    month_to_date = balance_info.get("month_to_date_usage", 0)
    account_balance = balance_info.get("account_balance", 0)
    month_to_date_balance = balance_info.get("month_to_date_balance", 0)
    generated_at = balance_info.get("generated_at", "Unknown")
    
    return f"""# DigitalOcean Account Balance

- **Current Account Balance**: ${account_balance:.2f}
- **Month-to-Date Usage**: ${month_to_date:.2f}
- **Month-to-Date Balance**: ${month_to_date_balance:.2f}
- **Last Updated**: {generated_at}

Note: A positive account balance indicates a credit, while a negative balance indicates an amount owed.
"""

@mcp.tool()
async def get_billing_history(limit: int = 10) -> str:
    """Get recent billing history with specified limit"""
    response = await do_request("get", "customers/my/billing_history")
    
    if "error" in response:
        return f"Error getting billing history: {response['error']}"
    
    billing_history = response.get("billing_history", [])
    
    if not billing_history:
        return "No billing history found."
    
    # Limit the number of entries
    billing_history = billing_history[:limit]
    
    result = "# Recent Billing History\n\n"
    for entry in billing_history:
        amount = entry.get("amount", "0")
        date = entry.get("date", "Unknown")
        invoice_id = entry.get("invoice_id", "N/A")
        description = entry.get("description", "No description")
        
        result += f"- **Date**: {date}\n"
        result += f"  - **Amount**: ${amount}\n"
        result += f"  - **Description**: {description}\n"
        if invoice_id and invoice_id != "N/A":
            result += f"  - **Invoice ID**: {invoice_id}\n"
        result += "\n"
    
    return result

@mcp.tool()
async def get_invoices(limit: int = 5) -> str:
    """Get recent invoices with specified limit"""
    response = await do_request("get", "customers/my/invoices")
    
    if "error" in response:
        return f"Error getting invoices: {response['error']}"
    
    invoices = response.get("invoices", [])
    
    if not invoices:
        return "No invoices found."
    
    # Limit the number of entries
    invoices = invoices[:limit]
    
    result = "# Recent Invoices\n\n"
    for invoice in invoices:
        invoice_uuid = invoice.get("invoice_uuid", "Unknown")
        amount = invoice.get("amount", "0")
        invoice_period = invoice.get("invoice_period", "Unknown")
        product = invoice.get("product", "Unknown")
        resource_uuid = invoice.get("resource_uuid", "Unknown")
        
        result += f"- **Invoice ID**: {invoice_uuid}\n"
        result += f"  - **Period**: {invoice_period}\n"
        result += f"  - **Amount**: ${amount}\n"
        result += f"  - **Product**: {product}\n"
        result += f"  - **Resource ID**: {resource_uuid}\n\n"
    
    return result

@mcp.tool()
async def get_cost_by_resource_type() -> str:
    """Get cost breakdown by resource type"""
    # This information isn't directly exposed by the DigitalOcean API
    # so we'll manually parse billing data to build resource breakdowns
    
    # Get billing history
    history_response = await do_request("get", "customers/my/billing_history")
    
    if "error" in history_response:
        return f"Error getting billing data: {history_response['error']}"
    
    billing_history = history_response.get("billing_history", [])
    
    if not billing_history:
        return "No billing history found for analysis."
    
    # Group costs by resource type
    resource_costs = {}
    
    for entry in billing_history:
        desc = entry.get("description", "")
        amount = float(entry.get("amount", 0))
        
        # Extract resource type from description (this is an approximation)
        resource_type = "Other"
        if "Droplet" in desc:
            resource_type = "Droplets"
        elif "Database" in desc or "PostgreSQL" in desc or "MySQL" in desc:
            resource_type = "Databases"
        elif "App Platform" in desc:
            resource_type = "App Platform"
        elif "Spaces" in desc:
            resource_type = "Spaces (Storage)"
        elif "Load Balancer" in desc:
            resource_type = "Load Balancers"
        elif "Kubernetes" in desc:
            resource_type = "Kubernetes"
        
        if resource_type in resource_costs:
            resource_costs[resource_type] += amount
        else:
            resource_costs[resource_type] = amount
    
    # Format the response
    result = "# Cost Breakdown by Resource Type\n\n"
    
    for resource_type, cost in sorted(resource_costs.items(), key=lambda x: x[1], reverse=True):
        result += f"- **{resource_type}**: ${cost:.2f}\n"
    
    return result

@mcp.tool()
async def get_app_platform_costs() -> str:
    """Get cost estimates for App Platform resources"""
    # First, get all apps
    apps_response = await do_request("get", "apps")
    
    if "error" in apps_response:
        return f"Error getting apps: {apps_response['error']}"
    
    apps = apps_response.get("apps", [])
    
    if not apps:
        return "No apps found to analyze costs."
    
    # Build approximate cost calculation
    # (This is an approximation as exact pricing depends on usage)
    result = "# App Platform Cost Estimates\n\n"
    
    total_cost = 0
    for app in apps:
        app_name = app.get("spec", {}).get("name", "Unknown")
        app_id = app.get("id", "Unknown")
        tier = app.get("spec", {}).get("tier", "basic")
        
        # Basic estimation logic based on component types
        app_cost = 0
        
        # Base costs vary by tier
        if tier == "basic":
            app_cost += 5  # $5/month basic tier base cost
        elif tier == "professional":
            app_cost += 12  # $12/month professional tier base cost
        elif tier == "enterprise":
            app_cost += 50  # Estimated enterprise tier cost
        
        # Add component costs (very approximate)
        spec = app.get("spec", {})
        
        # Count services
        services = spec.get("services", [])
        for service in services:
            if tier == "basic":
                app_cost += 5  # Basic service cost approximation
            else:
                app_cost += 10  # Professional service cost approximation
        
        # Count static sites
        static_sites = spec.get("static_sites", [])
        for site in static_sites:
            app_cost += 3  # Static site cost approximation
        
        # Count functions
        functions = spec.get("functions", [])
        for function in functions:
            app_cost += 2  # Function cost approximation
        
        # Count databases
        databases = spec.get("databases", [])
        for database in databases:
            app_cost += 7  # Database component cost approximation
        
        result += f"## {app_name} (ID: {app_id})\n"
        result += f"- **Tier**: {tier}\n"
        result += f"- **Services**: {len(services)} x ${5 if tier == 'basic' else 10} = ${len(services) * (5 if tier == 'basic' else 10)}\n"
        result += f"- **Static Sites**: {len(static_sites)} x $3 = ${len(static_sites) * 3}\n"
        result += f"- **Functions**: {len(functions)} x $2 = ${len(functions) * 2}\n"
        result += f"- **Database Components**: {len(databases)} x $7 = ${len(databases) * 7}\n"
        result += f"- **Estimated Monthly Cost**: ${app_cost:.2f}\n\n"
        
        total_cost += app_cost
    
    result += f"## Total Estimated App Platform Cost: ${total_cost:.2f}/month\n\n"
    result += """
Note: These are approximate estimates and actual costs may vary based on:
- Resource usage (bandwidth, requests, compute hours)
- Additional features enabled
- Storage consumption
- Scaling configurations

For exact pricing, please refer to the DigitalOcean App Platform pricing page or your billing dashboard.
"""
    
    return result

@mcp.tool()
async def get_database_costs() -> str:
    """Get cost estimates for PostgreSQL databases"""
    # Get all databases
    db_response = await do_request("get", "databases?type=pg")
    
    if "error" in db_response:
        return f"Error getting databases: {db_response['error']}"
    
    databases = db_response.get("databases", [])
    
    if not databases:
        return "No PostgreSQL databases found to analyze costs."
    
    # Database pricing estimates
    price_map = {
        "db-s-1vcpu-1gb": 15,
        "db-s-1vcpu-2gb": 30,
        "db-s-2vcpu-4gb": 60,
        "db-s-4vcpu-8gb": 120,
        "db-s-8vcpu-16gb": 240,
        "db-s-16vcpu-32gb": 480,
        "db-s-24vcpu-128gb": 960,
        "db-s-32vcpu-192gb": 1440
    }
    
    result = "# PostgreSQL Database Cost Estimates\n\n"
    
    total_cost = 0
    for db in databases:
        db_name = db.get("name", "Unknown")
        db_id = db.get("id", "Unknown")
        size = db.get("size", "Unknown")
        num_nodes = db.get("num_nodes", 1)
        
        # Calculate base cost
        base_cost = price_map.get(size, 15)  # Default to smallest if size unknown
        total_db_cost = base_cost * num_nodes
        
        result += f"## {db_name} (ID: {db_id})\n"
        result += f"- **Size**: {size}\n"
        result += f"- **Nodes**: {num_nodes}\n"
        result += f"- **Base Cost**: ${base_cost:.2f}/month\n"
        result += f"- **Total Database Cost**: ${total_db_cost:.2f}/month (${base_cost:.2f} × {num_nodes} nodes)\n\n"
        
        total_cost += total_db_cost
    
    result += f"## Total Estimated Database Cost: ${total_cost:.2f}/month\n\n"
    result += """
Note: These are approximate estimates and actual costs may vary based on:
- Additional storage beyond included amount
- Backups configuration
- Standby nodes
- Region pricing variations

For exact pricing, please refer to the DigitalOcean Database pricing page or your billing dashboard.
"""
    
    return result

# Billing Prompts
@mcp.prompt()
def analyze_costs_prompt() -> str:
    """Template for analyzing DigitalOcean costs"""
    return """
I need to analyze my DigitalOcean costs for the following:

- Current account balance and month-to-date usage
- Cost breakdown by resource type
- Detailed cost analysis for App Platform resources
- Estimated database costs
- Recommendations for cost optimization

Please provide me with a comprehensive cost analysis of my DigitalOcean account.
"""

@mcp.prompt()
def billing_history_prompt() -> str:
    """Template for retrieving and analyzing billing history"""
    return """
I need to review my DigitalOcean billing history with the following details:

- Recent transactions and charges
- Invoice information for the last [number] months
- Unusual or unexpected charges
- Cost trends over time

Please help me understand my billing history and any notable patterns or changes.
"""

# Run the server when executed directly
if __name__ == "__main__":
    mcp.run()