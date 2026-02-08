# Content Encryption Specification

**Version**: 2.0
**Last Updated**: 2026-02-07

## Overview

This specification defines end-to-end encryption for content in the Agent Runtime API. Encryption is applied at the **content level**, allowing individual content items to be encrypted independently.

**Key Principles:**
- **End-to-End Encryption**: Content encrypted client-side, server treats as opaque
- **Content-Level**: Each content item can be encrypted independently via AIContentBase
- **Simplified Metadata**: Encryption information stored as string attribute
- **External Key Management**: Keys managed outside the runtime (Azure Key Vault, AWS KMS, etc.)
- **Authenticated Encryption**: AES-256-GCM or ChaCha20-Poly1305 (AEAD)

## Encryption Model

### AIContentBase

All content types inherit from **AIContentBase**, which provides the `encryption` attribute:

**TypeSpec Source**: [messages.tsp](../typespec/messages.tsp) (lines 410-448)

```typescript
model AIContentBase {
  /**
   * Encryption information (simplified as string for XML).
   * Contains encryption key reference and metadata.
   *
   * FORMAT: JSON string or key reference
   */
  @xmlAttribute
  encryption?: string;
}
```

### Encryption Attribute Format

The `encryption` attribute accepts multiple formats:

#### Format 1: Simple Key Reference

```
"algorithm:keyId"
```

**Examples**:
- `"aes-256-gcm:key-id-123"`
- `"chacha20-poly1305:key-hipaa-001"`

#### Format 2: Named Encryption Scheme

```
"scheme-name"
```

**Examples**:
- `"hipaa-compliant-v1"`
- `"pci-dss-compliant"`
- `"e2e-encrypted"`

#### Format 3: JSON String (Advanced)

For complex scenarios requiring IV and authTag, use JSON-encoded metadata:

```json
{
  "algorithm": "AES-256-GCM",
  "keyId": "key-123",
  "iv": "randomIvValue123==",
  "authTag": "authTagValue456=="
}
```

Serialize as string in content:
```json
{
  "kind": "text",
  "text": "Encrypted content",
  "encryption": "{\"algorithm\":\"AES-256-GCM\",\"keyId\":\"key-123\",\"iv\":\"...\",\"authTag\":\"...\"}"
}
```

## Supported Algorithms

### AES-256-GCM (Recommended)

**Advanced Encryption Standard with Galois/Counter Mode**:
- **Key Size**: 256 bits (32 bytes)
- **IV Size**: 96 bits (12 bytes)
- **Tag Size**: 128 bits (16 bytes)
- **Properties**: Hardware-accelerated, NIST-approved
- **Use Cases**: Healthcare (HIPAA), finance, regulated industries

**Why GCM?**:
- Authenticated encryption (integrity + confidentiality)
- Parallelizable (fast on modern CPUs)
- FIPS 140-2 approved

### ChaCha20-Poly1305

- **Key Size**: 256 bits (32 bytes)
- **Nonce Size**: 96 bits (12 bytes)
- **Tag Size**: 128 bits (16 bytes)
- **Properties**: Constant-time, mobile-friendly
- **Use Cases**: Mobile apps, embedded systems, non-Intel platforms

**Why ChaCha20?**:
- Constant-time (resistant to timing attacks)
- No hardware acceleration required
- Better performance on ARM/mobile

## Encryption Flow

