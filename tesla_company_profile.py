import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

# Initialize API client
client = ApiClient()

# Get Tesla company profile
tesla_profile = client.call_api('YahooFinance/get_stock_profile', query={'symbol': 'TSLA'})

# Save the raw data to a JSON file
with open('tesla_profile_raw.json', 'w') as f:
    json.dump(tesla_profile, f, indent=4)

# Extract and print key information
if tesla_profile and 'quoteSummary' in tesla_profile and 'result' in tesla_profile['quoteSummary']:
    profile_data = tesla_profile['quoteSummary']['result'][0]['summaryProfile']
    
    print("Tesla Company Profile:")
    print("=====================")
    print(f"Company: Tesla, Inc. (TSLA)")
    print(f"Address: {profile_data.get('address1', 'N/A')}, {profile_data.get('city', 'N/A')}, {profile_data.get('zip', 'N/A')}")
    print(f"Country: {profile_data.get('country', 'N/A')}")
    print(f"Phone: {profile_data.get('phone', 'N/A')}")
    print(f"Website: {profile_data.get('website', 'N/A')}")
    print(f"Industry: {profile_data.get('industry', 'N/A')}")
    print(f"Sector: {profile_data.get('sector', 'N/A')}")
    print(f"Full-time Employees: {profile_data.get('fullTimeEmployees', 'N/A')}")
    print("\nBusiness Summary:")
    print(profile_data.get('longBusinessSummary', 'N/A'))
    
    # Create a formatted text file with the information
    with open('tesla_company_profile.txt', 'w') as f:
        f.write("TESLA COMPANY PROFILE\n")
        f.write("=====================\n\n")
        f.write(f"Company: Tesla, Inc. (TSLA)\n")
        f.write(f"Address: {profile_data.get('address1', 'N/A')}, {profile_data.get('city', 'N/A')}, {profile_data.get('zip', 'N/A')}\n")
        f.write(f"Country: {profile_data.get('country', 'N/A')}\n")
        f.write(f"Phone: {profile_data.get('phone', 'N/A')}\n")
        f.write(f"Website: {profile_data.get('website', 'N/A')}\n")
        f.write(f"Industry: {profile_data.get('industry', 'N/A')}\n")
        f.write(f"Sector: {profile_data.get('sector', 'N/A')}\n")
        f.write(f"Full-time Employees: {profile_data.get('fullTimeEmployees', 'N/A')}\n\n")
        f.write("Business Summary:\n")
        f.write(profile_data.get('longBusinessSummary', 'N/A'))
        
    print("\nCompany profile data saved to 'tesla_company_profile.txt'")
else:
    print("Error: Could not retrieve Tesla company profile data")
