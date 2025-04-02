from mcp.server.fastmcp import FastMCP
import subprocess
import os
import shutil
import uuid
import tempfile
from typing import Optional, List

mcp = FastMCP("DigitalOcean Function Deployer")

def run(cmd, cwd=None) -> str:
    """Execute a command and return its output."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise Exception(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()

def get_function_url(namespace: str, function_path: str) -> str:
    """Get the URL for a deployed function."""
    try:
        result = run(["doctl", "serverless", "fn", "get", function_path, "--url"])
        return result
    except:
        return "URL not available - please use 'doctl serverless fn get sample/hello --url' to get the function URL"

def validate_namespace(namespace: str, region: str) -> str:
    """Validate and return the actual namespace ID."""
    try:
        # List existing namespaces
        namespaces = run(["doctl", "serverless", "namespaces", "list", "--format", "ID,Label"])
        
        # Check if namespace exists by label
        for ns_line in namespaces.split('\n'):
            if namespace in ns_line:
                ns_id = ns_line.split()[0]
                return ns_id

        # Create new namespace if it doesn't exist
        result = run(["doctl", "serverless", "namespaces", "create", "--label", namespace, "--region", region])
        return namespace
    except Exception as e:
        raise Exception(f"Failed to validate/create namespace: {str(e)}")

def create_project_in_tmp(project_id: str) -> str:
    """Create a new serverless project in /tmp directory."""
    tmp_dir = tempfile.mkdtemp(prefix="doctl-serverless-")
    try:
        run(["doctl", "serverless", "init", "--language", "python", project_id], cwd=tmp_dir)
        return os.path.join(tmp_dir, project_id)
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise Exception(f"Failed to create project: {str(e)}")

@mcp.tool()
def deploy_function(
    python_file: str,
    namespace: str,
    region: str = "nyc1",
    requirements: Optional[List[str]] = None
) -> str:
    """
    Deploys a Python file as a serverless function to DigitalOcean using doctl.

    Args:
    - python_file: Path to your .py file
    - namespace: DO namespace to deploy into (can be namespace label)
    - region: DO region (default: nyc1)
    - requirements: Optional list of Python package requirements

    Returns:
    - Deployment result or error
    """
    tmp_dir = None
    try:
        if not os.path.isfile(python_file):
            return f"❌ File not found: {python_file}"

        # Check if doctl is installed and authenticated
        try:
            run(["doctl", "account", "get"])
        except Exception as e:
            return "❌ Error: doctl not installed or not authenticated. Please install doctl and authenticate with 'doctl auth init'"

        # Install serverless support
        try:
            run(["doctl", "serverless", "install"])
        except Exception as e:
            return "❌ Error: Failed to install serverless support. Please try manually: doctl serverless install"

        # Validate and get actual namespace
        try:
            actual_namespace = validate_namespace(namespace, region)
        except Exception as e:
            return f"❌ Error with namespace: {str(e)}"

        # Create project in /tmp
        project_id = f"mcp-func-{uuid.uuid4().hex[:6]}"
        try:
            project_path = create_project_in_tmp(project_id)
            tmp_dir = os.path.dirname(project_path)  # Store tmp_dir for cleanup
        except Exception as e:
            return f"❌ Error creating project: {str(e)}"

        try:
            # Copy user function to the correct location
            target_dir = os.path.join(project_path, "packages", "sample", "hello")
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(python_file, os.path.join(target_dir, "__main__.py"))

            # Create requirements.txt if specified
            if requirements:
                with open(os.path.join(target_dir, "requirements.txt"), "w") as f:
                    f.write("\n".join(requirements))

            # Connect to namespace
            run(["doctl", "serverless", "connect", actual_namespace])

            # Deploy from the temporary directory
            deploy_output = run(["doctl", "serverless", "deploy", "."], cwd=project_path)
            
            # Get function URL
            function_url = get_function_url(actual_namespace, "sample/hello")
            
            return f"""✅ Function deployed successfully!

Deployment Details:
------------------
Namespace: {namespace}
Function: sample/hello
Function URL: {function_url}

Deployment Output:
-----------------
{deploy_output}

To invoke your function:
curl -X POST {function_url} -H "Content-Type: application/json" -d '{{"name": "YourName"}}'
"""

        except Exception as e:
            return f"❌ Error during deployment: {str(e)}"

    except Exception as e:
        return f"❌ Error: {str(e)}"
    
    finally:
        # Clean up temporary directory
        if tmp_dir and os.path.exists(tmp_dir):
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except:
                pass

if __name__ == "__main__":
    print("Starting DO Function MCP Server")
    mcp.run()
