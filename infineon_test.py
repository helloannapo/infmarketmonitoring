#!/usr/bin/env python3
"""
Infineon Competitive Intelligence Test Suite
Comprehensive testing for all system components
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print test banner"""
    print("=" * 60)
    print("🧪 INFINEON COMPETITIVE INTELLIGENCE TEST SUITE")
    print("=" * 60)
    print("Testing all components of the Infineon intelligence system")
    print("=" * 60)

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup...")
    
    # Check Python version
    if sys.version_info >= (3, 7):
        print(f"   ✅ Python {sys.version.split()[0]} - Compatible")
    else:
        print(f"   ❌ Python {sys.version.split()[0]} - Incompatible")
        return False
    
    # Check .env file
    if os.path.exists('.env'):
        print("   ✅ .env file found")
    else:
        print("   ⚠️  .env file not found - will use defaults")
    
    # Check directories
    directories = ['data', 'analysis', 'exports', 'logs', 'intelligence']
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ directory exists")
        else:
            print(f"   ❌ {directory}/ directory missing")
            return False
    
    print("✅ Environment setup complete")
    return True

def test_imports():
    """Test all required package imports"""
    print("\n📦 Testing Package Imports...")
    
    packages = {
        'requests': 'HTTP requests',
        'bs4': 'BeautifulSoup for web scraping',
        'pandas': 'Data manipulation',
        'openai': 'AI analysis',
        'dotenv': 'Environment variables',
        'openpyxl': 'Excel file handling'
    }
    
    all_imports_ok = True
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError as e:
            print(f"   ❌ {package} - {description}: {e}")
            all_imports_ok = False
    
    if all_imports_ok:
        print("✅ All imports successful")
    else:
        print("❌ Some imports failed")
    
    return all_imports_ok

def test_configuration():
    """Test configuration system"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        from intelligence_sources_config import get_enabled_sources, list_all_sources
        sources = get_enabled_sources()
        
        if sources:
            print(f"   ✅ Found {len(sources)} enabled sources:")
            for key, source in sources.items():
                print(f"      - {source['name']}: {source['url']}")
        else:
            print("   ⚠️  No enabled sources found")
        
        print("✅ Configuration system working")
        return True
        
    except ImportError as e:
        print(f"   ❌ Configuration import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key == 'your_openai_api_key_here':
            print("   ⚠️  OpenAI API key not configured")
            print("   📝 Add your API key to .env file")
            return False
        
        openai.api_key = api_key
        
        # Test with a simple request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        if response.choices:
            print("   ✅ OpenAI API connection successful")
            return True
        else:
            print("   ❌ OpenAI API response empty")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        return False

def test_web_scraping():
    """Test web scraping capabilities"""
    print("\n🌐 Testing Web Scraping...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Test a simple website
        test_url = "https://httpbin.org/html"
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1')
        
        if title and title.text.strip():
            print("   ✅ Web scraping test successful")
            return True
        else:
            print("   ❌ Web scraping test failed - no content found")
            return False
            
    except Exception as e:
        print(f"   ❌ Web scraping error: {e}")
        return False

def test_excel_creation():
    """Test Excel file creation"""
    print("\n📊 Testing Excel Creation...")
    
    try:
        import pandas as pd
        from openpyxl import Workbook
        
        # Create test data
        test_data = [
            {'Date': '2025-08-16', 'Key insights': 'Test insight', 'Signal': 'Positive', 'Risk': 'Low'},
            {'Date': '2025-08-16', 'Key insights': 'Another test', 'Signal': 'Neutral', 'Risk': 'Medium'}
        ]
        
        df = pd.DataFrame(test_data)
        test_file = 'test_excel.xlsx'
        
        with pd.ExcelWriter(test_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test', index=False)
        
        if os.path.exists(test_file):
            os.remove(test_file)  # Clean up
            print("   ✅ Excel creation test successful")
            return True
        else:
            print("   ❌ Excel file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Excel creation error: {e}")
        return False

def test_main_components():
    """Test main system components"""
    print("\n🔧 Testing Main Components...")
    
    try:
        # Test scraper initialization
        from infineon_intelligence_scraper import ConfigurableIntelligenceScraper
        scraper = ConfigurableIntelligenceScraper()
        print("   ✅ Scraper initialization successful")
        
        # Test analyzer initialization (without API key)
        try:
            from infineon_intelligence_scraper import InfineonIntelligenceAnalyzer
            analyzer = InfineonIntelligenceAnalyzer("test_key")
            print("   ✅ Analyzer initialization successful")
        except ValueError:
            print("   ⚠️  Analyzer needs API key (expected)")
        
        # Test exporter initialization
        from infineon_intelligence_scraper import ExcelIntelligenceExporter
        exporter = ExcelIntelligenceExporter()
        print("   ✅ Exporter initialization successful")
        
        print("✅ Main components test successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Main components error: {e}")
        return False

def run_full_test():
    """Run a complete test of the system"""
    print("\n🚀 Running Full System Test...")
    
    try:
        # Import and run main function
        from infineon_intelligence_scraper import main
        
        print("   ⚠️  This will run the full intelligence analysis")
        print("   ⚠️  It may take several minutes and use API credits")
        
        response = input("   Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("   Skipping full test")
            return True
        
        print("   🚀 Starting full intelligence analysis...")
        main()
        print("   ✅ Full system test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Full system test error: {e}")
        return False

def generate_test_report(results):
    """Generate a test report"""
    print("\n" + "=" * 60)
    print("📋 TEST REPORT")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("   Your Infineon Intelligence System is ready!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Please check the errors above and fix issues")
    
    print("=" * 60)

def main():
    """Main test function"""
    print_banner()
    
    results = {}
    
    # Run all tests
    results['Environment Setup'] = test_environment()
    results['Package Imports'] = test_imports()
    results['Configuration'] = test_configuration()
    results['OpenAI Connection'] = test_openai_connection()
    results['Web Scraping'] = test_web_scraping()
    results['Excel Creation'] = test_excel_creation()
    results['Main Components'] = test_main_components()
    
    # Optional full test
    if all(results.values()):
        results['Full System Test'] = run_full_test()
    
    # Generate report
    generate_test_report(results)
    
    # Save test results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = f'logs/test_results_{timestamp}.json'
    
    os.makedirs('logs', exist_ok=True)
    with open(test_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'passed': sum(1 for r in results.values() if r),
                'total': len(results)
            }
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to: {test_file}")

if __name__ == "__main__":
    main()

