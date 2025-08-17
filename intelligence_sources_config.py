#!/usr/bin/env python3
"""
Configuration file for Infineon Intelligence Sources
"""

def get_enabled_sources():
    """Return the enabled intelligence sources"""
    return {
        'canary': {
            'name': 'Canary Media',
            'url': 'https://www.canarymedia.com/',
            'description': 'Clean energy news and analysis',
            'enabled': True
        },
        'industryweek': {
            'name': 'Industry Week',
            'url': 'https://www.industryweek.com/',
            'description': 'Manufacturing and industrial insights',
            'enabled': True
        },
        'eia': {
            'name': 'EIA Today in Energy',
            'url': 'https://www.eia.gov/todayinenergy/',
            'description': 'U.S. Energy Information Administration daily energy insights',
            'enabled': True
        }
    }

def get_source_by_key(key):
    """Get a specific source by its key"""
    sources = get_enabled_sources()
    return sources.get(key)

def is_source_enabled(key):
    """Check if a source is enabled"""
    source = get_source_by_key(key)
    return source and source.get('enabled', False)

def list_enabled_sources():
    """List all enabled sources"""
    sources = get_enabled_sources()
    enabled = {k: v for k, v in sources.items() if v.get('enabled', False)}
    return enabled

