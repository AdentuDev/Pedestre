import os
import csv
from PIL import Image
import pandas as pd
import subprocess
import json
import re

def convert_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

def parse_gps_coordinate(coordinate):
    match = re.match(r'(\d+) deg (\d+)\'.* (\d+\.\d+)\" (\w)', coordinate)
    if not match:
        print(f"GPS coordinate format is unexpected: {coordinate}")
        return None
    
    try:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4)

        return convert_to_decimal(degrees, minutes, seconds, direction)
    except Exception as e:
        print(f"Error parsing GPS coordinate: {coordinate} with error: {e}")
        return None

def get_image_metadata(image_path):
    try:
        result = subprocess.run(
            ['exiftool', '-j', image_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if result.returncode != 0:
            print(f"Error getting metadata for {image_path}: {result.stderr}")
            return {}

        # Ensure result is not empty
        if not result.stdout.strip():
            print(f"No metadata found for {image_path}")
            return {}

        try:
            metadata = json.loads(result.stdout)
        except json.JSONDecodeError as json_err:
            print(f"JSON decoding failed for {image_path}: {json_err}")
            return {}

        # Ensure metadata is not empty or malformed
        if not metadata or not isinstance(metadata, list) or len(metadata) == 0:
            print(f"Invalid or empty metadata for {image_path}")
            return {}

        return metadata[0]
    except Exception as e:
        print(f"Error getting metadata for {image_path}: {e}")
        return {}

def process_directory(directory):
    image_data = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif')):
                image_path = os.path.join(root, file)
                #print(f"Processing file: {image_path}")
                metadata = get_image_metadata(image_path)
                if not metadata:
                    print(f"No metadata found for: {image_path}")
                    continue
                #print(f"Metadata for {image_path}: {metadata}")
                
                image_info = {
                    'Image Path': image_path,
                    'Image Name': file,
                }
                if 'CreateDate' in metadata:
                    image_info['DateTimeOriginal'] = metadata['CreateDate']
                if 'GPSLatitude' in metadata:
                    try:
                        image_info['Latitude'] = parse_gps_coordinate(metadata['GPSLatitude'])
                    except ValueError as e:
                        print(f"Error parsing GPSLatitude for {image_path}: {e}")
                if 'GPSLongitude' in metadata:
                    try:
                        image_info['Longitude'] = parse_gps_coordinate(metadata['GPSLongitude'])
                    except ValueError as e:
                        print(f"Error parsing GPSLongitude for {image_path}: {e}")
                
                image_data.append(image_info)    
    return image_data

def save_to_csv(data, csv_file):
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)

def main():
    directory = '20240815'  # Replace with the correct path if different
    csv_file = '15 Agosto.csv'
    
    image_data = process_directory(directory)
    save_to_csv(image_data, csv_file)

    print(f"Metadata for images in '{directory}' has been saved to '{csv_file}'")

if __name__ == "__main__":
    main()
