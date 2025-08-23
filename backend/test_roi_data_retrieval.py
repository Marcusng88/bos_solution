#!/usr/bin/env python3
"""
Test ROI Metrics Data Retrieval - Comprehensive test to verify data access
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client

load_dotenv()

class ROIDataRetrievalTester:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {data}")
    
    async def test_connection(self):
        """Test basic Supabase connection"""
        try:
            if not self.supabase_url or not self.supabase_key:
                self.log_result("Connection", False, "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
                return False
            
            # Test connection by making a simple request
            response = await supabase_client._make_request("GET", "roi_metrics", params={"limit": "1"})
            if response.status_code == 200:
                self.log_result("Connection", True, "Successfully connected to Supabase")
                return True
            else:
                self.log_result("Connection", False, f"Connection failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Connection", False, f"Connection error: {str(e)}")
            return False
    
    async def test_table_exists(self):
        """Test if roi_metrics table exists"""
        try:
            response = await supabase_client._make_request("GET", "roi_metrics", params={"limit": "1"})
            if response.status_code == 200:
                self.log_result("Table Exists", True, "roi_metrics table exists and is accessible")
                return True
            else:
                self.log_result("Table Exists", False, f"Table access failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Table Exists", False, f"Table access error: {str(e)}")
            return False
    
    async def test_data_count(self):
        """Test data count retrieval"""
        try:
            response = await supabase_client._make_request("GET", "roi_metrics", params={"select": "id"})
            if response.status_code == 200:
                data = response.json()
                count = len(data)
                self.log_result("Data Count", True, f"Found {count} records in roi_metrics table", {"count": count})
                return count > 0
            else:
                self.log_result("Data Count", False, f"Count query failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Data Count", False, f"Count query error: {str(e)}")
            return False
    
    async def test_basic_data_retrieval(self):
        """Test basic data retrieval with all fields"""
        try:
            response = await supabase_client._make_request(
                "GET", 
                "roi_metrics", 
                params={
                    "select": "*",
                    "limit": "5",
                    "order": "update_timestamp.desc"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Check if all expected fields are present
                    expected_fields = [
                        'id', 'user_id', 'platform', 'campaign_id', 'post_id',
                        'content_type', 'content_category', 'views', 'likes',
                        'comments', 'shares', 'saves', 'clicks', 'ad_spend',
                        'revenue_generated', 'cost_per_click', 'cost_per_impression',
                        'roi_percentage', 'roas_ratio', 'created_at', 'posted_at',
                        'updated_at', 'update_timestamp'
                    ]
                    
                    sample_record = data[0]
                    missing_fields = [field for field in expected_fields if field not in sample_record]
                    
                    if not missing_fields:
                        self.log_result("Basic Data Retrieval", True, f"Successfully retrieved {len(data)} records with all expected fields")
                        return True
                    else:
                        self.log_result("Basic Data Retrieval", False, f"Missing fields: {missing_fields}", {"sample_record": sample_record})
                        return False
                else:
                    self.log_result("Basic Data Retrieval", False, "No data found")
                    return False
            else:
                self.log_result("Basic Data Retrieval", False, f"Data retrieval failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Basic Data Retrieval", False, f"Data retrieval error: {str(e)}")
            return False
    
    async def test_filtered_queries(self):
        """Test filtered queries by platform and date range"""
        try:
            # Test platform filter
            platform_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "platform": "eq.youtube",
                    "select": "platform,views,revenue_generated",
                    "limit": "3"
                }
            )
            
            if platform_response.status_code == 200:
                platform_data = platform_response.json()
                self.log_result("Platform Filter", True, f"Found {len(platform_data)} YouTube records")
            else:
                self.log_result("Platform Filter", False, f"Platform filter failed with status {platform_response.status_code}")
            
            # Test date range filter
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            
            date_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "update_timestamp": f"gte.{week_ago.isoformat()}",
                    "select": "update_timestamp,platform,views",
                    "limit": "3"
                }
            )
            
            if date_response.status_code == 200:
                date_data = date_response.json()
                self.log_result("Date Range Filter", True, f"Found {len(date_data)} records from last 7 days")
                return True
            else:
                self.log_result("Date Range Filter", False, f"Date filter failed with status {date_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Filtered Queries", False, f"Filtered queries error: {str(e)}")
            return False
    
    async def test_aggregation_queries(self):
        """Test aggregation queries for analytics"""
        try:
            # Test total revenue aggregation
            revenue_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "select": "revenue_generated,ad_spend,views,likes,comments",
                    "limit": "100"
                }
            )
            
            if revenue_response.status_code == 200:
                data = revenue_response.json()
                if data:
                    total_revenue = sum(float(r.get("revenue_generated", 0)) for r in data)
                    total_spend = sum(float(r.get("ad_spend", 0)) for r in data)
                    total_views = sum(int(r.get("views", 0)) for r in data)
                    
                    self.log_result("Aggregation Queries", True, 
                                  f"Calculated totals: Revenue=${total_revenue:.2f}, Spend=${total_spend:.2f}, Views={total_views}",
                                  {"total_revenue": total_revenue, "total_spend": total_spend, "total_views": total_views})
                    return True
                else:
                    self.log_result("Aggregation Queries", False, "No data for aggregation")
                    return False
            else:
                self.log_result("Aggregation Queries", False, f"Aggregation failed with status {revenue_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Aggregation Queries", False, f"Aggregation error: {str(e)}")
            return False
    
    async def test_api_endpoint_simulation(self):
        """Simulate API endpoint queries"""
        try:
            # Simulate the trends endpoint query
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            
            trends_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "update_timestamp": f"gte.{week_ago.isoformat()}",
                    "update_timestamp": f"lte.{now.isoformat()}",
                    "select": "update_timestamp,roi_percentage,revenue_generated",
                    "order": "update_timestamp.asc"
                }
            )
            
            if trends_response.status_code == 200:
                trends_data = trends_response.json()
                self.log_result("API Endpoint Simulation", True, f"Trends query returned {len(trends_data)} records")
                return True
            else:
                self.log_result("API Endpoint Simulation", False, f"Trends query failed with status {trends_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("API Endpoint Simulation", False, f"API simulation error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting ROI Metrics Data Retrieval Tests")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_connection,
            self.test_table_exists,
            self.test_data_count,
            self.test_basic_data_retrieval,
            self.test_filtered_queries,
            self.test_aggregation_queries,
            self.test_api_endpoint_simulation
        ]
        
        for test in tests:
            await test()
            await asyncio.sleep(0.5)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! ROI metrics data can be retrieved successfully.")
        else:
            print("⚠️  Some tests failed. Check the results above for details.")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
        
        return passed == total

async def main():
    """Main function"""
    tester = ROIDataRetrievalTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ CONCLUSION: ROI metrics data can be retrieved successfully!")
        return 0
    else:
        print("\n❌ CONCLUSION: Some issues found with ROI metrics data retrieval.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
