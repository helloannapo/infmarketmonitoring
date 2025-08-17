#!/usr/bin/env python3
"""
Infineon Competitive Intelligence Scraper
Specialized for Green Power market intelligence with Signal/Risk analysis framework
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import logging
import os
from typing import Dict, List, Any, Tuple
import openai
from dotenv import load_dotenv
from pathlib import Path

# Google Sheets integration
try:
    import gspread
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import GoogleAuthError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️  Google Sheets integration not available. Install with: pip install gspread google-auth")

# Load environment variables
load_dotenv()

# Create organized directory structure
def create_directories():
    """Create organized directories for file storage"""
    directories = ['data', 'analysis', 'logs', 'exports', 'intelligence']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Configure logging
def setup_logging():
    """Setup logging with organized file structure"""
    os.makedirs('logs', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/infineon_intelligence_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Initialize directories and logging
create_directories()
logger = setup_logging()
logger.info("Created organized directory structure")

class ConfigurableIntelligenceScraper:
    """Configurable scraper for competitive intelligence sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = {}
        
        # Import configuration
        try:
            from intelligence_sources_config import get_enabled_sources
            self.sources = get_enabled_sources()
        except ImportError:
            # Fallback to default sources if config not available
            self.sources = {
                'canary': {
                    'name': 'Canary Media',
                    'url': 'https://www.canarymedia.com/',
                    'description': 'Clean energy news and analysis'
                },
                'industryweek': {
                    'name': 'Industry Week',
                    'url': 'https://www.industryweek.com/',
                    'description': 'Manufacturing and industrial insights'
                },
                'eia': {
                    'name': 'EIA Today in Energy',
                    'url': 'https://www.eia.gov/todayinenergy/',
                    'description': 'U.S. Energy Information Administration daily energy insights'
                }
            }
    
    def add_source(self, key: str, name: str, url: str, description: str):
        """Add a new source to the scraper"""
        self.sources[key] = {
            'name': name,
            'url': url,
            'description': description
        }
        logger.info(f"Added new source: {name} ({url})")
    
    def remove_source(self, key: str):
        """Remove a source from the scraper"""
        if key in self.sources:
            removed = self.sources.pop(key)
            logger.info(f"Removed source: {removed['name']}")
        else:
            logger.warning(f"Source {key} not found")
    
    def list_sources(self):
        """List all configured sources"""
        logger.info("Configured sources:")
        for key, source in self.sources.items():
            logger.info(f"  {key}: {source['name']} - {source['url']}")
    
    def scrape_canary(self) -> Dict[str, Any]:
        """Scrape Canary Media for clean energy news and analysis"""
        logger.info("Scraping Canary Media for clean energy insights...")
        try:
            # Try to find news/articles page
            news_urls = [
                'https://www.canarymedia.com/',
                'https://www.canarymedia.com/articles',
                'https://www.canarymedia.com/news',
                'https://www.canarymedia.com/energy'
            ]
            
            data = {
                'source': 'Canary Media',
                'timestamp': datetime.now().isoformat(),
                'url': '',
                'headlines': [],
                'key_insights': [],
                'market_signals': []
            }
            
            for url in news_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data['url'] = url
                    
                    # Look for news articles, stories, recent content
                    news_selectors = [
                        'article', '.article', '.story', '.post', '.entry',
                        '.news-item', '.content-item', '.featured-article',
                        '[class*="article"]', '[class*="story"]', '[class*="post"]',
                        'h1', 'h2', 'h3'
                    ]
                    
                    news_items = []
                    for selector in news_selectors:
                        items = soup.select(selector)
                        if items:
                            news_items.extend(items)
                    
                    # Extract headlines from news items
                    for item in news_items[:10]:  # Limit to first 10 items
                        # Look for headline text
                        headline_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                        if headline_elem:
                            text = headline_elem.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                # Filter out navigation and common web elements
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # If no headlines found, try general content extraction
                    if not data['headlines']:
                        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=10)
                        for headline in headlines:
                            text = headline.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # Extract key insights from news content
                    content = soup.get_text()
                    
                    # Look for numbers and statistics in context
                    sentences = content.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if any(char.isdigit() for char in sentence) and 20 < len(sentence) < 300:
                            # Look for clean energy related statistics
                            energy_keywords = ['energy', 'electricity', 'renewable', 'solar', 'wind', 'battery', 'emission', 'carbon', 'clean', 'transition']
                            if any(keyword in sentence.lower() for keyword in energy_keywords):
                                clean_sentence = ' '.join(sentence.split())
                                if len(clean_sentence) > 20:
                                    data['key_insights'].append(clean_sentence)
                    
                    # Extract market signals from recent news
                    clean_energy_keywords = ['renewable', 'solar', 'wind', 'battery', 'electric vehicle', 'green energy', 'carbon', 'emission', 'transition', 'clean energy']
                    for keyword in clean_energy_keywords:
                        if keyword.lower() in content.lower():
                            sentences = content.split('.')
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if keyword.lower() in sentence.lower() and 20 < len(sentence) < 300:
                                    clean_sentence = ' '.join(sentence.split())
                                    if len(clean_sentence) > 20:
                                        data['market_signals'].append(clean_sentence)
                                        break
                    
                    if data['headlines'] or data['key_insights'] or data['market_signals']:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
            
            # Limit results to avoid token limits
            data['headlines'] = data['headlines'][:5]
            data['key_insights'] = data['key_insights'][:5]
            data['market_signals'] = data['market_signals'][:5]
            
            logger.info(f"Successfully scraped Canary Media: {len(data['headlines'])} headlines, {len(data['key_insights'])} insights")
            return data
            
        except Exception as e:
            logger.error(f"Error scraping Canary Media: {e}")
            return {'source': 'Canary Media', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def scrape_industryweek(self) -> Dict[str, Any]:
        """Scrape Industry Week for manufacturing and industrial insights"""
        logger.info("Scraping Industry Week for manufacturing insights...")
        try:
            # Try to find news/articles page
            news_urls = [
                'https://www.industryweek.com/',
                'https://www.industryweek.com/news',
                'https://www.industryweek.com/technology',
                'https://www.industryweek.com/operations'
            ]
            
            data = {
                'source': 'Industry Week',
                'timestamp': datetime.now().isoformat(),
                'url': '',
                'headlines': [],
                'key_insights': [],
                'market_signals': []
            }
            
            for url in news_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data['url'] = url
                    
                    # Look for news articles, stories, recent content
                    news_selectors = [
                        'article', '.article', '.story', '.post', '.entry',
                        '.news-item', '.content-item', '.featured-article',
                        '[class*="article"]', '[class*="story"]', '[class*="post"]',
                        'h1', 'h2', 'h3'
                    ]
                    
                    news_items = []
                    for selector in news_selectors:
                        items = soup.select(selector)
                        if items:
                            news_items.extend(items)
                    
                    # Extract headlines from news items
                    for item in news_items[:10]:  # Limit to first 10 items
                        # Look for headline text
                        headline_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                        if headline_elem:
                            text = headline_elem.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                # Filter out navigation and common web elements
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # If no headlines found, try general content extraction
                    if not data['headlines']:
                        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=10)
                        for headline in headlines:
                            text = headline.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # Extract key insights from news content
                    content = soup.get_text()
                    
                    # Look for numbers and statistics in context
                    sentences = content.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if any(char.isdigit() for char in sentence) and 20 < len(sentence) < 300:
                            # Look for manufacturing and industrial statistics
                            industry_keywords = ['manufacturing', 'production', 'automation', 'technology', 'industry', 'supply chain', 'efficiency', 'productivity']
                            if any(keyword in sentence.lower() for keyword in industry_keywords):
                                clean_sentence = ' '.join(sentence.split())
                                if len(clean_sentence) > 20:
                                    data['key_insights'].append(clean_sentence)
                    
                    # Extract market signals from recent news
                    industry_keywords = ['manufacturing', 'production', 'automation', 'technology', 'industry', 'supply chain', 'efficiency', 'productivity', 'semiconductor', 'automotive']
                    for keyword in industry_keywords:
                        if keyword.lower() in content.lower():
                            sentences = content.split('.')
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if keyword.lower() in sentence.lower() and 20 < len(sentence) < 300:
                                    clean_sentence = ' '.join(sentence.split())
                                    if len(clean_sentence) > 20:
                                        data['market_signals'].append(clean_sentence)
                                        break
                    
                    if data['headlines'] or data['key_insights'] or data['market_signals']:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
            
            # Limit results to avoid token limits
            data['headlines'] = data['headlines'][:5]
            data['key_insights'] = data['key_insights'][:5]
            data['market_signals'] = data['market_signals'][:5]
            
            logger.info(f"Successfully scraped Industry Week: {len(data['headlines'])} headlines, {len(data['key_insights'])} insights")
            return data
            
        except Exception as e:
            logger.error(f"Error scraping Industry Week: {e}")
            return {'source': 'Industry Week', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def scrape_eia(self) -> Dict[str, Any]:
        """Scrape EIA Today in Energy for daily energy insights"""
        logger.info("Scraping EIA Today in Energy for energy market insights...")
        try:
            # Try to find news/articles page
            news_urls = [
                'https://www.eia.gov/todayinenergy/',
                'https://www.eia.gov/todayinenergy/index.php',
                'https://www.eia.gov/outlooks/steo/',
                'https://www.eia.gov/'
            ]
            
            data = {
                'source': 'EIA Today in Energy',
                'timestamp': datetime.now().isoformat(),
                'url': '',
                'headlines': [],
                'key_insights': [],
                'market_signals': []
            }
            
            for url in news_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    data['url'] = url
                    
                    # Look for news articles, stories, recent content
                    news_selectors = [
                        'article', '.article', '.story', '.post', '.entry',
                        '.news-item', '.content-item', '.featured-article',
                        '[class*="article"]', '[class*="story"]', '[class*="post"]',
                        'h1', 'h2', 'h3'
                    ]
                    
                    news_items = []
                    for selector in news_selectors:
                        items = soup.select(selector)
                        if items:
                            news_items.extend(items)
                    
                    # Extract headlines from news items
                    for item in news_items[:10]:  # Limit to first 10 items
                        # Look for headline text
                        headline_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                        if headline_elem:
                            text = headline_elem.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                # Filter out navigation and common web elements
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # If no headlines found, try general content extraction
                    if not data['headlines']:
                        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=10)
                        for headline in headlines:
                            text = headline.text.strip()
                            text = ' '.join(text.split())
                            if text and len(text) > 10 and len(text) < 200:
                                if not any(skip in text.lower() for skip in ['menu', 'navigation', 'search', 'close', 'skip', 'subscribe', 'newsletter']):
                                    data['headlines'].append(text)
                    
                    # Extract key insights from news content
                    content = soup.get_text()
                    
                    # Look for numbers and statistics in context
                    sentences = content.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if any(char.isdigit() for char in sentence) and 20 < len(sentence) < 300:
                            # Look for energy market statistics
                            energy_keywords = ['energy', 'electricity', 'oil', 'gas', 'coal', 'renewable', 'solar', 'wind', 'battery', 'emission', 'carbon', 'consumption', 'production']
                            if any(keyword in sentence.lower() for keyword in energy_keywords):
                                clean_sentence = ' '.join(sentence.split())
                                if len(clean_sentence) > 20:
                                    data['key_insights'].append(clean_sentence)
                    
                    # Extract market signals from recent news
                    energy_keywords = ['energy', 'electricity', 'oil', 'gas', 'coal', 'renewable', 'solar', 'wind', 'battery', 'emission', 'carbon', 'consumption', 'production', 'market', 'price']
                    for keyword in energy_keywords:
                        if keyword.lower() in content.lower():
                            sentences = content.split('.')
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if keyword.lower() in sentence.lower() and 20 < len(sentence) < 300:
                                    clean_sentence = ' '.join(sentence.split())
                                    if len(clean_sentence) > 20:
                                        data['market_signals'].append(clean_sentence)
                                        break
                    
                    if data['headlines'] or data['key_insights'] or data['market_signals']:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
            
            # Limit results to avoid token limits
            data['headlines'] = data['headlines'][:5]
            data['key_insights'] = data['key_insights'][:5]
            data['market_signals'] = data['market_signals'][:5]
            
            logger.info(f"Successfully scraped EIA: {len(data['headlines'])} headlines, {len(data['key_insights'])} insights")
            return data
            
        except Exception as e:
            logger.error(f"Error scraping EIA: {e}")
            return {'source': 'EIA Today in Energy', 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def scrape_all_sources(self) -> Dict[str, Any]:
        """Scrape all configured sources"""
        logger.info("Starting comprehensive competitive intelligence scraping...")
        
        self.data = {}
        for key, source in self.sources.items():
            if key == 'canary':
                self.data[key] = self.scrape_canary()
            elif key == 'industryweek':
                self.data[key] = self.scrape_industryweek()
            elif key == 'eia':
                self.data[key] = self.scrape_eia()
            # Add more source handlers here as needed
            
            time.sleep(2)  # Be respectful to servers
        
        self.data['scraping_timestamp'] = datetime.now().isoformat()
        logger.info("Completed scraping all sources")
        return self.data

class InfineonIntelligenceAnalyzer:
    """AI-powered analysis for Infineon's competitive intelligence"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Use model from .env or default to gpt-4o (latest available)
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        openai.api_key = self.api_key
    
    def analyze_for_infineon(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze scraped data using Infineon's Signal/Risk framework - one row per day"""
        try:
            logger.info("Starting Infineon-specific competitive intelligence analysis...")
            
            # Collect all data for daily aggregation
            daily_data = {}
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            for source_key, source_data in data.items():
                if source_key == 'scraping_timestamp' or 'error' in source_data:
                    continue
                
                # Prepare data for analysis (limit content to avoid token limits)
                headlines = source_data.get('headlines', [])[:2]  # Limit to 2 headlines
                insights = source_data.get('key_insights', [])[:2]  # Limit to 2 insights
                signals = source_data.get('market_signals', [])[:2]  # Limit to 2 signals
                
                # Clean and truncate text to avoid token limits
                def clean_and_truncate_text(text_list, max_chars=150):
                    cleaned = []
                    for text in text_list:
                        # Remove excessive whitespace and newlines
                        cleaned_text = ' '.join(text.split())
                        
                        # Remove common web artifacts and navigation
                        artifacts = [
                            'Toggle filter', 'Chevron down', 'Read documentation', 'cross',
                            'Back to homepage', 'Contact Us', 'Useful links', 'Latest insights',
                            'Latest updates', 'Open data', 'About us', 'Careers',
                            'Toggle navigation', 'My User', 'Create account', 'Log in',
                            'View form', 'View source', 'History', 'Refresh', 'What links here',
                            'Browse Properties', 'From Open Energy Information'
                        ]
                        
                        for artifact in artifacts:
                            cleaned_text = cleaned_text.replace(artifact, '')
                        
                        # Remove excessive whitespace again
                        cleaned_text = ' '.join(cleaned_text.split())
                        
                        # Only add if meaningful and contains relevant keywords
                        if len(cleaned_text) > 30 and len(cleaned_text) < max_chars:
                            # Check if it contains relevant keywords for Infineon's hybrid AI industrial strategy
                            relevant_keywords = [
                                'ai', 'artificial intelligence', 'industrial', 'manufacturing', 'automation',
                                'predictive maintenance', 'edge computing', 'iot', 'smart', 'efficiency',
                                'reliability', 'sustainability', 'semiconductor', 'chip', 'power',
                                'motor', 'drive', 'equipment', 'optimization', 'machine learning',
                                'energy', 'electricity', 'renewable', 'solar', 'wind', 'battery',
                                'emission', 'carbon', 'clean', 'transition', 'investment', 'market',
                                'technology', 'research', 'production', 'factory', 'industry'
                            ]
                            if any(keyword in cleaned_text.lower() for keyword in relevant_keywords):
                                cleaned.append(cleaned_text)
                        elif len(cleaned_text) >= max_chars:
                            # Truncate and check if meaningful
                            truncated = cleaned_text[:max_chars] + "..."
                            relevant_keywords = [
                                'ai', 'artificial intelligence', 'industrial', 'manufacturing', 'automation',
                                'predictive maintenance', 'edge computing', 'iot', 'smart', 'efficiency',
                                'reliability', 'sustainability', 'semiconductor', 'chip', 'power'
                            ]
                            if any(keyword in truncated.lower() for keyword in relevant_keywords):
                                cleaned.append(truncated)
                    
                    return cleaned
                
                headlines = clean_and_truncate_text(headlines)
                insights = clean_and_truncate_text(insights)
                signals = clean_and_truncate_text(signals)
                
                # Aggregate data by day
                if current_date not in daily_data:
                    daily_data[current_date] = {
                        'sources': [],
                        'headlines': [],
                        'insights': [],
                        'signals': []
                    }
                
                daily_data[current_date]['sources'].append(source_data.get('source', 'Unknown'))
                daily_data[current_date]['headlines'].extend(headlines)
                daily_data[current_date]['insights'].extend(insights)
                daily_data[current_date]['signals'].extend(signals)
                
                logger.info(f"Added data from {source_data.get('source', 'Unknown')} to daily aggregation")
            
            # Now analyze aggregated daily data
            analysis_results = []
            
            for date, aggregated_data in daily_data.items():
                # Combine all data for the day
                all_headlines = aggregated_data['headlines'][:5]  # Limit to 5 headlines
                all_insights = aggregated_data['insights'][:5]  # Limit to 5 insights
                all_signals = aggregated_data['signals'][:5]  # Limit to 5 signals
                all_sources = aggregated_data['sources']
                
                # Log what's being sent to AI
                logger.info(f"Analyzing aggregated data for {date}:")
                logger.info(f"  Sources: {all_sources}")
                logger.info(f"  Headlines: {all_headlines}")
                logger.info(f"  Insights: {all_insights}")
                logger.info(f"  Signals: {all_signals}")
                
                # Create analysis prompt for daily aggregation
                prompt = f"""
                Analyze competitive intelligence for Infineon Technologies AG for {date}, focusing on their ambition to maximize efficiency, reliability, and sustainability in industrial operations by applying hybrid AI models to industrial equipment at scale.

                Sources analyzed: {', '.join(all_sources)}
                Headlines: {all_headlines}
                Key Insights: {all_insights}
                Market Signals: {all_signals}

                Using Infineon's Signal/Risk framework for Competitive and Market Intelligence Analysis:

                INFINEON'S STRATEGIC AMBITION: Maximize efficiency, reliability, and sustainability in industrial operations by applying hybrid AI models to industrial equipment at scale.

                SIGNAL ANALYSIS (Positive/Neutral/Negative):
                - 🟢 Positive: The event represents an opportunity for Infineon's hybrid AI industrial strategy. Examples: new AI regulations favoring edge computing, competitor delays in AI chip production, government funding for industrial AI, market growth in industrial IoT, increased demand for energy-efficient AI processing, breakthroughs in AI-powered predictive maintenance.
                - ⚪ Neutral: The event is noted for awareness but has no immediate impact on Infineon's hybrid AI industrial ambitions. Examples: general market news without AI/industrial implications, competitor changes in unrelated sectors.
                - 🔴 Negative: The event represents a threat to Infineon's hybrid AI industrial strategy. Examples: rival launching superior AI chips for industrial applications, competitor gaining major industrial AI design wins, regulatory changes that disadvantage Infineon's AI approach, breakthrough competitive AI technologies for industrial equipment.

                RISK ANALYSIS (Low/Medium/High):
                - Low: The potential impact is minor, easily manageable, or very unlikely to materialize. Examples: small competitor announcements, general market commentary, minor regulatory updates.
                - Medium: The event could have a significant impact, but it may not be immediate, or there may be time to formulate a response. Examples: competitor AI product announcements with future timelines, market trends affecting industrial AI demand in 6-12 months.
                - High: The event poses a direct, severe, and immediate threat (or opportunity) to Infineon's hybrid AI industrial objectives. Examples: major competitor design wins in industrial AI, immediate regulatory changes affecting AI deployment, supply chain disruptions for AI chips, breakthrough competitive AI technologies.

                Focus specifically on implications for Infineon's hybrid AI industrial strategy including:
                - AI-powered industrial equipment and automation
                - Edge computing and AI processing at scale
                - Predictive maintenance and reliability systems
                - Energy efficiency in industrial AI applications
                - Industrial IoT and smart manufacturing
                - Power semiconductors for AI processing (SiC, GaN, IGBT)
                - Industrial motor drives and power supplies with AI integration
                - Renewable energy systems with AI optimization

                Provide analysis in this exact format (do not include the field names in the content):
                Date: {date}
                Key insights: [Comprehensive analysis focusing on implications for Infineon's hybrid AI industrial strategy, competitive landscape, and strategic considerations for maximizing efficiency, reliability, and sustainability in industrial operations. Be thorough and detailed.]
                Signal: [Positive/Neutral/Negative with brief reasoning]
                Risk: [Low/Medium/High with brief reasoning]
                """
                
                # Call OpenAI API
                try:
                    logger.info(f"Calling OpenAI API with model: {self.model} for daily analysis")
                    
                    # Check if we have sufficient data for analysis
                    total_data_points = len(all_headlines) + len(all_insights) + len(all_signals)
                    if total_data_points < 2:
                        logger.warning(f"Insufficient data for analysis on {date}: only {total_data_points} data points")
                        analysis_text = "Unable to generate analysis due to insufficient data. Need at least 2 data points from sources."
                    else:
                        response = openai.ChatCompletion.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": "You are a competitive intelligence analyst specializing in industrial AI, semiconductor markets, and smart manufacturing. Focus on Infineon's ambition to maximize efficiency, reliability, and sustainability in industrial operations through hybrid AI models applied to industrial equipment at scale. Provide comprehensive daily analysis based on multiple sources."},
                                {"role": "user", "content": prompt}
                            ],
                            max_completion_tokens=1000
                        )
                        
                        analysis_text = response.choices[0].message.content
                        logger.info(f"Raw AI response for daily analysis {date}: {analysis_text}")
                        logger.info(f"Response length: {len(analysis_text)} characters")
                        
                        if not analysis_text:
                            logger.warning(f"Empty response from OpenAI API for daily analysis {date}")
                            analysis_text = "Unable to generate analysis due to insufficient data."
                        
                except openai.error.InvalidRequestError as e:
                    logger.error(f"Invalid model request for daily analysis {date}: {e}")
                    analysis_text = f"Model configuration error: {str(e)}. Please check OPENAI_MODEL setting."
                except openai.error.AuthenticationError as e:
                    logger.error(f"Authentication error for daily analysis {date}: {e}")
                    analysis_text = f"Authentication error: {str(e)}. Please check OPENAI_API_KEY."
                except Exception as e:
                    logger.error(f"Error calling OpenAI API for daily analysis {date}: {e}")
                    analysis_text = f"Error in AI analysis: {str(e)}"
                
                # Parse the analysis
                result = self._parse_analysis(analysis_text, f"Daily Analysis - {', '.join(all_sources)}")
                analysis_results.append(result)
                
                logger.info(f"Completed daily analysis for {date}")
            
            logger.info("Completed all competitive intelligence analysis")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in competitive intelligence analysis: {e}")
            return []
    
    def _parse_analysis(self, analysis_text: str, source: str) -> Dict[str, Any]:
        """Parse AI analysis into structured format"""
        try:
            lines = analysis_text.split('\n')
            result = {
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Source': source,
                'Key insights': '',
                'Signal': '',
                'Risk': ''
            }
            
            current_section = None
            section_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers
                if line.lower().startswith('date:'):
                    result['Date'] = line.replace('Date:', '').replace('date:', '').strip()
                elif line.lower().startswith('key insights:'):
                    current_section = 'Key insights'
                    section_content = []
                elif line.lower().startswith('signal:'):
                    current_section = 'Signal'
                    section_content = []
                elif line.lower().startswith('risk:'):
                    current_section = 'Risk'
                    section_content = []
                else:
                    # Add content to current section
                    if current_section:
                        section_content.append(line)
                        if current_section == 'Key insights':
                            # Clean the key insights content immediately
                            insights_text = ' '.join(section_content)
                            # Remove any date or header lines
                            lines = insights_text.split('\n')
                            filtered_lines = []
                            for line in lines:
                                line = line.strip()
                                if line and not line.lower().startswith('date:') and not line.lower().startswith('key insights:'):
                                    filtered_lines.append(line)
                            result['Key insights'] = ' '.join(filtered_lines).strip()
                            # Store the full content for later processing
                            result['_full_insights'] = result['Key insights']
                        elif current_section == 'Signal':
                            result['Signal'] = ' '.join(section_content)
                        elif current_section == 'Risk':
                            result['Risk'] = ' '.join(section_content)
            
            # Clean up the parsed content
            if result['Key insights']:
                # Remove any remaining "Key insights:" prefix and date lines
                cleaned_insights = result['Key insights']
                # Remove date and header lines that might be included
                lines = cleaned_insights.split('\n')
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith('date:') and not line.lower().startswith('key insights:'):
                        filtered_lines.append(line)
                cleaned_insights = ' '.join(filtered_lines)
                # Additional cleanup to remove any remaining artifacts
                cleaned_insights = cleaned_insights.replace('Date:', '').replace('date:', '').replace('Key insights:', '').replace('key insights:', '').strip()
                result['Key insights'] = cleaned_insights.strip()
                
                # Limit to 200 words but preserve more meaningful content
                words = result['Key insights'].split()
                if len(words) > 200:
                    # Try to find a good breaking point (end of sentence)
                    truncated = ' '.join(words[:200])
                    # Look for the last complete sentence
                    sentences = truncated.split('.')
                    if len(sentences) > 1:
                        # Remove the last incomplete sentence
                        complete_sentences = sentences[:-1]
                        result['Key insights'] = '. '.join(complete_sentences) + '.'
                    else:
                        result['Key insights'] = truncated + '...'
                else:
                    result['Key insights'] = ' '.join(words)
            
            if result['Signal']:
                # Extract just the signal type (Positive/Neutral/Negative)
                signal_lower = result['Signal'].lower()
                if 'positive' in signal_lower:
                    result['Signal'] = 'Positive'
                elif 'negative' in signal_lower:
                    result['Signal'] = 'Negative'
                else:
                    result['Signal'] = 'Neutral'
            
            if result['Risk']:
                # Extract just the risk level (Low/Medium/High)
                risk_lower = result['Risk'].lower()
                if 'high' in risk_lower:
                    result['Risk'] = 'High'
                elif 'medium' in risk_lower:
                    result['Risk'] = 'Medium'
                else:
                    result['Risk'] = 'Low'
            
                            # If no structured parsing worked, try to extract from the full text
                if not result['Key insights'] and not result['Signal'] and not result['Risk']:
                    # Fallback: look for patterns in the text
                    text_lower = analysis_text.lower()
                    if 'positive' in text_lower:
                        result['Signal'] = 'Positive'
                    elif 'negative' in text_lower:
                        result['Signal'] = 'Negative'
                    else:
                        result['Signal'] = 'Neutral'
                        
                    if 'high' in text_lower and 'risk' in text_lower:
                        result['Risk'] = 'High'
                    elif 'medium' in text_lower and 'risk' in text_lower:
                        result['Risk'] = 'Medium'
                    else:
                        result['Risk'] = 'Low'
                        
                    # Extract a summary from the text
                    sentences = analysis_text.split('.')
                    if sentences:
                        result['Key insights'] = sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]
                
                # Additional fallback parsing for Signal and Risk if they're still empty
                if not result['Signal'] or result['Signal'] == '' or not result['Risk'] or result['Risk'] == '':
                    text_lower = analysis_text.lower()
                    logger.info(f"Fallback parsing - Signal: {result['Signal']}, Risk: {result['Risk']}")
                    logger.info(f"Looking for patterns in text: {text_lower[-200:]}")  # Last 200 chars
                    
                    # Extract Signal - look for the specific patterns in the AI response
                    if not result['Signal']:
                        if '🟢 positive' in text_lower or 'signal: 🟢 positive' in text_lower:
                            result['Signal'] = 'Positive'
                            logger.info("Found 🟢 Positive signal")
                        elif '🔴 negative' in text_lower or 'signal: 🔴 negative' in text_lower:
                            result['Signal'] = 'Negative'
                            logger.info("Found 🔴 Negative signal")
                        elif 'positive' in text_lower and 'signal:' in text_lower:
                            result['Signal'] = 'Positive'
                            logger.info("Found Positive signal")
                        elif 'negative' in text_lower and 'signal:' in text_lower:
                            result['Signal'] = 'Negative'
                            logger.info("Found Negative signal")
                        else:
                            result['Signal'] = 'Neutral'
                            logger.info("Defaulting to Neutral signal")
                    
                    # Extract Risk - look for the specific patterns in the AI response
                    if not result['Risk']:
                        if 'risk: high' in text_lower or ('high' in text_lower and 'risk' in text_lower):
                            result['Risk'] = 'High'
                            logger.info("Found High risk")
                        elif 'risk: medium' in text_lower or ('medium' in text_lower and 'risk' in text_lower):
                            result['Risk'] = 'Medium'
                            logger.info("Found Medium risk")
                        elif 'risk: low' in text_lower or ('low' in text_lower and 'risk' in text_lower):
                            result['Risk'] = 'Low'
                            logger.info("Found Low risk")
                        else:
                            result['Risk'] = 'Low'
                            logger.info("Defaulting to Low risk")
            
            # Final cleanup for key insights - handle case where AI includes headers
            if result['Key insights']:
                # If the key insights still contain headers, try to extract just the content
                insights_text = result['Key insights']
                
                # Remove any date lines first
                lines = insights_text.split('\n')
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith('date:'):
                        filtered_lines.append(line)
                insights_text = ' '.join(filtered_lines)
                
                # Remove any remaining "key insights:" prefix
                if 'key insights:' in insights_text.lower():
                    parts = insights_text.split('key insights:')
                    if len(parts) > 1:
                        result['Key insights'] = parts[1].strip()
                    else:
                        result['Key insights'] = insights_text.strip()
                else:
                    result['Key insights'] = insights_text.strip()
                
                # Final cleanup to remove any remaining "Key insights:" prefix
                result['Key insights'] = result['Key insights'].replace('Key insights:', '').replace('key insights:', '').strip()
                
                # Limit to 200 words but preserve more meaningful content
                words = result['Key insights'].split()
                if len(words) > 200:
                    # Try to find a good breaking point (end of sentence)
                    truncated = ' '.join(words[:200])
                    # Look for the last complete sentence
                    sentences = truncated.split('.')
                    if len(sentences) > 1:
                        # Remove the last incomplete sentence
                        complete_sentences = sentences[:-1]
                        result['Key insights'] = '. '.join(complete_sentences) + '.'
                    else:
                        result['Key insights'] = truncated + '...'
                else:
                    result['Key insights'] = ' '.join(words)
            
            # Final fallback parsing for Signal and Risk if they're still empty
            if not result['Signal'] or result['Signal'] == '' or not result['Risk'] or result['Risk'] == '':
                text_lower = analysis_text.lower()
                
                # Extract Signal - look for the specific patterns in the AI response
                if not result['Signal'] or result['Signal'] == '':
                    if '🟢 positive' in text_lower or 'signal: 🟢 positive' in text_lower:
                        result['Signal'] = 'Positive'
                    elif '🔴 negative' in text_lower or 'signal: 🔴 negative' in text_lower:
                        result['Signal'] = 'Negative'
                    elif 'positive' in text_lower and 'signal:' in text_lower:
                        result['Signal'] = 'Positive'
                    elif 'negative' in text_lower and 'signal:' in text_lower:
                        result['Signal'] = 'Negative'
                    else:
                        result['Signal'] = 'Neutral'
                
                # Extract Risk - look for the specific patterns in the AI response
                if not result['Risk'] or result['Risk'] == '':
                    if 'risk: high' in text_lower or ('high' in text_lower and 'risk' in text_lower):
                        result['Risk'] = 'High'
                    elif 'risk: medium' in text_lower or ('medium' in text_lower and 'risk' in text_lower):
                        result['Risk'] = 'Medium'
                    elif 'risk: low' in text_lower or ('low' in text_lower and 'risk' in text_lower):
                        result['Risk'] = 'Low'
                    else:
                        result['Risk'] = 'Low'
            
            logger.info(f"Parsed result for {source}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Source': source,
                'Key insights': 'Analysis parsing error',
                'Signal': 'Neutral',
                'Risk': 'Low'
            }

