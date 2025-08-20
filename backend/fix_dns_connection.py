"""
Script to diagnose and fix DNS resolution issues for Supabase
"""

import asyncio
import os
import sys
import logging
import socket
import asyncpg
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_dns_resolution():
    """Test DNS resolution for Supabase hostname"""
    hostname = "db.zktakfluvzuxhwwvccqs.supabase.co"
    print(f"🌐 Testing DNS resolution for {hostname}")
    
    try:
        # Try to resolve the hostname
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip_address}")
        return True, ip_address
        
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False, None

async def test_connection_with_ip():
    """Test connection using IP address instead of hostname"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Missing DATABASE_URL")
        return False
    
    # Test DNS first
    dns_ok, ip_address = await test_dns_resolution()
    
    if not dns_ok:
        print("\n🔧 Trying alternative DNS resolution methods...")
        
        # Try different DNS resolution methods
        try:
            import dns.resolver
            result = dns.resolver.resolve("db.zktakfluvzuxhwwvccqs.supabase.co", "A")
            ip_address = str(result[0])
            print(f"✅ Alternative DNS resolution successful: {ip_address}")
        except Exception as e:
            print(f"❌ Alternative DNS also failed: {e}")
            return False
    
    if ip_address:
        # Create modified URL with IP address
        modified_url = database_url.replace("db.zktakfluvzuxhwwvccqs.supabase.co", ip_address)
        print(f"🔄 Testing connection with IP address: {ip_address}")
        
        try:
            conn = await asyncpg.connect(modified_url)
            result = await conn.fetchrow("SELECT version()")
            print(f"✅ Connection with IP successful: {result[0]}")
            await conn.close()
            return True, modified_url
        except Exception as e:
            print(f"❌ Connection with IP failed: {e}")
            return False, None
    
    return False, None

async def test_ssl_connection():
    """Test connection with different SSL settings"""
    database_url = os.getenv("DATABASE_URL")
    
    print("\n🔒 Testing SSL connection variations...")
    
    # Test with SSL disabled
    try:
        no_ssl_url = database_url + "?sslmode=disable"
        print("🔄 Testing without SSL...")
        conn = await asyncpg.connect(no_ssl_url)
        result = await conn.fetchrow("SELECT version()")
        print(f"✅ Connection without SSL successful: {result[0]}")
        await conn.close()
        return True, no_ssl_url
    except Exception as e:
        print(f"❌ Connection without SSL failed: {e}")
    
    # Test with SSL required but no verification
    try:
        ssl_no_verify_url = database_url + "?sslmode=require"
        print("🔄 Testing with SSL required...")
        conn = await asyncpg.connect(ssl_no_verify_url)
        result = await conn.fetchrow("SELECT version()")
        print(f"✅ Connection with SSL required successful: {result[0]}")
        await conn.close()
        return True, ssl_no_verify_url
    except Exception as e:
        print(f"❌ Connection with SSL required failed: {e}")
    
    return False, None

async def test_alternative_ports():
    """Test connection on alternative ports"""
    database_url = os.getenv("DATABASE_URL")
    base_url = database_url.replace(":5432", "")
    
    print("\n🔌 Testing alternative ports...")
    
    # Common PostgreSQL ports
    ports = [5432, 6543, 5433]
    
    for port in ports:
        try:
            test_url = base_url.replace(":5432", f":{port}")
            if f":{port}" not in test_url:
                test_url = test_url.replace("/postgres", f":{port}/postgres")
            
            print(f"🔄 Testing port {port}...")
            conn = await asyncpg.connect(test_url, command_timeout=5)
            result = await conn.fetchrow("SELECT version()")
            print(f"✅ Connection on port {port} successful: {result[0]}")
            await conn.close()
            return True, test_url
        except Exception as e:
            print(f"❌ Port {port} failed: {e}")
    
    return False, None

async def fix_windows_dns():
    """Provide Windows DNS fix instructions"""
    print("\n🔧 Windows DNS Fix Instructions:")
    print("=" * 40)
    print("1. Flush DNS cache:")
    print("   ipconfig /flushdns")
    print()
    print("2. Reset network adapter:")
    print("   ipconfig /release")
    print("   ipconfig /renew")
    print()
    print("3. Try alternative DNS servers:")
    print("   - Google DNS: 8.8.8.8, 8.8.4.4")
    print("   - Cloudflare DNS: 1.1.1.1, 1.0.0.1")
    print()
    print("4. Check Windows Firewall/Antivirus:")
    print("   - Temporarily disable to test")
    print("   - Add exception for Python/your app")
    print()
    print("5. Edit hosts file (as administrator):")
    print("   - Location: C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("   - Add line: [IP_ADDRESS] db.zktakfluvzuxhwwvccqs.supabase.co")

async def create_fixed_env():
    """Create a fixed .env file with working connection string"""
    print("\n📝 Attempting to create fixed connection...")
    
    # Test different connection methods
    methods = [
        test_ssl_connection,
        test_alternative_ports,
        test_connection_with_ip
    ]
    
    for method in methods:
        try:
            success, working_url = await method()
            if success:
                print(f"\n🎉 Found working connection!")
                print(f"Working URL format: {working_url.split('@')[1] if '@' in working_url else 'Local'}")
                
                # Offer to update .env file
                response = input("\nWould you like to update your .env file with the working URL? (y/n): ")
                if response.lower() == 'y':
                    await update_env_file(working_url)
                return True
        except Exception as e:
            print(f"Method failed: {e}")
    
    return False

async def update_env_file(working_url):
    """Update .env file with working database URL"""
    env_path = "d:\\Bos_Solution (2)\\bos_solution\\backend\\.env"
    
    try:
        # Read current .env file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update DATABASE_URL line
        updated_lines = []
        for line in lines:
            if line.startswith('DATABASE_URL='):
                updated_lines.append(f'DATABASE_URL={working_url}\n')
                print(f"✅ Updated DATABASE_URL in .env file")
            else:
                updated_lines.append(line)
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

async def main():
    """Main diagnostic function"""
    print("🔍 Diagnosing Supabase Connection Issues")
    print("=" * 50)
    
    # Basic network test
    print("1. Testing basic network connectivity...")
    try:
        # Test internet connection
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✅ Internet connection is working")
    except Exception as e:
        print(f"❌ No internet connection: {e}")
        return
    
    # DNS resolution test
    print("\n2. Testing DNS resolution...")
    dns_ok, ip_address = await test_dns_resolution()
    
    if not dns_ok:
        # Provide DNS fix instructions
        await fix_windows_dns()
        
        # Try to find a working connection method
        print("\n3. Attempting alternative connection methods...")
        success = await create_fixed_env()
        
        if not success:
            print("\n❌ Could not establish any database connection.")
            print("💡 Recommendations:")
            print("   1. Use the Supabase REST API (which is already working)")
            print("   2. Fix DNS issues using the instructions above")
            print("   3. Contact your network administrator")
    else:
        print("✅ DNS resolution is working")
        print("   The issue might be with SSL or port configuration")
        
        # Test SSL and port variations
        await create_fixed_env()

if __name__ == "__main__":
    asyncio.run(main())