### Client-Side Encryption

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Client Retrieves Key                                     │
│    - Fetch encryption key from KMS using keyId              │
│    - Key is 256-bit symmetric key                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Client Generates IV                                      │
│    - Generate cryptographically secure random 96-bit IV     │
│    - CRITICAL: IV must be unique for each encryption        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Client Encrypts Content                                  │
│    - Plaintext: Content to encrypt                          │
│    - Algorithm: AES-256-GCM or ChaCha20-Poly1305           │
│    - Output: Ciphertext + Authentication Tag                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Client Encodes for Transport                             │
│    - Base64-encode ciphertext                               │
│    - Base64-encode IV                                       │
│    - Base64-encode authTag                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Client Sends Encrypted Message                           │
│    POST /threads/{threadId}/messages                        │
│    {                                                         │
│      "role": "user",                                        │
│      "contents": [{                                         │
│        "kind": "text",                                      │
│        "text": "U2FsdGVkX1+vupppZksvRf...",              │
│        "encryption": "aes-256-gcm:key-id-123"              │
│      }]                                                     │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

### Server Behavior

**Server MUST:**
1. Store encrypted content as opaque blobs
2. Preserve `encryption` attribute metadata
3. NOT attempt to decrypt content
4. Forward encrypted content to authorized clients
5. Apply same retention/deletion policies as unencrypted content

**Server MUST NOT:**
1. Decrypt content
2. Access encryption keys
3. Log plaintext content
4. Index or search encrypted content

### Client-Side Decryption

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Client Receives Encrypted Message                        │
│    GET /threads/{threadId}/messages                         │
│    Response:                                                │
│    {                                                        │
│      "contents": [{                                        │
│        "kind": "text",                                     │
│        "text": "U2FsdGVkX1+vupppZksvRf...",            │
│        "encryption": "aes-256-gcm:key-id-123"            │
│      }]                                                    │
│    }                                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Client Parses Encryption Metadata                        │
│    - Extract keyId: "key-id-123"                           │
│    - Extract algorithm: "aes-256-gcm"                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Client Retrieves Key                                     │
│    - Fetch decryption key from KMS using keyId              │
│    - Verify client has permission to access key             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Client Decrypts Content                                  │
│    - Base64-decode ciphertext                               │
│    - Base64-decode IV from encryption metadata              │
│    - Base64-decode authTag from encryption metadata         │
│    - Decrypt using algorithm + key + IV                     │
│    - Verify authTag (integrity check)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Client Displays Plaintext                                │
│    - Render decrypted content to user                       │
│    - NEVER log plaintext content                            │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Simple Encrypted Text

**Request**:
```json
POST /threads/thread_123/messages
{
  "role": "user",
  "contents": [
    {
      "kind": "text",
      "text": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=",
      "encryption": "aes-256-gcm:key-id-123"
    }
  ]
}
```

**Response**:
```json
{
  "messageId": "msg_abc123",
  "role": "user",
  "contents": [
    {
      "kind": "text",
      "text": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=",
      "encryption": "aes-256-gcm:key-id-123"
    }
  ]
}
```

### Encrypted Function Result (HIPAA)

**Request**:
```json
POST /threads/thread_456/messages
{
  "role": "tool",
  "contents": [
    {
      "kind": "functionResult",
      "callId": "call_789",
      "name": "lookup_patient_record",
      "result": "eyJwYXRpZW50SWQiOiAiMTIzNCIsICJkaWFnbm9zaXMiOiAi...",
      "encryption": "hipaa-compliant-v1",
      "audience": "assistant"
    }
  ]
}
```

### Mixed Encrypted and Unencrypted Content

**Request**:
```json
POST /threads/thread_789/messages
{
  "role": "assistant",
  "contents": [
    {
      "kind": "text",
      "text": "I found your account information:"
    },
    {
      "kind": "text",
      "text": "eyJhY2NvdW50TnVtYmVyIjogIjEyMzQ1Njc4OTAifQ==",
      "encryption": "aes-256-gcm:key-pci-dss",
      "audience": "user"
    }
  ]
}
```

### XML Format

```xml
<message role="user">
  <text encryption="aes-256-gcm:key-id-123">
    U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=
  </text>
</message>
```

### Advanced: JSON Metadata in Encryption Attribute

```json
{
  "kind": "text",
  "text": "U2FsdGVkX1+vupppZksvRf...",
  "encryption": "{\"algorithm\":\"AES-256-GCM\",\"keyId\":\"key-123\",\"iv\":\"8Kk3Kgz5XjRlipRkwB==\",\"authTag\":\"GxcTlipRkwB0K1Y8Kk3K==\"}"
}
```

## Key Management

### External KMS Integration

**Supported Providers**:
- Azure Key Vault
- AWS KMS
- Google Cloud KMS
- HashiCorp Vault
- Custom KMS implementations

**Key Lifecycle**:
```
1. Key Generation → 2. Key Storage → 3. Key Rotation → 4. Key Deletion
```

### Key Rotation

**Best Practices**:
1. Rotate keys periodically (e.g., every 90 days)
2. Re-encrypt content with new keys
3. Maintain old keys for decryption during transition
4. Update `keyId` references in `encryption` attribute

**Example Key Rotation**:
```json
// Old message (key-id-123)
{
  "kind": "text",
  "text": "old-ciphertext",
  "encryption": "aes-256-gcm:key-id-123"
}

// After rotation (key-id-456)
{
  "kind": "text",
  "text": "new-ciphertext",
  "encryption": "aes-256-gcm:key-id-456"
}
```

## Security Considerations

### DO:
- ✅ Generate cryptographically secure random IVs
- ✅ Use unique IV for each encryption operation
- ✅ Verify authentication tags on decryption
- ✅ Implement key rotation policies
- ✅ Use external KMS for key storage
- ✅ Audit access to encryption keys
- ✅ Encrypt sensitive content (PII, PHI, PCI)

### DON'T:
- ❌ Reuse IVs across multiple encryptions
- ❌ Store keys in application code or config files
- ❌ Log plaintext content
- ❌ Skip authentication tag verification
- ❌ Use weak key derivation functions
- ❌ Implement custom crypto algorithms

## Compliance

### HIPAA (Healthcare)

**Requirements**:
- End-to-end encryption for PHI (Protected Health Information)
- Access controls tied to encryption keys
- Audit logs for key access
- Key rotation policies

**Example**:
```json
{
  "kind": "functionResult",
  "callId": "call_123",
  "name": "get_patient_diagnosis",
  "result": "encrypted-phi-data",
  "encryption": "hipaa-compliant-v1",
  "audience": "assistant"
}
```

### PCI-DSS (Payment Card Industry)

**Requirements**:
- Encrypt cardholder data at rest and in transit
- Protect cryptographic keys
- Implement key management procedures

**Example**:
```json
{
  "kind": "text",
  "text": "encrypted-credit-card-data",
  "encryption": "pci-dss-compliant:key-vault-001"
}
```

### GDPR (General Data Protection Regulation)

**Requirements**:
- Encrypt personal data
- Right to erasure (delete encryption keys)
- Data breach notification

## Implementation Example (Python)

### AES-256-GCM Encryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
import json

def encrypt_content_aes_gcm(plaintext: str, key: bytes, key_id: str) -> dict:
    """Encrypt content with AES-256-GCM"""
    aesgcm = AESGCM(key)  # key must be 32 bytes
    iv = os.urandom(12)   # 96-bit random IV

    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext = aesgcm.encrypt(iv, plaintext_bytes, None)

    # ciphertext includes appended auth tag (last 16 bytes)
    encrypted_data = ciphertext[:-16]
    auth_tag = ciphertext[-16:]

    # Create encryption metadata as JSON string
    encryption_metadata = json.dumps({
        "algorithm": "AES-256-GCM",
        "keyId": key_id,
        "iv": base64.b64encode(iv).decode(),
        "authTag": base64.b64encode(auth_tag).decode()
    })

    return {
        "text": base64.b64encode(encrypted_data).decode(),
        "encryption": encryption_metadata
    }

def decrypt_content_aes_gcm(ciphertext_b64: str, encryption_attr: str, key: bytes) -> str:
    """Decrypt content with AES-256-GCM"""
    aesgcm = AESGCM(key)

    # Parse encryption metadata
    metadata = json.loads(encryption_attr)

    # Decode from base64
    ct = base64.b64decode(ciphertext_b64)
    iv_bytes = base64.b64decode(metadata['iv'])
    tag = base64.b64decode(metadata['authTag'])

    # Reconstruct ciphertext with appended tag
    ciphertext_with_tag = ct + tag

    plaintext_bytes = aesgcm.decrypt(iv_bytes, ciphertext_with_tag, None)
    return plaintext_bytes.decode('utf-8')
```

### Simple Format (Recommended)

For simpler implementations, use the `"algorithm:keyId"` format and store IV/authTag out-of-band or embedded in the ciphertext:

```python
def encrypt_content_simple(plaintext: str, key: bytes, key_id: str) -> dict:
    """Encrypt content with simple encryption format"""
    aesgcm = AESGCM(key)
    iv = os.urandom(12)

    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext = aesgcm.encrypt(iv, plaintext_bytes, None)

    # Prepend IV to ciphertext (IV is not secret)
    combined = iv + ciphertext

    return {
        "text": base64.b64encode(combined).decode(),
        "encryption": f"aes-256-gcm:{key_id}"
    }

def decrypt_content_simple(ciphertext_b64: str, encryption_attr: str, key: bytes) -> str:
    """Decrypt content with simple encryption format"""
    aesgcm = AESGCM(key)

    # Decode from base64
    combined = base64.b64decode(ciphertext_b64)

    # Extract IV (first 12 bytes) and ciphertext
    iv = combined[:12]
    ciphertext_with_tag = combined[12:]

    plaintext_bytes = aesgcm.decrypt(iv, ciphertext_with_tag, None)
    return plaintext_bytes.decode('utf-8')
```

## Related Resources

- [AIContentBase Model](../api-reference/models/aicontentbase.md) - Base model with encryption
- [Content Types](../api-reference/content-types.md) - All content types support encryption
- [Security Compliance Guide](../guides/security-compliance.md) - Implementation patterns
- [TypeSpec Source](../typespec/messages.tsp) - AIContentBase definition (lines 410-448)