class ExcelIntelligenceExporter:
    """Export competitive intelligence to Excel with specified format"""
    
    def __init__(self):
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def export_to_excel(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Export analysis to Excel with Date, Key insights, Signal, Risk columns"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_filename = f'exports/infineon_intelligence_{timestamp}.xlsx'
            
            # Create DataFrame with required columns
            df = pd.DataFrame(analysis_results)
            
            # Ensure required columns exist
            required_columns = ['Date', 'Key insights', 'Signal', 'Risk']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Reorder columns as specified (removed Source column)
            df = df[['Date', 'Key insights', 'Signal', 'Risk']]
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Competitive Intelligence', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Competitive Intelligence']
                
                # Format headers
                from openpyxl.styles import Font, PatternFill, Alignment
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Competitive intelligence exported to Excel: {excel_filename}")
            return excel_filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise


class GoogleSheetsIntelligenceExporter:
    """Export Infineon intelligence data to Google Sheets"""
    
    def __init__(self):
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImportError("Google Sheets integration not available. Install gspread and google-auth")
        
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID') or os.getenv('SPREADSHEET_ID')
        self.client = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.error(f"Google credentials file not found: {self.credentials_file}")
                logger.info("Please download your service account credentials and save as 'credentials.json'")
                return False
            
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Authenticate
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope)
            
            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {e}")
            return False
    
    def create_or_open_spreadsheet(self, title: str = None) -> str:
        """Create a new spreadsheet or open existing one"""
        try:
            if not self.client:
                if not self.authenticate():
                    return None
            
            # Use provided spreadsheet ID if available
            if self.spreadsheet_id:
                try:
                    spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                    logger.info(f"Opened existing spreadsheet: {spreadsheet.title}")
                    return spreadsheet.url
                except Exception as e:
                    logger.warning(f"Could not open spreadsheet with ID {self.spreadsheet_id}: {e}")
                    logger.info("Will create new spreadsheet...")
            
            # Create new spreadsheet
            if not title:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                title = f"Infineon Intelligence {timestamp}"
            
            spreadsheet = self.client.create(title)
            logger.info(f"Created new Google Spreadsheet: {spreadsheet.title}")
            logger.info(f"Spreadsheet URL: {spreadsheet.url}")
            logger.info(f"Spreadsheet ID: {spreadsheet.id}")
            logger.info("💡 Save this ID in your .env file as GOOGLE_SPREADSHEET_ID for future use")
            
            return spreadsheet.url
            
        except Exception as e:
            logger.error(f"Error creating/opening spreadsheet: {e}")
            return None
    
    def export_to_sheets(self, analysis_results: List[Dict[str, Any]], spreadsheet_title: str = None) -> str:
        """Export analysis results to Google Sheets"""
        try:
            if not self.client:
                if not self.authenticate():
                    raise Exception("Failed to authenticate with Google Sheets")
            
            # Create or open spreadsheet
            spreadsheet_url = self.create_or_open_spreadsheet(spreadsheet_title)
            if not spreadsheet_url:
                raise Exception("Failed to create or open spreadsheet")
            
            # Get the spreadsheet
            if self.spreadsheet_id:
                spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            else:
                # Get the most recently created spreadsheet
                spreadsheets = self.client.openall()
                spreadsheet = spreadsheets[0]  # Most recent
            
            # Create or clear the main worksheet
            try:
                worksheet = spreadsheet.worksheet('Competitive Intelligence')
                worksheet.clear()
            except:
                worksheet = spreadsheet.add_worksheet(title='Competitive Intelligence', rows=100, cols=10)
            
            # Prepare data for Google Sheets
            headers = ['Date', 'Key insights', 'Signal', 'Risk']
            data = [headers]
            
            for result in analysis_results:
                row = [
                    result.get('Date', ''),
                    result.get('Key insights', ''),
                    result.get('Signal', ''),
                    result.get('Risk', '')
                ]
                data.append(row)
            
            # Update the worksheet
            worksheet.update('A1:D' + str(len(data)), data)
            
            # Format headers (basic formatting)
            worksheet.format('A1:D1', {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            logger.info(f"Successfully exported to Google Sheets: {spreadsheet_url}")
            return spreadsheet_url
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
            raise


def main():
    """Main function for Infineon competitive intelligence analysis"""
    logger.info("Starting Infineon Competitive Intelligence Analysis")
    
    try:
        # Step 1: Initialize scraper and show current sources
        scraper = ConfigurableIntelligenceScraper()
        scraper.list_sources()
        
        # Step 2: Scrape all sources
        data = scraper.scrape_all_sources()
        
        # Step 3: Save raw data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_data_file = f'data/infineon_intelligence_raw_{timestamp}.json'
        with open(raw_data_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Raw intelligence data saved to {raw_data_file}")
        
        # Step 4: AI Analysis using Infineon framework (one row per day)
        analyzer = InfineonIntelligenceAnalyzer()
        analysis_results = analyzer.analyze_for_infineon(data)
        
        # Step 5: Export to Excel
        exporter = ExcelIntelligenceExporter()
        excel_file = exporter.export_to_excel(analysis_results)
        
        # Step 5b: Export to Google Sheets (optional)
        google_sheets_url = None
        try:
            if GOOGLE_SHEETS_AVAILABLE:
                sheets_exporter = GoogleSheetsIntelligenceExporter()
                google_sheets_url = sheets_exporter.export_to_sheets(analysis_results)
                logger.info(f"Successfully exported to Google Sheets: {google_sheets_url}")
            else:
                logger.info("Google Sheets export skipped - dependencies not installed")
        except Exception as e:
            logger.warning(f"Google Sheets export failed: {e}")
            logger.info("Excel export completed successfully")
        
        # Step 6: Save analysis summary
        analysis_file = f'analysis/infineon_analysis_{timestamp}.txt'
        with open(analysis_file, 'w') as f:
            f.write("INFINEON COMPETITIVE INTELLIGENCE ANALYSIS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in analysis_results:
                f.write(f"Date: {result.get('Date', '')}\n")
                f.write(f"Signal: {result.get('Signal', '')}\n")
                f.write(f"Risk: {result.get('Risk', '')}\n")
                f.write(f"Key Insights: {result.get('Key insights', '')}\n")
                f.write("-" * 40 + "\n\n")
        
        logger.info("=" * 60)
        logger.info("INFINEON COMPETITIVE INTELLIGENCE COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Excel file: {excel_file}")
        if google_sheets_url:
            logger.info(f"Google Sheets: {google_sheets_url}")
        logger.info(f"Analysis file: {analysis_file}")
        logger.info(f"Raw data: {raw_data_file}")
        logger.info("=" * 60)
        
        # Print summary
        print("\n" + "=" * 60)
        print("INFINEON COMPETITIVE INTELLIGENCE SUMMARY")
        print("=" * 60)
        for result in analysis_results:
            print(f"📅 Date: {result.get('Date', '')}")
            print(f"📈 Signal: {result.get('Signal', '')}")
            print(f"⚠️  Risk: {result.get('Risk', '')}")
            print(f"💡 Key Insights: {result.get('Key insights', '')}")
            print("-" * 40)
        
    except Exception as e:
        logger.error(f"Main process failed: {e}")
        raise

if __name__ == "__main__":
    main()
