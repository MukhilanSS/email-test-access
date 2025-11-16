import pandas as pd
import json

# Read Excel file
df = pd.read_excel('emails.xlsx')  # Change to your actual filename

# Filter: Get rows where Active Subscription Plans is NOT "MEMBERSHIP - Monthly"
filtered_df = df[
   ((df['One-time Purchase Plans'] != 'DSA Pattern Mastery') &
    (df['One-time Purchase Plans'].notnull())) |

   ( (df['Active Subscription Plans'] != 'MEMBERSHIP - Monthly') &
    (df['Active Subscription Plans'] != 'DSA Pattern Mastery') &
    (df['Active Subscription Plans'].notnull()))
]

# Separate Gmail and non-Gmail addresses
gmail_emails = []
non_gmail_emails = []

for email in filtered_df['Email Address']:
    if pd.notna(email):  # Check if email is not NaN
        email = str(email).strip().lower()
        if email.endswith('@gmail.com'):
            gmail_emails.append(email)
        else:
            non_gmail_emails.append(email)

# Save Gmail emails to JSON file
with open('gmail_only.json', 'w') as f:
    json.dump(gmail_emails, f, indent=2)

print(f"Saved {len(gmail_emails)} Gmail addresses to gmail_only.json")

# Print non-Gmail addresses if any exist
if non_gmail_emails:
    print(f"\nFound {len(non_gmail_emails)} non-Gmail addresses:")
    for email in non_gmail_emails:
        print(f"  - {email}")
else:
    print("\nAll emails are Gmail addresses!")

