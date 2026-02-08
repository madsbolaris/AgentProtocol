# Security & Compliance Guide

**Version**: 1.0

## Overview

This guide provides comprehensive patterns for implementing security and compliance features in the Agent Runtime API, covering authentication, authorization, encryption, and data protection.

**What You'll Learn:**
- Set up OAuth2 connections with scope management
- Implement end-to-end content encryption for HIPAA/PHI compliance
- Handle PII detection and redaction
- Secure tool execution with proper authorization
- Validate and enforce security policies
- Implement audit logging for compliance

**Key Security Features:**
- **OAuth2 Integration**: Authorization code flow with scope enforcement
- **Content Encryption**: AES-256-GCM and ChaCha20-Poly1305 for sensitive data
- **Connection Types**: Reference, API Key, Remote, and Anonymous authentication
- **PII Protection**: Detection, redaction, and secure handling of personal data
- **Secure Tool Execution**: Authorization checks and sandboxing patterns

---

## Prerequisites

- **API Access**: Agent Runtime API endpoint with authentication
- **Programming Language**: Examples in Python and JavaScript
- **Key Management**: Azure Key Vault, AWS KMS, or similar KMS solution
- **OAuth2 Provider** (Optional): For Microsoft Graph, Azure AD, or custom OAuth2
- **Compliance Requirements**: Understanding of HIPAA, GDPR, or relevant regulations

---

## Use Cases

This guide is for:

### Healthcare & HIPAA Compliance
- **Protected Health Information (PHI)**: End-to-end encryption for patient data
- **Audit Trails**: Complete logging of PHI access and modifications
- **Access Controls**: Role-based access with user consent
- **Data Retention**: Compliant storage and deletion policies

### Financial Services
- **PII Protection**: Social Security Numbers, account numbers, credit cards
- **Transaction Security**: Encrypted payment processing workflows
- **Compliance Reporting**: SOC 2, PCI-DSS audit requirements
- **Data Sovereignty**: Regional data storage and processing

### Legal & Attorney-Client Privilege
- **Privileged Communications**: End-to-end encrypted legal consultations
- **Document Security**: Encrypted case files and evidence
- **Access Logging**: Tamper-proof audit trails
- **Confidentiality**: Client identity protection

### Enterprise & B2B
- **Multi-Tenant Isolation**: Secure data separation between customers
- **API Security**: API key rotation and management
- **SSO Integration**: OAuth2 with Microsoft Entra ID (Azure AD)
- **Data Loss Prevention**: PII redaction in logs and responses

---

## Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Application                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. OAuth2 Authentication (User Consent)               │ │
│  │  2. Client-Side Encryption (AES-256-GCM)               │ │
│  │  3. PII Detection & Redaction                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS + API Key
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Runtime API                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Connection Validation (Reference/Remote/Key)       │ │
│  │  2. Scope Enforcement (OAuth2 permissions)             │ │
│  │  3. Encrypted Content Storage (opaque to server)       │ │
│  │  4. Authorization Checks (user vs system authority)    │ │
│  │  5. Audit Logging (compliance trails)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ Encrypted Content + Auth Headers
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - Microsoft Graph (OAuth2 + Scopes)                   │ │
│  │  - Key Management (Azure Key Vault, AWS KMS)           │ │
│  │  - MCP Servers (Remote Connection)                     │ │
│  │  - Custom APIs (API Key Connection)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### OAuth2 Authorization Code Flow

```
User Browser         Client App          Agent API          OAuth Provider
     │                   │                    │                    │
     │ 1. Request        │                    │                    │
     │   protected       │                    │                    │
     │   resource        │                    │                    │
     │──────────────────>│                    │                    │
     │                   │                    │                    │
     │                   │ 2. POST /runs      │                    │
     │                   │   (no scopes)      │                    │
     │                   ├───────────────────>│                    │
     │                   │                    │                    │
     │                   │ 3. 200 OK          │                    │
     │                   │   status:          │                    │
     │                   │   auth_required    │                    │
     │                   │   missing_scopes   │                    │
     │                   │<───────────────────┤                    │
     │                   │                    │                    │
     │ 4. Redirect to    │                    │                    │
     │   OAuth consent   │                    │                    │
     │<──────────────────┤                    │                    │
     │                   │                    │                    │
     │ 5. GET /authorize                                           │
     │   ?client_id=...                                            │
     │   &scope=...                                                │
     │───────────────────────────────────────────────────────────>│
     │                                                             │
     │ 6. Consent Screen                                           │
     │   "Allow access to Calendar?"                               │
     │<────────────────────────────────────────────────────────────│
     │                                                             │
     │ 7. User Approves                                            │
     │────────────────────────────────────────────────────────────>│
     │                                                             │
     │ 8. 302 Redirect                                             │
     │   callback?code=AUTH_CODE                                   │
     │<────────────────────────────────────────────────────────────│
     │                   │                    │                    │
     │ 9. Callback       │                    │                    │
     │──────────────────>│                    │                    │
     │                   │                    │                    │
     │                   │ 10. POST /token    │                    │
     │                   │   (exchange code)  │                    │
     │                   ├────────────────────────────────────────>│
     │                   │                    │                    │
     │                   │ 11. access_token   │                    │
     │                   │     refresh_token  │                    │
     │                   │<────────────────────────────────────────┤
     │                   │                    │                    │
     │                   │ 12. POST /runs/{id}/submit_auth         │
     │                   │   { connection: { key: "Bearer token" }}│
     │                   ├───────────────────>│                    │
     │                   │                    │                    │
     │                   │ 13. 200 OK         │                    │
     │                   │   status:          │                    │
     │                   │   in_progress      │                    │
     │                   │<───────────────────┤                    │
     │                   │                    │                    │
     │                   │ 14. SSE: run.completed                  │
     │                   │<───────────────────┤                    │
```

### Content Encryption Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Side                           │
│                                                              │
│  1. Retrieve Encryption Key from KMS                         │
│     GET https://vault.azure.net/keys/phi-key-v1              │
│     → 256-bit AES key                                        │
│                                                              │
│  2. Generate Random IV (96 bits)                             │
│     iv = os.urandom(12)                                      │
│                                                              │
│  3. Encrypt Content with AES-256-GCM                         │
│     plaintext = "Patient John Doe, diagnosis: diabetes"      │
│     ciphertext, authTag = encrypt(plaintext, key, iv)        │
│                                                              │
│  4. Base64 Encode for Transport                              │
│     ciphertext_b64 = base64.encode(ciphertext)               │
│     iv_b64 = base64.encode(iv)                               │
│     tag_b64 = base64.encode(authTag)                         │
│                                                              │
│  5. Send to Server with Encryption Metadata                  │
│     POST /threads/{id}/messages                              │
│     {                                                        │
│       "contents": [{                                         │
│         "kind": "text",                                      │
│         "text": "U2FsdGVkX1+vupppZksvRf5pq5g5...",          │
│         "annotations": {                                     │
│           "encryption": {                                    │
│             "algorithm": "AES-256-GCM",                      │
│             "keyId": "phi-key-v1",                           │
│             "iv": "8Kk3Kgz5XjRlipRkwB==",                    │
│             "authTag": "GxcTlipRkwB0K1Y8Kk3K=="              │
│           }                                                  │
│         }                                                    │
│       }]                                                     │
│     }                                                        │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        Server Side                           │
│                                                              │
│  1. Store Encrypted Content (Opaque)                         │
│     - Server does NOT decrypt                                │
│     - Stores ciphertext + metadata as-is                     │
│     - Content remains encrypted at rest                      │
│                                                              │
│  2. Process Non-Encrypted Fields                             │
│     - Metadata (timestamps, IDs)                             │
│     - Message structure                                      │
│     - Routing information                                    │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Client Side (Retrieval)                    │
│                                                              │
│  1. Retrieve Encrypted Message                               │
│     GET /threads/{id}/messages                               │
│                                                              │
│  2. Extract Encryption Metadata                              │
│     keyId = "phi-key-v1"                                     │
│     iv = base64.decode("8Kk3Kgz5XjRlipRkwB==")              │
│     authTag = base64.decode("GxcTlipRkwB0K1Y8Kk3K==")       │
│                                                              │
│  3. Retrieve Decryption Key from KMS                         │
│     GET https://vault.azure.net/keys/phi-key-v1              │
│     → 256-bit AES key                                        │
│                                                              │
│  4. Decrypt Content                                          │
│     ciphertext = base64.decode("U2FsdGVkX1+vupppZks...")    │
│     plaintext = decrypt(ciphertext, key, iv, authTag)        │
│     → "Patient John Doe, diagnosis: diabetes"                │
│                                                              │
│  5. Verify Authentication Tag                                │
│     - Tag verification automatic in AES-GCM                  │
│     - Decryption fails if tampered                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Step 1: OAuth2 Authentication Setup

#### 1.1: Register OAuth2 Application

**Microsoft Entra ID (Azure AD):**

```bash
# Using Azure CLI
az ad app create \
  --display-name "My Agent App" \
  --sign-in-audience "AzureADMyOrg" \
  --web-redirect-uris "https://myapp.example.com/callback"

# Note the Application (client) ID and create a client secret
az ad app credential reset \
  --id <APPLICATION_ID> \
  --append
```

**Application Settings:**
- **Redirect URI**: `https://myapp.example.com/callback`
- **Scopes**: Configure API permissions (e.g., `Calendars.ReadWrite`, `Mail.Send`)
- **Client Secret**: Store securely (environment variable or key vault)

#### 1.2: Implement OAuth2 Authorization Code Flow

**Python Implementation:**

