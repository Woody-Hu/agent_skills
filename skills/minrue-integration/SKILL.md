---
name: minrue-integration
description: Integration with MinRUE backend (running via vLLM) for file processing and result retrieval. When Claude needs to send files to a local MinRUE backend for AI-powered processing and return the results.
license: Proprietary. LICENSE.txt has complete terms
---

# MinRUE Integration Guide

## Overview

This guide provides best practices for integrating with a local MinRUE backend running via vLLM. The minrue-integration skill enables you to send files to the MinRUE API, process them using AI models, and retrieve the results efficiently.

## Core Concepts

### MinRUE Backend

- **Local Deployment**: MinRUE runs as a local service using vLLM for model serving
- **API Endpoints**: RESTful API for file uploads, model inference, and result retrieval
- **Model Support**: Compatible with various LLM models deployed via vLLM
- **File Processing**: Handles text, documents, and structured data for AI analysis

### Workflow Components

1. **File Preparation**: Format and validate files before sending
2. **API Communication**: Send requests to MinRUE endpoints
3. **Model Inference**: Process files using configured AI models
4. **Result Handling**: Retrieve, parse, and present results
5. **Error Management**: Handle API errors and retries appropriately

## Usage Workflow

### Step 1: Verify MinRUE Service Status

```bash
# Check if MinRUE service is running
curl -X GET http://localhost:8000/v1/health

# Expected response:
# {"status": "ok", "models": ["model-name-1", "model-name-2"]}
```

### Step 2: Prepare Files for Processing

```python
# Example: Prepare text file for processing
import json
import os

# Read and validate file content
def prepare_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Validate content length (adjust based on model limits)
    if len(content) > 100000:
        raise ValueError("File content exceeds maximum length")
    
    return content

# Example usage
try:
    file_content = prepare_file("document.txt")
    print(f"Prepared file with {len(file_content)} characters")
except Exception as e:
    print(f"Error preparing file: {e}")
```

### Step 3: Send File to MinRUE API

```python
import requests
import json

# Configuration
MINRUE_URL = "http://localhost:8000/v1/process"
MODEL_NAME = "your-model-name"

# Send file for processing
def send_to_minrue(file_path, task_type="text-refinement"):
    # Prepare file
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
    
    # Request parameters
    data = {
        'model': MODEL_NAME,
        'task': task_type,
        'parameters': json.dumps({
            'temperature': 0.7,
            'max_tokens': 2000
        })
    }
    
    try:
        response = requests.post(MINRUE_URL, files=files, data=data, timeout=30)
        response.raise_for_status()  # Raise error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        raise

# Example usage
try:
    result = send_to_minrue("document.txt", task_type="text-refinement")
    print(f"Processing started with job ID: {result['job_id']}")
except Exception as e:
    print(f"Error sending file: {e}")
```

### Step 4: Retrieve Processing Results

```python
import requests
import time

# Configuration
MINRUE_RESULT_URL = "http://localhost:8000/v1/results"

# Retrieve processing results
def get_results(job_id, timeout=60, polling_interval=5):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{MINRUE_RESULT_URL}/{job_id}")
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'completed':
                return result['output']
            elif result['status'] == 'failed':
                raise Exception(f"Processing failed: {result['error']}")
            
            # Wait before polling again
            time.sleep(polling_interval)
            
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving results: {e}")
            time.sleep(polling_interval)
    
    raise TimeoutError("Result retrieval timed out")

# Example usage
try:
    # Assuming we have a job_id from the previous step
    job_id = "previous-job-id-123"
    results = get_results(job_id)
    print(f"Processing completed successfully")
    print(f"Results: {results[:500]}...")  # Show first 500 characters
except Exception as e:
    print(f"Error getting results: {e}")
```

### Step 5: Save and Present Results

