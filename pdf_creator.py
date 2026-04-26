from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os
def create_pdf_report(item):
    report_directory = '/root/pyserver/reports'
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)
    report_filename = f"{item['ID']}.pdf"
    report_path = os.path.join(report_directory, report_filename)

    # Create the PDF file
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter
    margin = 0.75 * inch
    y = height - margin
    x = margin

    # Define styles
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    detail_style = ParagraphStyle(
        name="Detail",
        fontSize=12,
        spaceBefore=5,
        spaceAfter=5,
    )

    # Add logo image and title
    logo_path = "pdf_icons/Logo.jpg"
    logo = Image(logo_path, width=1 * inch, height=1 * inch)
    c.drawImage(logo_path, x, y-1*inch, width=1.2 * inch, height=1.2 * inch)
    x += 2.2 * inch

    
    # c.setFillColor(colors.white)
    
    # title = Paragraph("Email Analysis Report", header_style)
    # title.wrapOn(c, width, height)
    # title.drawOn(c, x, y-0.90*inch)
    y -= 2.5 * inch
    x = margin
    # Generate line-by-line report
    # c.setFont("Helvetica", 14)
    y += 1.15 * inch
    c.drawString(x+4, y, f"MAILASSURE")

    

    now = datetime.now()  # Get current datetime
    today_date = now.date()  # Get current time from datetime object
    today_time = now.time()
    time_string = today_time.strftime("%H:%M:%SS")  # Format: HH:MM
    hours_minutes = time_string[:8]
   
    
    c.setFont("Helvetica", 12)
    # print("Today's date:", today)
    x += 5.8 * inch
    y += 1.3*inch
    c.drawString(x, y, f"mailassure.tech")
    y -= 0.34*inch
    c.drawString(x, y, f"03351893129")
    y -= 0.34*inch
    c.drawString(x, y, f"Rawalpindi, Pakistan")
    y -= 0.34*inch
    c.drawString(x, y, f"Date : {today_date}")
    # x += 5 * inch
    y -= 0.34*inch
    c.drawString(x, y, f"Time : {hours_minutes}")

    # y -= 0.25 * inch
    x=margin
    y-=2.5*inch
    c.setFont("Helvetica", 14)
    c.drawString(x, y, f"ID: {item['ID']}")
    y -= 0.5 * inch
    c.setFont("Helvetica", 14)
    c.drawString(x, y, f"Subject: {item['Subject']}")
    y -= 0.5 * inch
    c.setFont("Helvetica", 14)
    c.drawString(x, y, f"Date: {item['Date']}")
    y -= 0.5 * inch

    c.setFont("Helvetica", 14)
    c.drawString(x, y, f"Sender: {item['Sender']}")
    y -= 0.5 * inch
    c.drawString(x, y, f"Receiver: {item['Recipient']}")
    y -= 0.5 * inch

    # body = item['Body']
    # body = f"Body: {body}"
    body = item['Body']
    body_words = body.split()
    if(len(body_words)>100):
        body = " ".join(body_words[:100]+["..."])
    else:
        body = " ".join(body_words[:100])
    # body = " ".join(body_words[:100])
    body = f"Body: {body}"
    textobject = c.beginText(x, y)
    for line in body.splitlines():
        words = line.split()
        current_line = ""
        for word in words:
            # Check if adding the current word will make the line too long
            if c.stringWidth(current_line + word) > width - 2 * margin:
                textobject.textLine(current_line.strip())
                current_line = ""
            current_line += word + " "
        # Add the last line of text
        textobject.textLine(current_line.strip())
    c.drawText(textobject)

    y -= 0.5 * inch


    # Get remaining space in page

    # Set coordinates to remaining space
    c.setFillColorRGB(1, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(x, 50, "Note: This report will be deleted automatically from system after 1 hour to ensure the privacy of your data.")

    
    # Create a colored box depending on the result
    if item['Result'].lower() == 'spam':
        result_color = colors.maroon
    else:
        result_color = colors.lightgreen
    print("result_color ",result_color)
    c.setFillColor(result_color)
    # c.setStrokeColor(colors.black)
    c.roundRect(455, 375, 1.5 * inch, 1.5 * inch,10,stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(490, 420, f"{item['Score']}")
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(485, 350, f"Score")
    # c.drawCentredString(x + 7.5 * inch, y + 0.2 * inch, f"Score: {item['Score']}")
    # y -= 0.5 * inch
    
    c.setFillColorRGB(15/255, 108/255, 123/255)
    c.setStrokeColorRGB(15/255, 108/255, 123/255)
    c.rect(0, 550, 8.5 * inch, 0.75 * inch, stroke=1, fill=1)
     # Set stroke color to gray
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 570, f"EMAIL ANALYSIS REPORT")


    web_icon_path = "pdf_icons/website.png"
    web_icon = Image(web_icon_path, width=1 * inch, height=1 * inch)
    c.drawImage(web_icon_path, 443, 730, width=0.25 * inch, height=0.25 * inch)


    address_path = "pdf_icons/telephone.png"
    address_icon = Image(address_path, width=1 * inch, height=1 * inch)
    c.drawImage(address_path, 443, 706, width=0.25 * inch, height=0.25 * inch)

    location_path = "pdf_icons/address.png"
    location_icon = Image(location_path, width=1 * inch, height=1 * inch)
    c.drawImage(location_path, 443, 681, width=0.25 * inch, height=0.25 * inch)

    date_path = "pdf_icons/calendar.png"
    date_icon = Image(date_path, width=1 * inch, height=1 * inch)
    c.drawImage(date_path, 443, 657, width=0.25 * inch, height=0.25 * inch)

    time_path = "pdf_icons/clock.png"
    time_icon = Image(time_path, width=1 * inch, height=1 * inch)
    c.drawImage(time_path, 443, 633, width=0.25 * inch, height=0.25 * inch)

    # Save the PDF
    c.showPage()
    c.save()
    # print("pdf created successfully")

