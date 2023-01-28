from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import datetime
import base64
import os
import urllib
from urllib import request, parse
TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

def message_body():
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    PAGE_URL = f"https://uwaterloo.ca/food-services/locations-and-hours/daily-menu?field_uw_fs_dm_date_value%5Bvalue%5D%5Bdate%5D={date_today}"


    # Parse menu items and store it in an array

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    request = urllib.request.Request(PAGE_URL, headers=headers)
    response = urllib.request.urlopen(request)
    page_html = response.read()
    page_soup = soup(page_html, "html.parser")

    content = page_soup.findAll('div', attrs={'class': 'content'})

    try:
        mama_menu = content[12].text.split('\n')
    except:
        pass
    else:
        menu_array = []

        for item in mama_menu:
            if item != '' and item != 'Hot Dish' and item != '    Mudie’s  - Village 1    '\
                     and item != 'Induction Station':
                menu_array.append(item.strip())
        print(menu_array)


        # Format the message
        formatted_text = "Today's menu is: "
        for item in menu_array:
            formatted_text += f"\n{item}"
        return formatted_text


def lambda_handler(event, context):
    to_number = os.environ.get("to_number")
    from_number = os.environ.get("from_number")
    body = message_body()

    if not TWILIO_ACCOUNT_SID:
        return "Unable to access Twilio Account SID."
    elif not TWILIO_AUTH_TOKEN:
        return "Unable to access Twilio Auth Token."
    elif not to_number:
        return "The function needs a 'To' number in the format +12023351493"
    elif not from_number:
        return "The function needs a 'From' number in the format +19732644156"
    elif not body:
        return "The function needs a 'Body' message to send."

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e

    return "SMS sent successfully!"
