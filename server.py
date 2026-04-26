import asyncio
import csv
import base64
from collections import Counter
import os
import re
from urllib.parse import urlparse
import aiohttp
import email
from bs4 import BeautifulSoup
import string
from quart import Quart, request, jsonify
from quart_cors import cors, route_cors
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Quart(__name__)
app = cors(app, allow_origin="*", allow_headers=["Content-Type", "Authorization"])



def save_token_to_csv(token):
    with open('tokens.csv', 'w', newline='') as csvfile:
        fieldnames = ['access_token']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'access_token': token})

def get_saved_token():
    try:
        with open('tokens.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return row['access_token']
    except FileNotFoundError:
        return None

def get_email_details(credentials, email_id):
    service = build('gmail', 'v1', credentials=credentials)
    try:
        message = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
        raw_email = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        eml = email.message_from_bytes(raw_email)
        return eml
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None

def analyze_eml(eml):

    # *********************************Section statistics (mandatory) START*********************************

    # This SECTION extacts the following from eml file...
    # Number of text/plain sections
    # Number of text/html sections
    # Number of attachment sections
    # Number of application sections
    # Ratio of text/plain to any text sections
    # Length of texts in text/html section

    # Initialize the counts
    plain = 0
    html = 0
    other_text = -1 # Initialized with -1 to leave text/plain section
    application = 0
    image = 0

    # Iterate over the payload of the message
    for part in eml.walk():

        # get all content types in the email
        content_type = part.get_content_type()
        # Check if the part is a text/plain section
        if content_type == "text/plain":
            # Increment the count
            plain += 1
        if content_type == "text/html":
            # Increment the count
            html += 1
            # Get the text in the html section
            html_text = part.get_payload(decode=True)
            # Get the length of the text
            html_text_length = len(html_text)

        if content_type.startswith('text/'):
            # Increment the count
            other_text += 1

        if content_type.startswith('application/'):
            # Increment the count
            application += 1

        if content_type.startswith('image/'):
            # Increment the count
            image += 1

    # Print the count
    print("Number of text/plain sections:", plain)
    print("Number of text/html sections:", html)
    print("Number of application sections:", application)
    print("Number of image sections:", image)
    print("Ratio of text/plain to any text sections:", plain / other_text)
    print(f'Length of text in text/html section: {html_text_length}')

    # *********************************Section statistics (mandatory) END*********************************


    # *********************************Section Header statistics START*********************************
    # This SECTION extacts the following from eml file...
    # Number of standard headers
    # Number of In-Reply-To entities
    # Number of Received entities
    # Existence of User-Agent X
    # Existence of X-mailer

    # Initialize the count
    standard_headers_count = 0
    reply_to_count = 0
    received_count = 0
    user_agent_exists = False
    x_mailer_exists = False

    # List of standard headers
    standard_headers = ['From', 'To', 'Subject', 'Date', 'Message-ID']

    # Iterate over the headers in the message
    for key in eml.keys():
        # Check if the header is a standard header
        if key in standard_headers:
            # Increment the count
            standard_headers_count += 1
        if key == "Reply-To":
            # Increment the count
            reply_to_count += 1
        if key == "Received":
            # Increment the count
            received_count += 1
        # Check if the header is the User-Agent header
        if key.startswith('User-Agent'):
            user_agent_exists = True
        # Check if the header is the X-mailer header
        if key.startswith('X-mailer'):
            x_mailer_exists = True


    # Print the count
    print(f"Number of standard headers: {standard_headers_count}")
    print(f"Number of Reply-To entities: {reply_to_count}")
    print(f"Number of Received entities: {received_count}")
    print(f'User-Agent exists: {user_agent_exists}')
    print(f'X-Mailer exists: {x_mailer_exists}')
    # *********************************Section Header statistics END*********************************


    # *********************************Section MIME version  END*********************************

    # MIME version of the first section
    # Case variance in MIME-Version header tag

    # Check if the MIME-Version header exists
    if 'MIME-Version' in eml:
        # Get the value of the MIME-Version header
        mime_version = eml['MIME-Version']
        
        # Check if the value of the MIME-Version header is "1.0" (ignoring case)
        if mime_version.lower() == "1.0":
            # The MIME-Version header is "1.0"
            print("MIME-Version header is 1.0")
        else:
            # The MIME-Version header is not "1.0"
            print("MIME-Version header is not 1.0")
    else:
        # The MIME-Version header does not exist
        print("MIME-Version header does not exist")
    # *********************************Section MIME version  END*********************************


    # *********************************Section Message-ID END*********************************

    # Length of Message-ID
    # ASCII number of Message-ID boundary character (if any)
    # Existence of the domain of Message-ID (if any) in ID part
    # Is ID part hexadecimal (except the special characters)
    # Is ID part decimal (except the special characters)
    # Existence of dots in ID part
    # Existence of special characters in ID part
    # Is domain part hexadecimal (except the special characters)
    # Is domain part decimal (except the special characters)
    # Existence of dots in domain part
    # Existence of special characters other than dots in domain part

    # Get the Extract the Message-ID from the header
    message_id = eml.get("Message-ID")

    # Find the length of the Message-ID
    message_id_length = len(message_id)

    # Check if the Message-ID has a boundary character
    if "<" in message_id and ">" in message_id:
        # Find the index of the boundary character
        boundary_index = message_id.index("@")

        # Get the boundary character
        boundary_char = message_id[boundary_index]

        if boundary_char in message_id:
            # Split the message-ID string using the '@' character as the delimiter
            message_id_parts = message_id.split('@')
            domain_part = message_id_parts[1]
            domain_part = re.sub(r'[<>]', '', domain_part)

        # Get the ASCII number of the boundary character
        boundary_ascii = ord(boundary_char)

    # The regular expression pattern to match a hexadecimal string
    pattern = r'^[a-fA-F0-9]+$'

    # The ID part of the Message-ID
    id_part = message_id_parts[0]
    id_part = re.sub(r'[<>]', '', id_part)
    # Existence of dots in ID part
    num_dots_id = id_part.count(".")
    # Existence of dots in domain part
    num_dots_domain = domain_part.count(".")
    special_char = False
    # Existence of special characters in ID part
    if re.search(r'[^a-zA-Z0-9]', id_part):
        special_char = True

    # Remove special characters
    id_part_cleaned = id_part.translate(str.maketrans("", "", string.punctuation))
    domain_part_cleaned = domain_part.translate(str.maketrans("", "", string.punctuation))


    # Print the length of the Message-ID
    print(f"Length of Message-ID :{message_id_length}")
    # Print the ASCII number of the boundary character
    print(f"ASCII number of Message-ID boundary character :{boundary_ascii}")
    # Check if the domain is present in the ID part of the header
    if domain_part in message_id:
        print(f"Domain in Message-ID :{domain_part}")
    else:
        print(f"NO Domain in Message-ID.")
    # Check if the ID part is hexadecimal (except for the special characters)
    if re.match(pattern, id_part_cleaned):
        print(f"The ID part is hexadecimal : {id_part}")
    # Is ID part decimal (except the special characters)
    elif id_part_cleaned.isdecimal():
        print(f"The ID part is decimal :{id_part}")
    # Existence of dots in ID part
    print(f"There are {num_dots_id} dot(s) in the ID part of the Message-ID")
    # Existence of special characters in ID part
    print(f"Existence of special characters in ID part : {special_char}")
    # Is domain part hexadecimal (except the special characters)
    if re.match(pattern, id_part_cleaned):
        print(f"The domain part is hexadecimal : {domain_part}")
    # Is domain part decimal (except the special characters)
    elif domain_part_cleaned.isdecimal():
        print(f"The domain part is decimal :{domain_part}")
    # Existence of dots in domain part
    print(f"There are {num_dots_domain} dot(s) in the domain part of the Message-domain")
    # Existence of special characters other than dots in domain part
    print(f"Existence of special characters in domain part : {special_char}")
    # *********************************Section Message-ID END*********************************


    # *********************************Section Mail address and domain END*********************************

    # Number of From header tags in the mail thread
    # Number of To header tags in the mail thread
    # Number of unique To addresses in the mail thread
    # Number of unique Reply-To addresses in the mail thread
    # Number of unique domains in all email addresses
    # Ratio of unique To domains to the unique domains in all email addresses
    # Number of Cc addresses
    # Number of Bcc addresses
    # Number of Sender addresses
    # Is Return-Path addresses identical to Reply-To addresses
    # Number of To domains identical to From domain
    # Number of Cc domains identical to From domain
    # Number of Bcc domains identical to From domain
    # Is From domain same to Reply-To domain
    # Is From domain same to Return-Path domain
    # Is From entity bracketed
    # Is To entity bracketed


    # Initialize counts
    from_headers_count = 0
    to_headers_count = 0
    unique_to_headers_count = 0
    unique_reply_to_addresses_count = 0
    unique_domains_in_all_email_addresses_count = 0
    CC_addresses_count = 0
    BCC_addresses_count = 0
    sender_addresses_count = 0


    # Iterate over the headers in the message
    for key in eml.keys():
        # Number of From header tags in the mail thread
        if key == "From":
            # Increment the count
            from_headers_count += 1
        # Number To addresses in the mail thread
        if key == "To":
            # Increment the count
            to_headers_count += 1
            # Initialize a set to store the unique To addresses
            to_set = set()
            to_set.add(eml['To'])
        # Number of unique Reply-To addresses in the mail thread
        if key == "Reply-To":
            # Initialize a set to store the unique Reply-To addresses
            reply_to_set = set()
            reply_to_set.add(eml['Reply-To'])
        # Number of Cc addresses
        if key == "Cc":
            # Increment the count
            CC_addresses_count += 1
        # Number of Bcc addresses
        if key == "Bcc":
            # Increment the count
            BCC_addresses_count += 1
        # Number of Sender addresses
        if key == "Sender":
            # Increment the count
            sender_addresses_count += 1


    # Print the count
    print(f"Number of From header(s): {from_headers_count}")
    print(f"Number of To header(s): {to_headers_count}")
    print(f"Number of unique To addresses: {to_set}")
    print(f"Number of unique Reply-To addresses: {reply_to_set}")
    print(f"Number of Cc addresses: {CC_addresses_count}")
    print(f"Number of Bcc addresses: {BCC_addresses_count}")
    print(f"Number of Sender addresses: {sender_addresses_count}")


    # Is Return-Path addresses identical to Reply-To addresses
    is_ReturnPath_Address_similar_to_ReplyTo_Address = False

    return_path = eml.get("Return-Path")
    reply_to = eml.get("Reply-To")

    if return_path == reply_to:
        is_ReturnPath_Address_similar_to_ReplyTo_Address = True
    else:
        is_ReturnPath_Address_similar_to_ReplyTo_Address = False

    print("is_ReturnPath_Address_similar_to_ReplyTo_Address",is_ReturnPath_Address_similar_to_ReplyTo_Address)


    # print(f'Number of unique domains in all mails: {user_agent_exists}')



    # print(f'X-Mailer exists: {x_mailer_exists}')



    # is_From_Domain_identical_to_ReplyTo_Domain 

    from_address = eml.get("From")
    reply_to_address = eml.get("Reply-To")

    from_domain = from_address.split('@')[1].split('>')[0]
    reply_to_domain = reply_to_address.split('@')[1].split('>')[0]

    print("from_address ",from_address)
    print("reply_to_address",reply_to_address)


    is_From_Domain_identical_to_ReplyTo_Domain = False

    if from_domain == reply_to_domain:
        is_From_Domain_identical_to_ReplyTo_Domain = True
    else:
        is_From_Domain_identical_to_ReplyTo_Domain = False

    print("is_From_Domain_identical_to_ReplyTo_Domain ",is_From_Domain_identical_to_ReplyTo_Domain)



    # Number of unique domains in all email addresses

    email_addresses = eml.get_all('to', []) + eml.get_all('from', []) + eml.get_all('cc', []) + eml.get_all('bcc', [])

    unique_domains = set()
    for email_address in email_addresses:
        domain = email_address.split('@')[-1].split('>')[0]
        unique_domains.add(domain)

    # count number of unique domains
    num_unique_domains = len(unique_domains)

    print("Number of unique domains in all email addresses:", num_unique_domains)



    # Number of To domains identical to from Domain

    # Get the From domain
    from_domain = eml['From'].split('@')[1].split('>')[0]

    # Get a list of all the To domains
    to_domains = [to.split('@')[1].split('>')[0] for to in eml['To'].split(',')]

    # Count the occurrences of each domain in the To list
    to_domain_counts = Counter(to_domains)

    # Check how many times the From domain appears in the To list
    identical_domains_count = to_domain_counts[from_domain]

    print(f"Number of To domains identical to From Domain: {identical_domains_count}")



    # Is from domain same to Return-Path domain

    from_addr = eml.get("From")
    return_path_addr = eml.get("Return-Path")
    is_From_Domain_identical_to_ReturnPath_Domain = False

    # extract the domain parts of the addresses
    from_domain = from_addr.split("@")[1].strip(">")
    return_path_domain = return_path_addr.split("@")[1].strip(">")

    # check if the From and Return-Path domains are the same
    if from_domain == return_path_domain:
        is_From_Domain_identical_to_ReplyPath_Domain = True
    else:
        is_From_Domain_identical_to_ReplyPath_Domain = False

    print("is_From_Domain_identical_to_ReplyPath_Domain : ",is_From_Domain_identical_to_ReplyPath_Domain)


    # ********************************Section Mail address and domain END*********************************


    # ********************************Section boundary START*********************************

    # Length of the first boundary ID 
    # Does the first boundary ID start with an equal symbol (=) 
    # Existence of equal symbols (=) in the middle of the first boundary ID 
    # Existence of underscores in the first boundary ID 
    # Existence of dots in the first boundary ID 
    # Existence of the other special characters in the first boundary ID 
    # Is the first boundary ID hexadecimal (except the special characters) 
    # Is the first boundary ID decimal (except the special characters)



    # Length of the first boundary ID

    boundary = eml.get_boundary()

    boundary_length = len(boundary)

    print(f"Length of the first boundary ID: {boundary_length}")


    # Does the first boundary ID start with an equal symbol (=) 

    is_firstBoundaryID_starts_with_an_equal_symbol= boundary.startswith('=')

    print("is_firstBoundaryID_starts_with_an_equal_symbol : ",is_firstBoundaryID_starts_with_an_equal_symbol)


    # Existence of equal symbols (=) in the middle of the first boundary ID

    index = eml.as_string().find(boundary)

    if '=' in eml.as_string()[index:]:
        existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID = True
    else:
        existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID = False

    print("existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID ",existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID)


    # existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID = False

    existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID = '_' in boundary
    print("existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID : ",existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID)


    # existence_Of_Dots_In_The_First_Boundary_ID

    boundary = eml.get_boundary()
    existence_Of_Dots_In_The_First_Boundary_ID = '.' in boundary
    print(f"existence_Of_Dots_In_The_First_Boundary_ID: {existence_Of_Dots_In_The_First_Boundary_ID}")

    # Existence of the other special characters in the first boundary ID

    existence_Of_Other_Special_Characters_In_The_First_Boundary_ID = False
    if boundary:
        special_chars = ['+', '-', '~', '\'', '#', '$', '%', '&', '*', '!', '?', '@']
        for char in special_chars:
            if char in boundary:
                existence_Of_Other_Special_Characters_In_The_First_Boundary_ID= True


    print("existence_Of_Other_Special_Characters_In_The_First_Boundary_ID ",existence_Of_Other_Special_Characters_In_The_First_Boundary_ID)

    # Is the first boundary ID hexadecimal (except the special characters)

    is_First_boundary_ID_Hexadecimal = False
    regex = r"^[0-9a-fA-F]+$"
    if re.match(regex, boundary):
        is_First_boundary_ID_Hexadecimal = True
    else:
        is_First_boundary_ID_Hexadecimal = False

    print("is_First_boundary_ID_Hexadecimal ",is_First_boundary_ID_Hexadecimal)


    # Is the first boundary ID Decimal (except the special characters)

    is_First_boundary_ID_Decimal = False

    if re.search("^[0-9]+$", boundary):
        is_First_boundary_ID_Decimal = True
    else:
        is_First_boundary_ID_Decimal = False

    print("is_First_boundary_ID_Decimal ",is_First_boundary_ID_Decimal)


    # ********************************Section boundary END*********************************


    # ********************************Section Character set START*********************************

    # Index of charset in the first section 
    # Number of unique charset in all the sections


    # Index of charset in the first section 

    index_of_charset_in_the_first_section  = 0
    for part in eml.get_payload():
        if "charset=" in str(part):
            charset_index = str(part).find("charset=")
            index_of_charset_in_the_first_section = charset_index
            break

    print("index_of_charset_in_the_first_section : ",index_of_charset_in_the_first_section)


    # Number of unique charset in all the sections

    charsets = []

    # loop through all parts of the email
    for part in eml.walk():
        # check if charset exists for part
        if part.get_content_charset():
            # add charset to list if not already in the list
            if part.get_content_charset() not in charsets:
                charsets.append(part.get_content_charset())

    number_of_unique_charsets_in_all_sections = len(charsets)


    print("Number of unique charsets in all sections:",number_of_unique_charsets_in_all_sections)

    # ********************************Section Character set END*********************************


    # ********************************Section Cascading Style Sheets (CSS) START*********************************


    # Length of <style> bodies and inline style bodies


    # extract HTML content
    html_content = None
    for part in eml.walk():
        if part.get_content_type() == 'text/html':
            html_content = part.get_payload(decode=True)
            break

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # calculate the length of <style> bodies and inline style bodies
    style_lengths = []
    for tag in soup.find_all(['style', '[style]']):
        style_lengths.append(len(tag.text))

    # print the result
    print(f"Length of <style> bodies and inline style bodies: {sum(style_lengths)}")
    print(style_lengths)


    # Existence of direction: rtl style for backward rendering

    # extract HTML content from email message
    html = None
    for part in eml.walk():
        if part.get_content_type() == "text/html":
            html = part.get_payload(decode=True)
            break

    # parse HTML with BeautifulSoup and count occurrences of 'direction: rtl' in style attribute
    count = 0
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for element in soup.find_all(style=lambda value: value and 'direction: rtl' in value):
            count += 1

    print("Number of elements with 'direction: rtl' style:", count)





    # ********************************Section Cascading Style Sheets (CSS) END*********************************


    # ********************************Section JavaScript (JS) END*********************************

    # Existence of inline <script>

    for part in eml.walk():
        # check if the part is an HTML part
        if part.get_content_type() == 'text/html':
            # check if the part contains inline <script>
            if '<script>' in part.get_payload():
                print('Inline <script> found in HTML part.')


    # ********************************Section JavaScript (JS) END*********************************


    # ********************************Section Document Object Model (DOM) END*********************************
    # Depth of DOM object tree 



    # Parse the HTML content of the email body
    html_content = eml.get_payload()
    print("html_content : ",str(html_content))
    soup = BeautifulSoup(str(html_content), 'html.parser')

    # Calculate the depth of the DOM object tree
    depth = 0
    for child in soup.recursiveChildGenerator():
        if child.name:
            depth = max(depth, child.attrs.get('depth', 0))

    print("depth of DOM : ",depth)

    # Number of DOM leaf nodes 

    # Number of unique DOM leaf node types 

    # Mean of DOM leaf node depths 

    # Standard deviation of DOM leaf node depths



    # ********************************Section Document Object Model (DOM) END*********************************


    # ********************************Section Links END*********************************

    # Number of email addresses in text/html section


    # Find the text/html section
    html_part = None
    for part in eml.walk():
        if part.get_content_type() == 'text/html':
            html_part = part
            break

    if html_part is None:
        print('No text/html section found')
    else:
        # Parse the HTML content using beautifulsoup
        soup = BeautifulSoup(html_part.get_payload(decode=True), 'html.parser')
        
        # Find all email addresses in the HTML content
        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        email_addresses = set(re.findall(email_regex, str(soup)))
        
        print('Number of email addresses in text/html section:', len(email_addresses))


    # Number of <a href> and <a data-saferedirecturl> tags 

    # get the HTML part of the email
    html_part = None
    for part in eml.walk():
        if part.get_content_type() == 'text/html':
            html_part = part
            break

    # parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_part.get_payload(), 'html.parser')

    # count the number of <a href> and <a data-saferedirecturl> tags
    a_tags = soup.find_all('a')
    num_a_tags = len(a_tags)
    num_data_safere_directurl_tags = len(soup.find_all('a', {'data-saferedirecturl': True}))

    # print the results
    print('Number of <a href> tags: ', num_a_tags)
    print('Number of <a data-saferedirecturl> tags: ', num_data_safere_directurl_tags)


    # Number of URLs in text/html section 

    html_payload = ""
    for part in eml.walk():
        if part.get_content_type() == "text/html":
            html_payload += part.get_payload(decode=True).decode('utf-8')

    # Use BeautifulSoup to parse the HTML and extract all the URLs
    soup = BeautifulSoup(html_payload, "html.parser")
    urls = []
    for a_tag in soup.find_all('a', href=True):
        url = a_tag['href']
        # Remove any trailing spaces or punctuation marks
        url = re.sub('[\s\.\?,!]+$', '', url)
        urls.append(url)

    for a_tag in soup.find_all('a', attrs={"data-saferedirecturl": True}):
        url = a_tag['data-saferedirecturl']
        # Remove any trailing spaces or punctuation marks
        url = re.sub('[\s\.\?,!]+$', '', url)
        urls.append(url)

    # Print the number of URLs found in the text/html section
    print("Number of URLs in text/html section:", len(urls))


    # Ratio of unique domains to the domains of all URLs in any tags




    # ********************************Section Links END********************************


# endpoint for receiving the OAuth token
@app.route('/token', methods=['POST'])
async def receive_token():
    data = await request.get_json()

    if data and 'token' in data:
        token = data['token']
        print(f"Received token: {token}")  # Add this line
        save_token_to_csv(token)
        return 'Token received.', 200
    else:
        return 'No token received.', 400


@app.route('/upload', methods=['POST'])
async def upload():
    data = await request.get_json()

    if data and 'email_id' in data:
        email_id = data['email_id']

        # Get the OAuth token from the saved location
        token = get_saved_token()

        credentials = Credentials(token)

        email = get_email_details(credentials, email_id)

        if not email:
            return 'Failed to fetch email.', 400


        # Call the analyze_eml function with the email object
        analysis_results = analyze_eml(email)
        print(analysis_results)

        # Analyze the EML file here, and store the result in the "analysis_result" variable
        # ...
        analysis_result = {
            "email_id": email_id,
            "status": "safe"  # Replace this with the actual analysis result (e.g., "phishing" or "safe")
        }

        return jsonify(analysis_result), 200
    else:
        return 'No email ID received.', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('certs/cert.pem', 'certs/key.pem'))
