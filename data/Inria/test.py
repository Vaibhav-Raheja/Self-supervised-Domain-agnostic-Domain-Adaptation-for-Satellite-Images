import os

# Directory where your images are stored
image_directory = "./inria_splited_512_256/train/images"  # Update this path

# Path configurations
base_path = "./inria_splited_512_256/train/"
images_path = f"{base_path}images/"
gt_path = f"{base_path}gt/"

# Output file
output_file = "dataset_paths.txt"

# Fetch all TIFF files in the directory
file_names = [f for f in os.listdir(image_directory) if f.endswith('.tif')]

# Function to extract city name based on specific rules
def extract_city_name(file_name):
    # Remove extension and any trailing numbers
    base_name = file_name.split('.')[0]
    # Attempt to split by numbers and return the first part
    name_parts = [part for part in base_name if part.isalpha()]
    city_name = ''.join(name_parts)
    return city_name

# Open a file to write
with open(output_file, "w") as file:
    for name in file_names:
        city = extract_city_name(name)
        # Write formatted line to file
        file.write(f"{images_path}{name} {gt_path}{name} {city}\n")

print("File written successfully.")
