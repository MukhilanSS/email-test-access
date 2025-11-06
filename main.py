import requests
from urllib.parse import parse_qsl, urlencode


# --- User Configuration ---
# Enter the API URL where emails can be fetched
API_URL = "https://mocki.io/v1/a9442f61-491a-4126-8c87-e90e0fd0d4de"  # Replace with your actual API URL


def fetch_emails_from_api(api_url):
    """
    Fetches emails from the provided API endpoint and filters for Gmail addresses only.
    Expects a JSON response with an 'emails' field containing a list of email addresses.
    
    Only @gmail.com addresses are accepted. Other email addresses are logged but not included.
    
    Args:
        api_url (str): The URL endpoint to fetch emails from
        
    Returns:
        list: List of valid Gmail addresses, or empty list if fetch fails
    """
    try:
        print(f"Fetching emails from: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract emails from the 'emails' field
        if 'emails' in data:
            emails = data['emails']
            if isinstance(emails, list):
                print(f"✅ Successfully fetched {len(emails)} email(s) from API")
                
                # Filter for Gmail addresses only
                gmail_addresses = []
                non_gmail_addresses = []
                
                for email in emails:
                    if isinstance(email, str):
                        # Check if email ends with @gmail.com
                        if email.lower().endswith('@gmail.com'):
                            gmail_addresses.append(email)
                        else:
                            non_gmail_addresses.append(email)
                    else:
                        print(f"⚠️ Skipping invalid email format: {email}")
                
                # Display results
                print(f"\n📊 Email Filtering Summary:")
                print(f"   ✅ Valid Gmail addresses: {len(gmail_addresses)}")
                print(f"   ❌ Non-Gmail addresses rejected: {len(non_gmail_addresses)}")
                
                # Highlight non-Gmail addresses if any
                if non_gmail_addresses:
                    print(f"\n{'='*60}")
                    print(f"⚠️  WARNING: NON-GMAIL ADDRESSES DETECTED!")
                    print(f"{'='*60}")
                    print("The following email addresses were REJECTED (not @gmail.com):")
                    for idx, email in enumerate(non_gmail_addresses, 1):
                        print(f"   {idx}. ❌ {email}")
                    print(f"{'='*60}\n")
                
                # Display accepted Gmail addresses
                if gmail_addresses:
                    print(f"\n✅ Accepted Gmail addresses:")
                    for idx, email in enumerate(gmail_addresses, 1):
                        print(f"   {idx}. {email}")
                
                return gmail_addresses
            else:
                print("❌ Error: 'emails' field is not a list")
                return []
        else:
            print("❌ Error: 'emails' field not found in API response")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching emails from API: {e}")
        return []
    except ValueError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return []



def create_payload_with_new_emails(original_data_raw, new_emails):
    """
    Parses the original raw data string, removes existing 'reader' entries,
    and adds a new list of reader emails.
    
    Args:
        original_data_raw (str): URL-encoded form data string
        new_emails (list): List of email addresses to add as readers
        
    Returns:
        str: New URL-encoded payload with updated emails
    """
    # Use parse_qsl to maintain the order and structure of the original data.
    # It returns a list of (key, value) tuples.
    parsed_data = parse_qsl(original_data_raw, keep_blank_values=True)

    # Create a new list of data, excluding any keys that start with 'flipbook[readers]'
    # This effectively removes all the old email entries.
    filtered_data = [
        (k, v) for k, v in parsed_data if not k.startswith('flipbook[readers]')
    ]

    # Now, add the new emails to the list of data.
    # We will replicate the structure 'flipbook[readers][INDEX][KEY]'
    for i, email in enumerate(new_emails):
        # Add the email entry
        filtered_data.append((f'flipbook[readers][{i}][email]', email))
        # Add the 'type', assuming 'google' as per the original request
        filtered_data.append((f'flipbook[readers][{i}][type]', 'google'))
        # Add the 'password' field, which is empty in the original request
        filtered_data.append((f'flipbook[readers][{i}][password]', ''))

    # Encode the new list of tuples back into a URL-encoded string.
    # This will correctly format the data for the POST request.
    new_payload = urlencode(filtered_data)
    
    return new_payload


def update_heyzine_flipbook(url, headers, data_raw, emails):
    """
    Updates a Heyzine flipbook with new reader emails.
    
    Args:
        url (str): The Heyzine admin save endpoint URL
        headers (dict): HTTP headers including cookies and authentication
        data_raw (str): The raw form data from the flipbook configuration
        emails (list): List of email addresses to grant access to
        
    Returns:
        dict: Response data with 'success' boolean and 'message' or 'data'
    """
    if not emails:
        return {
            'success': False,
            'message': 'No emails provided'
        }
    
    print("\nPreparing payload with the following emails:")
    for email in emails:
        print(f"- {email}")
    
    # Generate the new payload string
    final_payload = create_payload_with_new_emails(data_raw, emails)
    
    print(f"\nSending POST request to: {url}")
    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=final_payload)
        response.raise_for_status()
        
        print("\n✅ Request successful!")
        print(f"Status Code: {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print("Response JSON:")
            print(response_data)
            return {
                'success': True,
                'data': response_data,
                'status_code': response.status_code
            }
        except requests.exceptions.JSONDecodeError:
            print("Response Text (not JSON):")
            print(response.text)
            return {
                'success': True,
                'data': response.text,
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return {
            'success': False,
            'message': str(e)
        }


def main():
    """
    Main function to execute the Heyzine flipbook update workflow.
    """
    # Heyzine endpoint
    heyzine_url = 'https://heyzine.com/admin/save'
    
    # Headers - UPDATE THESE WITH YOUR CURRENT SESSION
    heyzine_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '__stripe_mid=512c7379-c6c6-4496-834b-9859d563f7cc2c17f0; heyzine_session=v5qv0eum81ul3qaa49hur7htq6; __stripe_sid=c085838a-c64d-459a-b852-5fa1aebcc08dd7e638; g_state={"i_l":0,"i_ll":1762432048222,"i_b":"gAWg7pjVCKvXIDvpGwMzNq8azTwk6A/icxnpP4X6bew"}',
        'DNT': '1',
        'Origin': 'https://heyzine.com',
        'Referer': 'https://heyzine.com/admin/view?n=278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'X-NewRelic-ID': 'VwQEVFFUARAFVVFQDwIFUlA=',
        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMyMzU3NzkiLCJhcCI6IjUzODYxMDU0NCIsImlkIjoiMzFmZjM4ZmQ0NDNjMjc4NCIsInRyIjoiODE3OTdlY2EyNjU3ZTgwMzkxYjJhMjY5YmU4MDU0YWUiLCJ0aSI6MTc2MjQzMjEwNDA5M319',
        'sec-ch-ua': '"Not:A-Brand";v="24", "Chromium";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'traceparent': '00-81797eca2657e80391b2a269be8054ae-31ff38fd443c2784-01',
        'tracestate': '3235779@nr=0-1-3235779-538610544-31ff38fd443c2784----1762432104093',
    }
    
    # Flipbook data - UPDATE THIS WITH YOUR FLIPBOOK'S DATA
    heyzine_data_raw = 'flipbook%5Bid_upload%5D=14954245&flipbook%5Bquality%5D=&flipbook%5Bstate%5D=3&flipbook%5Bname%5D=278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf&flipbook%5Bver%5D=0&flipbook%5Bvol%5D=3&flipbook%5Bcustom_name%5D=&flipbook%5Bcustom_domain%5D=&flipbook%5Bsize%5D=849694&flipbook%5Bsize_original%5D=849694&flipbook%5Btemp%5D=%2Ftmp%2FphpEMKMAo&flipbook%5Bfile_exists%5D=&flipbook%5Bname_original%5D=java+syllabus.pdf&flipbook%5Bid_external%5D=&flipbook%5Berror%5D=&flipbook%5Bhash%5D=19a0ba2d&flipbook%5Bip%5D=106.200.12.123&flipbook%5Bupload_date%5D=2025-08-30+12%3A46%3A15&flipbook%5Badmin_key%5D=491a18e7aaa9cb94&flipbook%5Bconversion_type%5D=0&flipbook%5Bmode%5D=PDF&flipbook%5Bpaid_date%5D=&flipbook%5Bwidth%5D=596&flipbook%5Bheight%5D=842&flipbook%5Bconversion_date%5D=2025-08-30+12%3A46%3A19&flipbook%5Bversion_date%5D=&flipbook%5Blast_access_date%5D=2025-08-31+16%3A12%3A08&flipbook%5Bedit_access_date%5D=2025-09-20+17%3A13%3A14&flipbook%5Baccess_count%5D=3&flipbook%5Blast_download_date%5D=&flipbook%5Bdownload_count%5D=&flipbook%5Bdownload_enabled%5D=&flipbook%5Bdelete_date%5D=&flipbook%5Bcover_front%5D=&flipbook%5Bcover_back%5D=&flipbook%5Bthumbnail%5D=v3%2F278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf-thumb.jpg&flipbook%5Bfavicon%5D=&flipbook%5Btext_ratio%5D=&flipbook%5Btext%5D=&flipbook%5Bdownload%5D=&flipbook%5Bprivate_notes%5D=&flipbook%5Bnum_pages%5D=7&flipbook%5Bpublished%5D=1&flipbook%5Bid_user%5D=2261346&flipbook%5Bremove_date%5D=&flipbook%5Bthumbnail_url%5D=%2Ffiles%2Fuploaded%2Fv3%2F278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf-thumb.jpg&flipbook%5Babsolute_url%5D=%2Fflip-book%2F278d32d4d9.html&flipbook%5Bconfig%5D%5Bname%5D=278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf&flipbook%5Bconfig%5D%5Btitle%5D=&flipbook%5Bconfig%5D%5Bsubtitle%5D=&flipbook%5Bconfig%5D%5Bdescription%5D=&flipbook%5Bconfig%5D%5Badmin_note%5D=&flipbook%5Bconfig%5D%5Btitle_font%5D=&flipbook%5Bconfig%5D%5Bsubtitle_font%5D=&flipbook%5Bconfig%5D%5Bdescription_font%5D=&flipbook%5Bconfig%5D%5Bbackground%5D=%2Ffiles%2Fbackgrounds%2Fback98.jpg&flipbook%5Bconfig%5D%5Bbackground_color%5D=&flipbook%5Bconfig%5D%5Bbackground_style%5D%5Bblur%5D=0&flipbook%5Bconfig%5D%5Bbackground_style%5D%5Btransparency%5D=40&flipbook%5Bconfig%5D%5Bbackground_style%5D%5Bsize%5D=Cover&flipbook%5Bconfig%5D%5Bbackground_style%5D%5Bposition%5D=center+center&flipbook%5Bconfig%5D%5Bpages_type%5D=&flipbook%5Bconfig%5D%5Bcompany_logo%5D=&flipbook%5Bconfig%5D%5Bcompany_logo_link%5D=&flipbook%5Bconfig%5D%5Bcompany_logo_link_mode%5D=0&flipbook%5Bconfig%5D%5Bcompany_logo_style%5D=%7B%22max-width%22%3A%2220%25%22%2C%22top%22%3A%220px%22%2C%22bottom%22%3A%22auto%22%2C%22left%22%3A%2216px%22%2C%22right%22%3A%22auto%22%7D&flipbook%5Bconfig%5D%5Bshow_slider%5D=&flipbook%5Bconfig%5D%5Bshow_download%5D=&flipbook%5Bconfig%5D%5Bshow_print%5D=&flipbook%5Bconfig%5D%5Bshow_fullscreen%5D=&flipbook%5Bconfig%5D%5Bshow_text%5D=&flipbook%5Bconfig%5D%5Bshow_shadow%5D=1&flipbook%5Bconfig%5D%5Bshow_depth%5D=1&flipbook%5Bconfig%5D%5Bshow_zoom%5D=&flipbook%5Bconfig%5D%5Bshow_prevnext%5D=&flipbook%5Bconfig%5D%5Bshow_start%5D=&flipbook%5Bconfig%5D%5Bshow_end%5D=&flipbook%5Bconfig%5D%5Bshow_share%5D=&flipbook%5Bconfig%5D%5Bshow_search%5D=&flipbook%5Bconfig%5D%5Bshow_double%5D=0&flipbook%5Bconfig%5D%5Bshow_center%5D=1&flipbook%5Bconfig%5D%5Bshow_edges%5D=0&flipbook%5Bconfig%5D%5Bshow_round%5D=0&flipbook%5Bconfig%5D%5Bshow_binding%5D=0&flipbook%5Bconfig%5D%5Bshow_thumbpanel%5D=&flipbook%5Bconfig%5D%5Bshow_outline%5D=&flipbook%5Bconfig%5D%5Bshow_bookmarks%5D=&flipbook%5Bconfig%5D%5Bstart_page%5D=&flipbook%5Bconfig%5D%5Bend_page%5D=&flipbook%5Bconfig%5D%5Bload_page%5D=&flipbook%5Bconfig%5D%5Brtl%5D=&flipbook%5Bconfig%5D%5Bclick_zoom%5D=&flipbook%5Bconfig%5D%5Bsound_flip%5D=&flipbook%5Bconfig%5D%5Bcontrols_iconset%5D=iconset2_6&flipbook%5Bconfig%5D%5Bcontrols_style%5D=background-color%3Argba(255%2C+255%2C+255%2C+0.85)%3Btop%3A+20px%3B+bottom%3A+auto%3B+left%3A+auto%3B+right%3A+50px%3B+flex-direction%3A+row%3B+padding-left%3A+10px%3B+padding-right%3A+10px%3B+padding-top%3A+6px%3B+padding-bottom%3A+6px%3B+&flipbook%5Bconfig%5D%5Bcontrols_size%5D=md&flipbook%5Bconfig%5D%5Bback_link%5D=&flipbook%5Bconfig%5D%5Barrows%5D=&flipbook%5Bconfig%5D%5Bisize%5D=1.59396&flipbook%5Bconfig%5D%5Btype%5D=MAGAZINE&flipbook%5Bconfig%5D%5Bviewer%5D=magazine&flipbook%5Bconfig%5D%5Bviewer_dir%5D=0&flipbook%5Bconfig%5D%5Bpassword_enabled%5D=2&flipbook%5Bconfig%5D%5Bpassword%5D=1234&flipbook%5Bconfig%5D%5Bpassword_text%5D=&flipbook%5Bconfig%5D%5Bpassword_text_email%5D=&flipbook%5Bconfig%5D%5Bpassword_name%5D=4cd9ec2f67ede98ad867c370de03c094cc9a6477&flipbook%5Bconfig%5D%5Ballowed_domains%5D=&flipbook%5Bconfig%5D%5Ballowed_direct%5D=1&flipbook%5Bconfig%5D%5Ballowed_enabled%5D=0&flipbook%5Bconfig%5D%5Ballowed_meta_index%5D=1&flipbook%5Bconfig%5D%5Bsocial_title%5D=&flipbook%5Bconfig%5D%5Bsocial_description%5D=&flipbook%5Bconfig%5D%5Bsocial_thumbnail%5D=&flipbook%5Bconfig%5D%5BurlDownload%5D=%2Ffiles%2Fuploaded%2Fv3%2F278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf&flipbook%5Bconfig%5D%5BurlDownloadPdf%5D=%2Fflip-book%2Fpdf%2F278d32d4d9b907647f3e7d65dec0588f576e40eb.pdf&flipbook%5Bconfig%5D%5Bdcover%5D=0&flipbook%5Bconfig%5D%5BnumPages%5D=7&flipbook%5Bconfig%5D%5Bwidth%5D=596&flipbook%5Bconfig%5D%5Bheight%5D=842&flipbook%5Bconfig%5D%5Bfsize%5D=849694&flipbook%5Bconfig%5D%5Bidentity%5D=3227f77ecf85776f29274111a3ef4a26955fefc3e&flipbook%5Bconfig%5D%5Bname_short%5D=&flipbook%5Buser%5D%5Bid_user%5D=2261346&flipbook%5Buser%5D%5Bemail%5D=mukhilan2317ss%40gmail.com&flipbook%5Buser%5D%5Bname%5D=Mukhilan&flipbook%5Buser%5D%5Bpassword%5D=&flipbook%5Buser%5D%5Bpassword_recovery%5D=&flipbook%5Buser%5D%5Bcreated_date%5D=2025-08-30+12%3A44%3A16&flipbook%5Buser%5D%5Bupdated_date%5D=&flipbook%5Buser%5D%5Bdeleted_date%5D=&flipbook%5Buser%5D%5Bcreated_origin%5D=&flipbook%5Buser%5D%5Blogin_date%5D=&flipbook%5Buser%5D%5Blogin_attempt%5D=&flipbook%5Buser%5D%5Bip%5D=106.200.12.123&flipbook%5Buser%5D%5Bprofile%5D=&flipbook%5Buser%5D%5Bimage%5D=https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocLDNNB5vEdWp1GxvBTDlOcW8UOrkY4_CiOWkdDOWwm3OTbQq8qUlA%3Ds96-c&flipbook%5Buser%5D%5Bid_external%5D=103607436305015675627&flipbook%5Buser%5D%5Bid_user_payments%5D=&flipbook%5Buser%5D%5Bquality_mode%5D=0&flipbook%5Buser%5D%5Bstats_mode%5D=0&flipbook%5Buser%5D%5Bleads_mode%5D=0&flipbook%5Buser%5D%5Bcookieless%5D=0&flipbook%5Buser%5D%5Bdownload_mode%5D=0&flipbook%5Buser%5D%5Bitems_paid%5D=0&flipbook%5Buser%5D%5Bitems_downloaded%5D=0&flipbook%5Buser%5D%5Bpacks_enabled%5D=0&flipbook%5Buser%5D%5Bid_reseller%5D=&flipbook%5Buser%5D%5Bapi_key%5D=491a18e7aaa9cb94&flipbook%5Buser%5D%5Bdomain%5D=&flipbook%5Buser%5D%5Bdomain_home%5D=&flipbook%5Buser%5D%5Bdomains_allowed%5D=&flipbook%5Buser%5D%5Bdomains_direct%5D=1&flipbook%5Buser%5D%5Bdomain_pdf%5D=&flipbook%5Buser%5D%5Bmeta_index%5D=&flipbook%5Buser%5D%5Bid_team%5D=2261619&flipbook%5Buser%5D%5Bteam_owner%5D=0&flipbook%5Buser%5D%5Bteam_confirm%5D=&flipbook%5Buser%5D%5Bmail_contacted%5D=0&flipbook%5Buser%5D%5Bmail_allowed%5D=1&flipbook%5Buser%5D%5Bmail_leads%5D=1&flipbook%5Buser%5D%5Bmail_leads_address%5D=&flipbook%5Buser%5D%5Bmail_stats%5D=3&flipbook%5Buser%5D%5Bmail_marketing%5D=1&flipbook%5Buser%5D%5Buser_agent%5D=Mozilla%2F5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML%2C+like+Gecko)+Chrome%2F134.0.0.0+Safari%2F537.36&flipbook%5Buser%5D%5Bab_sample%5D=0&flipbook%5Buser%5D%5Bcountry%5D=in&flipbook%5Buser%5D%5Bcurrency%5D=&flipbook%5Buser%5D%5Btimezone%5D=&flipbook%5Breaders%5D%5B0%5D%5Bemail%5D=hi%40gmail.com&flipbook%5Breaders%5D%5B0%5D%5Btype%5D=google&flipbook%5Breaders%5D%5B0%5D%5Bpassword%5D=&flipbook%5Blayers%5D=&flipbook%5Blead%5D%5Bid_lead_form%5D=&flipbook%5Blead%5D%5Bname%5D=&flipbook%5Blead%5D%5Benabled%5D=0&flipbook%5Blead%5D%5Bpage%5D=3&flipbook%5Blead%5D%5Bskip%5D=1&flipbook%5Blead%5D%5Bprivacy%5D=0&flipbook%5Blead%5D%5Bprivacy_name%5D=&flipbook%5Blead%5D%5Bprivacy_link%5D=&flipbook%5Blead%5D%5Btext%5D=Sign+up+to+keep+reading&flipbook%5Blead%5D%5Btext_button%5D=Submit&flipbook%5Blead%5D%5Btext_skip%5D=Skip&flipbook%5Blead%5D%5Bpicture_url%5D=%2Ffiles%2Fforms%2Fform-1.svg&flipbook%5Blead%5D%5Btheme%5D=blur_light&flipbook%5Blead%5D%5Bfields%5D%5B0%5D%5Blabel%5D=Name&flipbook%5Blead%5D%5Bfields%5D%5B0%5D%5Btype%5D=text&flipbook%5Blead%5D%5Bfields%5D%5B0%5D%5Brequired%5D=1&flipbook%5Blead%5D%5Bfields%5D%5B1%5D%5Blabel%5D=Email&flipbook%5Blead%5D%5Bfields%5D%5B1%5D%5Btype%5D=email&flipbook%5Blead%5D%5Bfields%5D%5B1%5D%5Brequired%5D=1&flipbook%5Blead%5D%5Banswer_count%5D=&flipbook%5Blead%5D%5Banswer_date%5D=&flipbook%5Blead%5D%5Bcreate_date%5D=&flipbook%5Blead%5D%5Bdelete_date%5D=&flipbook%5Bbookmark%5D=&adminKey=&layers=%5B%7B%22id%22%3A%221756558143652%22%2C%22type%22%3A%22action%22%2C%22page%22%3A2%2C%22page_end%22%3Anull%2C%22origin%22%3A%22editor%22%2C%22css%22%3A%7B%22width%22%3A147%2C%22height%22%3A30%2C%22left%22%3A184.00866699219%2C%22top%22%3A549.00434494019%7D%2C%22wrapper%22%3A%7B%22width%22%3A498%2C%22height%22%3A703.996%2C%22left%22%3A163.81304931641%2C%22top%22%3A19.630435943604%7D%2C%22action%22%3A%7B%22highlight%22%3A0%2C%22target%22%3A%22%22%2C%22type%22%3Anull%2C%22subtype%22%3Anull%2C%22id_media%22%3Anull%2C%22extra%22%3A%7B%22new_tab%22%3Anull%2C%22text%22%3Anull%2C%22autoplay%22%3Anull%2C%22mute%22%3Anull%2C%22noscroll%22%3Anull%2C%22controls%22%3A1%2C%22loop%22%3Anull%2C%22keep%22%3Anull%2C%22once%22%3Anull%2C%22volume%22%3Anull%2C%22restart%22%3Anull%7D%7D%2C%22media%22%3A%7B%22id_media%22%3Anull%2C%22url%22%3Anull%2C%22type%22%3Anull%2C%22options%22%3A%7B%22display%22%3A%22inline%22%2C%22poster%22%3Anull%2C%22autoplay%22%3Anull%2C%22mute%22%3Anull%2C%22controls%22%3A1%2C%22noscroll%22%3Anull%2C%22loop%22%3Anull%2C%22keep%22%3Anull%2C%22once%22%3Anull%2C%22volume%22%3Anull%2C%22restart%22%3Anull%7D%7D%2C%22visible%22%3Afalse%2C%22active%22%3Afalse%7D%5D&bookmarks=%5B%5D'
    
    # Fetch emails from API
    emails_to_add = fetch_emails_from_api(API_URL)
    
    if not emails_to_add:
        print("⚠️ Warning: No emails were fetched from the API.")
        print("Please check your API URL and ensure it returns a valid response.")
        return
    
    # Update the Heyzine flipbook with the fetched emails
    result = update_heyzine_flipbook(
        url=heyzine_url,
        headers=heyzine_headers,
        data_raw=heyzine_data_raw,
        emails=emails_to_add
    )
    
    if result['success']:
        print("\n🎉 Flipbook successfully updated with new readers!")
    else:
        print(f"\n⚠️ Failed to update flipbook: {result['message']}")


if __name__ == "__main__":
    main()

