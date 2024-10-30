from datetime import datetime
from io import BytesIO
from os.path import dirname, abspath, basename, splitext

import requests
from PIL import Image

BASE_DIR = dirname(dirname(abspath(__file__)))

print(BASE_DIR)

def save_image_from_url(url,filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')):
    try:
        # Fetch the image content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        content_type =  response.headers.get("Content-Type")

        image_type = content_type.split("/")[-1]

        # Open the image with Pillow using a BytesIO stream
        image = Image.open(BytesIO(response.content))

        output_path  = f"{BASE_DIR}/images/{filename}.{image_type}"

        # Save the image locally
        image.save(output_path)
        print(f"Image saved at {output_path}")

        return output_path

    except Exception as e:
        print("An error occurred:", e)

        return False


def resize_image(input_path, target_width=750):
    # Open the image
    with Image.open(input_path) as img:
        # Check if the image width is greater than the target width
        if img.width > target_width:
            # Calculate the new height to maintain the aspect ratio
            aspect_ratio = img.height / img.width
            new_height = int(target_width * aspect_ratio)

            # Resize the image with the new dimensions
            resized_img = img.resize((target_width, new_height), Image.LANCZOS)

            output_path = f"{dirname(abspath(input_path))}/{splitext(basename(abspath(input_path)))[0]}-scaled{splitext(abspath(input_path))[1]}"

            print(output_path)

            # Save the resized image
            resized_img.save(output_path)
            print(f"Image resized to {target_width}px width, saved at {output_path}")

            return output_path
        else:
            print("Image width is already 750px or smaller; no resizing needed.")

            return input_path



if __name__ == '__main__':
    url = 'https://assets.nst.com.my/images/articles/IRAN-ISRAEL-CONFLICT_291024n01-2_1730133698.jpg'
    saved = save_image_from_url(url)

    resize_image(saved)

    pass