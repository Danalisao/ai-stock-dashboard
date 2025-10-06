"""
📰 News Aggregator
Fetch financial news from multiple FREE sources (RSS, scraping, social media)
"""

import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse
import re


class NewsAggregator:
    """Aggregate news from multiple free sources"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize news aggregator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config.get('news', {})
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_market_news(self, max_articles: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch general market news (not specific to a symbol)
        Used for discovering trending stocks across the entire market
        
        Args:
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of news articles from multiple sources
        """
        all_articles = []
        sources = self.config.get('sources', {})
        
        try:
            # MarketWatch RSS
            if sources.get('marketwatch', True):
                mw_articles = self._fetch_marketwatch_rss()
                all_articles.extend(mw_articles[:20])
                self.logger.info(f"Fetched {len(mw_articles)} articles from MarketWatch")
                time.sleep(1)
            
            # Seeking Alpha RSS
            if sources.get('seeking_alpha', True):
                sa_articles = self._fetch_seeking_alpha_rss()
                all_articles.extend(sa_articles[:20])
                self.logger.info(f"Fetched {len(sa_articles)} articles from Seeking Alpha")
                time.sleep(1)
            
            # Yahoo Finance Top Stories
            if sources.get('yahoo_finance', True):
                yf_articles = self._fetch_yahoo_top_stories()
                all_articles.extend(yf_articles[:20])
                self.logger.info(f"Fetched {len(yf_articles)} articles from Yahoo Finance")
                time.sleep(1)
            
            # Benzinga RSS
            if sources.get('benzinga', True):
                bz_articles = self._fetch_benzinga_rss()
                all_articles.extend(bz_articles[:20])
                self.logger.info(f"Fetched {len(bz_articles)} articles from Benzinga")
                time.sleep(1)
            
            # Deduplicate by URL
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                url = article.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append(article)
                    if len(unique_articles) >= max_articles:
                        break
            
            self.logger.info(f"Total unique market articles: {len(unique_articles)}")
            return unique_articles[:max_articles]
            
        except Exception as e:
            self.logger.error(f"Error fetching market news: {e}")
            return []
    
    def fetch_all_news(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch news from all enabled sources
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        all_articles = []
        sources = self.config.get('sources', {})
        
        try:
            # Yahoo Finance RSS
            if sources.get('yahoo_finance', True):
                yahoo_articles = self._fetch_yahoo_finance_rss(symbol)
                all_articles.extend(yahoo_articles)
                self.logger.info(f"Fetched {len(yahoo_articles)} articles from Yahoo Finance")
                time.sleep(1)  # Rate limiting
            
            # Finviz scraping
            if sources.get('finviz', True):
                finviz_articles = self._scrape_finviz_news(symbol)
                all_articles.extend(finviz_articles)
                self.logger.info(f"Fetched {len(finviz_articles)} articles from Finviz")
                time.sleep(1)
            
            # Generic RSS feeds
            rss_feeds = self.config.get('rss_feeds', [])
            for feed_url in rss_feeds:
                try:
                    rss_articles = self._fetch_rss_feed(feed_url, symbol)
                    all_articles.extend(rss_articles)
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            
            # Deduplicate by URL
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                url = article.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_articles.append(article)
            
            self.logger.info(f"Total unique articles for {symbol}: {len(unique_articles)}")
            return unique_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def _fetch_yahoo_finance_rss(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch news from Yahoo Finance RSS feed
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            List of articles
        """
        articles = []
        
        try:
            # Yahoo Finance doesn't have per-stock RSS, so we scrape the news page
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles (structure may change)
            news_items = soup.find_all('li', class_=re.compile(r'stream-item|article'))
            
            for item in news_items[:10]:  # Limit to 10 articles
                try:
                    title_elem = item.find('h3') or item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.find('a')
                    url = link['href'] if link and 'href' in link.attrs else None
                    
                    if url and not url.startswith('http'):
                        url = f"https://finance.yahoo.com{url}"
                    
                    # Try to get description
                    desc_elem = item.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Try to get date
                    time_elem = item.find('time')
                    pub_date = time_elem['datetime'] if time_elem and 'datetime' in time_elem.attrs else datetime.now().isoformat()
                    
                    if title and url:
                        articles.append({
                            'title': title,
                            'description': description,
                            'url': url,
                            'source': 'Yahoo Finance',
                            'published_date': pub_date,
                            'fetched_at': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing Yahoo Finance article: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo Finance news: {e}")
        
        return articles
    
    def _scrape_finviz_news(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Scrape news from Finviz
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            List of articles
        """
        articles = []
        
        try:
            url = f"https://finviz.com/quote.ashx?t={symbol}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news table
            news_table = soup.find('table', class_='fullview-news-outer')
            if not news_table:
                return articles
            
            news_rows = news_table.find_all('tr')
            
            current_date = datetime.now().date()
            
            for row in news_rows[:20]:  # Limit to 20 articles
                try:
                    # Get date/time
                    td_date = row.find('td', align='right')
                    if not td_date:
                        continue
                    
                    date_text = td_date.get_text(strip=True)
                    
                    # Parse date
                    if date_text:
                        # Finviz format: "Jan-05-25 10:30AM" or "10:30AM" (today)
                        if '-' in date_text:
                            pub_date = datetime.strptime(date_text, "%b-%d-%y %I:%M%p")
                        else:
                            # Today
                            time_part = datetime.strptime(date_text, "%I:%M%p").time()
                            pub_date = datetime.combine(current_date, time_part)
                    else:
                        pub_date = datetime.now()
                    
                    # Get link and title
                    link = row.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    article_url = link['href']
                    
                    # Get source
                    source_span = row.find('span')
                    source = source_span.get_text(strip=True) if source_span else 'Finviz'
                    
                    if title and article_url:
                        articles.append({
                            'title': title,
                            'description': '',
                            'url': article_url,
                            'source': source,
                            'published_date': pub_date.isoformat(),
                            'fetched_at': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing Finviz article: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Finviz: {e}")
        
        return articles
    
    def _fetch_rss_feed(self, feed_url: str, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch articles from RSS feed
        
        Args:
            feed_url: RSS feed URL
            symbol: Optional symbol to filter by
            
        Returns:
            List of articles
        """
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:20]:  # Limit to 20
                try:
                    title = entry.get('title', '')
                    description = entry.get('summary', '') or entry.get('description', '')
                    url = entry.get('link', '')
                    
                    # Try to get published date
                    pub_date = entry.get('published', '') or entry.get('updated', '')
                    if pub_date:
                        try:
                            pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                        except:
                            pub_date = datetime.now().isoformat()
                    else:
                        pub_date = datetime.now().isoformat()
                    
                    # Get source from feed title or URL
                    source = feed.feed.get('title', urlparse(feed_url).netloc)
                    
                    # Filter by symbol if provided
                    if symbol:
                        # Check if symbol appears in title or description
                        text = f"{title} {description}".upper()
                        if symbol.upper() not in text and f"${symbol.upper()}" not in text:
                            continue
                    
                    if title and url:
                        articles.append({
                            'title': title,
                            'description': description,
                            'url': url,
                            'source': source,
                            'published_date': pub_date,
                            'fetched_at': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing RSS entry: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return articles
    
    def _fetch_marketwatch_rss(self) -> List[Dict[str, Any]]:
        """Fetch general market news from MarketWatch RSS"""
        articles = []
        try:
            feed = feedparser.parse("https://www.marketwatch.com/rss/topstories")
            for entry in feed.entries[:30]:
                articles.append({
                    'title': entry.get('title', 'N/A'),
                    'url': entry.get('link', ''),
                    'description': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'source': 'MarketWatch',
                    'symbol': None  # Will be extracted by AI
                })
        except Exception as e:
            self.logger.error(f"Error fetching MarketWatch RSS: {e}")
        return articles
    
    def _fetch_seeking_alpha_rss(self) -> List[Dict[str, Any]]:
        """Fetch market news from Seeking Alpha RSS"""
        articles = []
        try:
            feed = feedparser.parse("https://seekingalpha.com/feed.xml")
            for entry in feed.entries[:30]:
                articles.append({
                    'title': entry.get('title', 'N/A'),
                    'url': entry.get('link', ''),
                    'description': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'source': 'Seeking Alpha',
                    'symbol': None
                })
        except Exception as e:
            self.logger.error(f"Error fetching Seeking Alpha RSS: {e}")
        return articles
    
    def _fetch_yahoo_top_stories(self) -> List[Dict[str, Any]]:
        """Fetch Yahoo Finance top stories"""
        articles = []
        try:
            url = "https://finance.yahoo.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles on homepage
            news_items = soup.find_all('h3', limit=30)
            for item in news_items:
                link_tag = item.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href', '')
                    if href and not href.startswith('http'):
                        href = f"https://finance.yahoo.com{href}"
                    
                    articles.append({
                        'title': title,
                        'url': href,
                        'description': '',
                        'published': datetime.now().isoformat(),
                        'source': 'Yahoo Finance',
                        'symbol': None
                    })
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo top stories: {e}")
        return articles
    
    def _fetch_benzinga_rss(self) -> List[Dict[str, Any]]:
        """Fetch Benzinga news RSS"""
        articles = []
        try:
            feed = feedparser.parse("https://www.benzinga.com/feed")
            for entry in feed.entries[:30]:
                articles.append({
                    'title': entry.get('title', 'N/A'),
                    'url': entry.get('link', ''),
                    'description': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'source': 'Benzinga',
                    'symbol': None
                })
        except Exception as e:
            self.logger.error(f"Error fetching Benzinga RSS: {e}")
        return articles
    
    def search_news_by_keyword(self, keywords: List[str], days: int = 7) -> List[Dict[str, Any]]:
        """
        Search news by keywords across sources
        
        Args:
            keywords: List of keywords to search
            days: Number of days to look back
            
        Returns:
            List of matching articles
        """
        articles = []
        
        # For each keyword, fetch news
        for keyword in keywords:
            # Try Yahoo Finance search
            try:
                url = f"https://finance.yahoo.com/lookup?s={keyword}"
                # Implementation would go here
                pass
            except Exception as e:
                self.logger.debug(f"Error searching for {keyword}: {e}")
        
        return articles
    
    def get_trending_stocks(self) -> List[str]:
        """
        Get trending stock symbols from Finviz
        
        Returns:
            List of trending symbols
        """
        symbols = []
        
        try:
            url = "https://finviz.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find trending tickers
                # Implementation depends on Finviz structure
                pass
            
        except Exception as e:
            self.logger.error(f"Error fetching trending stocks: {e}")
        
        return symbols
    
    def validate_article(self, article: Dict[str, Any]) -> bool:
        """
        Validate article data quality
        
        Args:
            article: Article dictionary
            
        Returns:
            True if valid
        """
        required_fields = ['title', 'url', 'source']
        
        # Check required fields
        for field in required_fields:
            if not article.get(field):
                return False
        
        # Validate URL format
        url = article.get('url', '')
        if not url.startswith('http'):
            return False
        
        # Check title length
        title = article.get('title', '')
        if len(title) < 10:
            return False
        
        return True
