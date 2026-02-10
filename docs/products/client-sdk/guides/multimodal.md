# Working with Multimodal Content

Send images, audio, video, and documents to agents.

## Overview

The Client SDK supports multimodal content - sending images, audio, video, and documents alongside text messages. This enables powerful use cases like image analysis, document processing, audio transcription, and video understanding.

---

## Sending Images

### From URL

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, ImageContent

    client = AgentProtocolClient("http://localhost:5000")

    response = await client.complete_chat(
        message="What's in this image?",
        content=[
            ImageContent(url="https://example.com/photo.jpg")
        ]
    )
    print(response)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, ImageContent } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    const response = await client.completeChat({
        message: "What's in this image?",
        content: [
            new ImageContent({ url: "https://example.com/photo.jpg" })
        ]
    });
    console.log(response);
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    var response = await client.CompleteChatAsync(
        message: "What's in this image?",
        content: new IContent[]
        {
            new ImageContent { Url = "https://example.com/photo.jpg" }
        }
    );
    Console.WriteLine(response);
    ```

### From File

=== "Python"

    ```python
    from microsoft.agents.protocol import ImageContent

    # Read image from disk
    with open("photo.jpg", "rb") as f:
        image_data = f.read()

    response = await client.complete_chat(
        message="Describe this image",
        content=[
            ImageContent(data=image_data, mime_type="image/jpeg")
        ]
    )
    ```

=== "TypeScript"

    ```typescript
    import { readFileSync } from 'fs';
    import { ImageContent } from '@microsoft/agents-protocol-client';

    // Read image from disk
    const imageData = readFileSync("photo.jpg");

    const response = await client.completeChat({
        message: "Describe this image",
        content: [
            new ImageContent({
                data: imageData,
                mimeType: "image/jpeg"
            })
        ]
    });
    ```

=== "C#"

    ```csharp
    using System.IO;

    // Read image from disk
    var imageData = File.ReadAllBytes("photo.jpg");

    var response = await client.CompleteChatAsync(
        message: "Describe this image",
        content: new IContent[]
        {
            new ImageContent
            {
                Data = imageData,
                MimeType = "image/jpeg"
            }
        }
    );
    ```

### Multiple Images

```python
response = await client.complete_chat(
    message="Compare these two images",
    content=[
        ImageContent(url="https://example.com/before.jpg"),
        ImageContent(url="https://example.com/after.jpg")
    ]
)
```

---

## Sending Audio

### Audio Files

=== "Python"

    ```python
    from microsoft.agents.protocol import AudioContent

    with open("recording.mp3", "rb") as f:
        audio_data = f.read()

    response = await client.complete_chat(
        message="Transcribe this audio",
        content=[
            AudioContent(data=audio_data, mime_type="audio/mpeg")
        ]
    )
    ```

=== "TypeScript"

    ```typescript
    import { AudioContent } from '@microsoft/agents-protocol-client';

    const audioData = readFileSync("recording.mp3");

    const response = await client.completeChat({
        message: "Transcribe this audio",
        content: [
            new AudioContent({
                data: audioData,
                mimeType: "audio/mpeg"
            })
        ]
    });
    ```

=== "C#"

    ```csharp
    var audioData = File.ReadAllBytes("recording.mp3");

    var response = await client.CompleteChatAsync(
        message: "Transcribe this audio",
        content: new IContent[]
        {
            new AudioContent
            {
                Data = audioData,
                MimeType = "audio/mpeg"
            }
        }
    );
    ```

**Supported Audio Formats:**

- MP3 (`audio/mpeg`)
- WAV (`audio/wav`)
- OGG (`audio/ogg`)
- M4A (`audio/mp4`)
- WebM (`audio/webm`)

---

## Sending Video

```python
from microsoft.agents.protocol import VideoContent

with open("clip.mp4", "rb") as f:
    video_data = f.read()

response = await client.complete_chat(
    message="Summarize what happens in this video",
    content=[
        VideoContent(data=video_data, mime_type="video/mp4")
    ]
)
```

**Supported Video Formats:**

- MP4 (`video/mp4`)
- WebM (`video/webm`)
- MOV (`video/quicktime`)
- AVI (`video/x-msvideo`)

!!! warning "Video Size Limits"
    Most agents have size limits for video files (typically 20-50 MB). For longer videos, consider:
    - Compressing the video
    - Extracting key frames as images
    - Splitting into shorter clips

---

## Sending Documents

### PDFs

```python
from microsoft.agents.protocol import DocumentContent

with open("report.pdf", "rb") as f:
    pdf_data = f.read()

response = await client.complete_chat(
    message="Summarize this document",
    content=[
        DocumentContent(data=pdf_data, mime_type="application/pdf")
    ]
)
```

### Office Documents

```python
# Word document
with open("document.docx", "rb") as f:
    doc_data = f.read()