```python
# Save results to file
def save_results(results, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to: {output_path}")

# Example usage
try:
    save_results(results, "processed_results.json")
    
    # If results contain text content, save as text file
    if isinstance(results, str):
        with open("processed_text.txt", 'w', encoding='utf-8') as f:
            f.write(results)
        print(f"Text results saved to: processed_text.txt")
        
except Exception as e:
    print(f"Error saving results: {e}")
```

## Detailed Examples

### Example 1: Text Refinement Workflow

```python
import os
import requests
import time

# Configuration
MINRUE_URL = "http://localhost:8000/v1/process"
MINRUE_RESULT_URL = "http://localhost:8000/v1/results"
MODEL_NAME = "mistral-7b-instruct"

# Complete workflow function
def process_text_file(file_path, output_path, task_type="text-refinement", timeout=120):
    """Process a text file using MinRUE backend and save results"""
    
    # 1. Prepare file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    # 2. Send to MinRUE
    print(f"Sending file to MinRUE: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
    
    data = {
        'model': MODEL_NAME,
        'task': task_type,
        'parameters': '{}'
    }
    
    response = requests.post(MINRUE_URL, files=files, data=data, timeout=30)
    response.raise_for_status()
    job_info = response.json()
    job_id = job_info['job_id']
    print(f"Processing started with job ID: {job_id}")
    
    # 3. Wait for results
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(3)
        
        try:
            result_response = requests.get(f"{MINRUE_RESULT_URL}/{job_id}")
            result_response.raise_for_status()
            result = result_response.json()
            
            if result['status'] == 'completed':
                # 4. Save results
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['output'])
                print(f"Processing completed. Results saved to: {output_path}")
                return True
            elif result['status'] == 'failed':
                raise Exception(f"Processing failed: {result['error']}")
                
        except requests.exceptions.RequestException as e:
            print(f"Polling error: {e}")
            time.sleep(2)
    
    raise TimeoutError("Processing timed out")

# Example usage
try:
    process_text_file(
        file_path="draft_article.txt",
        output_path="refined_article.txt",
        task_type="text-refinement"
    )
except Exception as e:
    print(f"Workflow failed: {e}")
```

### Example 2: Batch Processing

```python
import os
import concurrent.futures

# Batch process multiple files
def batch_process(files, output_dir, max_workers=3):
    """Process multiple files concurrently"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        
        # Submit all files for processing
        for file_path in files:
            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"processed_{filename}")
            future = executor.submit(
                process_text_file, 
                file_path=file_path, 
                output_path=output_path
            )
            future_to_file[future] = (file_path, output_path)
        
        # Collect results
        for future in concurrent.futures.as_completed(future_to_file):
            file_path, output_path = future_to_file[future]
            try:
                success = future.result()
                results[file_path] = {
                    'success': success,
                    'output_path': output_path
                }
            except Exception as e:
                results[file_path] = {
                    'success': False,
                    'error': str(e)
                }
    
    return results

# Example usage
try:
    input_files = [
        "file1.txt",
        "file2.txt", 
        "file3.txt"
    ]
    
    batch_results = batch_process(
        files=input_files,
        output_dir="processed_results",
        max_workers=2
    )
    
    # Print summary
    print("\nBatch Processing Summary:")
    for file_path, result in batch_results.items():
        status = "SUCCESS" if result['success'] else "FAILED"
        print(f"{file_path}: {status}")
        if not result['success']:
            print(f"  Error: {result['error']}")
            
except Exception as e:
    print(f"Batch processing failed: {e}")
```

## Best Practices

### API Communication

1. **Timeout Settings**: Configure appropriate timeouts for API requests
2. **Error Handling**: Implement retry logic for transient errors
3. **Rate Limiting**: Respect API rate limits to avoid service disruption
4. **Authentication**: Use API keys if authentication is enabled
5. **SSL/TLS**: Use HTTPS for secure communication in production

### File Management

