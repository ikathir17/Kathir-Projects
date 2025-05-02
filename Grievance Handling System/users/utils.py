import random
import string

def generate_captcha():
    # Generate a random string of 6 characters (mix of letters and numbers)
    characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(6))
    
    # Randomly make some characters italic by wrapping them in <i> tags
    captcha_html = ''
    for char in captcha_text:
        if random.choice([True, False]):
            captcha_html += f'<i>{char}</i>'
        else:
            captcha_html += char
            
    return captcha_text, captcha_html
