# app/utils/email_template.py

def render_email_template(content: str, subject: str = "", **kwargs) -> str:
    """
    Renders a professional Bee Logical style email template.
    """
    logo_url = kwargs.get("logo_url", "")
    company_name = kwargs.get("company_name", "Bee Logical")
    company_address = kwargs.get("company_address", "Office no 707, S No 52, Baner Business Bay, Pashan – Sus Rd, Pune Banglore Highway Pashan Exit, Behind Audi Showroom, off Mumbai, Mohan Nagar Co-Op Society, Baner, Pune, Maharashtra 411045.")
    website_url = kwargs.get("website_url", "https://www.bee-logical.com/")
    unsubscribe_url = kwargs.get("unsubscribe_url", "#")
    year = kwargs.get("year", 2025)

    subject_text = subject or f"Notification from {company_name}"

    # Fix for backslash issue in f-string
    if logo_url:
        logo_html = f'''<img src="{logo_url}" alt="{company_name} Logo"
        onerror="this.style.display='none';this.insertAdjacentHTML('afterend', '<span>{company_name}</span>')">'''
    else:
        logo_html = f"<span>{company_name}</span>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <style>
        body {{
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background-color: #f4f4f4;
          margin: 0;
          padding: 0;
          color: #333333;
        }}
        .email-wrapper {{
          width: 100%;
          padding: 20px 0;
          background-color: #f4f4f4;
        }}
        .email-container {{
          max-width: 600px;
          margin: 0 auto;
          background: #ffffff;
          border-radius: 10px;
          box-shadow: 0 3px 8px rgba(0,0,0,0.08);
          overflow: hidden;
        }}
        .header {{
          background: linear-gradient(90deg, #FFC107 0%, #FFB300 100%);
          padding: 30px 20px;
          text-align: center;
        }}
        .logo-box {{
          background: #ffffff;
          border: 2px solid #FFC107;
          display: inline-block;
          padding: 10px 20px;
          border-radius: 8px;
          margin-bottom: 15px;
        }}
        .logo-box img {{
          max-width: 160px;
          height: auto;
          display: block;
        }}
        .logo-box span {{
          font-size: 20px;
          font-weight: bold;
          color: #222;
        }}
        .header h1 {{
          margin: 0;
          font-size: 22px;
          font-weight: 700;
          color: #222;
        }}
        .content {{
          padding: 24px;
          line-height: 1.6;
          font-size: 15px;
          color: #444;
        }}
        .content a.button {{
          display: inline-block;
          margin: 20px 0;
          padding: 12px 28px;
          background-color: #222;
          color: #ffffff !important;
          font-weight: 600;
          text-decoration: none;
          border-radius: 6px;
        }}
        .footer {{
          background-color: #fafafa;
          color: #777;
          font-size: 13px;
          text-align: center;
          padding: 18px 20px;
          border-top: 1px solid #eee;
        }}
        .footer a {{
          color: #555;
          text-decoration: none;
          margin: 0 5px;
        }}
        @media only screen and (max-width: 600px) {{
          .content {{
            padding: 18px;
          }}
          .header h1 {{
            font-size: 20px;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="email-wrapper">
        <div class="email-container">
          
          <!-- Header -->
          <div class="header">
            <div class="logo-box">
              {logo_html}
            </div>
            <h1>{subject_text}</h1>
          </div>

          <!-- Body -->
          <div class="content">
            {content}
          </div>

          <!-- Footer -->
          <div class="footer">
            <p>{company_name}{ ((" • " + company_address) if company_address else "") }</p>
            <p>
              <a href="{website_url}">Visit Website</a> • 
              <a href="{unsubscribe_url}">Unsubscribe</a>
            </p>
            <p>&copy; {year} {company_name}. All rights reserved.</p>
            <p><em>This is an automated email, please do not reply.</em></p>
          </div>

        </div>
      </div>
    </body>
    </html>
    """
