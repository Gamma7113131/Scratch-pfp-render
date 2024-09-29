from PIL import Image
import requests
from io import BytesIO
import colorsys
import scratchattach as scratch3

# Function to convert lists of values to a combined string with a separator
def list_to_string(lst, num_digits=2):
    rounded_strings = [f"{int(round(num)):0{num_digits}d}" for num in lst]
    return ''.join(rounded_strings)

# Function to download and open an image from a URL
def url_to_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        raise ValueError("Image not found or could not be fetched")

# Function to convert RGB values to HSB (Hue, Saturation, Brightness)
def rgb_to_hsb(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = h * 98 + 1  # Convert hue to range [1, 99]
    s = s * 98 + 1  # Convert saturation to range [1, 99]
    v = v * 98 + 1  # Convert brightness to range [1, 99]
    return h, s, v

# Function to process the image and extract hue, saturation, and brightness
def process_image(url):
    image = url_to_image(url)
    image = image.convert('RGB')  # Ensure image is in RGB mode

    width, height = image.size
    hue = []
    saturation = []
    brightness = []

    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            h, s, v = rgb_to_hsb(r, g, b)
            hue.append(h)
            saturation.append(s)
            brightness.append(v)

    hue_str = list_to_string(hue)
    saturation_str = list_to_string(saturation)
    brightness_str = list_to_string(brightness)
    
    return hue_str, saturation_str, brightness_str

# Scratch connection setup
session_id = ".eJxVj81ugzAQhN-Fc0P97zi3VEpyySlSK7UXtOAFXIJNwahSq757bYlLtLf5dmdnfot1wdnDiMWhuMA4gqaUpymeihgG9Ek2VHKjuKbKCAFEGtqSlreiFlALZuDAvujxozqvp_kdmZ_Ou_6Kt7fjZf_aJZt76JzfuSk7sVKQkhFWcpNIBWvsqxygcjZhyqUiIr1JzH6C70IV3Yg_wed0p3UOEz5fg7fBP173sPT5fo_YcKt4i1JL3VqlmNHCAhpLOFN7WQNoYLkbLrEJYXDZ-TvMA9pHyxqa1D6nyhr66BqILvhyA0t5w-m-iS_b8t8_wMVqBA:1sk1h6:13yPz2Za7buBJGahs63UDmcugf8"
username = "Gamma7113131"
project_id = "1061478063"

session = scratch3.Session(session_id, username=username)
conn = session.connect_cloud(project_id)
client = scratch3.CloudRequests(conn)

# Fetch the user ID from the username
def fetch_user_id(username):
    url = f"https://api.scratch.mit.edu/users/{username}/"
    response = requests.get(url)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get('id')
    else:
        raise ValueError("User not found or could not be fetched")

# Handle the username request
@client.request
def username(user):
    print(f"Received username request with value: {user}")
    try:
        user_id = fetch_user_id(user)
        url = f'https://cdn2.scratch.mit.edu/get_image/user/{user_id}_50x50.png?v='
        print(f"Profile picture URL: {url}")
        hue_str, saturation_str, brightness_str = process_image(url)
        # Combine the strings with the required format
        combined_str = f"{hue_str}|{saturation_str}|{brightness_str}"
        conn.set_var("combined_hsb", combined_str[:254])  # Trim to fit Scratch's limit
        print("Successfully set the cloud variable.")
        return combined_str  # Return the combined string
    except Exception as e:
        print(f"Error: {e}")
        conn.set_var("combined_hsb", f"error: {e}")
        return f"error: {e}"

# Run the client
@client.event
def on_ready():
    print("Request handler is running")

client.run()
