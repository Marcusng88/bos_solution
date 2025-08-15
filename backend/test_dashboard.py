#!/usr/bin/env python3
"""
Test script for dashboard metrics
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.ai_agents import DashboardMetricsGenerator
    
    print("Testing DashboardMetricsGenerator...")
    gen = DashboardMetricsGenerator()
    
    # Test stats generation
    stats = gen.get_stats_cards_data()
    print("✅ Stats generation successful:", stats)
    
    # Test AI suggestions
    suggestions = gen.get_ai_suggestions()
    print(f"✅ AI suggestions generated: {len(suggestions)} suggestions")
    
    # Test competitor gaps
    gaps = gen.get_competitor_gaps()
    print(f"✅ Competitor gaps generated: {len(gaps)} gaps")
    
    # Test recent activities
    activities = gen.get_recent_activities()
    print(f"✅ Recent activities generated: {len(activities)} activities")
    
    print("\n🎉 All tests passed! Dashboard metrics are working correctly.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
