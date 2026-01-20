---
name: ragflow
description: RAGFlow integration toolkit for interacting with RAGFlow's RESTful API. When Claude needs to manage datasets, upload documents, perform chat completions, or work with knowledge graphs using RAGFlow's API.
license: Proprietary. LICENSE.txt has complete terms
---

# RAGFlow Integration Guide

## Overview

This guide provides comprehensive documentation for integrating with RAGFlow's RESTful API. RAGFlow is a powerful Retrieval-Augmented Generation (RAG) framework that enables you to manage datasets, upload documents, perform AI-powered chat completions, and work with knowledge graphs.

## Core Concepts

### Authentication

RAGFlow API uses API key authentication. You must include your API key in the `Authorization` header of all requests:

```bash
Authorization: Bearer <YOUR_API_KEY>
```

### API Endpoints

RAGFlow provides several key API categories:
- **OpenAI-Compatible API**: Chat completions for chats and agents
- **Dataset Management**: Create, update, delete, and list datasets
- **File Management**: Upload and manage documents within datasets
- **Knowledge Graph**: Construct and retrieve knowledge graphs

## Authentication Setup

```python
import requests

# Set up API key and base URL
API_KEY = "<YOUR_API_KEY>"
BASE_URL = "http://localhost:8000/v1"

# Create session with authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

session = requests.Session()
session.headers.update(headers)
```

## OpenAI-Compatible API

### Chat Completion

```python
def create_chat_completion(chat_id, messages, stream=False, reference=True, metadata_condition=None):
    """
    Create a chat completion using RAGFlow's OpenAI-compatible API
    """
    url = f"{BASE_URL}/chats_openai/{chat_id}/chat/completions"
    
    payload = {
        "model": "model",  # Server parses this automatically
        "messages": messages,
        "stream": stream,
        "extra_body": {
            "reference": reference,
            "metadata_condition": metadata_condition
        }
    }
    
    response = session.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Example usage
messages = [{"role": "user", "content": "Explain RAGFlow's main features"}]
result = create_chat_completion("chat_id_123", messages)
print(result["choices"][0]["message"]["content"])
```

### Agent Completion

```python
def create_agent_completion(agent_id, messages, stream=False, session_id=None):
    """
    Create an agent completion using RAGFlow's API
    """
    url = f"{BASE_URL}/agents_openai/{agent_id}/chat/completions"
    
    payload = {
        "model": "model",
        "messages": messages,
        "stream": stream
    }
    
    if session_id:
        payload["session_id"] = session_id
    
    response = session.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Example usage
messages = [{"role": "user", "content": "Help me analyze this document"}]
result = create_agent_completion("agent_id_123", messages)
print(result["choices"][0]["message"]["content"])
```

## Dataset Management

### Create Dataset

```python
def create_dataset(name, embedding_model="BAAI/bge-large-zh-v1.5@BAAI", 
                  permission="me", chunk_method="naive", parser_config=None):
    """
    Create a new dataset
    """
    url = f"{BASE_URL}/datasets"
    
    payload = {
        "name": name,
        "embedding_model": embedding_model,
        "permission": permission,
        "chunk_method": chunk_method
    }
    
    if parser_config:
        payload["parser_config"] = parser_config
    
    response = session.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Example usage with naive chunk method
parser_config = {
    "chunk_token_num": 512,
    "delimiter": "\n",
    "auto_keywords": 5,
    "auto_questions": 3
}

result = create_dataset("my_dataset", parser_config=parser_config)
dataset_id = result["data"]["id"]
print(f"Created dataset with ID: {dataset_id}")
```

### List Datasets

```python
def list_datasets(page=1, page_size=30, orderby="create_time", desc=True, name=None, id=None):
    """
    List datasets with optional filters
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
    
    url = f"{BASE_URL}/datasets"
    response = session.get(url, params=params)
    response.raise_for_status()
    
    return response.json()

# Example usage
result = list_datasets(page=1, page_size=10)
print(f"Found {result['total']} datasets")
for dataset in result['data']:
    print(f"- {dataset['name']} (ID: {dataset['id']})")
```

### Update Dataset

```python
def update_dataset(dataset_id, updates):
    """
    Update dataset configuration
    """
    url = f"{BASE_URL}/datasets/{dataset_id}"
    
    response = session.put(url, json=updates)
    response.raise_for_status()
    
    return response.json()

# Example usage
updates = {
    "name": "updated_dataset_name",
    "description": "Updated dataset description"
}

update_dataset(dataset_id, updates)
```

### Delete Datasets

```python
def delete_datasets(dataset_ids):
    """
    Delete one or more datasets
    """
    url = f"{BASE_URL}/datasets"
    
    payload = {
        "ids": dataset_ids
    }
    
    response = session.delete(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Example usage - delete a single dataset
delete_datasets([dataset_id])

# Example usage - delete multiple datasets
delete_datasets(["dataset_id_1", "dataset_id_2"])
```

## File Management

### Upload Documents

```python
def upload_documents(dataset_id, file_paths):
    """
    Upload one or more documents to a dataset
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/documents"
    
    # Create multipart form data
    files = []
    for file_path in file_paths:
        files.append(("file", (file_path.split("/")[-1], open(file_path, "rb"))))
    
    # Remove Content-Type header for multipart requests
    headers = session.headers.copy()
    if "Content-Type" in headers:
        del headers["Content-Type"]
    
    response = session.post(url, files=files, headers=headers)
    response.raise_for_status()
    
    # Close file handles
    for _, file_obj in files:
        file_obj.close()
    
    return response.json()

# Example usage
file_paths = ["./document1.txt", "./document2.pdf"]
result = upload_documents(dataset_id, file_paths)
print(f"Uploaded {len(result['data'])} documents")
```

