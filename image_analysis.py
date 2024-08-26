import argparse  
import dotenv  
import os  
import base64  
from PIL import Image, ImageDraw, ImageFont  
import math  
import pandas as pd  
import ast  
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient 
from openai import AzureOpenAI

 
  
def download_blob_to_file(blob_client, download_file_path):  
    with open(download_file_path, "wb") as download_file:  
        download_file.write(blob_client.download_blob().readall())  
  
# Function to convert image to base64  
def open_image_to_base64(file_path):  
    with open(file_path, "rb") as image_file:  
        image_data = image_file.read()  
        base64_data = base64.b64encode(image_data).decode("utf-8")  
        base64_url = f"data:image/jpeg;base64,{base64_data}"  
        return base64_url  
  
# Function to add grid overlay to image  
def add_grid_overlay(image_path):  
    # Load the image  
    image = Image.open(image_path)  
  
    # Get the dimensions of the image  
    width, height = image.size  
  
    # Calculate the coordinates for cropping  
    left = (width - 300) // 2  
    top = (height - 500) // 2  
    right = (width + 250) // 2  
    bottom = (height + 500) // 2  
  
    # Crop the image  
    cropped_image = image.crop((left, top, right, bottom))  
  
    # Create a draw object  
    draw = ImageDraw.Draw(cropped_image)  
  
    # Define the font and size for the grid numbers  
    font = ImageFont.load_default()  
  
    # Define the grid size and spacing  
    grid_size = 16  
    d = int(math.sqrt(grid_size))  
    grid_spacing = cropped_image.width // d  
    grid_spacing_height = cropped_image.height // d  
  
    # Draw the grid overlay  
    for i in range(d):  
        x = i * grid_spacing  
        y = i * grid_spacing_height  
        draw.line([(x, 0), (x, cropped_image.height)], fill=(255, 0, 0), width=2)  
        draw.line([(0, y), (cropped_image.width, y)], fill=(255, 0, 0), width=2)  
  
    for i in range(grid_size):  
        x = (i % d) * grid_spacing  
        y = (i // d) * grid_spacing_height  
        draw.text((x + 5, y + 5), str(i + 1), fill=(255, 0, 0), font=font)  
  
    file_name = os.path.basename(image_path)  
    file_name = file_name.replace('.jpg', '.png')  
    # Convert the cropped image to base64  
    file_path = os.path.join('cropped', file_name)  
    if not os.path.exists(file_path):  
        cropped_image.save(file_path)  
    return os.path.join('cropped', file_name)  
  
# Function to process images and convert to base64  
def process_images(blob_service_client, container_name, step, num_images):  
    container_client = blob_service_client.get_container_client(container_name)  
    blob_list = container_client.list_blobs()  
    base64_images = []  

    # Sort the blob list by image name
    sorted_blobs = sorted(blob_list, key=lambda x: x.name, reverse=True)

    # Process the images based on the step and number of images
    for i in range(0, len(sorted_blobs), step):
        if i >= num_images:
            break

        blob = sorted_blobs[i]
        if blob.name.endswith('.jpg') or blob.name.endswith('.png'):  
            blob_client = container_client.get_blob_client(blob.name)  
            if not os.path.exists('temp'):
                os.makedirs('temp')
            local_file_path = os.path.join("temp", os.path.basename(blob.name))  
            download_blob_to_file(blob_client, local_file_path)  
            cropped_image_path = add_grid_overlay(local_file_path)  
            base64_url = open_image_to_base64(cropped_image_path)  
            image_dict = {  
                'file_name': blob.name,  
                'base64_url': base64_url  
            }  
            base64_images.append(image_dict)  
            os.remove(local_file_path)  
      
    return base64_images  
  
def main(args):  
    
    dotenv.load_dotenv(args.azure_env_path)

    client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-01",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    ) 
  
 
    # Initialize the BlobServiceClient  
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))  
  
    # Define image container and process images  
    container_name = args.container_name
    step = args.step
    num_images = args.num_images  
    
    base64Frames = process_images(blob_service_client, container_name, step, num_images)  
    base64Urls = [image['base64_url'] for image in base64Frames]  
  
    # Prompt for the model  
    prompt = """Here is a series of 10 frames from a video of a building with screen displaying video ads  
    Your role is to monitor the screen and analyze the ads and detect any defect.  
  
    the images have a grid with 16 sections drawn in red with the number of the grid in the upper left corner from 1 to 16.  
  
    These are example defects that can happen:  
    - one section of the screen stays static across the 10 frames  
    - all the screen stays static across the 10 frames  
  
    The building is in the middle of the picture it has windows and screens all around. Windows are always static.  
    Only analyze the building screen, ignore all the other parts of the image and all other buildings and signs.  
    There is a Nasdaq logo at the bottom of the screen, it is always static, don't consider it as an ad and don't include it in any text extraction.  
  
    Your role is to:  
    1. Analyze each grid section independently and for each of the section, tell me if there is movement across the 10 frames  
    2. Analyze the whole building and tell me if there is a defect affecting the whole screen  
    3. Identify the different video ads on the screen and summarize the content of each ad, who is it for and what is the main message.  
    4. Classify each frame into the ad displayed on the screen  
  
    Return a JSON with the following structure  
    {"screen": {"defect":"Yes/No", "reason":"explain why you think there is a defect"},  
    "individual_sections":[{"number":1, "defect":"yes/no", "reason":"explain why you think there is a defect"}],  
    "ads": [{"advertiser": "Name of the advertiser for the ad", "summary": "description of the ad"}, ...],  
    "frames": [{"frame_number":1,"description":"visual description of the screen", "advertiser": "Name of the advertiser for the ad", "text": "the text displayed on the ad"}, ...],  
    }  
    """  
  
    # Assuming client.chat.completions.create is properly set up  
    response = client.chat.completions.create(  
        model="gpt-4o-mini",  
        response_format={ "type": "json_object" },  
        messages=[  
          {  
            "role": "user",  
            "content": [  
              {"type": "text", "text": prompt},  
               *map(lambda x: {"type":"image_url",   
                               "image_url": {"url":x}, "resize": 768}, base64Urls[:10]),  
            ],  
          }  
        ]  
      )  
  
    print(response.choices[0].message.content)  
  
    # Convert response to DataFrame  
    response_dict = ast.literal_eval(response.choices[0].message.content.replace('true','True'))  
    frames_df = pd.DataFrame(response_dict['frames'])  
  
    # Create DataFrame from base64Frames  
    images_df = pd.DataFrame(base64Frames[-10:])  
    final_df = pd.concat([images_df, frames_df], axis=1)  
  
    # Add timestamp  
    final_df['timestamp'] = pd.to_datetime(final_df['file_name'].str[11:-4], format='%Y%m%d%H%M%S')  
  
    # Add defect detection info  
    final_df['defect_detected'] = response_dict['screen']['defect']  
    final_df['defect_detected'] = final_df['defect_detected'].map({'True': True, 'False': False})  
    final_df['defect_reason'] = response_dict['screen']['reason']  
  
    # Add batch_id  
    final_df['batch_id'] = final_df['timestamp'].min().strftime('%Y%m%d%H%M%S') + '_' + final_df['timestamp'].max().strftime('%Y%m%d%H%M%S')  
  
    # Extract ads info  
    ads_df = pd.DataFrame(response_dict['ads'])  
    final_df = final_df.merge(ads_df, on='advertiser', how='left')  
  
    # Display final DataFrame  
    print(final_df[['timestamp','advertiser','summary','text','defect_detected','defect_reason','batch_id']])  
  
if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description='Process images and detect defects in video ads.')  
    parser.add_argument('--container_name', type=str, help='Name of the Azure Blob Storage container containing images')  
    parser.add_argument('--step', type=int, default=1, help='Step size for processing images')
    parser.add_argument('--num_images', type=int, default=10, help='Number of images to process')
    parser.add_argument("--azure_env_path", type=str, help="Path to the .env file containing Azure credentials")  
    args = parser.parse_args()  
    main(args)  
