import requests
import time

def test_simple_endpoint():
    """Test a simple endpoint to see if the server is working"""
    
    # Wait for server to be ready
    for i in range(5):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            print(f"Health check: {response.status_code} - {response.json()}")
            
            if response.status_code == 200:
                # Now test YouTube auth URL
                youtube_response = requests.get("http://localhost:8000/api/v1/youtube/auth/url", timeout=5)
                print(f"YouTube auth URL: {youtube_response.status_code}")
                if youtube_response.status_code == 200:
                    data = youtube_response.json()
                    print(f"Auth URL generated successfully")
                    print(f"URL starts with: {data.get('auth_url', '')[:50]}...")
                else:
                    print(f"Error: {youtube_response.text}")
                break
            
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
            time.sleep(1)

if __name__ == "__main__":
    test_simple_endpoint()
