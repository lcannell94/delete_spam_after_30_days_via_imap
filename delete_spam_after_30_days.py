import argparse
import imaplib
import email
from email.header import make_header
from datetime import datetime, timedelta

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    parser = argparse.ArgumentParser(description="Purge messages older than 30 days from INBOX.spam.")
    parser.add_argument('--server', required=True, help="IMAP server address")
    parser.add_argument('--username', required=True, help="IMAP username")
    parser.add_argument('--password', required=True, help="IMAP password")
    args = parser.parse_args()

    print(f"{get_timestamp()}: Starting...")

    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(args.server)
        mail.login(args.username, args.password)

        print(f"IMAP Server: {args.server}")
        print(f"Username: {args.username}")

        # Select the spam folder
        mail.select("INBOX.spam")
        
        # Get total messages in the spam folder
        result, data = mail.search(None, "ALL")
        if result != "OK":
            print("Error retrieving messages.")
            return

        total_messages = len(data[0].split())
        print(f"Total messages in INBOX.spam: {total_messages}")

        # Find messages older than 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
        result, data = mail.search(None, f"BEFORE {cutoff_date}")
        if result != "OK":
            print("Error searching for old messages.")
            return

        old_message_ids = data[0].split()
        print(f"Messages older than 30 days: {len(old_message_ids)}")

        if old_message_ids:
            # Print header
            print("\nSender\t\tSubject\t\tDate")
            print("---------------------------------------")

            # List messages
            for msg_id in old_message_ids:
                result, msg_data = mail.fetch(msg_id, "(RFC822)")
                if result != "OK":
                    print(f"Error fetching message ID {msg_id}")
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                sender = str(make_header(email.header.decode_header(msg.get("From", ""))))
                subject = str(make_header(email.header.decode_header(msg.get("Subject", ""))))
                date = msg.get("Date", "")

                print(f"{sender}\t{subject}\t{date}")
            
            print("\n")

            # Purge messages
            print(f"{get_timestamp()}: ...purging messages older than 30 days")
            for msg_id in old_message_ids:
                mail.store(msg_id, '+FLAGS', '\\Deleted')
            mail.expunge()

        print(f"{get_timestamp()}: ...Completed. Summary below:")
        
        # Fetch remaining messages count
        result, data = mail.search(None, "ALL")
        remaining_messages = len(data[0].split())

        print(f"IMAP Server: {args.server}")
        print(f"Username: {args.username}")
        print(f"Messages left in INBOX.spam: {remaining_messages}")

        print("\n" + "=" * 30 + "\n")

    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
