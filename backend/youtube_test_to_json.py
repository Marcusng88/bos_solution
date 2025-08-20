#!/usr/bin/env python3
"""
YouTube ROI Data Retrieval and JSON Export
Usage: python youtube_test_to_json.py [ACCESS_TOKEN]
If no token provided, it will try to get it from browser/frontend
"""

import json
import requests
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

class YouTubeROITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.results = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "base_url": base_url,
                "test_version": "1.0"
            },
            "connectivity_tests": {},
            "youtube_data": {},
            "errors": []
        }
    
    def log_error(self, error_msg):
        """Log error to results"""
        self.results["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": str(error_msg)
        })
        print(f"❌ ERROR: {error_msg}")
    
    def test_server_connectivity(self):
        """Test if backend server is running"""
        print("🔍 Testing server connectivity...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.results["connectivity_tests"]["backend_server"] = {
                    "status": "SUCCESS",
                    "response_time": response.elapsed.total_seconds(),
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else "OK"
                }
                print("✅ Backend server is running")
                return True
            else:
                self.results["connectivity_tests"]["backend_server"] = {
                    "status": "FAILED",
                    "status_code": response.status_code,
                    "response": response.text[:500]
                }
                print(f"❌ Server returned {response.status_code}")
                return False
        except Exception as e:
            self.results["connectivity_tests"]["backend_server"] = {
                "status": "ERROR",
                "error": str(e)
            }
            self.log_error(f"Cannot connect to server: {e}")
            return False
    
    def get_access_token_from_frontend(self):
        """Try to get access token from frontend storage or session"""
        print("🔑 Trying to get access token from frontend...")
        
        # Method 1: Check if frontend has any stored tokens (localStorage simulation)
        try:
            # This is a placeholder - in real scenario, we'd need the token from the user
            frontend_storage_path = Path("d:/Bos_Solution (2)/bos_solution/frontend/.next/cache")
            if frontend_storage_path.exists():
                print("📁 Frontend cache found, but token extraction not implemented")
        except Exception as e:
            print(f"⚠️  Frontend token check failed: {e}")
        
        # Method 2: Check environment or config files
        try:
            from dotenv import load_dotenv
            load_dotenv()
            potential_token = os.getenv("YOUTUBE_ACCESS_TOKEN")
            if potential_token and potential_token.startswith("ya29."):
                print("✅ Found token in environment")
                return potential_token
        except Exception as e:
            print(f"⚠️  Environment token check failed: {e}")
        
        return None
    
    def set_access_token(self, token):
        """Set the access token"""
        if not token or len(token) < 20:
            self.log_error("Invalid access token provided")
            return False
        
        self.access_token = token
        self.results["test_info"]["token_preview"] = f"{token[:20]}...{token[-10:]}"
        print(f"✅ Access token set: {token[:20]}...{token[-10:]}")
        return True
    
    def test_direct_google_api(self):
        """Test direct Google YouTube API calls"""
        if not self.access_token:
            self.log_error("No access token for Google API test")
            return False
        
        print("📺 Testing direct Google YouTube API...")
        
        try:
            # Test 1: Get channel info
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet,statistics,brandingSettings",
                    "mine": "true"
                },
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                channel_data = response.json()
                if channel_data.get("items"):
                    channel = channel_data["items"][0]
                    channel_info = {
                        "channel_id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "subscribers": int(channel["statistics"].get("subscriberCount", "0")),
                        "total_videos": channel["statistics"].get("videoCount", "0"),
                        "total_views": int(channel["statistics"].get("viewCount", "0")),
                        "published_at": channel["snippet"]["publishedAt"],
                        "country": channel["snippet"].get("country", "N/A"),
                        "custom_url": channel["snippet"].get("customUrl", "N/A")
                    }
                    
                    self.results["connectivity_tests"]["google_api"] = {
                        "status": "SUCCESS",
                        "channel_info": channel_info
                    }
                    self.results["youtube_data"]["channel_overview"] = channel_info
                    
                    print(f"✅ Channel: {channel_info['title']}")
                    print(f"   👥 Subscribers: {channel_info['subscribers']:,}")
                    print(f"   🎬 Videos: {channel_info['total_videos']}")
                    print(f"   👀 Total Views: {channel_info['total_views']:,}")
                    
                    return True
                else:
                    self.log_error("No channel found in Google API response")
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.results["connectivity_tests"]["google_api"] = {
                    "status": "FAILED",
                    "status_code": response.status_code,
                    "error": error_data
                }
                self.log_error(f"Google API failed: {response.status_code} - {error_data}")
                return False
                
        except Exception as e:
            self.results["connectivity_tests"]["google_api"] = {
                "status": "ERROR", 
                "error": str(e)
            }
            self.log_error(f"Google API test error: {e}")
            return False
    
    def test_recent_activity_endpoint(self, hours_back=24):
        """Test backend recent activity endpoint"""
        if not self.access_token:
            self.log_error("No access token for recent activity test")
            return False
        
        print(f"⏰ Testing recent activity (last {hours_back} hours)...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/youtube/recent-activity",
                params={
                    "access_token": self.access_token,
                    "hours_back": hours_back
                },
                timeout=60
            )
            
            if response.status_code == 200:
                activity_data = response.json()
                
                self.results["connectivity_tests"]["recent_activity"] = {
                    "status": "SUCCESS",
                    "summary": {
                        "total_activities": activity_data.get("total_activities", 0),
                        "videos_analyzed": len(activity_data.get("recent_activity", [])),
                        "cutoff_time": activity_data.get("cutoff_time")
                    }
                }
                
                self.results["youtube_data"]["recent_activity"] = activity_data
                
                # Summary output
                roi_summary = activity_data.get("roi_summary", {})
                print(f"✅ Recent Activity Retrieved:")
                print(f"   📊 Total Activities: {activity_data.get('total_activities', 0)}")
                print(f"   🔥 Recent Views: {roi_summary.get('total_recent_views', 0):,}")
                print(f"   ❤️ Recent Likes: {roi_summary.get('total_recent_likes', 0):,}")
                print(f"   💬 Recent Comments: {roi_summary.get('total_recent_comments', 0):,}")
                print(f"   📈 Avg Engagement: {roi_summary.get('avg_engagement_rate', 0):.1f}%")
                
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.results["connectivity_tests"]["recent_activity"] = {
                    "status": "FAILED",
                    "status_code": response.status_code,
                    "error": error_data
                }
                self.log_error(f"Recent activity failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.results["connectivity_tests"]["recent_activity"] = {
                "status": "ERROR",
                "error": str(e)
            }
            self.log_error(f"Recent activity test error: {e}")
            return False
    
    def test_roi_dashboard_endpoint(self, days_back=7):
        """Test backend ROI dashboard endpoint"""
        if not self.access_token:
            self.log_error("No access token for ROI dashboard test")
            return False
        
        print(f"💰 Testing ROI dashboard (last {days_back} days)...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/youtube/analytics/roi-dashboard",
                params={
                    "access_token": self.access_token,
                    "days_back": days_back,
                    "include_estimated_revenue": True
                },
                timeout=120
            )
            
            if response.status_code == 200:
                roi_data = response.json()
                
                self.results["connectivity_tests"]["roi_dashboard"] = {
                    "status": "SUCCESS",
                    "summary": "ROI Dashboard data retrieved successfully"
                }
                
                self.results["youtube_data"]["roi_analytics"] = roi_data
                
                # Summary output
                analytics = roi_data.get("roi_analytics", {})
                performance = analytics.get("performance_metrics", {})
                revenue = analytics.get("revenue_estimates", {})
                
                print(f"✅ ROI Dashboard Retrieved:")
                print(f"   👀 Views ({days_back} days): {performance.get('total_views_period', 0):,}")
                print(f"   ❤️ Likes: {performance.get('total_likes_period', 0):,}")
                print(f"   💬 Comments: {performance.get('total_comments_period', 0):,}")
                print(f"   ⏱️ Watch Time: {performance.get('total_watch_time_hours', 0):.1f} hours")
                print(f"   💵 Est. Monthly Revenue: ${revenue.get('estimated_monthly_revenue', 0):.2f}")
                print(f"   📊 Videos Analyzed: {performance.get('videos_analyzed', 0)}")
                
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.results["connectivity_tests"]["roi_dashboard"] = {
                    "status": "FAILED",
                    "status_code": response.status_code,
                    "error": error_data
                }
                self.log_error(f"ROI dashboard failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.results["connectivity_tests"]["roi_dashboard"] = {
                "status": "ERROR",
                "error": str(e)
            }
            self.log_error(f"ROI dashboard test error: {e}")
            return False
    
    def save_results_to_json(self, filename=None):
        """Save all test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_roi_test_results_{timestamp}.json"
        
        try:
            # Create results directory if it doesn't exist
            results_dir = Path("test_results")
            results_dir.mkdir(exist_ok=True)
            
            filepath = results_dir / filename
            
            # Add summary to results
            self.results["test_summary"] = {
                "total_tests": len(self.results["connectivity_tests"]),
                "successful_tests": sum(1 for test in self.results["connectivity_tests"].values() if test["status"] == "SUCCESS"),
                "failed_tests": sum(1 for test in self.results["connectivity_tests"].values() if test["status"] == "FAILED"),
                "error_tests": sum(1 for test in self.results["connectivity_tests"].values() if test["status"] == "ERROR"),
                "total_errors": len(self.results["errors"]),
                "data_retrieved": bool(self.results["youtube_data"])
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {filepath.absolute()}")
            print(f"📄 File size: {filepath.stat().st_size:,} bytes")
            
            return str(filepath.absolute())
            
        except Exception as e:
            self.log_error(f"Failed to save results: {e}")
            return None
    
    def run_full_test(self, hours_back=24, days_back=7):
        """Run complete test suite"""
        print("🚀 YouTube ROI Data Retrieval Test Suite")
        print("=" * 60)
        
        # Test 1: Server connectivity
        if not self.test_server_connectivity():
            print("❌ Cannot continue without backend server")
            self.save_results_to_json()
            return False
        
        # Test 2: Get access token
        if not self.access_token:
            token = self.get_access_token_from_frontend()
            if token:
                self.set_access_token(token)
            else:
                print("❌ No access token available")
                print("💡 Please provide token as argument: python youtube_test_to_json.py YOUR_TOKEN")
                self.save_results_to_json()
                return False
        
        # Test 3: Direct Google API
        print("\n" + "─" * 40)
        google_success = self.test_direct_google_api()
        
        # Test 4: Recent Activity
        print("\n" + "─" * 40)
        recent_success = self.test_recent_activity_endpoint(hours_back)
        
        # Test 5: ROI Dashboard  
        print("\n" + "─" * 40)
        roi_success = self.test_roi_dashboard_endpoint(days_back)
        
        # Final results
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS:")
        summary = self.results.get("test_summary", {})
        successful = sum([google_success, recent_success, roi_success])
        total = 3
        
        print(f"✅ Successful Tests: {successful}/{total}")
        print(f"❌ Failed Tests: {total - successful}/{total}")
        print(f"📊 Data Retrieved: {'Yes' if self.results['youtube_data'] else 'No'}")
        
        # Save results
        json_file = self.save_results_to_json()
        if json_file:
            print(f"\n🎯 ALL YOUR YOUTUBE ROI DATA IS SAVED IN:")
            print(f"   📁 {json_file}")
            
            # Show file contents summary
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    youtube_data = data.get("youtube_data", {})
                    print(f"\n📋 DATA SUMMARY:")
                    if "channel_overview" in youtube_data:
                        print(f"   📺 Channel Info: ✅")
                    if "recent_activity" in youtube_data:
                        activities = len(youtube_data["recent_activity"].get("recent_activity", []))
                        print(f"   ⏰ Recent Activities: {activities} items")
                    if "roi_analytics" in youtube_data:
                        print(f"   💰 ROI Analytics: ✅")
                        analytics = youtube_data["roi_analytics"].get("roi_analytics", {})
                        if "performance_metrics" in analytics:
                            print(f"   📊 Performance Metrics: ✅")
                        if "revenue_estimates" in analytics:
                            print(f"   💵 Revenue Estimates: ✅")
                        if "roi_recommendations" in analytics:
                            recs = len(analytics.get("roi_recommendations", []))
                            print(f"   💡 Recommendations: {recs} items")
            except Exception as e:
                print(f"⚠️  Could not read saved file: {e}")
        
        return successful == total


def main():
    """Main function"""
    tester = YouTubeROITester()
    
    # Get access token from command line argument
    if len(sys.argv) > 1:
        access_token = sys.argv[1]
        if not tester.set_access_token(access_token):
            print("❌ Invalid access token provided")
            return
    
    # Run the full test suite
    success = tester.run_full_test(hours_back=24, days_back=7)
    
    if success:
        print("\n🎉 All tests passed! Your YouTube ROI data is ready to use!")
    else:
        print("\n⚠️  Some tests failed, but available data has been saved.")


if __name__ == "__main__":
    main()
