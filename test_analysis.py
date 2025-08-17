#!/usr/bin/env python3
"""
Test script for the updated Infineon Intelligence Analysis
Tests the new daily aggregation and analysis framework
"""

import json
from datetime import datetime
from infineon_intelligence_scraper import InfineonIntelligenceAnalyzer

def test_analysis_framework():
    """Test the updated analysis framework with sample data"""
    
    # Sample scraped data structure
    sample_data = {
        'scraping_timestamp': datetime.now().isoformat(),
        'canary': {
            'source': 'Canary Media',
            'headlines': [
                'AI-powered predictive maintenance systems showing 30% efficiency gains in industrial operations',
                'New government funding for industrial AI and smart manufacturing announced',
                'Major competitor announces delays in AI chip production for industrial applications'
            ],
            'key_insights': [
                'AI-driven predictive maintenance reducing industrial downtime by 30%',
                'Federal funding of $3.2B allocated for industrial AI and smart manufacturing',
                'Production delays expected to last 8-10 months for competitor AI chips'
            ],
            'market_signals': [
                'Growing demand for edge AI processing in industrial equipment',
                'Increased investment in industrial IoT and smart manufacturing',
                'Supply chain challenges affecting AI semiconductor production'
            ]
        },
        'industryweek': {
            'source': 'Industry Week',
            'headlines': [
                'Industrial sector embracing hybrid AI models for equipment optimization',
                'Smart manufacturing driving demand for AI-powered semiconductors',
                'New regulations for AI deployment in industrial safety systems'
            ],
            'key_insights': [
                'Hybrid AI models becoming standard for industrial equipment optimization',
                'Industrial motor drives requiring AI-powered predictive maintenance',
                'AI safety regulations creating new market opportunities for reliable systems'
            ],
            'market_signals': [
                'Technology transition to AI-powered industrial equipment creating new design opportunities',
                'Industrial sector AI modernization driving semiconductor demand',
                'Regulatory changes opening new market segments for AI-powered industrial solutions'
            ]
        }
    }
    
    print("🧪 Testing Updated Infineon Intelligence Analysis Framework")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        analyzer = InfineonIntelligenceAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Run analysis
        print("\n📊 Running analysis with daily aggregation...")
        analysis_results = analyzer.analyze_for_infineon(sample_data)
        
        print(f"\n📈 Analysis completed! Generated {len(analysis_results)} daily analysis entries")
        
        # Display results
        for i, result in enumerate(analysis_results, 1):
            print(f"\n--- Daily Analysis #{i} ---")
            print(f"📅 Date: {result.get('Date', 'N/A')}")
            print(f"📈 Signal: {result.get('Signal', 'N/A')}")
            print(f"⚠️  Risk: {result.get('Risk', 'N/A')}")
            print(f"💡 Key Insights: {result.get('Key insights', 'N/A')}")
            
            # Validate format
            assert result.get('Date'), "Date should be present"
            assert result.get('Signal') in ['Positive', 'Neutral', 'Negative'], f"Invalid Signal: {result.get('Signal')}"
            assert result.get('Risk') in ['Low', 'Medium', 'High'], f"Invalid Risk: {result.get('Risk')}"
            assert result.get('Key insights'), "Key insights should be present"
            # Check word count instead of character count
            word_count = len(result.get('Key insights', '').split())
            assert word_count <= 300, f"Key insights should be 300 words or less (got {word_count} words)"
            
            print("✅ Format validation passed")
        
        print("\n🎉 All tests passed! Analysis framework working correctly.")
        
        # Save test results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file = f'analysis/test_analysis_results_{timestamp}.json'
        with open(test_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        print(f"💾 Test results saved to: {test_file}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_analysis_framework()
