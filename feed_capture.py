import argparse  
import os  
import time  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from azure.storage.blob import BlobServiceClient  
from dotenv import load_dotenv  
  
def main(livestream_url, interval, num_screenshots, azure_env_path, container_name):  
    # Load environment variables  
    load_dotenv(azure_env_path)  
      
    # Set up the Selenium WebDriver  
    driver = webdriver.Chrome()  
    driver.get(livestream_url)  
    driver.find_element(By.TAG_NAME, "body").click()  
  
    # Create a connection to the Azure Blob Storage  
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')  
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)  
    container_client = blob_service_client.get_container_client(container_name)  
  
    # Capture and save the screenshots  
    for i in range(num_screenshots):  
        # Generate the screenshot file name  
        now = time.strftime('%Y%m%d%H%M%S')  
        screenshot_file = f"screenshot_{now}.png"  
        screenshot_file_path = os.path.join("image", screenshot_file)  
  
        # Take the screenshot  
        driver.save_screenshot(screenshot_file_path)  
  
        # Upload the screenshot file to Azure Blob Storage  
        with open(screenshot_file_path, "rb") as data:  
            container_client.upload_blob(name=screenshot_file, data=data)  
  
        # Wait for the specified interval  
        time.sleep(interval)  
  
    # Close the WebDriver  
    driver.quit()  
  
if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Capture screenshots from a livestream and upload to Azure Blob Storage.")  
    parser.add_argument("livestream_url", type=str, help="URL of the livestream")  
    parser.add_argument("interval", type=int, help="Interval between screenshots in seconds")  
    parser.add_argument("num_screenshots", type=int, help="Number of screenshots to capture")  
    parser.add_argument("azure_env_path", type=str, help="Path to the .env file containing Azure credentials")  
    parser.add_argument("container_name", type=str, help="Name of the Azure Blob Storage container")  
  
    args = parser.parse_args()  
  
    main(args.livestream_url, args.interval, args.num_screenshots, args.azure_env_path, args.container_name)  
