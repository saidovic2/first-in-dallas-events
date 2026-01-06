"""Get Dataset ID from Apify Run ID"""
import requests

RUN_ID = "w5cFnw5KJFzrzQYef"
API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"

print(f"Fetching run details for: {RUN_ID}\n")

try:
    # Get run details
    run_url = f"https://api.apify.com/v2/actor-runs/{RUN_ID}?token={API_TOKEN}"
    response = requests.get(run_url, timeout=30)
    response.raise_for_status()
    
    run_data = response.json()['data']
    
    dataset_id = run_data.get('defaultDatasetId')
    
    if dataset_id:
        print(f"✓ Found Dataset ID: {dataset_id}")
        print(f"\nStats:")
        print(f"  Status: {run_data.get('status')}")
        print(f"  Started: {run_data.get('startedAt')}")
        print(f"  Finished: {run_data.get('finishedAt')}")
        
        # Get dataset stats
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}?token={API_TOKEN}"
        dataset_response = requests.get(dataset_url, timeout=30)
        
        if dataset_response.status_code == 200:
            dataset_info = dataset_response.json()['data']
            item_count = dataset_info.get('itemCount', 0)
            print(f"  Item Count: {item_count} events")
            
            print(f"\n{'='*60}")
            print(f"DATASET ID TO USE: {dataset_id}")
            print(f"{'='*60}")
        
    else:
        print("✗ No dataset found for this run")
        
except Exception as e:
    print(f"✗ Error: {e}")
