import requests
from urllib.parse import parse_qsl, urlencode


# --- User Configuration ---
# Enter the API URL where emails can be fetched
API_URL = "https://mocki.io/v1/98691845-b946-4a4a-b1a2-d4197f8c1bc0"  # Replace with your actual API URL


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
    Main function to execute the Heyzine library update workflow.
    """
    # Heyzine library endpoint (CHANGED)
    heyzine_url = 'https://heyzine.com/library/save'
    
    # Headers - UPDATE THESE WITH YOUR CURRENT SESSION
    heyzine_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'heyzine_session_ts=65e57980b5653f93e827cd4770f341c6f9221b0dc774fe2d0463a9f82cc7f81da%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22heyzine_session_ts%22%3Bi%3A1%3Bs%3A128%3A%22%C0%ABb%99%5BUOl%ECy%FB.%A0%05%84%993f4d8a7388d82bf969efc46d7b818d83ff4d7ab948a11296ce74ee963c4c9c99f%A9S%90c%F6%A6%F8%08%DF%0E%20%FEF3x%F9%89w%80%AF%12%07%AB%0D%A0%EC%03I%A7%2B%AA%1C%84%1A%1E%E5%22S%1BLf%3E%C5%FDW%9A%3F%22%3B%7D; __stripe_mid=70e12b88-a730-4f83-bff1-565df27bf12334ec35; heyzine_session=4h8gno3ergt1o3lr6hm7m9ee78; __stripe_sid=fe989f42-ab4d-46ae-bdb9-a45b152c91106cb396; g_state={"i_l":0,"i_ll":1762688130732,"i_b":"WYe6ruQrHqzr4RTLeyrD+NazqeycOB/ZauvgyI9gfHo"}',
        'DNT': '1',
        'Origin': 'https://heyzine.com',
        'Referer': 'https://heyzine.com/library/edit?n=0f819e940b99ddff4e3360a280decc3c553d65a5',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'X-NewRelic-ID': 'VwQEVFFUARAFVVFQDwIFUlA=',
        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMyMzU3NzkiLCJhcCI6IjUzODYxMDU0NCIsImlkIjoiMjkwYzIxM2Q2MDczOTY2NCIsInRyIjoiMmRjNGQ2YTdhYmJlMDFlYjFhMzFkZjE0ZGRiNzE1NDgiLCJ0aSI6MTc2MjY4ODE4MDU4M319',
        'sec-ch-ua': '"Not:A-Brand";v="24", "Chromium";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'traceparent': '00-2dc4d6a7abbe01eb1a31df14ddb71548-290c213d60739664-01',
        'tracestate': '3235779@nr=0-1-3235779-538610544-290c213d60739664----1762688180583',
    }
    
    # Library data - UPDATE THIS WITH YOUR LIBRARY'S DATA
    heyzine_data_raw = 'library%5Bid_library%5D=76986&library%5Bname%5D=0f819e940b99ddff4e3360a280decc3c553d65a5&library%5Bid_user%5D=2261619&library%5Bvol%5D=&library%5Bver%5D=2&library%5Bcustom_name%5D=notes.html&library%5Bpublished%5D=1&library%5Btitle%5D=DSA+Book-Shelf&library%5Bsubtitle%5D=&library%5Bdescription%5D=&library%5Bprivate_notes%5D=&library%5Bthumbnail%5D=0f819e940b99ddff4e3360a280decc3c553d65a5-2-thumb.jpg&library%5Bfavicon%5D=&library%5Blayout%5D=book&library%5Bbackground%5D=https%3A%2F%2Fcdnc.heyzine.com%2Ffiles%2Fbackgrounds%2Fback14.svg&library%5Bbackground_color%5D=&library%5Bbackground_style%5D%5Bblur%5D=0&library%5Bbackground_style%5D%5Btransparency%5D=40&library%5Bbackground_style%5D%5Bsize%5D=Cover&library%5Bbackground_style%5D%5Bposition%5D=center+center&library%5Bheader_style%5D%5Bback_color%5D=rgba(255%2C+255%2C+255%2C+1)&library%5Bheader_style%5D%5Bfont%5D=Arial&library%5Bheader_style%5D%5Bfont_color%5D=rgba(86%2C+41%2C+176%2C+1)&library%5Bheader_style%5D%5Bstyle%5D=transparent&library%5Bcompany_logo%5D=&library%5Bcompany_logo_link%5D=&library%5Bcompany_logo_link_mode%5D=&library%5Bcontrols_iconset%5D=iconset3_6&library%5Bcontrols_pos%5D=0&library%5Bshow_share%5D=0&library%5Bshow_fullscreen%5D=1&library%5Bshow_search%5D=1&library%5Bshow_shelf%5D=1&library%5Bshelf_color%5D=rgba(230%2C+46%2C+43%2C+0.67)&library%5Bflips_rounded%5D=1&library%5Bflips_details%5D=0&library%5Bflips_open%5D=2&library%5Bpassword_enabled%5D=2&library%5Bpassword_name%5D=&library%5Bpassword%5D=&library%5Bpassword_text%5D=&library%5Bpassword_text_email%5D=Athentication&library%5Ballowed_enabled%5D=0&library%5Ballowed_direct%5D=1&library%5Ballowed_domains%5D=&library%5Ballowed_meta_index%5D=1&library%5Bsocial_title%5D=&library%5Bsocial_description%5D=&library%5Bsocial_thumbnail%5D=&library%5Baccess_count%5D=2&library%5Bcreate_date%5D=2025-11-06+21%3A09%3A42&library%5Bedit_access_date%5D=2025-11-06+21%3A28%3A24&library%5Blast_access_date%5D=2025-11-06+21%3A53%3A48&library%5Bdelete_date%5D=&library%5Bremove_date%5D=&library%5Bthumbnail_url%5D=https%3A%2F%2Fcdnc.heyzine.com%2Ffiles%2Flibraries%2F0f819e940b99ddff4e3360a280decc3c553d65a5-2-thumb.jpg&library%5Babsolute_url%5D=%2Fshelf%2F0f819e940b.html&library%5Bflipbooks%5D%5B0%5D%5Bname%5D=7e109704da11fcc29bcb202a1ee9d57dc44f4394.pdf&library%5Bflipbooks%5D%5B0%5D%5Bposition%5D=0&library%5Bflipbooks%5D%5B0%5D%5Bupload_date%5D=2025-11-06+21%3A08%3A58&library%5Bflipbooks%5D%5B0%5D%5Bthumbnail_url%5D=%2Ffiles%2Fuploaded%2F7e109704da11fcc29bcb202a1ee9d57dc44f4394.pdf-thumb.jpg&library%5Bflipbooks%5D%5B0%5D%5Btitle%5D=DSA+NOTES&library%5Bflipbooks%5D%5B0%5D%5Bsubtitle%5D=&library%5Bflipbooks%5D%5B0%5D%5Bdescription%5D=&library%5Bflipbooks%5D%5B0%5D%5Burl%5D=https%3A%2F%2Fjb.hflip.co%2F7e109704da.html&library%5Bflipbooks%5D%5B0%5D%5Btext%5D=7e109704da11fcc29bcb202a1ee9d57dc44f4394.pdf.txt&library%5Bflipbooks%5D%5B1%5D%5Bname%5D=6b05841d5564f52a39dfc1da97beb27f77542883.pdf&library%5Bflipbooks%5D%5B1%5D%5Bposition%5D=1&library%5Bflipbooks%5D%5B1%5D%5Bupload_date%5D=2025-09-20+07%3A48%3A36&library%5Bflipbooks%5D%5B1%5D%5Bthumbnail_url%5D=%2Ffiles%2Fuploaded%2F6b05841d5564f52a39dfc1da97beb27f77542883.pdf-thumb.jpg&library%5Bflipbooks%5D%5B1%5D%5Btitle%5D=Dsa+Theory+Notes&library%5Bflipbooks%5D%5B1%5D%5Bsubtitle%5D=&library%5Bflipbooks%5D%5B1%5D%5Bdescription%5D=&library%5Bflipbooks%5D%5B1%5D%5Burl%5D=https%3A%2F%2Fjb.hflip.co%2F6b05841d55.html&library%5Bflipbooks%5D%5B1%5D%5Btext%5D=6b05841d5564f52a39dfc1da97beb27f77542883.pdf.txt&library%5Blinks%5D%5B0%5D%5Bid_library_link%5D=43230&library%5Blinks%5D%5B0%5D%5Bid_library%5D=76986&library%5Blinks%5D%5B0%5D%5Btext%5D=&library%5Blinks%5D%5B0%5D%5Burl%5D=&library%5Blinks%5D%5B0%5D%5Bicon%5D=&library%5Blinks%5D%5B0%5D%5Bcreate_date%5D=2025-11-06+21%3A28%3A24&library%5Blinks%5D%5B0%5D%5Bdelete_date%5D=&library%5Breaders%5D%5B0%5D%5Bid_reader%5D=2214237&library%5Breaders%5D%5B0%5D%5Bname%5D=0f819e940b99ddff4e3360a280decc3c553d65a5&library%5Breaders%5D%5B0%5D%5Bemail%5D=jayabhuvaneshwork%40gmail.com&library%5Breaders%5D%5B0%5D%5Bcontent%5D=1&library%5Breaders%5D%5B0%5D%5Btype%5D=google&library%5Breaders%5D%5B0%5D%5Bpassword%5D=&library%5Breaders%5D%5B0%5D%5Buser_name%5D=JAYA+BHUVANESH+WORK&library%5Breaders%5D%5B0%5D%5Bimage%5D=https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocKetySoXLqb2tycQnuPSiLNMuVLPZHJt9ll8UtvYdKFh1upqCk%3Ds96-c&library%5Breaders%5D%5B0%5D%5Bid_external%5D=118247032411357683846&library%5Breaders%5D%5B0%5D%5Bcreate_date%5D=2025-11-06+21%3A28%3A15&library%5Breaders%5D%5B0%5D%5Blogin_date%5D=2025-11-06+21%3A53%3A38&library%5Breaders%5D%5B0%5D%5Bemail_date%5D=&library%5Breaders%5D%5B0%5D%5Bdelete_date%5D=&library%5Breaders%5D%5B1%5D%5Bid_reader%5D=2214234&library%5Breaders%5D%5B1%5D%5Bname%5D=0f819e940b99ddff4e3360a280decc3c553d65a5&library%5Breaders%5D%5B1%5D%5Bemail%5D=rashwanth89%40gmail.com&library%5Breaders%5D%5B1%5D%5Bcontent%5D=1&library%5Breaders%5D%5B1%5D%5Btype%5D=google&library%5Breaders%5D%5B1%5D%5Bpassword%5D=&library%5Breaders%5D%5B1%5D%5Buser_name%5D=Rashwanth&library%5Breaders%5D%5B1%5D%5Bimage%5D=https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocJ_FfKqEQShmmQOa0rZNQY9m-2dmS9VcBt3uW-SkesSgmKt%3Ds96-c&library%5Breaders%5D%5B1%5D%5Bid_external%5D=107688680551273042966&library%5Breaders%5D%5B1%5D%5Bcreate_date%5D=2025-11-06+21%3A18%3A41&library%5Breaders%5D%5B1%5D%5Blogin_date%5D=2025-11-06+21%3A53%3A48&library%5Breaders%5D%5B1%5D%5Bemail_date%5D=&library%5Breaders%5D%5B1%5D%5Bdelete_date%5D='
    
    # Fetch emails from API
    emails_to_add = fetch_emails_from_api(API_URL)
    
    if not emails_to_add:
        print("⚠️ Warning: No emails were fetched from the API.")
        print("Please check your API URL and ensure it returns a valid response.")
        return
    
    # Update the Heyzine library with the fetched emails
    result = update_heyzine_library(
        url=heyzine_url,
        headers=heyzine_headers,
        data_raw=heyzine_data_raw,
        emails=emails_to_add
    )
    
    if result['success']:
        print("\n🎉 Library successfully updated with new readers!")
    else:
        print(f"\n⚠️ Failed to update library: {result['message']}")


if __name__ == "__main__":
    main()


