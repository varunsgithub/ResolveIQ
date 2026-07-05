import requests
from datetime import datetime, timedelta

def test_cfpb_api():
    # create a buffer of 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    url = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
    
    params = {
        "date_received_min" : start_date.isoformat(),
        "date_received_max" : end_date.isoformat(),
        "size" : 10
    }

    #Requests API used here.
    response = requests.get(url=url, params=params)

    if response.status_code != 200:
        print("Error in fetching data")
        return
    
    try:
         data = response.json()
    except requests.exceptions.JSONDecodeError:
         print("Failed to Parse JSON")
         return

    # Elastic search deep nested json
    total_complaints = data.get("hits", {}).get("total", {}).get("value", 0)
    print(f"Total complaints found in this window: {total_complaints}\n")
    complaints = data.get("hits", {}).get("hits", []) 
    
    for idx, item in enumerate(complaints[0:3], 1):
        source = item.get("_source", {})
    
        print(f"--- Complaint #{idx} ---")
        print(f"ID:       {source.get('complaint_id')}")
        print(f"Date:     {source.get('date_received')}")
        print(f"Product:  {source.get('product')}")
        print(f"Issue:    {source.get('issue')}")
        print(f"Company:  {source.get('company')}\n")
    
    
if __name__ == "__main__":
        test_cfpb_api()