#!/usr/bin/env python3
"""
MinRUE Client - A simple client for interacting with MinRUE backend via API

This script provides a command-line interface and Python API for:
1. Checking service status
2. Uploading files for processing
3. Retrieving processing results
4. Listing available models
5. Listing supported tasks

Usage:
    python minrue_client.py health
    python minrue_client.py models
    python minrue_client.py tasks
    python minrue_client.py process document.txt --output refined.txt --model mistral-7b-instruct --task text-refinement
    python minrue_client.py result job-1234567890 --output result.txt
"""

import argparse
import json
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MinRueClient:
    """Client for interacting with MinRUE backend API"""
    
    def __init__(self, base_url="http://localhost:8000/v1", timeout=30, retries=3):
        """
        Initialize MinRueClient
        
        Args:
            base_url (str): Base URL of MinRUE API
            timeout (int): Request timeout in seconds
            retries (int): Number of retry attempts for transient errors
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session(retries)
    
    def _create_session(self, retries):
        """Create HTTP session with retry logic"""
        session = requests.Session()
        
        # Handle both old and new urllib3 versions
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
    
    def get_health(self):
        """Check service health status"""
        url = f"{self.base_url}/health"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def list_models(self):
        """List available models"""
        url = f"{self.base_url}/models"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self):
        """List supported task types"""
        url = f"{self.base_url}/tasks"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def process_file(self, file_path, model="mistral-7b-instruct", task="text-refinement", parameters=None):
        """
        Upload file for processing
        
        Args:
            file_path (str): Path to file to process
            model (str): Model to use for processing
            task (str): Task type
            parameters (dict): Additional parameters for processing
            
        Returns:
            dict: Job information including job_id
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        url = f"{self.base_url}/process"
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
        
        data = {
            'model': model,
            'task': task,
            'parameters': json.dumps(parameters or {})
        }
        
        response = self.session.post(url, files=files, data=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_result(self, job_id, wait=False, timeout=60, polling_interval=5):
        """
        Get result for a specific job
        
        Args:
            job_id (str): Job ID to retrieve results for
            wait (bool): Whether to wait for processing to complete
            timeout (int): Maximum wait time in seconds
            polling_interval (int): Polling interval in seconds
            
        Returns:
            dict: Result information
        """
        url = f"{self.base_url}/results/{job_id}"
        
        start_time = time.time()
        
        while True:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'completed' or result['status'] == 'failed' or not wait:
                return result
            
            if time.time() - start_time > timeout:
                raise TimeoutError("Result retrieval timed out")
            
            time.sleep(polling_interval)


class MinRueCLI:
    """Command-line interface for MinRUE client"""
    
    def __init__(self):
        self.client = MinRueClient()
    
    def health(self):
        """Handle health command"""
        try:
            health = self.client.get_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def models(self):
        """Handle models command"""
        try:
            models = self.client.list_models()
            print(json.dumps(models, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def tasks(self):
        """Handle tasks command"""
        try:
            tasks = self.client.list_tasks()
            print(json.dumps(tasks, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def process(self, file_path, output_path=None, model="mistral-7b-instruct", task="text-refinement", parameters=None):
        """Handle process command"""
        try:
            print(f"Processing file: {file_path}")
            job_info = self.client.process_file(file_path, model, task, parameters)
            job_id = job_info['job_id']
            print(f"Processing started with job ID: {job_id}")
            
            if output_path:
                print(f"Waiting for results...")
                result = self.client.get_result(job_id, wait=True, timeout=120, polling_interval=3)
                
                if result['status'] == 'completed':
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result['output'])
                    print(f"Processing completed. Results saved to: {output_path}")
                    return 0
                else:
                    print(f"Processing failed: {result['error']}")
                    return 1
            else:
                print(f"To check results later: python minrue_client.py result {job_id}")
                return 0
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def result(self, job_id, output_path=None):
        """Handle result command"""
        try:
            print(f"Retrieving results for job ID: {job_id}")
            result = self.client.get_result(job_id, wait=True, timeout=60, polling_interval=3)
            
            if result['status'] == 'completed':
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result['output'])
                    print(f"Results saved to: {output_path}")
                else:
                    print("\n" + result['output'])
                return 0
            else:
                print(f"Processing failed: {result['error']}")
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main entry point for command-line interface"""
    parser = argparse.ArgumentParser(description="MinRUE Client for interacting with MinRUE backend")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health status")
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    
    # Tasks command
    tasks_parser = subparsers.add_parser("tasks", help="List supported task types")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Upload file for processing")
    process_parser.add_argument("file_path", help="Path to file to process")
    process_parser.add_argument("--output", "-o", help="Path to save results")
    process_parser.add_argument("--model", "-m", default="mistral-7b-instruct", help="Model to use")
    process_parser.add_argument("--task", "-t", default="text-refinement", help="Task type")
    process_parser.add_argument("--temperature", type=float, help="Temperature parameter")
    process_parser.add_argument("--max-tokens", type=int, help="Maximum tokens parameter")
    
    # Result command
    result_parser = subparsers.add_parser("result", help="Retrieve results for a job")
    result_parser.add_argument("job_id", help="Job ID to retrieve results for")
    result_parser.add_argument("--output", "-o", help="Path to save results")
    
    args = parser.parse_args()
    
    cli = MinRueCLI()
    
    # Handle parameters for process command
    parameters = {}
    if args.command == "process":
        if args.temperature is not None:
            parameters['temperature'] = args.temperature
        if args.max_tokens is not None:
            parameters['max_tokens'] = args.max_tokens
    
    # Execute command
    if args.command == "health":
        exit_code = cli.health()
    elif args.command == "models":
        exit_code = cli.models()
    elif args.command == "tasks":
        exit_code = cli.tasks()
    elif args.command == "process":
        exit_code = cli.process(args.file_path, args.output, args.model, args.task, parameters)
    elif args.command == "result":
        exit_code = cli.result(args.job_id, args.output)
    else:
        print(f"Unknown command: {args.command}")
        exit_code = 1
    
    exit(exit_code)


if __name__ == "__main__":
    main()
