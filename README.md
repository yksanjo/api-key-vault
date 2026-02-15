# API Key Vault

Secure, auditable storage for API keys with automatic rotation and usage monitoring.

## Features

- **Secure Storage**: AES-256 encryption for all stored API keys
- **Passphrase Protection**: Master passphrase protects your entire vault
- **Automatic Rotation**: Configurable rotation periods with automatic reminders
- **Usage Monitoring**: Track API key usage patterns and detect anomalies
- **Comprehensive Audit Logging**: Every operation is logged for compliance
- **Health Scores**: Get visibility into the security health of your keys

## Installation

```bash
# Clone or download the repository
cd api-key-vault

# Install dependencies
npm install
```

## Quick Start

```bash
# Initialize a new vault
npm start -- init

# Unlock the vault
npm start -- unlock

# Add an API key
npm start -- add -n "My API Key" -k "your-api-key-here" -s "aws"

# List all keys
npm start -- list

# Get a key (decrypted)
npm start -- get <key-id>

# Rotate a key
npm start -- rotate <key-id>

# Check health
npm start -- health
```

## Commands

### Vault Management

| Command | Description |
|---------|-------------|
| `keyvault init` | Initialize a new vault |
| `keyvault unlock` | Unlock the vault |
| `keyvault lock` | Lock the vault |

### Key Management

| Command | Description |
|---------|-------------|
| `keyvault add -n <name> -k <key>` | Add a new API key |
| `keyvault get <id>` | Get a key (decrypted) |
| `keyvault list` | List all keys (metadata only) |
| `keyvault update <id>` | Update a key |
| `keyvault delete <id>` | Delete a key |

### Rotation

| Command | Description |
|---------|-------------|
| `keyvault rotate <id>` | Manually rotate a key |
| `keyvault rotate:check` | Check keys needing rotation |
| `keyvault rotate:report` | Generate rotation report |

### Monitoring

| Command | Description |
|---------|-------------|
| `keyvault usage <id>` | Get usage statistics |
| `keyvault health` | Get vault health status |
| `keyvault audit` | View audit logs |

### Utilities

| Command | Description |
|---------|-------------|
| `keyvault generate` | Generate a new random API key |

## Options

### Add Command Options

```bash
-n, --name <name>       Key name (required)
-k, --key <key>         API key value (required)
-s, --service <service> Service name (default: default)
-r, --rotation <days>   Rotation period in days (default: 90)
-t, --tags <tags>       Comma-separated tags
```

### List Command Options

```bash
-s, --service <service>  Filter by service
-f, --format <format>    Output format: json or table (default: json)
```

### Update Command Options

```bash
-n, --name <name>       Key name
-s, --service <service> Service name
-r, --rotation <days>   Rotation period in days
-k, --key <key>         New API key value
--enable                Enable the key
--disable               Disable the key
```

## Programmatic Usage

```javascript
const VaultStorage = require('./src/storage/vault');
const AuditLogger = require('./src/services/audit');
const RotationService = require('./src/services/rotation');
const UsageMonitor = require('./src/services/monitoring');

// Initialize
const vault = new VaultStorage();
const audit = new AuditLogger();
const rotation = new RotationService(vault, audit);
const monitor = new UsageMonitor(vault, audit);

// Use the vault
await vault.init('master-passphrase');
const result = await vault.addKey({
  name: 'My API Key',
  key: 'api-key-value',
  service: 'aws',
  rotationDays: 90
});
```

## Security

- All API keys are encrypted using AES-256-CTR before storage
- Master passphrase is used to derive encryption key via bcrypt
- Key hashes are stored separately for verification
- Audit logs track all access and modifications

## File Structure

```
api-key-vault/
├── src/
│   ├── cli.js              # Command-line interface
│   ├── utils/
│   │   └── crypto.js       # Encryption utilities
│   ├── storage/
│   │   └── vault.js        # Vault storage
│   └── services/
│       ├── audit.js        # Audit logging
│       ├── rotation.js     # Rotation service
│       └── monitoring.js   # Usage monitoring
├── package.json
├── .env.example
└── README.md
```

## License

MIT
