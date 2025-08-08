import requests
import json
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(api_key="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")

def fetch_robot_description(api_key):
    """Fetch robot description from the API"""
    api_url = f"https://centrala.ag3nts.org/data/{api_key}/robotid.json"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data.get('description', '')
    except requests.RequestException as e:
        print(f"Error fetching robot description: {e}")
        return None

def generate_robot_image(description):
    """Generate robot image using DALL-E based on description"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A detailed image of a robot: {description}",
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def send_report(api_key, image_url):
    """Send the image URL to centrala"""
    report_data = {
        "task": "robotid",
        "apikey": api_key,
        "answer": image_url
    }
    
    report_url = "https://centrala.ag3nts.org/report"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(report_url, json=report_data, headers=headers)
        if response.status_code == 200:
            print("Success!")
            print(response.text)
            return True
        else:
            print(f"Error sending report: {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print(f"Error sending report: {e}")
        return False

def main():
    api_key = "b76d036a-560e-48a2-b895-7f7fb0115cec"
    
    print("Fetching robot description...")
    description = fetch_robot_description(api_key)
    
    if not description:
        print("Failed to fetch robot description")
        return
    
    print(f"Robot description: {description}")
    print("Generating robot image...")
    
    image_url = generate_robot_image(description)
    
    if not image_url:
        print("Failed to generate robot image")
        return
    
    print(f"Image generated: {image_url}")
    
    # Send the image URL to centrala
    print("Sending report to centrala...")
    success = send_report(api_key, image_url)
    
    if success:
        print("Robot image generation and submission completed successfully!")
    else:
        print("Failed to submit the image URL")

if __name__ == "__main__":
    main()