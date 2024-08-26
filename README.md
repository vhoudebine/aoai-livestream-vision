# Livestream Screenshot Capture and Analysis  
   
This repository contains two main Python scripts for capturing screenshots from a livestream, uploading them to Azure Blob Storage, and analyzing the images for defects in video ads. Below you will find instructions on how to set up and use these scripts.  
   
## Repository Contents  
   
- `feed_capture.py`: Captures screenshots from a livestream and uploads them to Azure Blob Storage.  
- `image_analysis.py`: Downloads images from Azure Blob Storage, processes them, and analyzes them for defects in video ads.  
- `requirements.txt`: List of dependencies required to run the scripts.  
   
## Prerequisites  
   
- Python 3.7+  
- Azure Blob Storage account  
- Azure OpenAI account  
- Google Chrome browser installed  
- Chrome WebDriver installed  
   
## Setup  
   
1. **Clone the repository:**  
  
   ```bash  
   git clone https://github.com/your-username/repository-name.git  
   cd repository-name  
   ```  
   
2. **Install the dependencies:**  
  
   ```bash  
   pip install -r requirements.txt  
   ```  
   
3. **Create a `.env` file with your Azure credentials:**  
  
   ```plaintext  
   AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string  
   AZURE_OPENAI_API_KEY=your_openai_api_key  
   AZURE_OPENAI_ENDPOINT=your_openai_endpoint  
   ```  
   
## Usage  
   
### Capturing Screenshots  
   
Use the `feed_capture.py` script to capture screenshots from a livestream and upload them to Azure Blob Storage.  
   
#### Command-line Arguments:  
   
- `--livestream_url`: URL of the livestream.  
- `--interval`: Interval between screenshots in seconds.  
- `--num_screenshots`: Number of screenshots to capture.  
- `--azure_env_path`: Path to the `.env` file containing Azure credentials.  
- `--container_name`: Name of the Azure Blob Storage container.  
   
#### Example:  
   
```bash  
python feed_capture.py --livestream_url "http://example.com/livestream" --interval 10 --num_screenshots 5 --azure_env_path ".env" --container_name "your-container-name"  
```  
   
### Analyzing Images  
   
Use the `image_analysis.py` script to download images from Azure Blob Storage, process them, and analyze them for defects in video ads.  
   
#### Command-line Arguments:  
   
- `--container_name`: Name of the Azure Blob Storage container containing images.  
- `--step`: Step size for processing images.  
- `--num_images`: Number of images to process.  
- `--azure_env_path`: Path to the `.env` file containing Azure credentials.  
   
#### Example:  
   
```bash  
python image_analysis.py --container_name "your-container-name" --step 1 --num_images 10 --azure_env_path ".env"  
```  
   
## Output  
   
The `image_analysis.py` script will output a DataFrame displaying the following information:  
   
- `timestamp`: Timestamp of the image.  
- `advertiser`: Name of the advertiser for the ad.  
- `summary`: Description of the ad.  
- `text`: The text displayed on the ad.  
- `defect_detected`: Indicates if a defect was detected.  
- `defect_reason`: Reason for the defect.  
- `batch_id`: Batch ID for the images processed.  
   
