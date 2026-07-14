#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import argparse
import sys

def generate_console_url(access_key, secret_key, session_token=None):
    print("[*] Building AWS Federation Token...")
    
    session_json = {
        "sessionId": access_key,
        "sessionKey": secret_key
    }
    if session_token:
        session_json["sessionToken"] = session_token

    session_string = json.dumps(session_json)
    encoded_session = urllib.parse.quote_plus(session_string)

    # 1. Get the sign-in token from the AWS Federation endpoint
    federation_url = f"https://signin.aws.amazon.com/federation?Action=getSigninToken&Session={encoded_session}"
    
    try:
        response = urllib.request.urlopen(federation_url)
        token_data = json.loads(response.read())
        signin_token = token_data.get('SigninToken')
        print("[+] Successfully retrieved SigninToken!")
    except Exception as e:
        print(f"[-] Failed to get federation token. Are the keys valid? Error: {e}")
        sys.exit(1)

    # 2. Construct the final magic login URL
    issuer = "JerichoArsenal"
    destination = "https://console.aws.amazon.com/"
    
    login_url = (
        f"https://signin.aws.amazon.com/federation?Action=login"
        f"&Issuer={issuer}"
        f"&Destination={urllib.parse.quote_plus(destination)}"
        f"&SigninToken={signin_token}"
    )
    
    print("\n[====== MAGIC CONSOLE LINK ======]")
    print(login_url)
    print("[==================================]\n")
    print("[*] Paste the link above into a browser (preferably Incognito/Containers) to access the AWS Web Console.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert AWS CLI Keys into a Web Console Login URL")
    parser.add_argument("-a", "--access-key", required=True, help="AWS Access Key ID")
    parser.add_argument("-s", "--secret-key", required=True, help="AWS Secret Access Key")
    parser.add_argument("-t", "--token", required=False, help="AWS Session Token (Required for assumed roles/SSRF)")
    
    args = parser.parse_args()
    generate_console_url(args.access_key, args.secret_key, args.token)
