# import requests

# # Replace this with your actual ApyHub API token
# API_TOKEN = "--"

# url = "https://api.apyhub.com/ai/summarize-text"

# def summarize_text(text, length="medium"):
#     headers = {
#         "apy-token": API_TOKEN,
#         "Content-Type": "application/json"
#     }
#     data = {
#         "text": text,
#         "length": length
#     }
#     response = requests.post(url, json=data, headers=headers)
#     if response.status_code == 200:
#         result = response.json()
#         # Extract summary from nested "data"
#         summary = result.get("data", {}).get("summary")
#         return summary
#     else:
#         print("Error:", response.status_code, response.text)
#         return None

# # Example usage
# policy_section = "Privacy Policy\n\nLast updated: January 1, 2026\n\nThis Privacy Policy describes how ExampleApp collects, uses, and shares your personal information when you use our website and services.\n\nInformation We Collect\nWe may collect personal information such as your name, email address, phone number, IP address, device identifiers, and usage data when you register or interact with our services. We also collect information through cookies and similar tracking technologies.\n\nHow We Use Your Information\nWe use the collected information to provide and improve our services, personalize user experience, communicate with users, analyze usage patterns, and display relevant advertisements.\n\nCookies and Tracking Technologies\nWe use cookies, web beacons, and analytics tools to understand how users interact with our platform. Third-party advertising partners may also place cookies on your device.\n\nSharing of Information\nWe may share your personal information with third-party service providers, advertising partners, and analytics providers for business and marketing purposes. These third parties may use the information in accordance with their own privacy policies.\n\nData Retention\nWe retain your personal information for as long as necessary to fulfill the purposes outlined in this policy or as required by law. Retention periods are determined based on business needs.\n\nYour Rights\nDepending on your location, you may have certain rights regarding your personal information, including access and correction. However, deletion or opt-out mechanisms may be limited.\n\nSecurity\nWe take reasonable measures to protect your information, but no system is completely secure.\n\nChanges to This Policy\nWe may update this Privacy Policy from time to time. Continued use of the service indicates acceptance of the updated policy."
# summary = summarize_text(policy_section, length="medium")
# print("Summary:", summary)