### Update Document

```python
def update_document(dataset_id, document_id, updates):
    """
    Update document configuration
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/documents/{document_id}"
    
    response = session.put(url, json=updates)
    response.raise_for_status()
    
    return response.json()

# Example usage
updates = {
    "name": "renamed_document.txt",
    "chunk_method": "naive",
    "parser_config": {"chunk_token_num": 256}
}

update_document(dataset_id, "document_id_123", updates)
```

## Knowledge Graph Operations

### Construct Knowledge Graph

```python
def construct_knowledge_graph(dataset_id):
    """
    Construct a knowledge graph for a dataset using GraphRAG
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/run_graphrag"
    
    response = session.post(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
result = construct_knowledge_graph(dataset_id)
graphrag_task_id = result["data"]["graphrag_task_id"]
print(f"Started knowledge graph construction with task ID: {graphrag_task_id}")
```

### Get Knowledge Graph

```python
def get_knowledge_graph(dataset_id):
    """
    Retrieve the knowledge graph for a dataset
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/knowledge_graph"
    
    response = session.get(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
graph = get_knowledge_graph(dataset_id)
print(f"Knowledge graph has {len(graph['data']['graph']['nodes'])} nodes")
```

### Get Graph Construction Status

```python
def get_graphrag_status(dataset_id):
    """
    Get the status of knowledge graph construction
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/trace_graphrag"
    
    response = session.get(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
status = get_graphrag_status(dataset_id)
print(f"Graph construction progress: {status['data']['progress'] * 100}%")
print(f"Status message: {status['data']['progress_msg']}")
```

### Delete Knowledge Graph

```python
def delete_knowledge_graph(dataset_id):
    """
    Delete the knowledge graph for a dataset
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/knowledge_graph"
    
    response = session.delete(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
delete_knowledge_graph(dataset_id)
```

## RAPTOR Operations

### Construct RAPTOR

```python
def construct_raptor(dataset_id):
    """
    Construct a RAPTOR index for a dataset
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/run_raptor"
    
    response = session.post(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
result = construct_raptor(dataset_id)
raptor_task_id = result["data"]["raptor_task_id"]
print(f"Started RAPTOR construction with task ID: {raptor_task_id}")
```

### Get RAPTOR Status

```python
def get_raptor_status(dataset_id):
    """
    Get the status of RAPTOR construction
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/trace_raptor"
    
    response = session.get(url)
    response.raise_for_status()
    
    return response.json()

# Example usage
status = get_raptor_status(dataset_id)
print(f"RAPTOR construction progress: {status['data']['progress'] * 100}%")
print(f"Status message: {status['data']['progress_msg']}")
```

## Error Handling

```python
def handle_ragflow_error(response):
    """
    Handle RAGFlow API errors
    """
    try:
        error_data = response.json()
        error_code = error_data.get("code")
        error_message = error_data.get("message", "Unknown error")
        return f"RAGFlow Error {error_code}: {error_message}"
    except:
        return f"HTTP Error {response.status_code}: {response.text}"

# Example usage
try:
    result = create_dataset("existing_dataset")
except requests.exceptions.HTTPError as e:
    error_msg = handle_ragflow_error(e.response)
    print(f"Failed to create dataset: {error_msg}")
```

## Best Practices

### Chunk Methods

RAGFlow supports various chunk methods for different content types:

| Method | Use Case |
|--------|----------|
| naive | General content (default) |
| book | Book content with chapters |
| email | Email content |
| laws | Legal documents |
| manual | Manual content |
| paper | Research papers |
| presentation | PowerPoint presentations |
| qa | Question-answer pairs |
| table | Tabular data |
| tag | Content with tags |

### Parser Configuration

When using the naive chunk method, you can configure:
- `chunk_token_num`: Token count per chunk (default: 512)
- `delimiter`: Delimiter for splitting text
- `auto_keywords`: Number of auto-generated keywords (0-32)
- `auto_questions`: Number of auto-generated questions (0-10)
- `layout_recognize`: Whether to use layout recognition for PDFs

### Performance Considerations

1. **Batch Operations**: When uploading multiple documents, upload them in batches
2. **Chunk Size**: Adjust chunk size based on your model's context window
3. **Metadata**: Use metadata conditions to filter retrieval results
4. **Streaming**: Use streaming for long responses to improve user experience
5. **Caching**: Cache frequently accessed results to reduce API calls

## API Reference

### Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid API key |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |
| 1001 | Invalid Chunk ID | Invalid chunk identifier |
| 1002 | Chunk Update Failed | Failed to update chunk |

### Common Request Headers

```bash
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

### Common Response Format

```json
{
  "code": 0,
  "data": { /* response data */ },
  "message": "success"
}
```

## Troubleshooting

### Connection Issues

- **Error 10061**: Check if RAGFlow service is running
- **Error 401**: Verify API key is correct
- **Error 403**: Ensure you have permission to access the resource
- **Error 404**: Check if dataset/document ID is valid

### Performance Issues

- For large datasets, increase page size in list operations
- Reduce chunk token size for faster processing
- Use smaller batch sizes when uploading documents

### Knowledge Graph Issues

- Ensure dataset has documents before constructing knowledge graph
- Check GraphRAG task status for detailed progress
- Verify dataset has sufficient content for meaningful graph construction

## Next Steps

1. **API Key**: Obtain your RAGFlow API key from the RAGFlow UI
2. **Service Setup**: Ensure RAGFlow service is running and accessible
3. **Start Small**: Begin with simple operations like listing datasets
4. **Experiment**: Try different chunk methods and parser configurations
5. **Build Workflows**: Create end-to-end workflows for your use cases
