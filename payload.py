import requests

# Replace with your bot's server URL
BOT_SERVER_URL = "http://your-bot-server.com"

def send_command(computer_id, command):
    """
    Sends a command to the bot server.
    """
    try:
        response = requests.post(
            f"{BOT_SERVER_URL}/command",
            json={"computer_id": computer_id, "command": command}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    computer_id = "COMPUTER_1"  # Unique ID for each computer
    command = ".screenshot"     # Command to execute
    result = send_command(computer_id, command)
    print(result)