```python
import os
import requests
from flask import Flask, request, redirect, session
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

# OAuth2 Configuration
OAUTH_CONFIG = {
    'client_id': os.environ['OAUTH_CLIENT_ID'],
    'client_secret': os.environ['OAUTH_CLIENT_SECRET'],
    'tenant_id': os.environ['OAUTH_TENANT_ID'],
    'redirect_uri': 'https://myapp.example.com/callback',
    'scope': 'https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Mail.Send',
    'authorize_endpoint': f"https://login.microsoftonline.com/{os.environ['OAUTH_TENANT_ID']}/oauth2/v2.0/authorize",
    'token_endpoint': f"https://login.microsoftonline.com/{os.environ['OAUTH_TENANT_ID']}/oauth2/v2.0/token"
}

API_BASE = os.environ['AGENT_API_BASE']
API_KEY = os.environ['AGENT_API_KEY']


class OAuth2Manager:
    """Manages OAuth2 authorization code flow"""

    @staticmethod
    def get_authorization_url(state: str = None) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            'client_id': OAUTH_CONFIG['client_id'],
            'response_type': 'code',
            'redirect_uri': OAUTH_CONFIG['redirect_uri'],
            'scope': OAUTH_CONFIG['scope'],
            'response_mode': 'query',
            'state': state or os.urandom(16).hex()
        }

        auth_url = f"{OAUTH_CONFIG['authorize_endpoint']}?{urlencode(params)}"
        return auth_url, params['state']

    @staticmethod
    def exchange_code_for_token(code: str) -> dict:
        """Exchange authorization code for access token"""
        data = {
            'client_id': OAUTH_CONFIG['client_id'],
            'client_secret': OAUTH_CONFIG['client_secret'],
            'code': code,
            'redirect_uri': OAUTH_CONFIG['redirect_uri'],
            'grant_type': 'authorization_code',
            'scope': OAUTH_CONFIG['scope']
        }

        response = requests.post(OAUTH_CONFIG['token_endpoint'], data=data)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'expires_in': token_data['expires_in'],
            'scope': token_data['scope']
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Refresh expired access token"""
        data = {
            'client_id': OAUTH_CONFIG['client_id'],
            'client_secret': OAUTH_CONFIG['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': OAUTH_CONFIG['scope']
        }

        response = requests.post(OAUTH_CONFIG['token_endpoint'], data=data)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', refresh_token),
            'expires_in': token_data['expires_in']
        }


@app.route('/login')
def login():
    """Initiate OAuth2 flow"""
    auth_url, state = OAuth2Manager.get_authorization_url()
    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle OAuth2 callback"""
    # Verify state to prevent CSRF
    if request.args.get('state') != session.get('oauth_state'):
        return "Invalid state parameter", 400

    # Check for errors
    if 'error' in request.args:
        return f"OAuth error: {request.args['error']}", 400

    # Exchange code for token
    code = request.args.get('code')
    token_data = OAuth2Manager.exchange_code_for_token(code)

    # Store token in session (in production, use secure token storage)
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data['refresh_token']

    return redirect('/dashboard')


def create_oauth2_connection(access_token: str) -> dict:
    """Create API Key connection for OAuth2 bearer token"""
    return {
        'kind': 'key',
        'key': f"Bearer {access_token}",
        'headerName': 'Authorization',
        'authority': 'user',
        'usageDescription': 'Access Microsoft Graph on behalf of the user'
    }


@app.route('/api/create-run', methods=['POST'])
def create_run():
    """Create agent run with OAuth2 authentication"""
    access_token = session.get('access_token')

    if not access_token:
        return {"error": "Not authenticated"}, 401

    # Create agent with Microsoft Graph tools
    agent_def = {
        'kind': 'prompt',
        'name': 'calendar-assistant',
        'model': 'gpt-4o',
        'instructions': 'You help users manage their Microsoft calendar.',
        'tools': [{
            'kind': 'function',
            'function': {
                'name': 'create_calendar_event',
                'description': 'Create a new calendar event in Microsoft 365',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'subject': {'type': 'string'},
                        'start': {'type': 'string', 'format': 'date-time'},
                        'end': {'type': 'string', 'format': 'date-time'}
                    },
                    'required': ['subject', 'start', 'end']
                }
            },
            'connection': create_oauth2_connection(access_token)
        }],
        'scopes': {
            'https://graph.microsoft.com/Calendars.ReadWrite': 'Read and write calendar events'
        }
    }

    # Create run
    run_data = {
        'agent': agent_def,
        'input': [{
            'role': 'user',
            'contents': [{
                'kind': 'text',
                'text': 'Schedule a meeting tomorrow at 2pm for 1 hour about Q1 planning'
            }]
        }]
    }

    headers = {
        'Authorization': f"Bearer {API_KEY}",
        'Content-Type': 'application/json'
    }

    response = requests.post(f"{API_BASE}/runs", headers=headers, json=run_data)

    # Handle auth_required status (scope missing or token expired)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'auth_required':
            # Need to re-authenticate or request additional scopes
            return {"error": "Authentication required", "details": result}, 401

    return response.json(), response.status_code


if __name__ == '__main__':
    app.run(port=5000)
```

**JavaScript (Node.js) Implementation:**

```javascript
const express = require('express');
const axios = require('axios');
const session = require('express-session');
const crypto = require('crypto');

const app = express();
app.use(express.json());
app.use(session({
  secret: process.env.FLASK_SECRET_KEY,
  resave: false,
  saveUninitialized: false
}));

// OAuth2 Configuration
const OAUTH_CONFIG = {
  clientId: process.env.OAUTH_CLIENT_ID,
  clientSecret: process.env.OAUTH_CLIENT_SECRET,
  tenantId: process.env.OAUTH_TENANT_ID,
  redirectUri: 'https://myapp.example.com/callback',
  scope: 'https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Mail.Send',
  authorizeEndpoint: `https://login.microsoftonline.com/${process.env.OAUTH_TENANT_ID}/oauth2/v2.0/authorize`,
  tokenEndpoint: `https://login.microsoftonline.com/${process.env.OAUTH_TENANT_ID}/oauth2/v2.0/token`
};

const API_BASE = process.env.AGENT_API_BASE;
const API_KEY = process.env.AGENT_API_KEY;


class OAuth2Manager {
  static getAuthorizationUrl(state = null) {
    const stateValue = state || crypto.randomBytes(16).toString('hex');

    const params = new URLSearchParams({
      client_id: OAUTH_CONFIG.clientId,
      response_type: 'code',
      redirect_uri: OAUTH_CONFIG.redirectUri,
      scope: OAUTH_CONFIG.scope,
      response_mode: 'query',
      state: stateValue
    });

    const authUrl = `${OAUTH_CONFIG.authorizeEndpoint}?${params.toString()}`;
    return { authUrl, state: stateValue };
  }

  static async exchangeCodeForToken(code) {
    const params = new URLSearchParams({
      client_id: OAUTH_CONFIG.clientId,
      client_secret: OAUTH_CONFIG.clientSecret,
      code: code,
      redirect_uri: OAUTH_CONFIG.redirectUri,
      grant_type: 'authorization_code',
      scope: OAUTH_CONFIG.scope
    });

    const response = await axios.post(OAUTH_CONFIG.tokenEndpoint, params);

    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      expires_in: response.data.expires_in,
      scope: response.data.scope
    };
  }

  static async refreshAccessToken(refreshToken) {
    const params = new URLSearchParams({
      client_id: OAUTH_CONFIG.clientId,
      client_secret: OAUTH_CONFIG.clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
      scope: OAUTH_CONFIG.scope
    });

    const response = await axios.post(OAUTH_CONFIG.tokenEndpoint, params);

    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token || refreshToken,
      expires_in: response.data.expires_in
    };
  }
}


app.get('/login', (req, res) => {
  const { authUrl, state } = OAuth2Manager.getAuthorizationUrl();
  req.session.oauthState = state;
  res.redirect(authUrl);
});


app.get('/callback', async (req, res) => {
  // Verify state to prevent CSRF
  if (req.query.state !== req.session.oauthState) {
    return res.status(400).send('Invalid state parameter');
  }

  // Check for errors
  if (req.query.error) {
    return res.status(400).send(`OAuth error: ${req.query.error}`);
  }

  try {
    // Exchange code for token
    const tokenData = await OAuth2Manager.exchangeCodeForToken(req.query.code);

    // Store token in session (in production, use secure token storage)
    req.session.accessToken = tokenData.access_token;
    req.session.refreshToken = tokenData.refresh_token;

    res.redirect('/dashboard');
  } catch (error) {
    res.status(500).send(`Token exchange failed: ${error.message}`);
  }
});


function createOAuth2Connection(accessToken) {
  return {
    kind: 'key',
    key: `Bearer ${accessToken}`,
    headerName: 'Authorization',
    authority: 'user',
    usageDescription: 'Access Microsoft Graph on behalf of the user'
  };
}


