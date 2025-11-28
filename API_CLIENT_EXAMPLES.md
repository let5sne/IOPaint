# IOPaint API 客户端示例

本文档提供多种编程语言的API调用示例。

## 目录
- [Python](#python)
- [JavaScript/Node.js](#javascriptnodejs)
- [cURL](#curl)
- [PHP](#php)
- [Java](#java)
- [Go](#go)

---

## 配置信息

```bash
API_URL=http://localhost:8080
API_KEY=your_secret_key_change_me
```

---

## Python

### 基础示例

```python
import requests

def remove_watermark(image_path, mask_path=None, api_key="your_secret_key_change_me"):
    """去除图片水印"""
    url = "http://localhost:8080/api/v1/remove-watermark"
    headers = {"X-API-Key": api_key}

    files = {
        "image": open(image_path, "rb")
    }

    if mask_path:
        files["mask"] = open(mask_path, "rb")

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        # 保存结果
        output_path = "result.png"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✓ 处理成功！结果已保存到: {output_path}")
        print(f"处理时间: {response.headers.get('X-Processing-Time')}秒")
        return output_path
    else:
        print(f"✗ 处理失败: {response.status_code}")
        print(response.json())
        return None

# 使用示例
remove_watermark("input.jpg")
```

### 高级示例（含错误处理和重试）

```python
import requests
import time
from pathlib import Path

class IOPaintClient:
    """IOPaint API客户端"""

    def __init__(self, api_url="http://localhost:8080", api_key=None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def health_check(self):
        """健康检查"""
        response = self.session.get(f"{self.api_url}/api/v1/health")
        return response.json()

    def get_stats(self):
        """获取使用统计"""
        response = self.session.get(f"{self.api_url}/api/v1/stats")
        return response.json()

    def remove_watermark(
        self,
        image_path,
        mask_path=None,
        output_path=None,
        max_retries=3,
        timeout=120
    ):
        """
        去除图片水印

        参数:
            image_path: 输入图片路径
            mask_path: 遮罩图片路径（可选）
            output_path: 输出路径（可选，默认为input_result.png）
            max_retries: 最大重试次数
            timeout: 超时时间（秒）

        返回:
            成功返回输出路径，失败返回None
        """
        # 准备文件
        files = {"image": open(image_path, "rb")}
        if mask_path:
            files["mask"] = open(mask_path, "rb")

        # 确定输出路径
        if output_path is None:
            input_path = Path(image_path)
            output_path = input_path.parent / f"{input_path.stem}_result.png"

        # 重试逻辑
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.api_url}/api/v1/remove-watermark",
                    files=files,
                    timeout=timeout
                )

                if response.status_code == 200:
                    # 保存结果
                    with open(output_path, "wb") as f:
                        f.write(response.content)

                    print(f"✓ 处理成功！")
                    print(f"  输出: {output_path}")
                    print(f"  处理时间: {response.headers.get('X-Processing-Time')}秒")
                    print(f"  图片尺寸: {response.headers.get('X-Image-Size')}")
                    return str(output_path)

                elif response.status_code == 429:
                    # 限流，等待后重试
                    wait_time = 2 ** attempt
                    print(f"⚠ 请求过于频繁，等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue

                else:
                    # 其他错误
                    print(f"✗ 处理失败 ({response.status_code})")
                    error_data = response.json()
                    print(f"  错误: {error_data.get('detail', '未知错误')}")
                    return None

            except requests.Timeout:
                print(f"⚠ 请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                else:
                    print("✗ 超过最大重试次数")
                    return None

            except Exception as e:
                print(f"✗ 发生错误: {e}")
                return None

            finally:
                # 关闭文件
                for f in files.values():
                    if hasattr(f, 'close'):
                        f.close()

        return None

    def batch_process(self, image_dir, output_dir=None, mask_dir=None):
        """
        批量处理图片

        参数:
            image_dir: 输入图片目录
            output_dir: 输出目录（可选）
            mask_dir: 遮罩目录（可选，按文件名匹配）
        """
        image_dir = Path(image_dir)
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)

        # 支持的图片格式
        image_exts = {".jpg", ".jpeg", ".png", ".webp"}
        images = [
            f for f in image_dir.iterdir()
            if f.suffix.lower() in image_exts
        ]

        print(f"找到 {len(images)} 张图片")

        results = {"success": 0, "failed": 0}
        for i, image_path in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}] 处理: {image_path.name}")

            # 查找对应的遮罩
            mask_path = None
            if mask_dir:
                mask_path = Path(mask_dir) / image_path.name
                if not mask_path.exists():
                    mask_path = None

            # 确定输出路径
            if output_dir:
                out_path = output_dir / f"{image_path.stem}_result.png"
            else:
                out_path = image_path.parent / f"{image_path.stem}_result.png"

            # 处理
            result = self.remove_watermark(image_path, mask_path, out_path)
            if result:
                results["success"] += 1
            else:
                results["failed"] += 1

        # 总结
        print("\n" + "=" * 60)
        print(f"批量处理完成！")
        print(f"  成功: {results['success']}")
        print(f"  失败: {results['failed']}")
        print("=" * 60)

# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = IOPaintClient(
        api_url="http://localhost:8080",
        api_key="your_secret_key_change_me"
    )

    # 健康检查
    print("健康检查:", client.health_check())

    # 单张图片处理
    client.remove_watermark("test.jpg")

    # 批量处理
    client.batch_process("./input_images", "./output_images")
```

---

## JavaScript/Node.js

### 使用 axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function removeWatermark(imagePath, maskPath = null, apiKey = 'your_secret_key_change_me') {
    const url = 'http://localhost:8080/api/v1/remove-watermark';

    const formData = new FormData();
    formData.append('image', fs.createReadStream(imagePath));

    if (maskPath) {
        formData.append('mask', fs.createReadStream(maskPath));
    }

    try {
        const response = await axios.post(url, formData, {
            headers: {
                'X-API-Key': apiKey,
                ...formData.getHeaders()
            },
            responseType: 'arraybuffer',
            timeout: 120000  // 120秒超时
        });

        // 保存结果
        const outputPath = 'result.png';
        fs.writeFileSync(outputPath, response.data);

        console.log('✓ 处理成功！');
        console.log(`  输出: ${outputPath}`);
        console.log(`  处理时间: ${response.headers['x-processing-time']}秒`);

        return outputPath;

    } catch (error) {
        if (error.response) {
            console.error('✗ 处理失败:', error.response.status);
            console.error('  错误:', error.response.data.toString());
        } else {
            console.error('✗ 请求失败:', error.message);
        }
        return null;
    }
}

// 使用示例
removeWatermark('input.jpg');
```

### 完整客户端类

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

class IOPaintClient {
    constructor(apiUrl = 'http://localhost:8080', apiKey = null) {
        this.apiUrl = apiUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.client = axios.create({
            baseURL: this.apiUrl,
            headers: {
                'X-API-Key': apiKey
            },
            timeout: 120000
        });
    }

    async healthCheck() {
        const response = await this.client.get('/api/v1/health');
        return response.data;
    }

    async getStats() {
        const response = await this.client.get('/api/v1/stats');
        return response.data;
    }

    async removeWatermark(imagePath, maskPath = null, outputPath = null) {
        const formData = new FormData();
        formData.append('image', fs.createReadStream(imagePath));

        if (maskPath) {
            formData.append('mask', fs.createReadStream(maskPath));
        }

        // 确定输出路径
        if (!outputPath) {
            const parsed = path.parse(imagePath);
            outputPath = path.join(parsed.dir, `${parsed.name}_result.png`);
        }

        try {
            const response = await this.client.post('/api/v1/remove-watermark', formData, {
                headers: formData.getHeaders(),
                responseType: 'arraybuffer'
            });

            fs.writeFileSync(outputPath, response.data);

            console.log('✓ 处理成功！');
            console.log(`  输出: ${outputPath}`);
            console.log(`  处理时间: ${response.headers['x-processing-time']}秒`);

            return outputPath;

        } catch (error) {
            if (error.response) {
                console.error('✗ 处理失败:', error.response.status);
            } else {
                console.error('✗ 请求失败:', error.message);
            }
            return null;
        }
    }
}

// 使用示例
(async () => {
    const client = new IOPaintClient('http://localhost:8080', 'your_secret_key_change_me');

    // 健康检查
    const health = await client.healthCheck();
    console.log('健康检查:', health);

    // 处理图片
    await client.removeWatermark('test.jpg');
})();
```

---

## cURL

### 基础使用

```bash
# 简单调用
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: your_secret_key_change_me" \
  -F "image=@input.jpg" \
  -o result.png

# 带遮罩
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: your_secret_key_change_me" \
  -F "image=@input.jpg" \
  -F "mask=@mask.png" \
  -o result.png

# 显示详细信息
curl -X POST http://localhost:8080/api/v1/remove-watermark \
  -H "X-API-Key: your_secret_key_change_me" \
  -F "image=@input.jpg" \
  -o result.png \
  -v

# 健康检查
curl http://localhost:8080/api/v1/health
```

### Bash脚本批量处理

```bash
#!/bin/bash

API_URL="http://localhost:8080/api/v1/remove-watermark"
API_KEY="your_secret_key_change_me"
INPUT_DIR="./input"
OUTPUT_DIR="./output"

mkdir -p "$OUTPUT_DIR"

for image in "$INPUT_DIR"/*.{jpg,jpeg,png}; do
    [ -f "$image" ] || continue

    filename=$(basename "$image")
    name="${filename%.*}"
    output="$OUTPUT_DIR/${name}_result.png"

    echo "处理: $filename"

    curl -X POST "$API_URL" \
        -H "X-API-Key: $API_KEY" \
        -F "image=@$image" \
        -o "$output" \
        -s -w "状态码: %{http_code}, 时间: %{time_total}s\n"
done

echo "批量处理完成！"
```

---

## PHP

```php
<?php

class IOPaintClient {
    private $apiUrl;
    private $apiKey;

    public function __construct($apiUrl = 'http://localhost:8080', $apiKey = null) {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->apiKey = $apiKey;
    }

    public function healthCheck() {
        $ch = curl_init($this->apiUrl . '/api/v1/health');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        return json_decode($response, true);
    }

    public function removeWatermark($imagePath, $maskPath = null, $outputPath = null) {
        $url = $this->apiUrl . '/api/v1/remove-watermark';

        // 准备文件
        $postData = [
            'image' => new CURLFile($imagePath)
        ];

        if ($maskPath) {
            $postData['mask'] = new CURLFile($maskPath);
        }

        // 确定输出路径
        if (!$outputPath) {
            $pathInfo = pathinfo($imagePath);
            $outputPath = $pathInfo['dirname'] . '/' . $pathInfo['filename'] . '_result.png';
        }

        // 发送请求
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'X-API-Key: ' . $this->apiKey
        ]);
        curl_setopt($ch, CURLOPT_TIMEOUT, 120);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode == 200) {
            file_put_contents($outputPath, $response);
            echo "✓ 处理成功！输出: $outputPath\n";
            return $outputPath;
        } else {
            echo "✗ 处理失败 (HTTP $httpCode)\n";
            return null;
        }
    }
}

// 使用示例
$client = new IOPaintClient('http://localhost:8080', 'your_secret_key_change_me');

// 健康检查
print_r($client->healthCheck());

// 处理图片
$client->removeWatermark('test.jpg');
?>
```

---

## Java

```java
import okhttp3.*;
import java.io.*;
import java.nio.file.*;

public class IOPaintClient {
    private final String apiUrl;
    private final String apiKey;
    private final OkHttpClient client;

    public IOPaintClient(String apiUrl, String apiKey) {
        this.apiUrl = apiUrl.replaceAll("/$", "");
        this.apiKey = apiKey;
        this.client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .build();
    }

    public String removeWatermark(String imagePath, String maskPath, String outputPath) throws IOException {
        // 构建请求
        MultipartBody.Builder builder = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("image", "image.jpg",
                RequestBody.create(new File(imagePath), MediaType.parse("image/*")));

        if (maskPath != null) {
            builder.addFormDataPart("mask", "mask.png",
                RequestBody.create(new File(maskPath), MediaType.parse("image/*")));
        }

        RequestBody requestBody = builder.build();

        Request request = new Request.Builder()
            .url(apiUrl + "/api/v1/remove-watermark")
            .addHeader("X-API-Key", apiKey)
            .post(requestBody)
            .build();

        // 发送请求
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                // 保存结果
                if (outputPath == null) {
                    Path path = Paths.get(imagePath);
                    String name = path.getFileName().toString();
                    name = name.substring(0, name.lastIndexOf('.'));
                    outputPath = path.getParent().resolve(name + "_result.png").toString();
                }

                try (InputStream is = response.body().byteStream();
                     FileOutputStream fos = new FileOutputStream(outputPath)) {
                    byte[] buffer = new byte[4096];
                    int bytesRead;
                    while ((bytesRead = is.read(buffer)) != -1) {
                        fos.write(buffer, 0, bytesRead);
                    }
                }

                System.out.println("✓ 处理成功！输出: " + outputPath);
                return outputPath;
            } else {
                System.err.println("✗ 处理失败: " + response.code());
                System.err.println(response.body().string());
                return null;
            }
        }
    }

    public static void main(String[] args) {
        IOPaintClient client = new IOPaintClient(
            "http://localhost:8080",
            "your_secret_key_change_me"
        );

        try {
            client.removeWatermark("test.jpg", null, null);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

---

## Go

```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
    "path/filepath"
    "time"
)

type IOPaintClient struct {
    apiURL string
    apiKey string
    client *http.Client
}

func NewIOPaintClient(apiURL, apiKey string) *IOPaintClient {
    return &IOPaintClient{
        apiURL: apiURL,
        apiKey: apiKey,
        client: &http.Client{
            Timeout: 120 * time.Second,
        },
    }
}

func (c *IOPaintClient) RemoveWatermark(imagePath, maskPath, outputPath string) error {
    // 准备multipart请求
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)

    // 添加图片
    imageFile, err := os.Open(imagePath)
    if err != nil {
        return err
    }
    defer imageFile.Close()

    imagePart, err := writer.CreateFormFile("image", filepath.Base(imagePath))
    if err != nil {
        return err
    }
    io.Copy(imagePart, imageFile)

    // 添加遮罩（如果有）
    if maskPath != "" {
        maskFile, err := os.Open(maskPath)
        if err != nil {
            return err
        }
        defer maskFile.Close()

        maskPart, err := writer.CreateFormFile("mask", filepath.Base(maskPath))
        if err != nil {
            return err
        }
        io.Copy(maskPart, maskFile)
    }

    writer.Close()

    // 创建请求
    req, err := http.NewRequest("POST", c.apiURL+"/api/v1/remove-watermark", body)
    if err != nil {
        return err
    }

    req.Header.Set("X-API-Key", c.apiKey)
    req.Header.Set("Content-Type", writer.FormDataContentType())

    // 发送请求
    resp, err := c.client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    // 检查响应
    if resp.StatusCode != 200 {
        return fmt.Errorf("请求失败: %d", resp.StatusCode)
    }

    // 确定输出路径
    if outputPath == "" {
        ext := filepath.Ext(imagePath)
        name := imagePath[:len(imagePath)-len(ext)]
        outputPath = name + "_result.png"
    }

    // 保存结果
    outFile, err := os.Create(outputPath)
    if err != nil {
        return err
    }
    defer outFile.Close()

    _, err = io.Copy(outFile, resp.Body)
    if err != nil {
        return err
    }

    fmt.Printf("✓ 处理成功！输出: %s\n", outputPath)
    fmt.Printf("  处理时间: %s秒\n", resp.Header.Get("X-Processing-Time"))

    return nil
}

func main() {
    client := NewIOPaintClient("http://localhost:8080", "your_secret_key_change_me")

    err := client.RemoveWatermark("test.jpg", "", "")
    if err != nil {
        fmt.Printf("错误: %v\n", err)
    }
}
```

---

## 错误处理

### 常见错误代码

| 状态码 | 错误 | 解决方案 |
|--------|------|----------|
| 401 | 未授权 | 检查API Key是否正确 |
| 400 | 请求错误 | 检查图片格式、大小是否符合要求 |
| 429 | 请求过多 | 降低请求频率，稍后重试 |
| 500 | 服务器错误 | 检查服务器日志，联系技术支持 |
| 503 | 服务不可用 | 服务器可能正在重启，稍后重试 |

### 限流说明

默认限流：每秒10个请求，突发20个请求

如果遇到429错误，建议：
1. 使用指数退避重试策略
2. 减少并发请求数
3. 联系管理员增加配额

---

## 性能优化建议

1. **批量处理**：合理控制并发数（建议2-4个并发）
2. **图片预处理**：压缩大图片后再上传
3. **复用连接**：使用HTTP keep-alive
4. **错误重试**：实现指数退避策略
5. **超时设置**：根据图片大小设置合理超时时间

---

## 支持

如有问题，请访问：
- 文档：`http://localhost:8080/docs`
- GitHub：https://github.com/let5sne/IOPaint/issues
