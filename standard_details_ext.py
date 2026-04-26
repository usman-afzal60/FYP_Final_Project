import re
import email

def extract_standard_details(eml):
    details = []
    details.append(eml.get('Subject'))
    details.append(eml.get('Date'))
    details.append(eml.get('From'))
    details.append(eml.get('To'))
    body=""
    for part in eml.walk():
    #         if part.get_content_type() == 'text/html':
    #             html_content = part.get_payload(decode=True)
    #             texts.append(html_content)
    #             break
            if part.get_content_type() == 'text/plain':
                plaintext = part.get_payload()
                details.append(plaintext)
                break
    return details