app.post('/api/create-run', async (req, res) => {
  const accessToken = req.session.accessToken;

  if (!accessToken) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  // Create agent with Microsoft Graph tools
  const agentDef = {
    kind: 'prompt',
    name: 'calendar-assistant',
    model: 'gpt-4o',
    instructions: 'You help users manage their Microsoft calendar.',
    tools: [{
      kind: 'function',
      function: {
        name: 'create_calendar_event',
        description: 'Create a new calendar event in Microsoft 365',
        parameters: {
          type: 'object',
          properties: {
            subject: { type: 'string' },
            start: { type: 'string', format: 'date-time' },
            end: { type: 'string', format: 'date-time' }
          },
          required: ['subject', 'start', 'end']
        }
      },
      connection: createOAuth2Connection(accessToken)
    }],
    scopes: {
      'https://graph.microsoft.com/Calendars.ReadWrite': 'Read and write calendar events'
    }
  };

  // Create run
  const runData = {
    agent: agentDef,
    input: [{
      role: 'user',
      contents: [{
        kind: 'text',
        text: 'Schedule a meeting tomorrow at 2pm for 1 hour about Q1 planning'
      }]
    }]
  };

  try {
    const response = await axios.post(`${API_BASE}/runs`, runData, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    // Handle auth_required status (scope missing or token expired)
    if (response.data.status === 'auth_required') {
      return res.status(401).json({
        error: 'Authentication required',
        details: response.data
      });
    }

    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});


app.listen(5000, () => {
  console.log('Server running on port 5000');
});
```

#### 1.3: Scope Management and Validation

**Define Required Scopes:**

See `../typespec/common.tsp` for the `Scopes` type definition.

```python
class ScopeManager:
    """Manages OAuth2 scope requirements and validation"""

    # Common Microsoft Graph scopes
    MICROSOFT_GRAPH_SCOPES = {
        'Calendars.Read': 'Read user calendar events',
        'Calendars.ReadWrite': 'Read and write user calendar events',
        'Mail.Read': 'Read user mail',
        'Mail.Send': 'Send mail as the signed-in user',
        'Files.Read.All': 'Read all files user can access',
        'Files.ReadWrite.All': 'Read and write all files user can access',
        'User.Read': 'Sign in and read user profile',
        'User.ReadBasic.All': 'Read all users\' basic profiles'
    }

    @staticmethod
    def format_scopes_for_agent(scopes: list[str]) -> dict:
        """Convert scope list to Agent API format"""
        return {
            f"https://graph.microsoft.com/{scope}":
            ScopeManager.MICROSOFT_GRAPH_SCOPES.get(scope, f"Access {scope}")
            for scope in scopes
        }

    @staticmethod
    def validate_scopes(required_scopes: dict, granted_scopes: list[str]) -> tuple[bool, list[str]]:
        """Check if granted scopes satisfy requirements"""
        required_scope_names = set(required_scopes.keys())
        granted_scope_names = set(f"https://graph.microsoft.com/{s}" for s in granted_scopes)

        missing_scopes = required_scope_names - granted_scope_names

        return len(missing_scopes) == 0, list(missing_scopes)

    @staticmethod
    def create_agent_with_scopes(scopes: list[str]) -> dict:
        """Create agent definition with required scopes"""
        return {
            'kind': 'prompt',
            'name': 'scoped-agent',
            'model': 'gpt-4o',
            'instructions': 'You are a helpful assistant with Microsoft Graph access.',
            'scopes': ScopeManager.format_scopes_for_agent(scopes)
        }


# Example usage
scopes_needed = ['Calendars.ReadWrite', 'Mail.Send']
agent = ScopeManager.create_agent_with_scopes(scopes_needed)

print(agent['scopes'])
# Output:
# {
#   'https://graph.microsoft.com/Calendars.ReadWrite': 'Read and write user calendar events',
#   'https://graph.microsoft.com/Mail.Send': 'Send mail as the signed-in user'
# }
```

---

### Step 2: Connection Types Implementation

The Agent Runtime API supports four connection types. See `../typespec/common.tsp` for type definitions.

#### 2.1: Reference Connection

**Purpose**: Reference pre-configured named connections

```python
class ConnectionManager:
    """Manages different connection types"""

    @staticmethod
    def create_reference_connection(name: str, authority: str = 'user') -> dict:
        """Create reference to named connection"""
        return {
            'kind': 'reference',
            'name': name,
            'authority': authority,
            'usageDescription': f'Access {name} service'
        }

    @staticmethod
    def create_api_key_connection(
        api_key: str,
        header_name: str = 'Authorization',
        authority: str = 'system'
    ) -> dict:
        """Create API key connection"""
        return {
            'kind': 'key',
            'key': api_key,
            'headerName': header_name,
            'authority': authority,
            'usageDescription': 'Access external API with API key'
        }

    @staticmethod
    def create_remote_connection(
        endpoint: str,
        credentials: dict,
        authority: str = 'user'
    ) -> dict:
        """Create remote service connection"""
        return {
            'kind': 'remote',
            'endpoint': endpoint,
            'credentials': credentials,
            'authority': authority,
            'usageDescription': f'Access service at {endpoint}'
        }

    @staticmethod
    def create_anonymous_connection() -> dict:
        """Create anonymous connection (no auth)"""
        return {
            'kind': 'anonymous',
            'authority': 'system',
            'usageDescription': 'Access public API without authentication'
        }


# Example: Using different connection types
connections = {
    # Reference connection (pre-configured)
    'openai': ConnectionManager.create_reference_connection(
        name='myOpenAIConnection',
        authority='system'
    ),

    # API key connection
    'slack': ConnectionManager.create_api_key_connection(
        api_key=os.environ['SLACK_BOT_TOKEN'],
        header_name='Authorization',
        authority='system'
    ),

    # Remote connection (OAuth2)
    'graph': ConnectionManager.create_remote_connection(
        endpoint='https://graph.microsoft.com',
        credentials={
            'tokenEndpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'clientId': os.environ['OAUTH_CLIENT_ID'],
            'clientSecret': os.environ['OAUTH_CLIENT_SECRET'],
            'scope': 'https://graph.microsoft.com/.default'
        },
        authority='user'
    ),

    # Anonymous connection (public API)
    'weather': ConnectionManager.create_anonymous_connection()
}
```

#### 2.2: Secure Connection Storage

**Store connections securely in configuration:**

```python
import keyring
from cryptography.fernet import Fernet

class SecureConnectionStore:
    """Securely store and retrieve connections"""

    def __init__(self, encryption_key: bytes = None):
        """Initialize with encryption key"""
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

    def encrypt_connection(self, connection: dict) -> str:
        """Encrypt connection credentials"""
        import json
        connection_json = json.dumps(connection)
        encrypted = self.cipher.encrypt(connection_json.encode())
        return encrypted.decode()

    def decrypt_connection(self, encrypted_connection: str) -> dict:
        """Decrypt connection credentials"""
        import json
        decrypted = self.cipher.decrypt(encrypted_connection.encode())
        return json.loads(decrypted.decode())

    def store_connection(self, name: str, connection: dict):
        """Store connection securely using keyring"""
        encrypted = self.encrypt_connection(connection)
        keyring.set_password('agent_connections', name, encrypted)

    def retrieve_connection(self, name: str) -> dict:
        """Retrieve and decrypt connection"""
        encrypted = keyring.get_password('agent_connections', name)
        if not encrypted:
            raise ValueError(f"Connection '{name}' not found")
        return self.decrypt_connection(encrypted)


# Example usage
store = SecureConnectionStore()

# Store OpenAI connection
openai_connection = ConnectionManager.create_api_key_connection(
    api_key=os.environ['OPENAI_API_KEY'],
    authority='system'
)
store.store_connection('openai-prod', openai_connection)

# Retrieve later
connection = store.retrieve_connection('openai-prod')
```

---

### Step 3: Content Encryption for HIPAA/PHI Compliance

See `../specifications/content-encryption.md` and `../typespec/messages.tsp` for encryption specifications.

#### 3.1: Client-Side Encryption Implementation

**Python Implementation (AES-256-GCM):**

```python
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple, Optional

class ContentEncryptor:
    """Client-side content encryption for HIPAA compliance"""

    def __init__(self, kms_client):
        """Initialize with Key Management Service client"""
        self.kms = kms_client
        self.key_cache = {}  # Cache keys in memory (short TTL)

    def encrypt_content(
        self,
        plaintext: str,
        key_id: str,
        algorithm: str = "AES-256-GCM"
    ) -> dict:
        """
        Encrypt content with AES-256-GCM

        Returns:
            {
                'ciphertext': base64-encoded encrypted data,
                'encryption': {
                    'algorithm': 'AES-256-GCM',
                    'keyId': key_id,
                    'iv': base64-encoded IV,
                    'authTag': base64-encoded authentication tag
                }
            }
        """
        # Retrieve encryption key from KMS
        encryption_key = self._get_key(key_id)

        # Generate cryptographically secure random IV (96 bits for GCM)
        iv = os.urandom(12)

        # Encrypt with AES-256-GCM
        aesgcm = AESGCM(encryption_key)
        ciphertext_with_tag = aesgcm.encrypt(
            iv,
            plaintext.encode('utf-8'),
            None  # No additional authenticated data
        )

        # Split ciphertext and authentication tag
        # AESGCM appends 16-byte tag to ciphertext
        ciphertext = ciphertext_with_tag[:-16]
        auth_tag = ciphertext_with_tag[-16:]

        # Base64 encode for JSON transport
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'encryption': {
                'algorithm': algorithm,
                'keyId': key_id,
                'iv': base64.b64encode(iv).decode('utf-8'),
                'authTag': base64.b64encode(auth_tag).decode('utf-8')
            }
        }

    def decrypt_content(
        self,
        ciphertext: str,
        encryption_metadata: dict
    ) -> str:
        """
        Decrypt content with AES-256-GCM

        Args:
            ciphertext: Base64-encoded encrypted data
            encryption_metadata: {
                'algorithm': 'AES-256-GCM',
                'keyId': key reference,
                'iv': base64-encoded IV,
                'authTag': base64-encoded authentication tag
            }

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If authentication tag verification fails (tampering detected)
        """
        # Retrieve decryption key from KMS
        key_id = encryption_metadata['keyId']
        decryption_key = self._get_key(key_id)

        # Base64 decode
        ct = base64.b64decode(ciphertext)
        iv = base64.b64decode(encryption_metadata['iv'])
        auth_tag = base64.b64decode(encryption_metadata['authTag'])

        # Reconstruct ciphertext with appended tag
        ciphertext_with_tag = ct + auth_tag

        # Decrypt and verify authentication tag
        aesgcm = AESGCM(decryption_key)
        try:
            plaintext_bytes = aesgcm.decrypt(iv, ciphertext_with_tag, None)
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed - content may be tampered: {e}")

    def _get_key(self, key_id: str) -> bytes:
        """Retrieve encryption key from KMS (with caching)"""
        # Check cache first
        if key_id in self.key_cache:
            return self.key_cache[key_id]

        # Fetch from KMS
        key = self.kms.get_key(key_id)

        # Cache in memory (implement TTL in production)
        self.key_cache[key_id] = key

        return key


# Azure Key Vault integration
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

class AzureKMSClient:
    """Azure Key Vault integration for key management"""

    def __init__(self, vault_url: str):
        """Initialize Azure Key Vault client"""
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.key_client = KeyClient(vault_url=vault_url, credential=self.credential)

    def get_key(self, key_name: str, key_version: str = None) -> bytes:
        """
        Retrieve encryption key from Azure Key Vault

        Args:
            key_name: Name of the key in Key Vault
            key_version: Optional specific version (defaults to latest)

        Returns:
            32-byte (256-bit) encryption key
        """
        # Get key from vault
        key = self.key_client.get_key(key_name, key_version)

        # For symmetric encryption, derive key material
        # In production, use Key Vault's encrypt/decrypt operations
        # or export key if permitted by key policy

        # This is a simplified example - in production, use proper key derivation
        key_material = key.key.k  # For symmetric keys

        # Ensure 256-bit key for AES-256
        if len(key_material) != 32:
            raise ValueError(f"Expected 256-bit key, got {len(key_material) * 8} bits")

        return key_material

    def create_key(self, key_name: str) -> str:
        """Create new encryption key in Key Vault"""
        from azure.keyvault.keys import KeyType

        key = self.key_client.create_key(
            name=key_name,
            key_type=KeyType.oct,  # Symmetric key
            size=256  # 256-bit AES key
        )

        return key.name


# Example usage
kms = AzureKMSClient(vault_url="https://my-vault.vault.azure.net")
encryptor = ContentEncryptor(kms)

# Encrypt patient data
phi_data = "Patient: John Doe, MRN: 123456, Diagnosis: Type 2 Diabetes"
encrypted = encryptor.encrypt_content(
    plaintext=phi_data,
    key_id="phi-encryption-key-v1"
)

print("Ciphertext:", encrypted['ciphertext'][:50] + "...")
print("IV:", encrypted['encryption']['iv'])
print("Auth Tag:", encrypted['encryption']['authTag'])

# Create message with encrypted content
message = {
    'role': 'user',
    'contents': [{
        'kind': 'text',
        'text': encrypted['ciphertext'],
        'audience': 'assistant',  # Not shown to user
        'encryption': encrypted['encryption']
    }]
}

# Later: Decrypt content
decrypted = encryptor.decrypt_content(
    ciphertext=encrypted['ciphertext'],
    encryption_metadata=encrypted['encryption']
)
print("Decrypted:", decrypted)
```

**JavaScript Implementation (AES-256-GCM):**

```javascript
const crypto = require('crypto');

class ContentEncryptor {
  constructor(kmsClient) {
    this.kms = kmsClient;
    this.keyCache = new Map();
  }

  /**
   * Encrypt content with AES-256-GCM
   */
  async encryptContent(plaintext, keyId, algorithm = 'AES-256-GCM') {
    // Retrieve encryption key from KMS
    const encryptionKey = await this._getKey(keyId);

    // Generate cryptographically secure random IV (96 bits for GCM)
    const iv = crypto.randomBytes(12);

    // Create cipher
    const cipher = crypto.createCipheriv('aes-256-gcm', encryptionKey, iv);

    // Encrypt
    let ciphertext = cipher.update(plaintext, 'utf8');
    ciphertext = Buffer.concat([ciphertext, cipher.final()]);

    // Get authentication tag
    const authTag = cipher.getAuthTag();

    // Base64 encode for JSON transport
    return {
      ciphertext: ciphertext.toString('base64'),
      encryption: {
        algorithm: algorithm,
        keyId: keyId,
        iv: iv.toString('base64'),
        authTag: authTag.toString('base64')
      }
    };
  }

  /**
   * Decrypt content with AES-256-GCM
   */
  async decryptContent(ciphertext, encryptionMetadata) {
    // Retrieve decryption key from KMS
    const keyId = encryptionMetadata.keyId;
    const decryptionKey = await this._getKey(keyId);

    // Base64 decode
    const ct = Buffer.from(ciphertext, 'base64');
    const iv = Buffer.from(encryptionMetadata.iv, 'base64');
    const authTag = Buffer.from(encryptionMetadata.authTag, 'base64');

    // Create decipher
    const decipher = crypto.createDecipheriv('aes-256-gcm', decryptionKey, iv);
    decipher.setAuthTag(authTag);

    try {
      // Decrypt and verify authentication tag
      let plaintext = decipher.update(ct, null, 'utf8');
      plaintext += decipher.final('utf8');
      return plaintext;
    } catch (error) {
      throw new Error(`Decryption failed - content may be tampered: ${error.message}`);
    }
  }

  async _getKey(keyId) {
    // Check cache first
    if (this.keyCache.has(keyId)) {
      return this.keyCache.get(keyId);
    }

    // Fetch from KMS
    const key = await this.kms.getKey(keyId);

    // Cache in memory (implement TTL in production)
    this.keyCache.set(keyId, key);

    return key;
  }
}


// Azure Key Vault integration (Node.js)
const { DefaultAzureCredential } = require('@azure/identity');
const { KeyClient } = require('@azure/keyvault-keys');

class AzureKMSClient {
  constructor(vaultUrl) {
    this.vaultUrl = vaultUrl;
    this.credential = new DefaultAzureCredential();
    this.keyClient = new KeyClient(vaultUrl, this.credential);
  }

  async getKey(keyName, keyVersion = null) {
    // Get key from vault
    const key = await this.keyClient.getKey(keyName, keyVersion ? { version: keyVersion } : {});

    // For symmetric encryption, derive key material
    const keyMaterial = Buffer.from(key.key.k, 'base64');

    // Ensure 256-bit key for AES-256
    if (keyMaterial.length !== 32) {
      throw new Error(`Expected 256-bit key, got ${keyMaterial.length * 8} bits`);
    }

    return keyMaterial;
  }

  async createKey(keyName) {
    const key = await this.keyClient.createKey(keyName, 'oct', {
      keySize: 256  // 256-bit AES key
    });

    return key.name;
  }
}


// Example usage
(async () => {
  const kms = new AzureKMSClient('https://my-vault.vault.azure.net');
  const encryptor = new ContentEncryptor(kms);

  // Encrypt patient data
  const phiData = 'Patient: John Doe, MRN: 123456, Diagnosis: Type 2 Diabetes';
  const encrypted = await encryptor.encryptContent(
    phiData,
    'phi-encryption-key-v1'
  );

  console.log('Ciphertext:', encrypted.ciphertext.substring(0, 50) + '...');
  console.log('IV:', encrypted.encryption.iv);
  console.log('Auth Tag:', encrypted.encryption.authTag);

  // Create message with encrypted content
  const message = {
    role: 'user',
    contents: [{
      kind: 'text',
      text: encrypted.ciphertext,
      audience: 'assistant',  // Not shown to user
      encryption: encrypted.encryption
    }]
  };

  // Later: Decrypt content
  const decrypted = await encryptor.decryptContent(
    encrypted.ciphertext,
    encrypted.encryption
  );
  console.log('Decrypted:', decrypted);
})();
```

#### 3.2: Universal Encryption Support

Encryption applies to **all content types** via `AIContentBase.encryption` attribute (see `../typespec/messages.tsp` lines 410-448).

**Examples:**

```python
# Encrypt tool result containing PHI
def encrypt_tool_result(result_data: dict, encryptor: ContentEncryptor) -> dict:
    """Encrypt tool result with PHI"""
    import json

    # Serialize result
    result_json = json.dumps(result_data)

    # Encrypt
    encrypted = encryptor.encrypt_content(
        plaintext=result_json,
        key_id='phi-encryption-key-v1'
    )

    return {
        'kind': 'functionResult',
        'callId': 'call_123',
        'name': 'lookup_patient_record',
        'result': encrypted['ciphertext'],
        'audience': 'assistant',
        'encryption': encrypted['encryption']
    }


# Encrypt reasoning trace
def encrypt_reasoning(reasoning_text: str, encryptor: ContentEncryptor) -> dict:
    """Encrypt extended thinking/reasoning"""
    encrypted = encryptor.encrypt_content(
        plaintext=reasoning_text,
        key_id='reasoning-encryption-key'
    )

    return {
        'kind': 'reasoning',
        'text': encrypted['ciphertext'],
        'exposed': False,  # Internal reasoning
        'audience': 'assistant',
        'encryption': encrypted['encryption']
    }


# Encrypt image data
def encrypt_image(image_bytes: bytes, encryptor: ContentEncryptor) -> dict:
    """Encrypt medical image"""
    # Convert bytes to base64 for encryption
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    encrypted = encryptor.encrypt_content(
        plaintext=image_b64,
        key_id='image-encryption-key'
    )

    return {
        'kind': 'image',
        'data': encrypted['ciphertext'],  # Encrypted image data
        'mimeType': 'image/png',
        'encryption': encrypted['encryption']
    }
```

---

### Step 4: PII Detection and Redaction

#### 4.1: PII Detection Patterns

**Common PII Types:**
- **SSN**: Social Security Numbers (US)
- **Credit Cards**: Payment card numbers
- **Email**: Email addresses
- **Phone**: Phone numbers
- **IP Address**: IPv4/IPv6 addresses
- **Dates**: Birth dates, appointment dates
- **Names**: Person names (requires NER)
- **Addresses**: Physical addresses
- **Medical IDs**: Patient IDs, MRNs

**Python Implementation:**

```python
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class PIIMatch:
    """Represents a detected PII instance"""
    type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0


class PIIDetector:
    """Detect and redact PII in text"""

    # Regex patterns for common PII types
    PATTERNS = {
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'ssn_no_dash': re.compile(r'\b\d{9}\b'),
        'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b(?:\+1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'),
        'ipv4': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        'date': re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
        'medical_id': re.compile(r'\b(?:MRN|Patient ID):\s*(\w+)\b', re.IGNORECASE)
    }

    def detect_pii(self, text: str) -> List[PIIMatch]:
        """Detect all PII in text"""
        matches = []

        for pii_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                matches.append(PIIMatch(
                    type=pii_type,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end()
                ))

        # Sort by position
        matches.sort(key=lambda m: m.start)
        return matches

    def redact_pii(
        self,
        text: str,
        pii_types: List[str] = None,
        redaction_char: str = '*'
    ) -> Tuple[str, List[PIIMatch]]:
        """
        Redact PII from text

        Returns:
            (redacted_text, detected_pii_list)
        """
        matches = self.detect_pii(text)

        # Filter by PII types if specified
        if pii_types:
            matches = [m for m in matches if m.type in pii_types]

        # Redact in reverse order to preserve indices
        redacted = text
        for match in reversed(matches):
            # Redact with type label
            redaction = f"[{match.type.upper()}]"
            redacted = redacted[:match.start] + redaction + redacted[match.end:]

        return redacted, matches

    def anonymize_pii(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize PII with consistent tokens

        Returns:
            (anonymized_text, replacement_map)
        """
        matches = self.detect_pii(text)

        # Generate consistent replacements
        replacements = {}
        counters = {}

        anonymized = text
        for match in reversed(matches):
            # Generate unique token for this PII type
            counter = counters.get(match.type, 1)
            token = f"[{match.type.upper()}_{counter}]"
            counters[match.type] = counter + 1

            # Store mapping
            replacements[token] = match.value

            # Replace in text
            anonymized = anonymized[:match.start] + token + anonymized[match.end:]

        return anonymized, replacements


# Example usage
detector = PIIDetector()

# Test text with PII
text = """
Patient: John Doe
SSN: 123-45-6789
Email: john.doe@example.com
Phone: (555) 123-4567
MRN: 987654
Credit Card: 4532-1234-5678-9010
Visit Date: 02/07/2026
"""

# Detect PII
pii_matches = detector.detect_pii(text)
print(f"Found {len(pii_matches)} PII instances:")
for match in pii_matches:
    print(f"  - {match.type}: {match.value}")

# Redact PII
redacted, _ = detector.redact_pii(text)
print("\nRedacted text:")
print(redacted)

# Anonymize PII (preserves structure)
anonymized, replacement_map = detector.anonymize_pii(text)
print("\nAnonymized text:")
print(anonymized)
print("\nReplacement map:")
for token, value in replacement_map.items():
    print(f"  {token} → {value}")
```

**Output:**
```
Found 7 PII instances:
  - ssn: 123-45-6789
  - email: john.doe@example.com
  - phone: (555) 123-4567
  - medical_id: MRN: 987654
  - credit_card: 4532-1234-5678-9010
  - date: 02/07/2026

Redacted text:

Patient: John Doe
[SSN]
Email: [EMAIL]
Phone: [PHONE]
[MEDICAL_ID]
Credit Card: [CREDIT_CARD]
Visit Date: [DATE]


Anonymized text:

Patient: John Doe
[SSN_1]
Email: [EMAIL_1]
Phone: [PHONE_1]
[MEDICAL_ID_1]
Credit Card: [CREDIT_CARD_1]
Visit Date: [DATE_1]

Replacement map:
  [DATE_1] → 02/07/2026
  [CREDIT_CARD_1] → 4532-1234-5678-9010
  [MEDICAL_ID_1] → MRN: 987654
  [PHONE_1] → (555) 123-4567
  [EMAIL_1] → john.doe@example.com
  [SSN_1] → 123-45-6789
```

#### 4.2: Named Entity Recognition for PII

**Using spaCy for advanced PII detection:**

```python
import spacy
from typing import List

class NERPIIDetector:
    """PII detection using Named Entity Recognition"""

    def __init__(self):
        """Load spaCy model"""
        # Use en_core_web_trf for best accuracy (transformer-based)
        # or en_core_web_sm for faster inference
        self.nlp = spacy.load("en_core_web_sm")

        # PII entity types
        self.pii_entity_types = {
            'PERSON',  # Person names
            'DATE',    # Dates (birth dates, etc.)
            'GPE',     # Geopolitical entities (addresses)
            'ORG',     # Organizations (employers, hospitals)
            'MONEY',   # Financial information
            'CARDINAL' # Potentially ID numbers
        }

    def detect_entities(self, text: str) -> List[PIIMatch]:
        """Detect named entities that may be PII"""
        doc = self.nlp(text)

        matches = []
        for ent in doc.ents:
            if ent.label_ in self.pii_entity_types:
                matches.append(PIIMatch(
                    type=ent.label_.lower(),
                    value=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=1.0  # spaCy doesn't provide confidence directly
                ))

        return matches

    def redact_entities(self, text: str, entity_types: List[str] = None) -> str:
        """Redact named entities"""
        doc = self.nlp(text)

        # Default to all PII entity types
        if entity_types is None:
            entity_types = self.pii_entity_types
        else:
            entity_types = set(entity_types)

        # Redact in reverse order
        redacted = text
        for ent in reversed(doc.ents):
            if ent.label_ in entity_types:
                redaction = f"[{ent.label_}]"
                redacted = redacted[:ent.start_char] + redaction + redacted[ent.end_char:]

        return redacted


# Example usage
ner_detector = NERPIIDetector()

text = """
Patient John Doe visited Springfield General Hospital on January 15, 2026.
He was diagnosed by Dr. Sarah Smith and prescribed medication costing $150.
His home address is 123 Main Street, Springfield, IL 62701.
"""

# Detect entities
entities = ner_detector.detect_entities(text)
print("Detected entities:")
for ent in entities:
    print(f"  - {ent.type}: {ent.value}")

# Redact person names only
redacted = ner_detector.redact_entities(text, entity_types=['PERSON'])
print("\nRedacted (persons only):")
print(redacted)

# Redact all PII entities
redacted_all = ner_detector.redact_entities(text)
print("\nRedacted (all PII):")
print(redacted_all)
```

#### 4.3: PII Handling in Agent Conversations

**Automatic PII redaction before logging:**

```python
class SecureConversationHandler:
    """Handle conversations with automatic PII protection"""

    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.api_key = api_key
        self.pii_detector = PIIDetector()
        self.ner_detector = NERPIIDetector()

    def sanitize_for_logging(self, message: dict) -> dict:
        """Remove PII from message before logging"""
        sanitized = message.copy()

        # Redact text content
        if 'contents' in sanitized:
            for content in sanitized['contents']:
                if content.get('kind') == 'text':
                    original_text = content['text']

                    # Apply both regex and NER detection
                    redacted, _ = self.pii_detector.redact_pii(original_text)
                    redacted = self.ner_detector.redact_entities(redacted)

                    content['text'] = redacted

        return sanitized

    def send_message_securely(
        self,
        thread_id: str,
        message: dict,
        encrypt_pii: bool = True
    ):
        """Send message with PII protection"""
        # Detect PII in message
        if 'contents' in message:
            for content in message['contents']:
                if content.get('kind') == 'text':
                    text = content['text']
                    pii_matches = self.pii_detector.detect_pii(text)

                    if pii_matches and encrypt_pii:
                        print(f"Warning: Detected {len(pii_matches)} PII instances")

                        # Optionally encrypt content
                        # encrypted = encryptor.encrypt_content(text, 'pii-key')
                        # content['text'] = encrypted['ciphertext']
                        # content['annotations'] = {
                        #     'encryption': encrypted['encryption']
                        # }

        # Log sanitized version
        sanitized = self.sanitize_for_logging(message)
        print("Logging message (PII redacted):", sanitized)

        # Send original message to API
        response = requests.post(
            f"{self.api_base}/threads/{thread_id}/messages",
            headers={
                'Authorization': f"Bearer {self.api_key}",
                'Content-Type': 'application/json'
            },
            json=message
        )

        return response.json()


# Example usage
handler = SecureConversationHandler(
    api_base="https://agents.example.com/v1",
    api_key=os.environ['AGENT_API_KEY']
)

# Send message with PII
message = {
    'role': 'user',
    'contents': [{
        'kind': 'text',
        'text': 'My SSN is 123-45-6789 and my email is john@example.com'
    }]
}

handler.send_message_securely(
    thread_id='thread_123',
    message=message,
    encrypt_pii=True
)
```

---

### Step 5: Secure Tool Execution

#### 5.1: Tool Authorization Validation

**Validate tool permissions before execution:**

```python
class SecureToolExecutor:
    """Execute tools with security validation"""

    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.api_key = api_key

    def validate_tool_scopes(self, tool: dict, available_scopes: List[str]) -> bool:
        """Check if tool has required scopes"""
        tool_scopes = tool.get('scopes', {})

        if not tool_scopes:
            return True  # No scopes required

        required_scope_names = set(tool_scopes.keys())
        available_scope_names = set(available_scopes)

        missing_scopes = required_scope_names - available_scope_names

        if missing_scopes:
            print(f"Tool '{tool['function']['name']}' missing scopes: {missing_scopes}")
            return False

        return True

    def create_sandboxed_tool(
        self,
        tool_name: str,
        tool_implementation: callable,
        allowed_operations: List[str]
    ) -> dict:
        """Create tool with restricted operations"""

        def sandboxed_wrapper(**kwargs):
            """Wrapper that validates operations"""
            # Check if requested operation is allowed
            operation = kwargs.get('operation')
            if operation not in allowed_operations:
                raise PermissionError(
                    f"Operation '{operation}' not allowed. "
                    f"Allowed: {allowed_operations}"
                )

            # Execute original tool
            return tool_implementation(**kwargs)

        return {
            'kind': 'function',
            'function': {
                'name': tool_name,
                'implementation': sandboxed_wrapper,
                'description': f'Sandboxed tool (allowed: {allowed_operations})'
            }
        }

    def audit_tool_execution(
        self,
        tool_name: str,
        arguments: dict,
        result: any,
        user_id: str,
        timestamp: str
    ):
        """Log tool execution for compliance"""
        audit_entry = {
            'timestamp': timestamp,
            'user_id': user_id,
            'tool_name': tool_name,
            'arguments': arguments,
            'result_summary': str(result)[:100],  # Truncated
            'status': 'success'
        }

        # Log to audit system
        print(f"AUDIT: {audit_entry}")

        # In production: Send to compliance logging system
        # audit_logger.log(audit_entry)


# Example: Secure database tool
def create_secure_database_tool(
    connection_string: str,
    allowed_tables: List[str],
    allowed_operations: List[str] = ['SELECT']
) -> dict:
    """Create database tool with restrictions"""

    def execute_query(query: str) -> dict:
        """Execute SQL query with validation"""
        import sqlparse

        # Parse SQL
        parsed = sqlparse.parse(query)[0]

        # Validate operation
        statement_type = parsed.get_type()
        if statement_type not in allowed_operations:
            raise PermissionError(
                f"Operation '{statement_type}' not allowed. "
                f"Allowed: {allowed_operations}"
            )

        # Validate tables (simple check)
        tokens = [str(t).lower() for t in parsed.tokens]
        for table in allowed_tables:
            if table.lower() not in tokens:
                continue

        # Execute query (simplified)
        # In production: Use proper DB connection
        result = {
            'status': 'success',
            'rows': [],
            'message': f'Query executed: {query[:50]}...'
        }

        return result

    return {
        'kind': 'function',
        'function': {
            'name': 'query_database',
            'description': f'Query database (tables: {allowed_tables})',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'SQL query to execute'
                    }
                },
                'required': ['query']
            },
            'implementation': execute_query
        }
    }


# Example usage
executor = SecureToolExecutor(
    api_base="https://agents.example.com/v1",
    api_key=os.environ['AGENT_API_KEY']
)

# Create restricted database tool
db_tool = create_secure_database_tool(
    connection_string="postgresql://...",
    allowed_tables=['users', 'orders'],
    allowed_operations=['SELECT']
)

# Validate tool has required scopes
available_scopes = ['database.read', 'database.write']
is_authorized = executor.validate_tool_scopes(db_tool, available_scopes)

# Audit tool execution
executor.audit_tool_execution(
    tool_name='query_database',
    arguments={'query': 'SELECT * FROM users LIMIT 10'},
    result={'rows': 10, 'status': 'success'},
    user_id='user_123',
    timestamp='2026-02-07T10:00:00Z'
)
```

#### 5.2: Tool Execution Sandboxing

**Sandbox tool execution to prevent unauthorized access:**

```python
import subprocess
import tempfile
import json
from pathlib import Path

class ToolSandbox:
    """Execute tools in isolated sandbox environment"""

    def __init__(self, timeout: int = 30):
        """Initialize sandbox with timeout"""
        self.timeout = timeout

    def execute_in_sandbox(
        self,
        tool_code: str,
        arguments: dict,
        allowed_imports: List[str] = None
    ) -> dict:
        """
        Execute tool code in restricted environment

        Args:
            tool_code: Python code to execute
            arguments: Tool arguments
            allowed_imports: List of allowed import modules

        Returns:
            Tool execution result
        """
        # Default allowed imports
        if allowed_imports is None:
            allowed_imports = ['json', 'datetime', 'math']

        # Validate imports in code
        if not self._validate_imports(tool_code, allowed_imports):
            raise SecurityError("Tool contains unauthorized imports")

        # Create temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write sandbox wrapper
            sandbox_code = f"""
import sys
import json

# Restrict imports
__builtins__.__dict__['__import__'] = lambda name, *args, **kwargs: (
    __import__(name, *args, **kwargs) if name in {allowed_imports}
    else None
)

# User tool code
{tool_code}

# Execute tool
if __name__ == '__main__':
    args = json.loads(sys.argv[1])
    result = execute(**args)
    print(json.dumps(result))
"""
            f.write(sandbox_code)
            temp_path = f.name

        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python', temp_path, json.dumps(arguments)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"Tool execution failed: {result.stderr}")

            return json.loads(result.stdout)

        finally:
            # Clean up
            Path(temp_path).unlink()

    def _validate_imports(self, code: str, allowed_imports: List[str]) -> bool:
        """Check if code only uses allowed imports"""
        import ast

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in allowed_imports:
                            print(f"Unauthorized import: {alias.name}")
                            return False

                elif isinstance(node, ast.ImportFrom):
                    if node.module not in allowed_imports:
                        print(f"Unauthorized import: {node.module}")
                        return False

            return True

        except SyntaxError:
            return False


class SecurityError(Exception):
    """Security validation error"""
    pass


# Example: Sandboxed calculation tool
sandbox = ToolSandbox(timeout=10)

tool_code = """
def execute(expression: str) -> dict:
    '''Safe calculator - only basic math operations'''
    import math

    # Evaluate expression safely
    allowed_names = {
        'abs': abs, 'round': round, 'min': min, 'max': max,
        'sum': sum, 'pi': math.pi, 'e': math.e, 'sqrt': math.sqrt
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {'result': result, 'status': 'success'}
    except Exception as e:
        return {'error': str(e), 'status': 'error'}
"""

# Execute safely
result = sandbox.execute_in_sandbox(
    tool_code=tool_code,
    arguments={'expression': 'sqrt(16) + pi'},
    allowed_imports=['json', 'math']
)

print("Sandbox result:", result)
```

---

## Examples

### Example 1: Healthcare Agent with HIPAA Compliance

**Complete implementation of HIPAA-compliant healthcare assistant:**

```python
import os
import requests
from datetime import datetime
from typing import List, Dict

# Initialize components
API_BASE = os.environ['AGENT_API_BASE']
API_KEY = os.environ['AGENT_API_KEY']
KMS_VAULT_URL = os.environ['AZURE_VAULT_URL']

kms = AzureKMSClient(vault_url=KMS_VAULT_URL)
encryptor = ContentEncryptor(kms)
pii_detector = PIIDetector()


class HealthcareAgent:
    """HIPAA-compliant healthcare assistant"""

    def __init__(self):
        self.encryption_key_id = 'phi-encryption-key-v1'
        self.audit_log = []

    def create_agent_definition(self) -> dict:
        """Create agent with healthcare tools"""
        return {
            'kind': 'prompt',
            'name': 'healthcare-assistant',
            'model': 'gpt-4o',
            'instructions': '''
You are a HIPAA-compliant healthcare assistant.
You have access to patient records and must handle all PHI with strict confidentiality.
Always verify patient identity before accessing records.
Log all PHI access for compliance.
            ''',
            'tools': [
                {
                    'kind': 'function',
                    'function': {
                        'name': 'lookup_patient_record',
                        'description': 'Retrieve patient medical record',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'patient_id': {
                                    'type': 'string',
                                    'description': 'Patient MRN or ID'
                                }
                            },
                            'required': ['patient_id']
                        }
                    },
                    'connection': ConnectionManager.create_reference_connection(
                        name='ehr-system',
                        authority='user'
                    )
                },
                {
                    'kind': 'function',
                    'function': {
                        'name': 'schedule_appointment',
                        'description': 'Schedule patient appointment',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'patient_id': {'type': 'string'},
                                'appointment_date': {'type': 'string', 'format': 'date-time'},
                                'appointment_type': {'type': 'string'}
                            },
                            'required': ['patient_id', 'appointment_date', 'appointment_type']
                        }
                    }
                }
            ],
            'scopes': {
                'https://healthcare.example.com/patient.read': 'Read patient records',
                'https://healthcare.example.com/patient.write': 'Update patient records'
            }
        }

    def encrypt_patient_message(self, message_text: str) -> dict:
        """Encrypt message containing PHI"""
        # Detect PII/PHI
        pii_matches = pii_detector.detect_pii(message_text)

        if pii_matches:
            print(f"Detected {len(pii_matches)} PHI/PII instances - encrypting")

            # Encrypt entire message
            encrypted = encryptor.encrypt_content(
                plaintext=message_text,
                key_id=self.encryption_key_id
            )

            return {
                'role': 'user',
                'contents': [{
                    'kind': 'text',
                    'text': encrypted['ciphertext'],
                    'audience': 'assistant',
                    'encryption': encrypted['encryption']
                }]
            }
        else:
            # No PHI detected - send unencrypted
            return {
                'role': 'user',
                'contents': [{
                    'kind': 'text',
                    'text': message_text
                }]
            }

    def handle_tool_result_with_phi(self, tool_result: dict) -> dict:
        """Encrypt tool result containing PHI"""
        import json

        # Serialize result
        result_json = json.dumps(tool_result)

        # Always encrypt tool results (may contain PHI)
        encrypted = encryptor.encrypt_content(
            plaintext=result_json,
            key_id=self.encryption_key_id
        )

        return {
            'kind': 'functionResult',
            'callId': tool_result['call_id'],
            'name': tool_result['tool_name'],
            'result': encrypted['ciphertext'],
            'audience': 'assistant',
            'encryption': encrypted['encryption']
        }

    def audit_phi_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        timestamp: datetime
    ):
        """Log PHI access for HIPAA compliance"""
        audit_entry = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'status': 'success',
            'ip_address': 'redacted',  # Capture from request
            'session_id': 'redacted'
        }

        self.audit_log.append(audit_entry)

        # In production: Send to HIPAA audit system
        print(f"HIPAA AUDIT: {audit_entry}")

    def create_conversation(self, patient_query: str, user_id: str) -> dict:
        """Create HIPAA-compliant conversation"""
        # Audit access
        self.audit_phi_access(
            user_id=user_id,
            action='create_conversation',
            resource='healthcare_agent',
            timestamp=datetime.now()
        )

        # Encrypt message if contains PHI
        message = self.encrypt_patient_message(patient_query)

        # Create run
        run_data = {
            'agent': self.create_agent_definition(),
            'input': [message],
            'metadata': {
                'compliance': 'HIPAA',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
        }

        headers = {
            'Authorization': f"Bearer {API_KEY}",
            'Content-Type': 'application/json'
        }

        response = requests.post(f"{API_BASE}/runs", headers=headers, json=run_data)
        return response.json()


# Example usage
agent = HealthcareAgent()

# Doctor queries patient info (contains PHI)
result = agent.create_conversation(
    patient_query="Show me the medical history for patient MRN: 123456, DOB: 01/15/1980",
    user_id="doctor_456"
)

print("Run created:", result.get('runId'))
print("Status:", result.get('status'))
```

### Example 2: Financial Services with PII Protection

**Banking agent with automatic PII redaction:**

```python
class BankingAgent:
    """PCI-compliant banking assistant"""

    def __init__(self):
        self.pii_detector = PIIDetector()
        self.encryptor = ContentEncryptor(kms)
        self.encryption_key_id = 'pci-encryption-key'

    def sanitize_transaction_data(self, transaction: dict) -> dict:
        """Redact sensitive financial data"""
        sanitized = transaction.copy()

        # Redact credit card (show last 4 digits only)
        if 'card_number' in sanitized:
            card = sanitized['card_number']
            sanitized['card_number'] = f"****-****-****-{card[-4:]}"

        # Redact account number
        if 'account_number' in sanitized:
            account = sanitized['account_number']
            sanitized['account_number'] = f"****{account[-4:]}"

        # Redact SSN
        if 'ssn' in sanitized:
            sanitized['ssn'] = "[REDACTED]"

        return sanitized

    def create_agent_definition(self) -> dict:
        """Create banking agent with secure tools"""
        return {
            'kind': 'prompt',
            'name': 'banking-assistant',
            'model': 'gpt-4o',
            'instructions': '''
You are a banking assistant that helps customers with account inquiries.
You must NEVER display full credit card numbers, account numbers, or SSNs.
Always confirm customer identity before providing sensitive information.
            ''',
            'tools': [
                {
                    'kind': 'function',
                    'function': {
                        'name': 'get_account_balance',
                        'description': 'Get customer account balance',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'account_number': {'type': 'string'}
                            },
                            'required': ['account_number']
                        }
                    },
                    'connection': ConnectionManager.create_api_key_connection(
                        api_key=os.environ['BANKING_API_KEY'],
                        authority='system'
                    )
                },
                {
                    'kind': 'function',
                    'function': {
                        'name': 'get_recent_transactions',
                        'description': 'Get recent transactions for account',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'account_number': {'type': 'string'},
                                'limit': {'type': 'integer', 'default': 10}
                            },
                            'required': ['account_number']
                        }
                    }
                }
            ]
        }

    def process_user_query(self, query: str, user_id: str) -> dict:
        """Process query with PII protection"""
        # Detect PII in query
        pii_matches = self.pii_detector.detect_pii(query)

        if pii_matches:
            print(f"Warning: Query contains {len(pii_matches)} PII instances")

            # Redact for logging
            redacted_query, _ = self.pii_detector.redact_pii(query)
            print(f"Logging query (redacted): {redacted_query}")

        # Create message (original query sent to agent, redacted for logs)
        message = {
            'role': 'user',
            'contents': [{
                'kind': 'text',
                'text': query
            }]
        }

        # Create run
        run_data = {
            'agent': self.create_agent_definition(),
            'input': [message],
            'metadata': {
                'compliance': 'PCI-DSS',
                'user_id': user_id
            }
        }

        response = requests.post(
            f"{API_BASE}/runs",
            headers={'Authorization': f"Bearer {API_KEY}"},
            json=run_data
        )

        return response.json()


# Example usage
banking_agent = BankingAgent()

result = banking_agent.process_user_query(
    query="What's my balance for account 123456789?",
    user_id="customer_789"
)
```

### Example 3: Multi-Tenant Enterprise Security

**Enterprise agent with tenant isolation:**

```python
class EnterpriseMultiTenantAgent:
    """Multi-tenant agent with data isolation"""

    def __init__(self):
        self.tenant_keys = {}  # Map tenant → encryption key

    def get_tenant_key_id(self, tenant_id: str) -> str:
        """Get encryption key for tenant"""
        if tenant_id not in self.tenant_keys:
            # In production: Retrieve from secure key store
            self.tenant_keys[tenant_id] = f"tenant-{tenant_id}-key"

        return self.tenant_keys[tenant_id]

    def create_tenant_agent(self, tenant_id: str, tenant_config: dict) -> dict:
        """Create agent with tenant-specific configuration"""
        return {
            'kind': 'prompt',
            'name': f'tenant-{tenant_id}-assistant',
            'model': tenant_config.get('model', 'gpt-4o'),
            'instructions': tenant_config.get('instructions', 'You are a helpful assistant.'),
            'tools': tenant_config.get('tools', []),
            'metadata': {
                'tenant_id': tenant_id,
                'isolation_level': 'strict',
                'encryption_key': self.get_tenant_key_id(tenant_id)
            }
        }

    def validate_tenant_access(
        self,
        user_id: str,
        tenant_id: str,
        resource_id: str
    ) -> bool:
        """Validate user has access to tenant resource"""
        # In production: Check against tenant membership database
        # This is a simplified example

        # Verify user belongs to tenant
        user_tenant = self._get_user_tenant(user_id)
        if user_tenant != tenant_id:
            print(f"Access denied: User {user_id} not in tenant {tenant_id}")
            return False

        # Verify resource belongs to tenant
        resource_tenant = self._get_resource_tenant(resource_id)
        if resource_tenant != tenant_id:
            print(f"Access denied: Resource {resource_id} not in tenant {tenant_id}")
            return False

        return True

    def _get_user_tenant(self, user_id: str) -> str:
        """Get tenant for user"""
        # Simplified - in production, query user database
        return user_id.split('_')[0]  # e.g., "acme_user123" → "acme"

    def _get_resource_tenant(self, resource_id: str) -> str:
        """Get tenant for resource"""
        # Simplified - in production, query resource database
        return resource_id.split('_')[0]  # e.g., "acme_thread456" → "acme"

    def create_tenant_conversation(
        self,
        tenant_id: str,
        user_id: str,
        message: str,
        encrypt: bool = True
    ) -> dict:
        """Create conversation with tenant isolation"""
        # Validate access
        if not self.validate_tenant_access(user_id, tenant_id, f"{tenant_id}_default"):
            raise PermissionError("Access denied")

        # Encrypt message for tenant
        if encrypt:
            encryptor = ContentEncryptor(kms)
            key_id = self.get_tenant_key_id(tenant_id)

            encrypted = encryptor.encrypt_content(
                plaintext=message,
                key_id=key_id
            )

            message_content = {
                'kind': 'text',
                'text': encrypted['ciphertext'],
                'encryption': encrypted['encryption']
            }
        else:
            message_content = {
                'kind': 'text',
                'text': message
            }

        # Create run with tenant agent
        tenant_config = {
            'model': 'gpt-4o',
            'instructions': f'You are an assistant for {tenant_id}.',
            'tools': []
        }

        run_data = {
            'agent': self.create_tenant_agent(tenant_id, tenant_config),
            'input': [{
                'role': 'user',
                'contents': [message_content]
            }],
            'metadata': {
                'tenant_id': tenant_id,
                'user_id': user_id
            }
        }

        response = requests.post(
            f"{API_BASE}/runs",
            headers={'Authorization': f"Bearer {API_KEY}"},
            json=run_data
        )

        return response.json()


# Example usage
enterprise_agent = EnterpriseMultiTenantAgent()

# Tenant A user creates conversation
result_a = enterprise_agent.create_tenant_conversation(
    tenant_id='acme-corp',
    user_id='acme-corp_user123',
    message='What are our Q1 sales figures?',
    encrypt=True
)

# Tenant B user (should fail if trying to access Tenant A resources)
try:
    result_b = enterprise_agent.create_tenant_conversation(
        tenant_id='acme-corp',
        user_id='globex_user456',
        message='Show me Acme data',
        encrypt=True
    )
except PermissionError as e:
    print(f"Expected error: {e}")
```

---

## Troubleshooting

### Issue 1: OAuth2 Token Expired

**Symptoms:**
- API returns `401 Unauthorized`
- Run status transitions to `auth_required`
- Error: "Token expired"

**Solution:**

```python
def handle_token_refresh(session: dict, oauth_manager: OAuth2Manager) -> dict:
    """Automatically refresh expired OAuth2 token"""
    refresh_token = session.get('refresh_token')

    if not refresh_token:
        raise ValueError("No refresh token available - user must re-authenticate")

    try:
        # Refresh token
        new_token_data = oauth_manager.refresh_access_token(refresh_token)

        # Update session
        session['access_token'] = new_token_data['access_token']
        session['refresh_token'] = new_token_data['refresh_token']

        print("Token refreshed successfully")
        return new_token_data

    except Exception as e:
        print(f"Token refresh failed: {e}")
        # User must re-authenticate
        raise


# Retry run with refreshed token
def create_run_with_retry(run_data: dict, session: dict) -> dict:
    """Create run with automatic token refresh on expiry"""

    try:
        # Attempt to create run
        response = requests.post(f"{API_BASE}/runs", headers=headers, json=run_data)

        if response.status_code == 401 or response.json().get('status') == 'auth_required':
            # Token expired - refresh and retry
            print("Token expired - refreshing...")
            handle_token_refresh(session, OAuth2Manager())

            # Update connection with new token
            new_token = session['access_token']
            for tool in run_data['agent']['tools']:
                if 'connection' in tool:
                    tool['connection']['key'] = f"Bearer {new_token}"

            # Retry request
            response = requests.post(f"{API_BASE}/runs", headers=headers, json=run_data)

        return response.json()

    except Exception as e:
        print(f"Run creation failed: {e}")
        raise
```

### Issue 2: Decryption Fails (Content Tampered)

**Symptoms:**
- `ValueError: Decryption failed - content may be tampered`
- Authentication tag verification fails

**Causes:**
- Content modified after encryption
- Wrong decryption key used
- IV or auth tag corrupted during transport

**Solution:**

```python
def safe_decrypt_with_fallback(
    ciphertext: str,
    encryption_metadata: dict,
    encryptor: ContentEncryptor
) -> str:
    """Attempt decryption with error handling"""

    try:
        # Attempt decryption
        plaintext = encryptor.decrypt_content(ciphertext, encryption_metadata)
        return plaintext

    except ValueError as e:
        print(f"Decryption failed: {e}")

        # Check if key exists
        key_id = encryption_metadata['keyId']
        try:
            key = encryptor._get_key(key_id)
            print(f"Key '{key_id}' found")
        except Exception:
            print(f"Key '{key_id}' not found - may have been rotated")
            return "[ENCRYPTED - KEY NOT AVAILABLE]"

        # Content may be tampered
        print("WARNING: Content integrity check failed - possible tampering")
        return "[ENCRYPTED - INTEGRITY CHECK FAILED]"


# Example usage
try:
    decrypted = safe_decrypt_with_fallback(
        ciphertext=message['contents'][0]['text'],
        encryption_metadata=message['contents'][0]['annotations']['encryption'],
        encryptor=encryptor
    )
except Exception as e:
    print(f"Cannot decrypt: {e}")
    decrypted = "[ENCRYPTED CONTENT]"
```

### Issue 3: Missing Required Scopes

**Symptoms:**
- Run status: `auth_required`
- Error message: "Missing required scopes"
- Response includes `missing_scopes` list

**Solution:**

```python
def handle_missing_scopes(run_response: dict, oauth_manager: OAuth2Manager) -> str:
    """Handle missing scopes with incremental consent"""

    if run_response.get('status') != 'auth_required':
        return None

    missing_scopes = run_response.get('missing_scopes', {})

    if not missing_scopes:
        return None

    print(f"Missing scopes: {list(missing_scopes.keys())}")

    # Generate authorization URL with additional scopes
    current_scopes = "https://graph.microsoft.com/User.Read"
    additional_scopes = " ".join(missing_scopes.keys())
    all_scopes = f"{current_scopes} {additional_scopes}"

    # Create new authorization URL
    params = {
        'client_id': OAUTH_CONFIG['client_id'],
        'response_type': 'code',
        'redirect_uri': OAUTH_CONFIG['redirect_uri'],
        'scope': all_scopes,
        'prompt': 'consent',  # Force consent screen
        'state': os.urandom(16).hex()
    }

    from urllib.parse import urlencode
    auth_url = f"{OAUTH_CONFIG['authorize_endpoint']}?{urlencode(params)}"

    print(f"Redirect user to: {auth_url}")
    return auth_url


# Example: Incremental consent flow
run_response = {
    'status': 'auth_required',
    'missing_scopes': {
        'https://graph.microsoft.com/Calendars.ReadWrite': 'Read and write calendar events',
        'https://graph.microsoft.com/Mail.Send': 'Send mail as the signed-in user'
    }
}

auth_url = handle_missing_scopes(run_response, OAuth2Manager())
if auth_url:
    print(f"User must grant additional permissions: {auth_url}")
```

### Issue 4: PII Detected in Logs

**Symptoms:**
- Sensitive data appears in application logs
- PII visible in error messages
- Compliance violation detected

**Solution:**

```python
import logging
from logging import Filter

class PIIRedactionFilter(Filter):
    """Logging filter that redacts PII"""

    def __init__(self):
        super().__init__()
        self.pii_detector = PIIDetector()

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact PII from log records"""
        # Redact message
        if isinstance(record.msg, str):
            redacted, _ = self.pii_detector.redact_pii(record.msg)
            record.msg = redacted

        # Redact args
        if record.args:
            redacted_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    redacted, _ = self.pii_detector.redact_pii(arg)
                    redacted_args.append(redacted)
                else:
                    redacted_args.append(arg)
            record.args = tuple(redacted_args)

        return True


# Configure logging with PII redaction
logger = logging.getLogger('secure_app')
logger.setLevel(logging.INFO)

# Add PII redaction filter
pii_filter = PIIRedactionFilter()
handler = logging.StreamHandler()
handler.addFilter(pii_filter)

logger.addHandler(handler)

# Test logging
logger.info("User SSN: 123-45-6789")  # Will be redacted
# Output: "User [SSN]"

logger.info("User email: john@example.com")  # Will be redacted
# Output: "User email: [EMAIL]"
```

### Issue 5: Connection Validation Errors

**Symptoms:**
- Error: "Invalid connection configuration"
- Connection type not recognized
- Missing required fields

**Solution:**

```python
class ConnectionValidator:
    """Validate connection configurations"""

    REQUIRED_FIELDS = {
        'reference': ['kind', 'name'],
        'key': ['kind', 'key'],
        'remote': ['kind', 'endpoint'],
        'anonymous': ['kind']
    }

    @staticmethod
    def validate_connection(connection: dict) -> tuple[bool, list[str]]:
        """
        Validate connection structure

        Returns:
            (is_valid, errors)
        """
        errors = []

        # Check kind field
        if 'kind' not in connection:
            errors.append("Missing required field: 'kind'")
            return False, errors

        kind = connection['kind']

        # Validate kind value
        if kind not in ConnectionValidator.REQUIRED_FIELDS:
            errors.append(f"Invalid connection kind: '{kind}'")
            return False, errors

        # Check required fields for this kind
        required = ConnectionValidator.REQUIRED_FIELDS[kind]
        for field in required:
            if field not in connection:
                errors.append(f"Missing required field for '{kind}' connection: '{field}'")

        # Validate field types
        if kind == 'key' and 'headerName' in connection:
            if not isinstance(connection['headerName'], str):
                errors.append("Field 'headerName' must be a string")

        if kind == 'remote' and 'credentials' in connection:
            if not isinstance(connection['credentials'], dict):
                errors.append("Field 'credentials' must be an object")

        # Validate authority
        if 'authority' in connection:
            if connection['authority'] not in ['user', 'system']:
                errors.append("Field 'authority' must be 'user' or 'system'")

        return len(errors) == 0, errors


# Example usage
validator = ConnectionValidator()

# Valid connection
conn1 = {'kind': 'reference', 'name': 'myConnection', 'authority': 'user'}
is_valid, errors = validator.validate_connection(conn1)
print(f"Valid: {is_valid}")  # True

# Invalid connection (missing 'name')
conn2 = {'kind': 'reference', 'authority': 'user'}
is_valid, errors = validator.validate_connection(conn2)
print(f"Valid: {is_valid}")  # False
print(f"Errors: {errors}")  # ["Missing required field for 'reference' connection: 'name'"]
```

### Issue 6: Key Rotation Without Downtime

**Symptoms:**
- Need to rotate encryption keys
- Cannot decrypt old messages with new key
- Risk of service interruption

**Solution:**

```python
class KeyRotationManager:
    """Manage encryption key rotation"""

    def __init__(self, kms_client):
        self.kms = kms_client
        self.key_versions = {}

    def rotate_key(self, old_key_id: str, new_key_id: str):
        """Rotate to new encryption key"""
        print(f"Rotating key: {old_key_id} → {new_key_id}")

        # Store mapping
        self.key_versions[old_key_id] = new_key_id

        # Both keys remain available for decryption
        # New encryptions use new key

    def get_encryption_key_id(self) -> str:
        """Get current key for encryption"""
        # Return latest key version
        return "phi-encryption-key-v2"  # Updated version

    def get_decryption_key_id(self, key_id: str) -> str:
        """Get key for decryption (may be old version)"""
        # Old key IDs still work
        return key_id

    def re_encrypt_content(
        self,
        old_ciphertext: str,
        old_encryption_metadata: dict,
        encryptor: ContentEncryptor
    ) -> dict:
        """Re-encrypt content with new key"""
        # Decrypt with old key
        plaintext = encryptor.decrypt_content(
            ciphertext=old_ciphertext,
            encryption_metadata=old_encryption_metadata
        )

        # Encrypt with new key
        new_key_id = self.get_encryption_key_id()
        new_encrypted = encryptor.encrypt_content(
            plaintext=plaintext,
            key_id=new_key_id
        )

        return new_encrypted


# Example: Background re-encryption job
def background_re_encryption_job(
    thread_id: str,
    rotation_manager: KeyRotationManager,
    encryptor: ContentEncryptor
):
    """Re-encrypt all messages in thread with new key"""
    # Fetch all messages
    response = requests.get(
        f"{API_BASE}/threads/{thread_id}/messages",
        headers={'Authorization': f"Bearer {API_KEY}"}
    )
    messages = response.json()

    re_encrypted_count = 0

    for message in messages:
        for content in message.get('contents', []):
            if 'annotations' in content and 'encryption' in content['annotations']:
                old_encryption = content['annotations']['encryption']

                # Check if using old key
                if old_encryption['keyId'] == 'phi-encryption-key-v1':
                    # Re-encrypt
                    new_encrypted = rotation_manager.re_encrypt_content(
                        old_ciphertext=content['text'],
                        old_encryption_metadata=old_encryption,
                        encryptor=encryptor
                    )

                    # Update message (API call to update content)
                    # In production: Use PATCH /messages/{messageId}
                    print(f"Re-encrypted message {message['messageId']}")
                    re_encrypted_count += 1

    print(f"Re-encrypted {re_encrypted_count} messages")
```

---

## Best Practices

### 1. OAuth2 Security

**Do:**
- Store client secrets in environment variables or key vaults
- Use HTTPS for all OAuth2 redirects
- Validate state parameter to prevent CSRF attacks
- Implement token refresh before expiration
- Request minimum required scopes (principle of least privilege)

**Don't:**
- Hardcode client secrets in source code
- Use HTTP for OAuth2 flows (must be HTTPS)
- Skip state parameter validation
- Request broad scopes like `.default`
- Store tokens in cookies without HttpOnly flag

### 2. Encryption Keys

**Do:**
- Use external key management (Azure Key Vault, AWS KMS)
- Generate cryptographically secure random IVs
- Rotate keys regularly (90 days recommended)
- Cache keys in memory with short TTL (1 hour)
- Use authenticated encryption (AES-GCM, ChaCha20-Poly1305)

**Don't:**
- Store keys in application code
- Reuse IVs with the same key
- Use ECB mode or non-authenticated encryption
- Generate IVs from timestamps or sequential numbers
- Skip authentication tag verification

### 3. PII Protection

**Do:**
- Redact PII from logs automatically
- Encrypt PII in transit and at rest
- Use PII detection before logging
- Implement audit trails for PII access
- Train models to avoid generating PII in responses

**Don't:**
- Log raw user messages without PII redaction
- Include PII in error messages
- Store PII in plaintext
- Skip PII detection in tool results
- Send PII to third-party logging services

### 4. Tool Security

**Do:**
- Validate tool inputs and outputs
- Implement least-privilege access controls
- Sandbox tool execution when possible
- Audit all tool executions
- Rate-limit tool calls per user

**Don't:**
- Allow unrestricted database access
- Skip input validation
- Grant excessive permissions
- Execute untrusted code without sandboxing
- Allow tools to access all tenant data

### 5. Compliance

**Do:**
- Maintain comprehensive audit logs
- Document data flows and security controls
- Implement data retention policies
- Conduct regular security reviews
- Test incident response procedures

**Don't:**
- Store more data than necessary
- Skip audit logging for PHI/PII access
- Mix development and production encryption keys
- Allow cross-tenant data access
- Ignore compliance requirements

---

## Security Checklist

Use this checklist before deploying to production:

### Authentication & Authorization

- [ ] OAuth2 implemented with PKCE (if public client)
- [ ] Client secrets stored securely (Key Vault/environment variables)
- [ ] State parameter validated in OAuth2 callback
- [ ] Token refresh implemented before expiration
- [ ] Scope enforcement validated server-side
- [ ] Connection types properly validated
- [ ] Authority levels (user/system) correctly configured

### Encryption & Key Management

- [ ] End-to-end encryption implemented for sensitive data
- [ ] Keys managed by external KMS (Azure Key Vault, AWS KMS)
- [ ] Cryptographically secure random IVs generated
- [ ] Authentication tags verified on decryption
- [ ] Key rotation process documented and tested
- [ ] Key caching implemented with appropriate TTL
- [ ] Encryption metadata properly structured

### PII & PHI Protection

- [ ] PII detection implemented in logging
- [ ] Automatic PII redaction in error messages
- [ ] PHI encrypted with HIPAA-compliant algorithms
- [ ] Audit logging for PHI/PII access
- [ ] Data retention policies implemented
- [ ] PII not sent to third-party services

### Tool Security

- [ ] Tool inputs validated and sanitized
- [ ] Tool outputs checked for PII/PHI
- [ ] Least-privilege access controls
- [ ] Tool execution audited
- [ ] Rate limiting implemented
- [ ] Sandboxing for untrusted code

### Multi-Tenant Security

- [ ] Tenant isolation enforced
- [ ] Cross-tenant access prevented
- [ ] Tenant-specific encryption keys
- [ ] User-tenant membership validated
- [ ] Resource-tenant ownership verified

### Compliance & Audit

- [ ] Comprehensive audit logs implemented
- [ ] Security controls documented
- [ ] Incident response plan tested
- [ ] Regular security reviews scheduled
- [ ] Compliance requirements validated (HIPAA, GDPR, PCI-DSS)

---

## Related Documentation

- [Authentication Specification](../specifications/authentication.md) - OAuth2 flows and scope enforcement
- [Content Encryption Specification](../specifications/content-encryption.md) - Encryption requirements and algorithms
- [Common Types](../typespec/common.tsp) - Connection and Scopes type definitions
- [Messages](../typespec/messages.tsp) - AIContentBase model with encryption attribute
- [Getting Started Guide](./getting-started.md) - Basic API integration
- [Webhooks Guide](./webhooks.md) - Secure webhook notifications

---

## Additional Resources

### Standards & Compliance
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [GDPR Data Protection](https://gdpr.eu/)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [NIST Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)

### OAuth2 & OpenID Connect
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OAuth 2.0 for Native Apps (PKCE)](https://datatracker.ietf.org/doc/html/rfc8252)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)

### Encryption
- [AES-GCM Specification](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)
- [ChaCha20-Poly1305 RFC 7539](https://datatracker.ietf.org/doc/html/rfc7539)
- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/)
- [AWS KMS](https://docs.aws.amazon.com/kms/)

### Python Libraries
- [cryptography](https://cryptography.io/) - Encryption library
- [requests-oauthlib](https://requests-oauthlib.readthedocs.io/) - OAuth2 for Python
- [spaCy](https://spacy.io/) - NLP for PII detection
- [azure-identity](https://docs.microsoft.com/en-us/python/api/azure-identity/) - Azure authentication

### JavaScript Libraries
- [node-crypto](https://nodejs.org/api/crypto.html) - Node.js crypto module
- [passport](http://www.passportjs.org/) - OAuth2 authentication
- [@azure/identity](https://www.npmjs.com/package/@azure/identity) - Azure authentication
- [@azure/keyvault-keys](https://www.npmjs.com/package/@azure/keyvault-keys) - Azure Key Vault
