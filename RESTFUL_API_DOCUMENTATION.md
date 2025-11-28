# IOPaint REST API Documentation

Official REST API documentation for IOPaint Watermark Removal Service.

**Version:** v1
**Base URL:** `https://api.iopaint.com` (production) or `http://localhost:8080` (development)
**Protocol:** HTTPS (production), HTTP (development)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Models](#models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Best Practices](#best-practices)
8. [SDKs & Libraries](#sdks--libraries)
9. [Changelog](#changelog)

---

## Introduction

The IOPaint API provides AI-powered watermark removal capabilities through a simple REST API. Built on the LaMa (Large Mask Inpainting) model, it offers fast and high-quality image restoration.

### Key Features

- **Fast Processing**: 1-2 seconds for 1024x1024 images
- **High Quality**: State-of-the-art AI model
- **Simple Integration**: Standard REST API with multipart/form-data
- **Flexible**: Optional mask support for precise control
- **Scalable**: From hobby projects to enterprise deployments

### API Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| Watermark Removal | ✅ Available | Remove watermarks from images |
| Auto Detection | ⏳ Coming Soon | Automatic watermark detection |
| Batch Processing | ⏳ Coming Soon | Process multiple images at once |
| Webhook Callbacks | ⏳ Coming Soon | Async processing with callbacks |

---

## Authentication

The IOPaint API uses API keys for authentication. All requests must include your API key in the request header.

### Obtaining an API Key

1. Sign up at [https://iopaint.com/signup](https://iopaint.com/signup)
2. Navigate to your [Dashboard](https://iopaint.com/dashboard)
3. Generate a new API key
4. Store it securely (keys cannot be recovered)

### Using Your API Key

Include your API key in the `X-API-Key` header with every request:

```http
X-API-Key: your_api_key_here
```

### Security Best Practices

- ⚠️ **Never expose your API key in client-side code**
- ✅ Store keys in environment variables
- ✅ Rotate keys periodically
- ✅ Use different keys for development and production
- ✅ Revoke compromised keys immediately

### Example

```bash
# ✅ Correct
curl https://api.iopaint.com/api/v1/health \
  -H "X-API-Key: $IOPAINT_API_KEY"

# ❌ Incorrect (hardcoded key)
curl https://api.iopaint.com/api/v1/health \
  -H "X-API-Key: sk_live_1234567890abcdef"
```

---

## API Endpoints

### Base URL

```
Production: https://api.iopaint.com
Development: http://localhost:8080
```

### Endpoint Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/remove-watermark` | POST | Remove watermark from image |
| `/api/v1/health` | GET | Service health check |
| `/api/v1/stats` | GET | Account usage statistics |

---

## 1. Remove Watermark

Remove watermarks or unwanted objects from images using AI.

### Endpoint

```http
POST /api/v1/remove-watermark
```

### Authentication

Required. Include `X-API-Key` header.

### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `X-API-Key` | string | Yes | Your API key |
| `Content-Type` | string | Yes | Must be `multipart/form-data` |

### Request Body

Submit as `multipart/form-data`:

| Field | Type | Required | Max Size | Description |
|-------|------|----------|----------|-------------|
| `image` | file | Yes | 10 MB | Image to process (JPEG, PNG, WebP) |
| `mask` | file | No | 10 MB | Optional mask (white = remove, black = keep) |

### Image Requirements

- **Formats**: JPEG, PNG, WebP
- **Max Dimension**: 4096px (width or height)
- **Max File Size**: 10 MB
- **Color Mode**: RGB (grayscale will be converted)

### Mask Requirements

- **Format**: PNG (8-bit grayscale or RGB)
- **Dimension**: Must match image size (auto-resized if different)
- **White (255)**: Areas to remove/inpaint
- **Black (0)**: Areas to preserve
- **Gray**: Partial inpainting (blend)

### Response

**Success (200 OK)**

Returns the processed image as `image/png`.

**Response Headers:**

| Header | Type | Description |
|--------|------|-------------|
| `Content-Type` | string | `image/png` |
| `X-Processing-Time` | float | Processing time in seconds |
| `X-Image-Size` | string | Original image dimensions (e.g., "1024x768") |

### Examples

#### cURL

```bash
# Basic usage (no mask)
curl -X POST https://api.iopaint.com/api/v1/remove-watermark \
  -H "X-API-Key: $IOPAINT_API_KEY" \
  -F "image=@/path/to/image.jpg" \
  -o result.png

# With mask
curl -X POST https://api.iopaint.com/api/v1/remove-watermark \
  -H "X-API-Key: $IOPAINT_API_KEY" \
  -F "image=@/path/to/image.jpg" \
  -F "mask=@/path/to/mask.png" \
  -o result.png

# Verbose output
curl -X POST https://api.iopaint.com/api/v1/remove-watermark \
  -H "X-API-Key: $IOPAINT_API_KEY" \
  -F "image=@image.jpg" \
  -v \
  -o result.png
```

#### Python

```python
import requests

url = "https://api.iopaint.com/api/v1/remove-watermark"
headers = {"X-API-Key": "your_api_key_here"}

# Basic usage
with open("image.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, headers=headers, files=files)

if response.status_code == 200:
    with open("result.png", "wb") as f:
        f.write(response.content)
    print(f"✓ Success! Processing time: {response.headers['X-Processing-Time']}s")
else:
    print(f"✗ Error {response.status_code}: {response.json()}")
```

#### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('image', fs.createReadStream('image.jpg'));

axios.post('https://api.iopaint.com/api/v1/remove-watermark', form, {
    headers: {
        'X-API-Key': process.env.IOPAINT_API_KEY,
        ...form.getHeaders()
    },
    responseType: 'arraybuffer'
})
.then(response => {
    fs.writeFileSync('result.png', response.data);
    console.log('✓ Success!');
})
.catch(error => {
    console.error('✗ Error:', error.response?.status, error.response?.data);
});
```

#### PHP

```php
<?php
$ch = curl_init('https://api.iopaint.com/api/v1/remove-watermark');

curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, [
    'image' => new CURLFile('/path/to/image.jpg')
]);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'X-API-Key: your_api_key_here'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$result = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode == 200) {
    file_put_contents('result.png', $result);
    echo "✓ Success!\n";
} else {
    echo "✗ Error: $httpCode\n";
}
?>
```

#### Go

```go
package main

import (
    "bytes"
    "io"
    "mime/multipart"
    "net/http"
    "os"
)

func main() {
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)

    // Add image file
    file, _ := os.Open("image.jpg")
    defer file.Close()
    part, _ := writer.CreateFormFile("image", "image.jpg")
    io.Copy(part, file)
    writer.Close()

    // Create request
    req, _ := http.NewRequest("POST", "https://api.iopaint.com/api/v1/remove-watermark", body)
    req.Header.Set("X-API-Key", os.Getenv("IOPAINT_API_KEY"))
    req.Header.Set("Content-Type", writer.FormDataContentType())

    // Send request
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()

    // Save result
    out, _ := os.Create("result.png")
    defer out.Close()
    io.Copy(out, resp.Body)
}
```

---

## 2. Health Check

Check the API service status and availability.

### Endpoint

```http
GET /api/v1/health
```

### Authentication

Not required.

### Response

**Success (200 OK)**

```json
{
  "status": "healthy",
  "model": "lama",
  "device": "cuda",
  "gpu_available": true
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service status: `healthy` or `unhealthy` |
| `model` | string | Current AI model name |
| `device` | string | Compute device: `cuda` (GPU) or `cpu` |
| `gpu_available` | boolean | GPU availability |

### Example

```bash
curl https://api.iopaint.com/api/v1/health
```

```python
import requests

response = requests.get("https://api.iopaint.com/api/v1/health")
print(response.json())
# Output: {'status': 'healthy', 'model': 'lama', 'device': 'cuda', 'gpu_available': True}
```

---

## 3. Usage Statistics

Retrieve your account usage statistics.

### Endpoint

```http
GET /api/v1/stats
```

### Authentication

Required. Include `X-API-Key` header.

### Response

**Success (200 OK)**

```json
{
  "total": 1250,
  "success": 1230,
  "failed": 20,
  "total_processing_time": 1845.5,
  "avg_processing_time": 1.5
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total requests made |
| `success` | integer | Successful requests |
| `failed` | integer | Failed requests |
| `total_processing_time` | float | Cumulative processing time (seconds) |
| `avg_processing_time` | float | Average processing time (seconds) |

### Example

```bash
curl https://api.iopaint.com/api/v1/stats \
  -H "X-API-Key: $IOPAINT_API_KEY"
```

```python
import requests

headers = {"X-API-Key": "your_api_key_here"}
response = requests.get("https://api.iopaint.com/api/v1/stats", headers=headers)
stats = response.json()

print(f"Total requests: {stats['total']}")
print(f"Success rate: {stats['success'] / stats['total'] * 100:.2f}%")
print(f"Average time: {stats['avg_processing_time']:.2f}s")
```

---

## Models

### LaMa (Current)

**Large Mask Inpainting** - Fast and efficient inpainting model.

| Property | Value |
|----------|-------|
| **Name** | `lama` |
| **Speed** | ⚡⚡⚡⚡⚡ (1-2s for 1024x1024) |
| **Quality** | ⭐⭐⭐⭐ |
| **VRAM** | ~1GB |
| **Best For** | Watermark removal, object removal |

### Future Models (Coming Soon)

| Model | Speed | Quality | VRAM | Use Case |
|-------|-------|---------|------|----------|
| **SD Inpainting** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ~4GB | Creative editing |
| **SDXL Inpainting** | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~8GB | Professional work |

---

## Error Handling

### Error Response Format

All errors return a JSON object with the following structure:

```json
{
  "error": "ErrorType",
  "detail": "Human-readable error message",
  "status_code": 400
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid request parameters |
| `401` | Unauthorized | Missing or invalid API key |
| `413` | Payload Too Large | File exceeds size limit |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Service temporarily unavailable |

### Error Types

#### 401 Unauthorized

**Missing API Key:**

```json
{
  "error": "Unauthorized",
  "detail": "Missing API Key. Please provide X-API-Key header.",
  "status_code": 401
}
```

**Invalid API Key:**

```json
{
  "error": "Unauthorized",
  "detail": "Invalid API Key",
  "status_code": 401
}
```

#### 400 Bad Request

**Invalid Image Format:**

```json
{
  "error": "Bad Request",
  "detail": "Invalid image format: cannot identify image file",
  "status_code": 400
}
```

**Image Too Large:**

```json
{
  "error": "Bad Request",
  "detail": "Image too large. Max dimension: 4096px",
  "status_code": 400
}
```

**File Too Large:**

```json
{
  "error": "Bad Request",
  "detail": "Image too large. Max size: 10MB",
  "status_code": 400
}
```

#### 429 Rate Limit Exceeded

```json
{
  "error": "Too Many Requests",
  "detail": "Rate limit exceeded. Please try again later.",
  "status_code": 429
}
```

**Headers:**

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1672531200
```

#### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "detail": "Processing failed: CUDA out of memory",
  "status_code": 500
}
```

### Error Handling Best Practices

```python
import requests
import time

def remove_watermark_with_retry(image_path, max_retries=3):
    """Remove watermark with exponential backoff retry"""
    url = "https://api.iopaint.com/api/v1/remove-watermark"
    headers = {"X-API-Key": os.getenv("IOPAINT_API_KEY")}

    for attempt in range(max_retries):
        try:
            with open(image_path, "rb") as f:
                response = requests.post(
                    url,
                    headers=headers,
                    files={"image": f},
                    timeout=120
                )

            if response.status_code == 200:
                return response.content

            elif response.status_code == 429:
                # Rate limit - exponential backoff
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            elif response.status_code in [500, 503]:
                # Server error - retry
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception(f"Server error: {response.json()}")

            else:
                # Client error - don't retry
                raise Exception(f"Error {response.status_code}: {response.json()}")

        except requests.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout. Retrying... ({attempt + 1}/{max_retries})")
                continue
            else:
                raise

    raise Exception("Max retries exceeded")
```

---

## Rate Limiting

### Rate Limit Rules

| Plan | Rate Limit | Burst | Quota |
|------|------------|-------|-------|
| **Free** | 2 req/min | 5 | 10/day |
| **Basic** | 10 req/min | 20 | 3,000/month |
| **Pro** | 30 req/min | 60 | 20,000/month |
| **Enterprise** | Custom | Custom | Custom |

### Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1672531200
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per time window |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

### Handling Rate Limits

```python
import requests
import time

def wait_for_rate_limit_reset(response):
    """Wait until rate limit resets"""
    if response.status_code == 429:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        current_time = int(time.time())
        wait_time = max(0, reset_time - current_time)

        print(f"Rate limited. Waiting {wait_time}s for reset...")
        time.sleep(wait_time + 1)  # Add 1s buffer
        return True
    return False
```

### Best Practices

1. **Check remaining quota** before making requests
2. **Implement exponential backoff** for retries
3. **Cache results** to avoid duplicate requests
4. **Use batch endpoints** (when available) for multiple images
5. **Upgrade your plan** if consistently hitting limits

---

## Best Practices

### Performance Optimization

#### 1. Image Preprocessing

```python
from PIL import Image

def optimize_image(image_path, max_size=2048):
    """Resize large images before upload"""
    img = Image.open(image_path)

    # Check if resize needed
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.LANCZOS)

    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Save optimized
    output = "optimized.jpg"
    img.save(output, quality=95, optimize=True)
    return output
```

#### 2. Concurrent Processing

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def process_batch(image_paths, api_key, max_workers=4):
    """Process multiple images concurrently"""
    def process_one(path):
        headers = {"X-API-Key": api_key}
        with open(path, "rb") as f:
            response = requests.post(
                "https://api.iopaint.com/api/v1/remove-watermark",
                headers=headers,
                files={"image": f}
            )
        return path, response

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_one, image_paths))

    return results
```

#### 3. Connection Reuse

```python
import requests

# Reuse session for multiple requests
session = requests.Session()
session.headers.update({"X-API-Key": api_key})

for image_path in image_paths:
    with open(image_path, "rb") as f:
        response = session.post(
            "https://api.iopaint.com/api/v1/remove-watermark",
            files={"image": f}
        )
```

### Security

#### Environment Variables

```bash
# .env file
IOPAINT_API_KEY=sk_live_1234567890abcdef

# .gitignore
.env
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("IOPAINT_API_KEY")
```

#### API Key Rotation

```python
# Rotate keys periodically
def rotate_api_key():
    old_key = os.getenv("IOPAINT_API_KEY")
    new_key = generate_new_key()  # From dashboard

    # Test new key
    test_response = requests.get(
        "https://api.iopaint.com/api/v1/health",
        headers={"X-API-Key": new_key}
    )

    if test_response.status_code == 200:
        # Update environment
        update_env("IOPAINT_API_KEY", new_key)
        # Revoke old key from dashboard
        revoke_key(old_key)
```

### Cost Optimization

#### 1. Cache Results

```python
import hashlib
import os

def get_cached_result(image_path):
    """Check if result already cached"""
    # Generate cache key from file content
    with open(image_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    cache_path = f"cache/{file_hash}.png"
    if os.path.exists(cache_path):
        return cache_path
    return None

def process_with_cache(image_path, api_key):
    """Process with caching"""
    # Check cache first
    cached = get_cached_result(image_path)
    if cached:
        print(f"✓ Using cached result: {cached}")
        return cached

    # Process via API
    result = remove_watermark(image_path, api_key)

    # Save to cache
    with open(image_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    cache_path = f"cache/{file_hash}.png"
    with open(cache_path, "wb") as f:
        f.write(result)

    return cache_path
```

#### 2. Monitor Usage

```python
def check_quota_before_request(api_key):
    """Check quota before making expensive requests"""
    headers = {"X-API-Key": api_key}
    response = requests.get(
        "https://api.iopaint.com/api/v1/stats",
        headers=headers
    )

    stats = response.json()
    quota_used = stats['total']
    plan_limit = 3000  # Basic plan

    remaining = plan_limit - quota_used
    if remaining < 100:
        print(f"⚠️ Warning: Only {remaining} requests remaining!")

    return remaining > 0
```

---

## SDKs & Libraries

### Official SDKs

#### Python

```bash
pip install iopaint-sdk
```

```python
from iopaint import IOPaintClient

client = IOPaintClient(api_key="your_api_key")

# Simple usage
result = client.remove_watermark("image.jpg")

# With options
result = client.remove_watermark(
    image="image.jpg",
    mask="mask.png",
    output="result.png"
)

# Batch processing
results = client.batch_process(
    images=["img1.jpg", "img2.jpg"],
    output_dir="./results"
)
```

#### JavaScript/TypeScript

```bash
npm install iopaint-sdk
```

```javascript
const { IOPaintClient } = require('iopaint-sdk');

const client = new IOPaintClient({
    apiKey: process.env.IOPAINT_API_KEY
});

// Simple usage
await client.removeWatermark('image.jpg', 'result.png');

// With mask
await client.removeWatermark('image.jpg', 'result.png', {
    mask: 'mask.png'
});
```

### Community Libraries

| Language | Library | Author |
|----------|---------|--------|
| Go | `iopaint-go` | Community |
| Ruby | `iopaint-rb` | Community |
| Java | `iopaint-java` | Community |
| PHP | `iopaint-php` | Community |

---

## Changelog

### v1.0.0 (2025-11-28)

**Initial Release**

- ✨ `/api/v1/remove-watermark` endpoint
- ✨ `/api/v1/health` endpoint
- ✨ `/api/v1/stats` endpoint
- ✨ API key authentication
- ✨ Rate limiting
- ✨ Support for JPEG, PNG, WebP
- ✨ Optional mask support
- ✨ Processing time metrics

### Coming Soon

- 🔜 `/api/v1/batch` - Batch processing endpoint
- 🔜 `/api/v1/detect` - Automatic watermark detection
- 🔜 Webhook callbacks for async processing
- 🔜 Additional models (SD, SDXL)
- 🔜 Custom model training

---

## Support

### Resources

- **API Status**: [status.iopaint.com](https://status.iopaint.com)
- **Dashboard**: [iopaint.com/dashboard](https://iopaint.com/dashboard)
- **Documentation**: [docs.iopaint.com](https://docs.iopaint.com)
- **GitHub**: [github.com/let5sne/IOPaint](https://github.com/let5sne/IOPaint)

### Contact

- **Email**: support@iopaint.com
- **Discord**: [discord.gg/iopaint](https://discord.gg/iopaint)
- **Issues**: [GitHub Issues](https://github.com/let5sne/IOPaint/issues)

### SLA (Service Level Agreement)

| Plan | Uptime | Support Response |
|------|--------|------------------|
| Free | 95% | Community |
| Basic | 99% | 48 hours |
| Pro | 99.5% | 24 hours |
| Enterprise | 99.9% | 4 hours |

---

## Legal

### Terms of Service

By using the IOPaint API, you agree to our [Terms of Service](https://iopaint.com/terms).

### Privacy Policy

We respect your privacy. See our [Privacy Policy](https://iopaint.com/privacy).

### Data Processing

- Images are processed in memory and not stored
- Uploaded images are deleted immediately after processing
- We do not train models on your data
- Logs contain only metadata (no image content)

### Usage Restrictions

**Allowed:**
- ✅ Removing watermarks from your own content
- ✅ Restoring old photos
- ✅ Object removal for creative projects
- ✅ Commercial use (with appropriate plan)

**Prohibited:**
- ❌ Removing copyright protection
- ❌ Processing illegal content
- ❌ Violating third-party rights
- ❌ Automated scraping without permission

---

**© 2025 IOPaint. All rights reserved.**

*Last updated: 2025-11-28*
