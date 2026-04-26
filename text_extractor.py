import email
def extract_text_sections(eml):
    texts = []
    for part in eml.walk():
    #         if part.get_content_type() == 'text/html':
    #             html_content = part.get_payload(decode=True)
    #             texts.append(html_content)
    #             break
            if part.get_content_type() == 'text/plain':
                plaintext = part.get_payload()
                texts.append(plaintext)
                break
    return texts