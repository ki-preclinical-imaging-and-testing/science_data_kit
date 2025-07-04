"""
PubMed Integration Provider for Science Data Kit

This module provides integration with the PubMed platform,
allowing users to access and analyze scientific literature data from PubMed
within the Science Data Kit environment.

PubMed is a free search engine accessing primarily the MEDLINE database of references
and abstracts on life sciences and biomedical topics.
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

class PubMedProvider:
    """
    Provider for integrating with the PubMed platform.
    
    This class provides methods for connecting to PubMed's open API,
    retrieving literature data, querying local PubMed databases,
    and importing data into Neo4j.
    
    Attributes:
        base_url: The base URL of the PubMed API.
        api_key: The API key for authenticating with PubMed API.
        local_db_path: Path to the local PubMed database (if available).
    """
    
    def __init__(
        self, 
        base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        api_key: Optional[str] = None,
        local_db_path: Optional[str] = None
    ):
        """
        Initialize the PubMed provider.
        
        Args:
            base_url: The base URL of the PubMed API.
            api_key: The API key for authenticating with PubMed API.
            local_db_path: Path to the local PubMed database (if available).
        """
        self.base_url = base_url
        self.api_key = api_key
        self.local_db_path = local_db_path
        self.session = requests.Session()
    
    def search(self, query: str, max_results: int = 100) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Search for articles in PubMed.
        
        Args:
            query: The search query.
            max_results: Maximum number of results to return.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the search was successful, False otherwise.
            - result: The search results if successful, or an error message if not.
        """
        try:
            # Construct the search URL
            search_url = f"{self.base_url}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            # Execute the search
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    return True, []
                
                # Fetch details for the found IDs
                return self.fetch_articles(id_list)
            else:
                return False, f"Search failed: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Error searching PubMed: {str(e)}"
    
    def fetch_articles(self, article_ids: List[str]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Fetch article details from PubMed by IDs.
        
        Args:
            article_ids: List of PubMed article IDs.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the fetch was successful, False otherwise.
            - result: The article details if successful, or an error message if not.
        """
        try:
            # Construct the fetch URL
            fetch_url = f"{self.base_url}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(article_ids),
                "retmode": "xml"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            # Execute the fetch
            response = self.session.get(fetch_url, params=params)
            
            if response.status_code == 200:
                # Parse the XML response
                return self._parse_pubmed_xml(response.text)
            else:
                return False, f"Fetch failed: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Error fetching articles from PubMed: {str(e)}"
    
    def _parse_pubmed_xml(self, xml_text: str) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Parse PubMed XML response into a list of article dictionaries.
        
        Args:
            xml_text: The XML text to parse.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the parsing was successful, False otherwise.
            - result: The parsed articles if successful, or an error message if not.
        """
        try:
            root = ET.fromstring(xml_text)
            articles = []
            
            for article_element in root.findall(".//PubmedArticle"):
                article = {}
                
                # Extract PMID
                pmid_element = article_element.find(".//PMID")
                if pmid_element is not None:
                    article["pmid"] = pmid_element.text
                
                # Extract article title
                title_element = article_element.find(".//ArticleTitle")
                if title_element is not None:
                    article["title"] = title_element.text
                
                # Extract abstract
                abstract_elements = article_element.findall(".//AbstractText")
                if abstract_elements:
                    article["abstract"] = " ".join([elem.text for elem in abstract_elements if elem.text])
                
                # Extract journal information
                journal_element = article_element.find(".//Journal")
                if journal_element is not None:
                    journal = {}
                    
                    journal_title_element = journal_element.find(".//Title")
                    if journal_title_element is not None:
                        journal["title"] = journal_title_element.text
                    
                    journal_issn_element = journal_element.find(".//ISSN")
                    if journal_issn_element is not None:
                        journal["issn"] = journal_issn_element.text
                    
                    article["journal"] = journal
                
                # Extract publication date
                pub_date_element = article_element.find(".//PubDate")
                if pub_date_element is not None:
                    year_element = pub_date_element.find("Year")
                    month_element = pub_date_element.find("Month")
                    day_element = pub_date_element.find("Day")
                    
                    pub_date = {}
                    if year_element is not None:
                        pub_date["year"] = year_element.text
                    if month_element is not None:
                        pub_date["month"] = month_element.text
                    if day_element is not None:
                        pub_date["day"] = day_element.text
                    
                    article["publication_date"] = pub_date
                
                # Extract authors
                author_elements = article_element.findall(".//Author")
                if author_elements:
                    authors = []
                    for author_element in author_elements:
                        author = {}
                        
                        last_name_element = author_element.find("LastName")
                        if last_name_element is not None:
                            author["last_name"] = last_name_element.text
                        
                        fore_name_element = author_element.find("ForeName")
                        if fore_name_element is not None:
                            author["fore_name"] = fore_name_element.text
                        
                        initials_element = author_element.find("Initials")
                        if initials_element is not None:
                            author["initials"] = initials_element.text
                        
                        authors.append(author)
                    
                    article["authors"] = authors
                
                # Extract keywords
                keyword_elements = article_element.findall(".//Keyword")
                if keyword_elements:
                    article["keywords"] = [elem.text for elem in keyword_elements if elem.text]
                
                # Extract MeSH terms
                mesh_heading_elements = article_element.findall(".//MeshHeading")
                if mesh_heading_elements:
                    mesh_terms = []
                    for mesh_element in mesh_heading_elements:
                        descriptor_element = mesh_element.find("DescriptorName")
                        if descriptor_element is not None:
                            mesh_terms.append(descriptor_element.text)
                    
                    article["mesh_terms"] = mesh_terms
                
                articles.append(article)
            
            return True, articles
        
        except Exception as e:
            return False, f"Error parsing PubMed XML: {str(e)}"
    
    def download_database(self, destination_path: str) -> Tuple[bool, str]:
        """
        Download PubMed database for local querying.
        
        Args:
            destination_path: Path where the database should be saved.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the download was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            # This is a placeholder for the actual implementation
            # In a real implementation, this would download the PubMed database
            # from the appropriate source and save it to the specified path
            
            # For now, we'll just create a dummy file
            with open(destination_path, 'w') as f:
                f.write('{"message": "PubMed database placeholder"}')
            
            self.local_db_path = destination_path
            return True, f"PubMed database downloaded to {destination_path}"
        
        except Exception as e:
            return False, f"Error downloading PubMed database: {str(e)}"
    
    def query_local_database(self, query: str) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Query the local PubMed database.
        
        Args:
            query: The search query.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the query was successful, False otherwise.
            - result: The query results if successful, or an error message if not.
        """
        try:
            if not self.local_db_path:
                return False, "Local database path not set"
            
            if not os.path.exists(self.local_db_path):
                return False, f"Local database not found at {self.local_db_path}"
            
            # This is a placeholder for the actual implementation
            # In a real implementation, this would query the local PubMed database
            
            # For now, we'll just return a dummy result
            return True, [{"pmid": "12345", "title": "Dummy article for query: " + query}]
        
        except Exception as e:
            return False, f"Error querying local PubMed database: {str(e)}"
    
    def import_to_neo4j(self, articles: List[Dict[str, Any]], db_manager: Any) -> Tuple[bool, str]:
        """
        Import PubMed articles into Neo4j.
        
        Args:
            articles: The articles to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            # Create nodes for articles
            for article in articles:
                # Create article node
                article_query = """
                MERGE (a:Article:PubMed {pmid: $pmid})
                SET a.title = $title,
                    a.abstract = $abstract,
                    a.source = 'PubMed'
                RETURN a
                """
                article_params = {
                    "pmid": article.get("pmid", ""),
                    "title": article.get("title", ""),
                    "abstract": article.get("abstract", "")
                }
                db_manager.execute_query(article_query, params=article_params)
                
                # Create journal node and relationship
                if "journal" in article:
                    journal_query = """
                    MERGE (j:Journal:PubMed {title: $title})
                    SET j.issn = $issn,
                        j.source = 'PubMed'
                    WITH j
                    MATCH (a:Article:PubMed {pmid: $pmid})
                    MERGE (a)-[:PUBLISHED_IN]->(j)
                    RETURN j
                    """
                    journal_params = {
                        "title": article.get("journal", {}).get("title", ""),
                        "issn": article.get("journal", {}).get("issn", ""),
                        "pmid": article.get("pmid", "")
                    }
                    db_manager.execute_query(journal_query, params=journal_params)
                
                # Create author nodes and relationships
                if "authors" in article:
                    for author in article["authors"]:
                        author_query = """
                        MERGE (au:Author:PubMed {
                            last_name: $last_name,
                            fore_name: $fore_name,
                            initials: $initials
                        })
                        SET au.source = 'PubMed'
                        WITH au
                        MATCH (a:Article:PubMed {pmid: $pmid})
                        MERGE (au)-[:AUTHORED]->(a)
                        RETURN au
                        """
                        author_params = {
                            "last_name": author.get("last_name", ""),
                            "fore_name": author.get("fore_name", ""),
                            "initials": author.get("initials", ""),
                            "pmid": article.get("pmid", "")
                        }
                        db_manager.execute_query(author_query, params=author_params)
                
                # Create keyword nodes and relationships
                if "keywords" in article:
                    for keyword in article["keywords"]:
                        keyword_query = """
                        MERGE (k:Keyword:PubMed {name: $name})
                        SET k.source = 'PubMed'
                        WITH k
                        MATCH (a:Article:PubMed {pmid: $pmid})
                        MERGE (a)-[:HAS_KEYWORD]->(k)
                        RETURN k
                        """
                        keyword_params = {
                            "name": keyword,
                            "pmid": article.get("pmid", "")
                        }
                        db_manager.execute_query(keyword_query, params=keyword_params)
                
                # Create MeSH term nodes and relationships
                if "mesh_terms" in article:
                    for term in article["mesh_terms"]:
                        term_query = """
                        MERGE (m:MeSHTerm:PubMed {name: $name})
                        SET m.source = 'PubMed'
                        WITH m
                        MATCH (a:Article:PubMed {pmid: $pmid})
                        MERGE (a)-[:HAS_MESH_TERM]->(m)
                        RETURN m
                        """
                        term_params = {
                            "name": term,
                            "pmid": article.get("pmid", "")
                        }
                        db_manager.execute_query(term_query, params=term_params)
            
            return True, f"Imported {len(articles)} articles into Neo4j"
        
        except Exception as e:
            return False, f"Error importing PubMed articles into Neo4j: {str(e)}"
    
    def search_and_import(self, query: str, db_manager: Any, max_results: int = 100) -> Tuple[bool, str]:
        """
        Search for articles in PubMed and import them into Neo4j.
        
        This is a convenience method that combines search and import_to_neo4j.
        
        Args:
            query: The search query.
            db_manager: The Neo4j database manager to use for importing.
            max_results: Maximum number of results to return.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the process was successful, False otherwise.
            - message: A message describing the result.
        """
        # Search for articles
        success, result = self.search(query, max_results)
        if not success:
            return False, result
        
        # Import the articles into Neo4j
        return self.import_to_neo4j(result, db_manager)