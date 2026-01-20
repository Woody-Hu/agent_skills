#!/usr/bin/env python3
"""
RAGFlow Client - A comprehensive client for interacting with RAGFlow's RESTful API

This script provides a full-featured Python API and command-line interface for:
1. Chat completions (OpenAI-compatible)
2. Dataset management
3. Document upload and management
4. Knowledge graph operations
5. RAPTOR index management

Usage:
    python ragflow_client.py --help
    python ragflow_client.py chat --chat-id chat123 --message "Hello"
    python ragflow_client.py dataset create --name my_dataset
    python ragflow_client.py document upload --dataset-id ds123 --file document.txt
"""

import argparse
import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RagflowClient:
    """Comprehensive client for RAGFlow API interactions"""
    
    def __init__(self, api_key, base_url="http://localhost:8000/v1", timeout=30, retries=3):
        """
        Initialize RagflowClient
        
        Args:
            api_key (str): RAGFlow API key for authentication
            base_url (str): Base URL of RAGFlow API
            timeout (int): Request timeout in seconds
            retries (int): Number of retry attempts for transient errors
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session(retries)
    
    def _create_session(self, retries):
        """Create HTTP session with retry logic"""
        session = requests.Session()
        
        # Set default headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        session.headers.update(headers)
        
        # Configure retry strategy
        try:
            # For urllib3 v2.0+
            retry_strategy = Retry(
                total=retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
            )
        except TypeError:
            # For urllib3 v1.x
            retry_strategy = Retry(
                total=retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    # ==============================
    # OpenAI-Compatible API
    # ==============================
    
    def create_chat_completion(self, chat_id, messages, stream=False, reference=True, metadata_condition=None):
        """
        Create a chat completion using RAGFlow's OpenAI-compatible API
        
        Args:
            chat_id (str): Chat ID
            messages (list): List of message objects [{'role': 'user', 'content': 'message'}]
            stream (bool): Whether to use streaming response
            reference (bool): Include references in response
            metadata_condition (dict): Metadata filter conditions
            
        Returns:
            dict: Chat completion response
        """
        url = f"{self.base_url}/chats_openai/{chat_id}/chat/completions"
        
        payload = {
            "model": "model",  # Server parses this automatically
            "messages": messages,
            "stream": stream,
            "extra_body": {
                "reference": reference,
                "metadata_condition": metadata_condition
            }
        }
        
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def create_agent_completion(self, agent_id, messages, stream=False, session_id=None):
        """
        Create an agent completion using RAGFlow's API
        
        Args:
            agent_id (str): Agent ID
            messages (list): List of message objects [{'role': 'user', 'content': 'message'}]
            stream (bool): Whether to use streaming response
            session_id (str): Agent session ID
            
        Returns:
            dict: Agent completion response
        """
        url = f"{self.base_url}/agents_openai/{agent_id}/chat/completions"
        
        payload = {
            "model": "model",
            "messages": messages,
            "stream": stream
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    # ==============================
    # Dataset Management
    # ==============================
    
    def create_dataset(self, name, embedding_model="BAAI/bge-large-zh-v1.5@BAAI", 
                      permission="me", chunk_method="naive", parser_config=None):
        """
        Create a new dataset
        
        Args:
            name (str): Dataset name
            embedding_model (str): Embedding model to use
            permission (str): Permission level ("me" or "team")
            chunk_method (str): Chunk method for document processing
            parser_config (dict): Parser configuration
            
        Returns:
            dict: Created dataset information
        """
        url = f"{self.base_url}/datasets"
        
        payload = {
            "name": name,
            "embedding_model": embedding_model,
            "permission": permission,
            "chunk_method": chunk_method
        }
        
        if parser_config:
            payload["parser_config"] = parser_config
        
        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def list_datasets(self, page=1, page_size=30, orderby="create_time", desc=True, name=None, id=None):
        """
        List datasets with optional filters
        
        Args:
            page (int): Page number
            page_size (int): Items per page
            orderby (str): Field to order by
            desc (bool): Whether to sort descending
            name (str): Filter by name
            id (str): Filter by ID
            
        Returns:
            dict: List of datasets
        """
        params = {
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc
        }
        
        if name:
            params["name"] = name
        if id:
            params["id"] = id
        
        url = f"{self.base_url}/datasets"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def update_dataset(self, dataset_id, updates):
        """
        Update dataset configuration
        
        Args:
            dataset_id (str): Dataset ID
            updates (dict): Fields to update
            
        Returns:
            dict: Update response
        """
        url = f"{self.base_url}/datasets/{dataset_id}"
        
        response = self.session.put(url, json=updates, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def delete_datasets(self, dataset_ids):
        """
        Delete one or more datasets
        
        Args:
            dataset_ids (list): List of dataset IDs
            
        Returns:
            dict: Delete response
        """
        url = f"{self.base_url}/datasets"
        
        payload = {
            "ids": dataset_ids
        }
        
        response = self.session.delete(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    # ==============================
    # Document Management
    # ==============================
    
    def upload_documents(self, dataset_id, file_paths):
        """
        Upload one or more documents to a dataset
        
        Args:
            dataset_id (str): Dataset ID
            file_paths (list): List of file paths to upload
            
        Returns:
            dict: Upload response
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents"
        
        # Create multipart form data
        files = []
        for file_path in file_paths:
            files.append(("file", (os.path.basename(file_path), open(file_path, "rb"))))
        
        # Remove Content-Type header for multipart requests
        headers = self.session.headers.copy()
        if "Content-Type" in headers:
            del headers["Content-Type"]
        
        response = self.session.post(url, files=files, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        # Close file handles
        for _, file_obj in files:
            file_obj.close()
        
        return response.json()
    
    def update_document(self, dataset_id, document_id, updates):
        """
        Update document configuration
        
        Args:
            dataset_id (str): Dataset ID
            document_id (str): Document ID
            updates (dict): Fields to update
            
        Returns:
            dict: Update response
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}"
        
        response = self.session.put(url, json=updates, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    # ==============================
    # Knowledge Graph Operations
    # ==============================
    
    def construct_knowledge_graph(self, dataset_id):
        """
        Construct a knowledge graph for a dataset
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Graph construction response
        """
        url = f"{self.base_url}/datasets/{dataset_id}/run_graphrag"
        
        response = self.session.post(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def get_knowledge_graph(self, dataset_id):
        """
        Retrieve the knowledge graph for a dataset
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Knowledge graph data
        """
        url = f"{self.base_url}/datasets/{dataset_id}/knowledge_graph"
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def get_graphrag_status(self, dataset_id):
        """
        Get the status of knowledge graph construction
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Construction status
        """
        url = f"{self.base_url}/datasets/{dataset_id}/trace_graphrag"
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def delete_knowledge_graph(self, dataset_id):
        """
        Delete the knowledge graph for a dataset
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Delete response
        """
        url = f"{self.base_url}/datasets/{dataset_id}/knowledge_graph"
        
        response = self.session.delete(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    # ==============================
    # RAPTOR Operations
    # ==============================
    
    def construct_raptor(self, dataset_id):
        """
        Construct a RAPTOR index for a dataset
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: RAPTOR construction response
        """
        url = f"{self.base_url}/datasets/{dataset_id}/run_raptor"
        
        response = self.session.post(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def get_raptor_status(self, dataset_id):
        """
        Get the status of RAPTOR construction
        
        Args:
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Construction status
        """
        url = f"{self.base_url}/datasets/{dataset_id}/trace_raptor"
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()


class RagflowCLI:
    """Command-line interface for RagflowClient"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="RAGFlow Client for API interactions")
        self._setup_parser()
    
    def _setup_parser(self):
        """Set up command-line argument parser"""
        # API key and base URL
        self.parser.add_argument('--api-key', '-k', required=True, help='RAGFlow API key')
        self.parser.add_argument('--base-url', '-u', default='http://localhost:8000/v1', help='RAGFlow API base URL')
        
        # Subparsers for different commands
        subparsers = self.parser.add_subparsers(dest='command', help='Command to execute')
        subparsers.required = True
        
        # Chat commands
        chat_parser = subparsers.add_parser('chat', help='Chat completion operations')
        chat_subparsers = chat_parser.add_subparsers(dest='chat_cmd')
        chat_subparsers.required = True
        
        chat_completion_parser = chat_subparsers.add_parser('completion', help='Create chat completion')
        chat_completion_parser.add_argument('--chat-id', required=True, help='Chat ID')
        chat_completion_parser.add_argument('--message', required=True, help='Chat message')
        chat_completion_parser.add_argument('--stream', action='store_true', help='Use streaming response')
        chat_completion_parser.add_argument('--no-reference', action='store_true', help='Do not include references')
        
        # Dataset commands
        dataset_parser = subparsers.add_parser('dataset', help='Dataset management operations')
        dataset_subparsers = dataset_parser.add_subparsers(dest='dataset_cmd')
        dataset_subparsers.required = True
        
        dataset_create_parser = dataset_subparsers.add_parser('create', help='Create dataset')
        dataset_create_parser.add_argument('--name', required=True, help='Dataset name')
        dataset_create_parser.add_argument('--embedding-model', default='BAAI/bge-large-zh-v1.5@BAAI', help='Embedding model')
        
        dataset_list_parser = dataset_subparsers.add_parser('list', help='List datasets')
        dataset_list_parser.add_argument('--page', type=int, default=1, help='Page number')
        dataset_list_parser.add_argument('--page-size', type=int, default=10, help='Items per page')
        
        dataset_delete_parser = dataset_subparsers.add_parser('delete', help='Delete datasets')
        dataset_delete_parser.add_argument('--ids', nargs='+', required=True, help='Dataset IDs to delete')
        
        # Document commands
        document_parser = subparsers.add_parser('document', help='Document management operations')
        document_subparsers = document_parser.add_subparsers(dest='document_cmd')
        document_subparsers.required = True
        
        document_upload_parser = document_subparsers.add_parser('upload', help='Upload documents')
        document_upload_parser.add_argument('--dataset-id', required=True, help='Dataset ID')
        document_upload_parser.add_argument('--file', nargs='+', required=True, help='Files to upload')
    
    def run(self, args=None):
        """Run the CLI"""
        args = self.parser.parse_args(args)
        
        # Create client instance
        client = RagflowClient(args.api_key, args.base_url)
        
        # Execute command
        if args.command == 'chat':
            if args.chat_cmd == 'completion':
                messages = [{"role": "user", "content": args.message}]
                reference = not args.no_reference
                result = client.create_chat_completion(args.chat_id, messages, args.stream, reference)
                if args.stream:
                    print("Streaming response...")
                    print(result)
                else:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'dataset':
            if args.dataset_cmd == 'create':
                result = client.create_dataset(args.name, args.embedding_model)
                print(f"Created dataset: {result['data']['name']} (ID: {result['data']['id']})")
            elif args.dataset_cmd == 'list':
                result = client.list_datasets(args.page, args.page_size)
                print(f"Found {result['total']} datasets:")
                for dataset in result['data']:
                    print(f"- {dataset['name']} (ID: {dataset['id']}) - {dataset['document_count']} documents")
            elif args.dataset_cmd == 'delete':
                client.delete_datasets(args.ids)
                print(f"Deleted {len(args.ids)} datasets")
        
        elif args.command == 'document':
            if args.document_cmd == 'upload':
                result = client.upload_documents(args.dataset_id, args.file)
                print(f"Uploaded {len(result['data'])} documents")
                for doc in result['data']:
                    print(f"- {doc['name']} (ID: {doc['id']})")
        
        return 0


def handle_ragflow_error(response):
    """
    Handle RAGFlow API errors
    
    Args:
        response (requests.Response): Response object that caused the error
        
    Returns:
        str: Formatted error message
    """
    try:
        error_data = response.json()
        error_code = error_data.get("code")
        error_message = error_data.get("message", "Unknown error")
        return f"RAGFlow Error {error_code}: {error_message}"
    except:
        return f"HTTP Error {response.status_code}: {response.text}"


if __name__ == "__main__":
    try:
        cli = RagflowCLI()
        exit(cli.run())
    except requests.exceptions.HTTPError as e:
        error_msg = handle_ragflow_error(e.response)
        print(f"Error: {error_msg}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
