# test_function.py

def main(params):
    """
    A simple test function for DigitalOcean Functions.
    Accepts a name parameter and returns a greeting.
    """
    name = params.get("name", "World")
    message = f"Hello, {name}! 👋 Your function is working from DO live stream!"

    return {
        "statusCode": 200,
        "body": message
    }