response = await client.complete_chat(
    message="Extract key points from this document",
    content=[
        DocumentContent(
            data=doc_data,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    ]
)
```

**Supported Document Formats:**

| Format | MIME Type |
|--------|-----------|
| PDF | `application/pdf` |
| Word (.docx) | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Excel (.xlsx) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PowerPoint (.pptx) | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| Plain Text | `text/plain` |
| Markdown | `text/markdown` |
| HTML | `text/html` |

---

## Mixed Content

Combine text with multiple media types:

```python
response = await client.complete_chat(
    message="Analyze this product listing",
    content=[
        ImageContent(url="https://example.com/product.jpg"),
        DocumentContent(url="https://example.com/specs.pdf"),
        TextContent(text="Product ID: ABC123, Price: $299")
    ]
)
```

---

## Streaming with Multimodal

```python
await client.stream_chat(
    message="Describe this image in detail",
    content=[
        ImageContent(url="https://example.com/landscape.jpg")
    ],
    on_text_chunk=lambda text: print(text, end="", flush=True)
)
```

---

## Best Practices

### 1. Optimize File Sizes

```python
from PIL import Image
import io

# Resize large images before sending
def resize_image(image_path: str, max_size: int = 2048) -> bytes:
    """Resize image to max dimension while preserving aspect ratio."""
    img = Image.open(image_path)

    # Calculate new size
    ratio = min(max_size / img.width, max_size / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))

    # Resize and compress
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()

# Usage
image_data = resize_image("large_photo.jpg")
response = await client.complete_chat(
    message="Analyze this image",
    content=[ImageContent(data=image_data, mime_type="image/jpeg")]
)
```

### 2. Use URLs for Large Files

```python
# Instead of uploading large files directly:
with open("large_video.mp4", "rb") as f:
    video_data = f.read()  # Could be 100+ MB!

# Upload to storage first, then send URL:
video_url = await upload_to_storage("large_video.mp4")
response = await client.complete_chat(
    message="Analyze this video",
    content=[VideoContent(url=video_url)]
)
```

### 3. Validate File Types

```python
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/ogg"]

def validate_file(file_data: bytes, mime_type: str, allowed_types: list) -> bool:
    """Validate file type and size."""
    if mime_type not in allowed_types:
        raise ValueError(f"Unsupported file type: {mime_type}")

    if len(file_data) > 10 * 1024 * 1024:  # 10 MB
        raise ValueError("File too large (max 10 MB)")

    return True

# Usage
validate_file(image_data, "image/jpeg", ALLOWED_IMAGE_TYPES)
```

### 4. Handle Errors Gracefully

```python
from microsoft.agents.protocol import AgentValidationException

try:
    response = await client.complete_chat(
        message="Analyze this image",
        content=[ImageContent(url=image_url)]
    )
except AgentValidationException as e:
    if "image" in str(e).lower():
        print("The agent couldn't process the image. Try a different format or smaller size.")
    else:
        print(f"Validation error: {e}")
```

### 5. Provide Context with Media

```python
# Bad - no context
response = await client.complete_chat(
    message="Analyze",
    content=[ImageContent(url=image_url)]
)

# Good - clear instructions
response = await client.complete_chat(
    message="Analyze this chest X-ray and identify any abnormalities. Provide confidence scores.",
    content=[ImageContent(url=xray_url)]
)
```

---

## Use Cases

### Image Analysis

```python
# Product catalog
response = await client.complete_chat(
    message="Generate a product description for this item. Include details about color, style, and features.",
    content=[ImageContent(url=product_image)]
)

# Medical imaging
response = await client.complete_chat(
    message="Review this medical scan. Identify any concerning features.",
    content=[ImageContent(data=scan_data, mime_type="image/jpeg")]
)

# Document scanning
response = await client.complete_chat(
    message="Extract all text from this receipt and structure it as JSON.",
    content=[ImageContent(url=receipt_photo)]
)
```

### Audio Transcription

```python
# Meeting transcription
response = await client.complete_chat(
    message="Transcribe this meeting and create action items.",
    content=[AudioContent(url=recording_url)]
)

# Voice notes
response = await client.complete_chat(
    message="Transcribe this voice note and summarize the key points.",
    content=[AudioContent(data=voice_note, mime_type="audio/mpeg")]
)
```

### Document Processing

```python
# Contract analysis
response = await client.complete_chat(
    message="Review this contract and highlight any unusual clauses.",
    content=[DocumentContent(url=contract_pdf)]
)

# Resume parsing
response = await client.complete_chat(
    message="Extract name, email, experience, and education from this resume.",
    content=[DocumentContent(data=resume_data, mime_type="application/pdf")]
)
```

---

## Next Steps

<div class="grid cards" markdown>

- **:material-database: Data Model**

    Understand content types

    [:octicons-arrow-right-24: Data Model](../concepts/data-model.md)

- **:material-tools: Tools**

    Combine with function calling

    [:octicons-arrow-right-24: Tools Guide](tools.md)

- **:material-lightbulb: Multimodal Assistant Tutorial**

    Build a multimodal assistant

    [:octicons-arrow-right-24: Tutorial](../guides/tutorials/multimodal-assistant.md)

</div>
