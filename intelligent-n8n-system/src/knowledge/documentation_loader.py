"""
N8N Documentation Loader for Intelligent n8n Workflow Creation System

This module handles loading and processing n8n documentation from various sources
into the LightRAG knowledge base.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import aiofiles
import aiohttp
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

from ..core.config import get_config


class DocumentationSource:
    """Represents a documentation source"""
    
    def __init__(self, name: str, url: str, source_type: str, priority: int = 1):
        self.name = name
        self.url = url
        self.source_type = source_type  # 'web', 'api', 'github'
        self.priority = priority
        self.last_updated: Optional[datetime] = None
        self.content_hash: Optional[str] = None


class N8nDocumentationLoader:
    """Loads and processes n8n documentation from various sources"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        self.cache_dir = Path(self.config.lightrag.documentation_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize documentation sources
        self.sources = [
            DocumentationSource(
                name="n8n_main_docs",
                url=self.config.lightrag.n8n_docs_url,
                source_type="web",
                priority=1
            ),
            DocumentationSource(
                name="n8n_nodes_base",
                url=self.config.lightrag.n8n_nodes_repo,
                source_type="github",
                priority=2
            ),
            DocumentationSource(
                name="n8n_community_nodes",
                url=self.config.lightrag.n8n_community_nodes_repo,
                source_type="github",
                priority=3
            ),
            DocumentationSource(
                name="n8n_api_docs",
                url=self.config.lightrag.n8n_api_docs_url,
                source_type="web",
                priority=4
            ),
        ]
        
        # HTTP client for downloads
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def load_all_documentation(self) -> Dict[str, Any]:
        """
        Load documentation from all configured sources
        
        Returns:
            Dict containing loaded documentation with metadata
        """
        self.logger.info("Starting documentation loading process")
        
        results = {
            "sources": [],
            "total_documents": 0,
            "total_size": 0,
            "load_time": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        # Load from each source
        for source in self.sources:
            try:
                self.logger.info(f"Loading documentation from {source.name}")
                
                source_result = await self._load_source_documentation(source)
                results["sources"].append(source_result)
                results["total_documents"] += source_result.get("documents_count", 0)
                results["total_size"] += source_result.get("total_size", 0)
                
            except Exception as e:
                self.logger.error(f"Failed to load from {source.name}: {e}")
                results["sources"].append({
                    "name": source.name,
                    "status": "failed",
                    "error": str(e),
                    "documents_count": 0,
                    "total_size": 0
                })
        
        results["load_time"] = time.time() - start_time
        
        # Save summary
        await self._save_load_summary(results)
        
        self.logger.info(f"Documentation loading completed: {results['total_documents']} documents, {results['total_size']} bytes")
        
        return results
    
    async def _load_source_documentation(self, source: DocumentationSource) -> Dict[str, Any]:
        """Load documentation from a specific source"""
        
        # Check if source needs updating
        if not await self._should_update_source(source):
            self.logger.info(f"Source {source.name} is up to date, skipping")
            return await self._load_cached_source(source)
        
        # Load based on source type
        if source.source_type == "web":
            return await self._load_web_documentation(source)
        elif source.source_type == "github":
            return await self._load_github_documentation(source)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")
    
    async def _load_web_documentation(self, source: DocumentationSource) -> Dict[str, Any]:
        """Load documentation from web sources"""
        
        documents = []
        total_size = 0
        
        try:
            # Get main page
            response = await self.client.get(source.url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract documentation links
            doc_links = self._extract_documentation_links(soup, source.url)
            
            # Load each documentation page
            for link in doc_links[:50]:  # Limit to first 50 pages
                try:
                    doc_content = await self._load_web_page(link)
                    if doc_content:
                        documents.append(doc_content)
                        total_size += len(doc_content.get("content", ""))
                        
                except Exception as e:
                    self.logger.warning(f"Failed to load page {link}: {e}")
            
            # Save to cache
            await self._save_source_cache(source, documents)
            
            return {
                "name": source.name,
                "status": "success",
                "documents_count": len(documents),
                "total_size": total_size,
                "url": source.url,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load web documentation from {source.name}: {e}")
            raise
    
    async def _load_github_documentation(self, source: DocumentationSource) -> Dict[str, Any]:
        """Load documentation from GitHub repositories"""
        
        documents = []
        total_size = 0
        
        try:
            # Extract repo info from URL
            repo_info = self._parse_github_url(source.url)
            if not repo_info:
                raise ValueError(f"Invalid GitHub URL: {source.url}")
            
            # Get repository contents
            api_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/contents"
            
            # Load README and documentation files
            readme_docs = await self._load_github_readme(repo_info)
            if readme_docs:
                documents.extend(readme_docs)
                total_size += sum(len(doc.get("content", "")) for doc in readme_docs)
            
            # Load node documentation
            node_docs = await self._load_github_node_docs(repo_info)
            if node_docs:
                documents.extend(node_docs)
                total_size += sum(len(doc.get("content", "")) for doc in node_docs)
            
            # Save to cache
            await self._save_source_cache(source, documents)
            
            return {
                "name": source.name,
                "status": "success",
                "documents_count": len(documents),
                "total_size": total_size,
                "url": source.url,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load GitHub documentation from {source.name}: {e}")
            raise
    
    async def _load_web_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Load and process a single web page"""
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '.documentation',
                '.docs-content', '#content', '.page-content'
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            if not content_element:
                content_element = soup.find('body')
            
            # Convert to markdown
            content_html = str(content_element) if content_element else ""
            content_markdown = markdownify(content_html, heading_style="ATX")
            
            # Clean up content
            content_markdown = self._clean_markdown_content(content_markdown)
            
            if len(content_markdown.strip()) < 100:  # Skip very short content
                return None
            
            return {
                "title": title_text,
                "url": url,
                "content": content_markdown,
                "source_type": "web",
                "timestamp": datetime.now().isoformat(),
                "word_count": len(content_markdown.split()),
                "char_count": len(content_markdown)
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to load web page {url}: {e}")
            return None
    
    async def _load_github_readme(self, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Load README files from GitHub repository"""
        
        documents = []
        
        try:
            # Get README
            readme_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/readme"
            response = await self.client.get(readme_url, headers={"Accept": "application/vnd.github.v3+json"})
            
            if response.status_code == 200:
                readme_data = response.json()
                
                # Decode base64 content
                import base64
                content = base64.b64decode(readme_data["content"]).decode('utf-8')
                
                documents.append({
                    "title": f"{repo_info['repo']} - README",
                    "url": readme_data["html_url"],
                    "content": content,
                    "source_type": "github_readme",
                    "timestamp": datetime.now().isoformat(),
                    "word_count": len(content.split()),
                    "char_count": len(content)
                })
            
        except Exception as e:
            self.logger.warning(f"Failed to load README from {repo_info['owner']}/{repo_info['repo']}: {e}")
        
        return documents
    
    async def _load_github_node_docs(self, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Load node documentation from GitHub repository"""
        
        documents = []
        
        try:
            # Get repository contents
            contents_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/contents"
            response = await self.client.get(contents_url, headers={"Accept": "application/vnd.github.v3+json"})
            
            if response.status_code != 200:
                return documents
            
            contents = response.json()
            
            # Look for node directories
            node_dirs = [item for item in contents if item["type"] == "dir" and "node" in item["name"].lower()]
            
            for node_dir in node_dirs[:20]:  # Limit to first 20 nodes
                try:
                    node_docs = await self._load_node_directory(repo_info, node_dir["name"])
                    documents.extend(node_docs)
                except Exception as e:
                    self.logger.warning(f"Failed to load node {node_dir['name']}: {e}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load node docs from {repo_info['owner']}/{repo_info['repo']}: {e}")
        
        return documents
    
    async def _load_node_directory(self, repo_info: Dict[str, str], node_name: str) -> List[Dict[str, Any]]:
        """Load documentation for a specific node"""
        
        documents = []
        
        try:
            # Get node directory contents
            node_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/contents/nodes/{node_name}"
            response = await self.client.get(node_url, headers={"Accept": "application/vnd.github.v3+json"})
            
            if response.status_code != 200:
                return documents
            
            node_contents = response.json()
            
            # Look for documentation files
            doc_files = [
                item for item in node_contents 
                if item["type"] == "file" and item["name"].endswith((".md", ".txt", ".json"))
            ]
            
            for doc_file in doc_files:
                try:
                    file_response = await self.client.get(doc_file["download_url"])
                    if file_response.status_code == 200:
                        content = file_response.text
                        
                        documents.append({
                            "title": f"{node_name} - {doc_file['name']}",
                            "url": doc_file["html_url"],
                            "content": content,
                            "source_type": "github_node_doc",
                            "node_name": node_name,
                            "file_name": doc_file["name"],
                            "timestamp": datetime.now().isoformat(),
                            "word_count": len(content.split()),
                            "char_count": len(content)
                        })
                
                except Exception as e:
                    self.logger.warning(f"Failed to load {doc_file['name']} for node {node_name}: {e}")
        
        except Exception as e:
            self.logger.warning(f"Failed to load node directory {node_name}: {e}")
        
        return documents
    
    def _extract_documentation_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract documentation links from HTML"""
        
        links = []
        
        # Look for common documentation link patterns
        link_selectors = [
            'a[href*="/docs/"]',
            'a[href*="/documentation/"]',
            'a[href*="/guide/"]',
            'a[href*="/tutorial/"]',
            'a[href*="/api/"]',
            '.docs-nav a',
            '.documentation a',
            '.sidebar a'
        ]
        
        for selector in link_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"{base_url.rstrip('/')}{href}"
                    elif not href.startswith('http'):
                        href = f"{base_url.rstrip('/')}/{href}"
                    
                    links.append(href)
        
        # Remove duplicates and filter
        unique_links = list(set(links))
        filtered_links = [link for link in unique_links if self._is_documentation_link(link)]
        
        return filtered_links[:100]  # Limit to first 100 links
    
    def _is_documentation_link(self, url: str) -> bool:
        """Check if URL is likely to be documentation"""
        
        doc_keywords = ['docs', 'documentation', 'guide', 'tutorial', 'api', 'reference']
        skip_keywords = ['github.com', 'twitter.com', 'facebook.com', 'linkedin.com']
        
        url_lower = url.lower()
        
        # Skip external social links
        if any(skip in url_lower for skip in skip_keywords):
            return False
        
        # Must contain documentation keywords
        return any(keyword in url_lower for keyword in doc_keywords)
    
    def _parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub URL to extract owner and repo"""
        
        try:
            # Handle various GitHub URL formats
            if 'github.com' not in url:
                return None
            
            parts = url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                return {
                    'owner': parts[0],
                    'repo': parts[1]
                }
            
            return None
            
        except Exception:
            return None
    
    def _clean_markdown_content(self, content: str) -> str:
        """Clean and format markdown content"""
        
        # Remove excessive whitespace
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line or (cleaned_lines and cleaned_lines[-1]):
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove common web artifacts
        artifacts = [
            'Skip to main content',
            'Edit on GitHub',
            'Last updated',
            'Table of Contents',
            'Navigation',
            'Footer'
        ]
        
        for artifact in artifacts:
            content = content.replace(artifact, '')
        
        return content.strip()
    
    async def _should_update_source(self, source: DocumentationSource) -> bool:
        """Check if source needs updating"""
        
        cache_file = self.cache_dir / f"{source.name}_cache.json"
        
        if not cache_file.exists():
            return True
        
        try:
            async with aiofiles.open(cache_file, 'r') as f:
                cache_data = json.loads(await f.read())
            
            last_updated = datetime.fromisoformat(cache_data.get('last_updated', '1970-01-01'))
            update_interval = timedelta(hours=self.config.lightrag.update_interval_hours)
            
            return datetime.now() - last_updated > update_interval
            
        except Exception:
            return True
    
    async def _save_source_cache(self, source: DocumentationSource, documents: List[Dict[str, Any]]):
        """Save source documentation to cache"""
        
        cache_file = self.cache_dir / f"{source.name}_cache.json"
        
        cache_data = {
            'source_name': source.name,
            'source_url': source.url,
            'last_updated': datetime.now().isoformat(),
            'documents_count': len(documents),
            'documents': documents
        }
        
        async with aiofiles.open(cache_file, 'w') as f:
            await f.write(json.dumps(cache_data, indent=2, ensure_ascii=False))
        
        self.logger.info(f"Cached {len(documents)} documents for {source.name}")
    
    async def _load_cached_source(self, source: DocumentationSource) -> Dict[str, Any]:
        """Load cached source documentation"""
        
        cache_file = self.cache_dir / f"{source.name}_cache.json"
        
        try:
            async with aiofiles.open(cache_file, 'r') as f:
                cache_data = json.loads(await f.read())
            
            documents = cache_data.get('documents', [])
            total_size = sum(len(doc.get('content', '')) for doc in documents)
            
            return {
                "name": source.name,
                "status": "cached",
                "documents_count": len(documents),
                "total_size": total_size,
                "url": source.url,
                "last_updated": cache_data.get('last_updated'),
                "from_cache": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load cache for {source.name}: {e}")
            return {
                "name": source.name,
                "status": "cache_error",
                "error": str(e),
                "documents_count": 0,
                "total_size": 0
            }
    
    async def _save_load_summary(self, results: Dict[str, Any]):
        """Save documentation loading summary"""
        
        summary_file = self.cache_dir / "load_summary.json"
        
        async with aiofiles.open(summary_file, 'w') as f:
            await f.write(json.dumps(results, indent=2, ensure_ascii=False))
        
        self.logger.info(f"Saved load summary to {summary_file}")
    
    async def get_documentation_for_ingestion(self) -> List[Dict[str, Any]]:
        """
        Get all cached documentation ready for LightRAG ingestion
        
        Returns:
            List of documents formatted for LightRAG
        """
        
        documents = []
        
        for source in self.sources:
            cache_file = self.cache_dir / f"{source.name}_cache.json"
            
            if cache_file.exists():
                try:
                    async with aiofiles.open(cache_file, 'r') as f:
                        cache_data = json.loads(await f.read())
                    
                    source_docs = cache_data.get('documents', [])
                    documents.extend(source_docs)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load cached docs for {source.name}: {e}")
        
        # Format for LightRAG ingestion
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "title": doc.get("title", "Untitled"),
                "content": doc.get("content", ""),
                "metadata": {
                    "url": doc.get("url", ""),
                    "source_type": doc.get("source_type", "unknown"),
                    "timestamp": doc.get("timestamp", datetime.now().isoformat()),
                    "word_count": doc.get("word_count", 0),
                    "char_count": doc.get("char_count", 0),
                    "node_name": doc.get("node_name"),
                    "file_name": doc.get("file_name")
                }
            }
            formatted_docs.append(formatted_doc)
        
        self.logger.info(f"Prepared {len(formatted_docs)} documents for LightRAG ingestion")
        
        return formatted_docs


# CLI interface for documentation loading
async def main():
    """Main function for CLI usage"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Load n8n documentation into knowledge base")
    parser.add_argument("--force-update", action="store_true", help="Force update all sources")
    parser.add_argument("--source", help="Load specific source only")
    parser.add_argument("--list-sources", action="store_true", help="List available sources")
    
    args = parser.parse_args()
    
    async with N8nDocumentationLoader() as loader:
        
        if args.list_sources:
            print("Available documentation sources:")
            for source in loader.sources:
                print(f"  - {source.name}: {source.url} ({source.source_type})")
            return
        
        if args.source:
            # Load specific source
            source = next((s for s in loader.sources if s.name == args.source), None)
            if not source:
                print(f"Source '{args.source}' not found")
                return
            
            result = await loader._load_source_documentation(source)
            print(f"Loaded {result['documents_count']} documents from {result['name']}")
        else:
            # Load all sources
            results = await loader.load_all_documentation()
            print(f"Loaded {results['total_documents']} documents from {len(results['sources'])} sources")
            print(f"Total size: {results['total_size']} bytes")
            print(f"Load time: {results['load_time']:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
