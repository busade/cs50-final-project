from urllib.parse import urlparse
import httplib2,random,string, qrcode
from PIL import Image
from io import BytesIO


def image_to_bytes(img):
    # Convert a Pillow Image to bytes
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='PNG')
    img_bytes = img_byte_array.getvalue()
    return img_bytes

def generate_qrcode(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = image_to_bytes(img)
    return img_bytes

def generate_short_url():
    base = "short.ly/"
    char = string.ascii_letters + string.digits
    res = ''.join(random.choices(char, k=6))
    ur= base +res
    return ur

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False