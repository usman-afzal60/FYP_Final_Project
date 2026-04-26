import csv
import email
import os
import email.utils
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import string
from collections import Counter
from email.generator import BytesGenerator
from io import BytesIO

def extract_str_attr(eml):
    # write header row 
    headers = ["Number of text/plain sections", "Number of application sections","Number of image sections","Length of text in text/html section","Number of standard headers","Number of Reply-To entities","Number of Received entities","User-Agent exists","X-Mailer exists","Length of Message-ID","ASCII number of Message-ID boundary character","Domain in Message-ID","The ID part is hexadecimal","The ID part is decimal","The Domain part is hexadecimal","The Domain part is decimal","Existence of special characters in ID part","Number of dot(s) in the ID part of the Message-ID","Number of From header(s)","Number of To header(s)","Number of unique To addresses","Number of Cc addresses","Number of Bcc addresses","Number of Sender addresses","is_ReturnPath_Address_similar_to_ReplyTo_Address","is_From_Domain_identical_to_ReplyTo_Domain","Number of unique domains in all email addresses","Number of To domains identical to From Domain","is_From_Domain_identical_to_ReplyPath_Domain","Length of the first boundary ID","is_firstBoundaryID_starts_with_an_equal_symbol","existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID","existence_Of_Dots_In_The_First_Boundary_ID","existence_Of_Other_Special_Characters_In_The_First_Boundary_ID","is_First_boundary_ID_Hexadecimal","is_First_boundary_ID_Decimal","index_of_charset_in_the_first_section","Number of unique charsets in all sections","Length of <style> bodies and inline style bodies","Number of elements with 'direction: rtl' style","Inline <script> found in HTML part","depth of DOM","Number of email addresses in text/html section","Number of <a href> tags","Number of <a data-saferedirecturl> tags","number of URLS in text/html section"]
    plain = 0
    html = 0
    other_text = -1 # Initialized with -1 to leave text/plain section
    application = 0
    image = 0


    standard_headers_count = 0
    reply_to_count = 0
    received_count = 0
    user_agent_exists = False
    x_mailer_exists = False 

    # extract fields from parsed email
    for part in eml.walk():
    # get all content types in the email
        content_type = part.get_content_type()
        # Check if the part is a text/plain section
        if content_type == "text/plain":
            # Increment the count
            plain += 1
        if content_type == "text/html":
            # Increment the count
            # html += 1
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

    message_id = eml.get("Message-ID")
    message_id_str = str(message_id)
    message_id_length = len(message_id_str)
    is_id_part_hexadecimal = False
    is_id_part_decimal = False
    is_domain_part_hexadecimal = False
    is_domain_part_decimal = False

    # Check if the Message-ID has a boundary character
    if "<" in message_id_str and ">" in message_id_str:
        # Find the index of the boundary character
        if "@" in message_id_str:
            boundary_index = message_id_str.index("@")
            boundary_char = message_id_str[boundary_index]
            # Your code for processing the message_id after finding the index
        else:
            # Handle the case where "@" is not present in the message_id
            pass

    # Split the message-ID string using the '@' character as the delimiter
    message_id_parts = message_id_str.split('@')
    if len(message_id_parts) > 1:
        domain_part = message_id_parts[1]
        domain_part = re.sub(r'[<>]', '', domain_part)
    else:
        # Handle cases where '@' is not present
        pass

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
    if domain_part in str(message_id):
        print(f"Domain in Message-ID: {domain_part}")
    else:
        print("NO Domain in Message-ID.")

    # Check if the ID part is hexadecimal (except for the special characters)
    if re.match(r'^[0-9a-fA-F]+$', id_part_cleaned):
        is_id_part_hexadecimal = True
    else:
        is_id_part_hexadecimal = False
    
    print("The ID part is hexadecimal : ",is_id_part_hexadecimal)
    # Is ID part decimal (except the special characters)
    if re.match(r'^\d+$',id_part_cleaned):
        is_id_part_decimal = True
    else:
        is_id_part_decimal = False
        
    print("The ID part is decimal : ",is_id_part_decimal)
    # Existence of dots in ID part
    print(f"There are {num_dots_id} dot(s) in the ID part of the Message-ID")
    # Existence of special characters in ID part
    print(f"Existence of special characters in ID part : {special_char}")
    # Is domain part hexadecimal (except the special characters)
    if re.match(r'^[0-9a-fA-F]+$', domain_part_cleaned):
        is_domain_part_hexadecimal = True
    else:
        is_domain_part_hexadecimal = False
    
    # Is domain part decimal (except the special characters)

    print("is_domain_Part_hexadecimal ",is_domain_part_hexadecimal)

    if re.match(r'^\d+$',domain_part_cleaned):
        is_domain_part_decimal = True
    else:
        is_domain_part_decimal = False

    print("is_domain_part_decimal ",is_domain_part_decimal)
    # Existence of dots in domain part
    print(f"There are {num_dots_domain} dot(s) in the domain part of the Message-domain")
    # Existence of special characters other than dots in domain part
    print(f"Existence of special characters in domain part : {special_char}")

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
            reply_to_set.add(str(eml['Reply-To']))
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
    # print(f"Number of unique Reply-To addresses: {reply_to_set}")
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

    from_address = eml.get("From")
    reply_to_address = eml.get("Reply-To")

    print("From address ",from_address)
    print("reply_to adddress ",reply_to_address)

    from_address_str = str(from_address)
    from_domain = from_address_str.split('@')[1].split('>')[0] if '@' in from_address_str else None

    if reply_to_address is not None:
        reply_to_address_str = str(reply_to_address)
        if '@' in reply_to_address_str:
            reply_to_domain = reply_to_address_str.split('@')[1].split('>')[0]
        else:
            # Handle cases where '@' is not present
            pass
    else:
        reply_to_domain = None

        

    is_From_Domain_identical_to_ReplyTo_Domain = False

    if from_domain == reply_to_domain:
        is_From_Domain_identical_to_ReplyTo_Domain = True
    else:
        is_From_Domain_identical_to_ReplyTo_Domain = False

    print("is_From_Domain_identical_to_ReplyTo_Domain ",is_From_Domain_identical_to_ReplyTo_Domain)
    

    email_addresses = eml.get_all('to', []) + eml.get_all('from', []) + eml.get_all('cc', []) + eml.get_all('bcc', [])

    unique_domains = set()
    for email_address in email_addresses:
        email_address_str = str(email_address)
        domain = email_address_str.split('@')[-1].split('>')[0] if '@' in email_address_str else None
        unique_domains.add(domain)

    # count number of unique domains
    num_unique_domains = len(unique_domains)

    print("Number of unique domains in all email addresses:", num_unique_domains)


    # Get the From domain
    from_address_str = str(eml['From'])
    from_domain = from_address_str.split('@')[1].split('>')[0] if '@' in from_address_str else None

    # Get a list of all the To domains
    if eml['To'] is not None:
        to_domains = [to.split('@')[1].split('>')[0] for to in eml['To'].split(',') if '@' in to]
    else:
        to_domains = []

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
    from_addr_str = str(from_addr)
    from_domain = from_addr_str.split('@')[1].strip('>') if '@' in from_addr_str else None
    if return_path_addr and "@" in return_path_addr:
        return_path_domain = return_path_addr.split("@")[1].strip(">")
    else:
        return_path_domain = ""

    # check if the From and Return-Path domains are the same
    if from_domain == return_path_domain:
        is_From_Domain_identical_to_ReplyPath_Domain = True
    else:
        is_From_Domain_identical_to_ReplyPath_Domain = False

    print("is_From_Domain_identical_to_ReplyPath_Domain : ",is_From_Domain_identical_to_ReplyPath_Domain)


    boundary = eml.get_boundary()

    if(boundary):
        boundary_length = len(boundary)
    else:
        boundary_length = 0

    print(f"Length of the first boundary ID: {boundary_length}")


    # Does the first boundary ID start with an equal symbol (=) 

    if(boundary):
        is_firstBoundaryID_starts_with_an_equal_symbol= boundary.startswith('=')

    print("is_firstBoundaryID_starts_with_an_equal_symbol : ",is_firstBoundaryID_starts_with_an_equal_symbol)


    # Existence of equal symbols (=) in the middle of the first boundary ID
    existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID = False

    # if (boundary):
    #     buffer = BytesIO()
    #     generator = BytesGenerator(buffer, mangle_from_=False, maxheaderlen=0)
    #     generator.flatten(eml, charset='utf-8')
    #     eml_string = buffer.getvalue().decode('utf-8', errors='replace')
    #     index = eml_string.find(boundary)

    #     if '=' in eml_string[index:]:
    #         existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID = True



    # print("existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID ",existence_Of_Equal_Symbols_In_The_Middle_Of_The_First_Boundary_ID)


    existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID = False

    if(boundary):
        existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID = '_' in boundary

    print("existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID : ",existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID)


    # existence_Of_Dots_In_The_First_Boundary_ID
    existence_Of_Dots_In_The_First_Boundary_ID = False

    if(boundary):
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
    if boundary:
        if re.match(regex, boundary):
            is_First_boundary_ID_Hexadecimal = True

    print("is_First_boundary_ID_Hexadecimal ",is_First_boundary_ID_Hexadecimal)


    # Is the first boundary ID Decimal (except the special characters)

    is_First_boundary_ID_Decimal = False
    if boundary:
        if re.search("^[0-9]+$", boundary):
            is_First_boundary_ID_Decimal = True
        

    print("is_First_boundary_ID_Decimal ",is_First_boundary_ID_Decimal)

    
    # Index of charset in the first section 

    index_of_charset_in_the_first_section  = 0
    
    for part in eml.get_payload():
        if isinstance(part, str):
            part_str = part
        else:
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            part_str = payload.decode('utf-8', errors='replace')
        
        if "charset=" in part_str:
            charset_index = part_str.find("charset=")
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

    
    # extract HTML content
    html_content = None
    for part in eml.walk():
        if part.get_content_type() == 'text/html':
            html_content = part.get_payload(decode=True)
            break

    # parse the HTML using BeautifulSoup
    if html_content is not None:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Your code to process the soup object
    else:
        # Handle the case where html_content is None, if necessary
        pass

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
    count_style = 0
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for element in soup.find_all(style=lambda value: value and 'direction: rtl' in value):
            count_style += 1

    print("Number of elements with 'direction: rtl' style:", count_style)


    # ********************************Section JavaScript (JS) END*********************************

    # Existence of inline <script>

    is_inline_script_found = False

    for part in eml.walk():
        # check if the part is an HTML part
        if part.get_content_type() == 'text/html':
            # check if the part contains inline <script>
            if '<script>' in part.get_payload():
                is_inline_script_found = True


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
    if html_part is not None:
        soup = BeautifulSoup(html_part.get_payload(), 'html.parser')
        # Your code to process the soup object
    else:
        # Handle the case where html_part is None, if necessary
        pass

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
            html_payload += part.get_payload(decode=True).decode('latin-1')

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
    output_file = "new.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # create a CSV writer object
        csvwriter = csv.writer(csvfile)

        # write header row to CSV file
        csvwriter.writerow(["Number of text/plain sections", "Number of application sections","Number of image sections","Length of text in text/html section","Number of standard headers","Number of Reply-To entities","Number of Received entities","User-Agent exists","X-Mailer exists","Length of Message-ID","ASCII number of Message-ID boundary character","Domain in Message-ID","The ID part is hexadecimal","The ID part is decimal","The Domain part is hexadecimal","The Domain part is decimal","Existence of special characters in ID part","Number of dot(s) in the ID part of the Message-ID","Number of From header(s)","Number of To header(s)","Number of unique To addresses","Number of Cc addresses","Number of Bcc addresses","Number of Sender addresses","is_ReturnPath_Address_similar_to_ReplyTo_Address","is_From_Domain_identical_to_ReplyTo_Domain","Number of unique domains in all email addresses","Number of To domains identical to From Domain","is_From_Domain_identical_to_ReplyPath_Domain","Length of the first boundary ID","is_firstBoundaryID_starts_with_an_equal_symbol","existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID","existence_Of_Dots_In_The_First_Boundary_ID","existence_Of_Other_Special_Characters_In_The_First_Boundary_ID","is_First_boundary_ID_Hexadecimal","is_First_boundary_ID_Decimal","index_of_charset_in_the_first_section","Number of unique charsets in all sections","Length of <style> bodies and inline style bodies","Number of elements with 'direction: rtl' style","Inline <script> found in HTML part","depth of DOM","Number of email addresses in text/html section","Number of <a href> tags","Number of <a data-saferedirecturl> tags","number of URLS in text/html section"])
        csvwriter.writerow([plain, application,image,html_text_length,standard_headers_count,reply_to_count,received_count,user_agent_exists,x_mailer_exists,message_id_length,boundary_ascii,domain_part,is_id_part_hexadecimal,is_id_part_decimal,is_domain_part_hexadecimal,is_domain_part_decimal,special_char,num_dots_id,from_headers_count,to_headers_count,len(to_set),CC_addresses_count,BCC_addresses_count,sender_addresses_count,is_ReturnPath_Address_similar_to_ReplyTo_Address,is_From_Domain_identical_to_ReplyTo_Domain,num_unique_domains,identical_domains_count,is_From_Domain_identical_to_ReplyPath_Domain,boundary_length,is_firstBoundaryID_starts_with_an_equal_symbol,existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID,existence_Of_Dots_In_The_First_Boundary_ID,existence_Of_Other_Special_Characters_In_The_First_Boundary_ID,is_First_boundary_ID_Hexadecimal,is_First_boundary_ID_Decimal,index_of_charset_in_the_first_section,number_of_unique_charsets_in_all_sections,sum(style_lengths),count_style,is_inline_script_found,depth,len(email_addresses),num_a_tags,num_data_safere_directurl_tags,len(urls)])
    return[headers, [plain, application,image,html_text_length,standard_headers_count,reply_to_count,received_count,user_agent_exists,x_mailer_exists,message_id_length,boundary_ascii,domain_part,is_id_part_hexadecimal,is_id_part_decimal,is_domain_part_hexadecimal,is_domain_part_decimal,special_char,num_dots_id,from_headers_count,to_headers_count,len(to_set),CC_addresses_count,BCC_addresses_count,sender_addresses_count,is_ReturnPath_Address_similar_to_ReplyTo_Address,is_From_Domain_identical_to_ReplyTo_Domain,num_unique_domains,identical_domains_count,is_From_Domain_identical_to_ReplyPath_Domain,boundary_length,is_firstBoundaryID_starts_with_an_equal_symbol,existence_Of_UnderScores_Symbols_In_The_First_Boundary_ID,existence_Of_Dots_In_The_First_Boundary_ID,existence_Of_Other_Special_Characters_In_The_First_Boundary_ID,is_First_boundary_ID_Hexadecimal,is_First_boundary_ID_Decimal,index_of_charset_in_the_first_section,number_of_unique_charsets_in_all_sections,sum(style_lengths),count_style,is_inline_script_found,depth,len(email_addresses),num_a_tags,num_data_safere_directurl_tags,len(urls)]]