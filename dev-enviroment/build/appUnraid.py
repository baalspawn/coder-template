import json
import urllib.request
import base64
import io
from PIL import Image
import websocket
import discord
import datetime
import subprocess
from dotenv import load_dotenv
import os
#from discord.ext import commands

#Specify the path to the image you want to upload
output_image_path = "/app/generated_image_advanced.png" # Make sure the file excists

# Load enviroment
load_dotenv()

# access enviroment variables
channel_id = os.getenv("CHANNEL_ID")
discord_token = os.getenv("DISCORD_TOKEN")

# Discord bot configuration
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
#channel_id =  # Replace with your channel ID

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
 
# Configuration Comfyui
server_address = "192.168.5.98:8188"
#192.168.5.211:8188
def load_workflow(filename="workflow.json"):
    with open(filename, 'r') as file:
        return json.load(file)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def update_workflow_with_image(workflow, image_path):
    base64_image = encode_image_to_base64 (image_path)
    workflow["69"]["inputs"]["image"] = base64_image
    return workflow

#def update_workflow_with_prompt(workflow, input_rompt):
#    workflow["6"]["inputs"]["text"] = input_rompt

def queue_prompt(prompt):
    data = json.dumps({"prompt": prompt}).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response body: {e.read().decode('utf-8')}")
        raise

def get_image(prompt_id):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws")

    print(f"Waiting for image data for prompt ID: {prompt_id}")

    while True:
        message = ws.recv()
        if isinstance(message, str):
            data = json.loads(message)
            print(f"Received message: {data}")
            if data['type'] == 'executing':
                if data['data']['node'] is None and data['data']['prompt_id'] == prompt_id:
                    print("Execution completed")
                    break
        elif isinstance(message, bytes):
            print("Recieved binary data (likely image)")
            image = Image.open(io.BytesIO(message[8:])) #skip first 8 bytes (message type)
            ws.close()
            return image

    ws.close()
    return None



# Discord Menu and Commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return
 
    if message.content.startswith('Hi'):
        await message.channel.send('Hello! please use /prompt: to generate image')
    elif message.content.startswith('/prompt:'):
            await message.channel.send('Working on your prompt:')
            user_input = message.content.split(' ', 1)[1]
            await message.channel.send(f"You entered: {user_input}")
            # Load workflow form JSON file
            workflow = load_workflow()
            print ("Workflow loaded successfully.")
            # adding the prompt to the workflow
            inputPrompt = user_input
            workflow["5"]["inputs"]["text"] = inputPrompt
            await message.channel.send('Generating Image')
            response = queue_prompt(workflow)
            prompt_id = response['prompt_id']
            await message.channel.send(f"Prompt queued with ID: {prompt_id}")
            # fetching finnished picture
            image = get_image(prompt_id)
            if image:
                now = datetime.datetime.now()
                date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
                output_filename = f"GenImg_{date_string}.png"
                image.save(output_filename)
                output_image_path = f"/app/{output_filename}"
                print(f"Image saved as {output_filename}")
                print(f"Image size: {image.size}")
                print(f"Image mode: {image.mode}")
            else:
                print("Failed to retrieve image")

            print("Script execution completed.")
            await message.channel.send('Fetching image:')
            await message.channel.send(file=discord.File(output_image_path))

            
client.run(discord_token)