1. **Validation**: Check file size, format, and content before sending
2. **Compression**: Compress large files to reduce transfer time
3. **Encoding**: Ensure proper UTF-8 encoding for text files
4. **Metadata**: Include relevant metadata with file uploads
5. **Cleanup**: Remove temporary files after processing

### Performance Optimization

1. **Batch Processing**: Process multiple files concurrently when appropriate
2. **Connection Pooling**: Reuse HTTP connections for multiple requests
3. **Streaming**: Use streaming for very large files to reduce memory usage
4. **Caching**: Cache results for repeated requests with identical inputs
5. **Model Selection**: Choose appropriate models based on task requirements

### Error Management

```python
# Robust error handling example
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure session with retry logic
def create_session():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Usage
session = create_session()
try:
    response = session.get("http://localhost:8000/v1/health", timeout=10)
    response.raise_for_status()
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.ConnectionError as conn_err:
    print(f"Connection error occurred: {conn_err}")
except requests.exceptions.Timeout as timeout_err:
    print(f"Timeout error occurred: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"An error occurred: {req_err}")
```

## Technical Details

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Check service status and available models |
| `/v1/process` | POST | Upload file and start processing |
| `/v1/results/{job_id}` | GET | Retrieve results for a specific job |
| `/v1/models` | GET | List available models |
| `/v1/tasks` | GET | List supported task types |

### Request Formats

#### File Processing Request
```http
POST /v1/process HTTP/1.1
Content-Type: multipart/form-data;

model=mistral-7b-instruct
&task=text-refinement
&parameters={"temperature": 0.7, "max_tokens": 2000}
&file=@document.txt
```

#### Result Retrieval Response
```json
{
  "job_id": "job-1234567890",
  "status": "completed",
  "output": "Refined text content...",
  "processing_time": 4.5,
  "model_used": "mistral-7b-instruct"
}
```

### Supported File Types

- **Text**: .txt, .md, .rst, .adoc
- **Documents**: .docx, .pdf (text extraction)
- **Structured Data**: .json, .csv, .yaml
- **Code**: .py, .js, .java, .cpp, .html, .css

## Troubleshooting

### Common Issues

1. **Service Not Found**
   ```
   Error: Connection refused
   ```
   - Verify MinRUE service is running
   - Check correct port number (default: 8000)
   - Ensure firewall allows connections to the port

2. **File Too Large**
   ```
   Error: 413 Payload Too Large
   ```
   - Check file size limits in MinRUE configuration
   - Compress large files if supported
   - Split very large files into smaller chunks

3. **Model Not Found**
   ```
   Error: Model 'unknown-model' not found
   ```
   - Check available models with `/v1/models` endpoint
   - Ensure correct model name in request
   - Verify model is properly deployed in vLLM

4. **Processing Timeout**
   ```
   Error: Request timed out
   ```
   - Increase timeout settings in client code
   - Check server load and resource availability
   - For large files, consider longer polling intervals

### Debugging Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Server Logs**
   ```bash
   # View MinRUE server logs
   tail -f minrue_server.log
   ```

3. **Test API with curl**
   ```bash
   # Test file upload
   curl -X POST http://localhost:8000/v1/process \
        -F "model=mistral-7b-instruct" \
        -F "task=text-refinement" \
        -F "file=@test.txt"
   ```

## Security Considerations

1. **Local Access Only**: Restrict MinRUE API access to localhost in development
2. **Authentication**: Enable API key authentication in production environments
3. **Input Validation**: Sanitize all inputs to prevent injection attacks
4. **Data Privacy**: Avoid sending sensitive data unless encryption is enabled
5. **Resource Limits**: Set resource limits to prevent DoS attacks

## Next Steps

1. **Verify Installation**: Ensure MinRUE backend is properly installed and running
2. **Test API**: Validate API endpoints using simple curl commands
3. **Implement Client**: Use the examples in this guide to create integration code
4. **Optimize**: Adjust parameters based on performance testing
5. **Monitor**: Set up monitoring for API performance and error rates
