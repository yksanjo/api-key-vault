#!/usr/bin/env node

/**
 * CLI - Command-line interface for API Key Vault
 */

const { Command } = require('commander');
const readline = require('readline');
const VaultStorage = require('./storage/vault');
const AuditLogger = require('./services/audit');
const RotationService = require('./services/rotation');
const UsageMonitor = require('./services/monitoring');

// Initialize services
const vault = new VaultStorage();
const auditLogger = new AuditLogger();
const rotationService = new RotationService(vault, auditLogger);
const usageMonitor = new UsageMonitor(vault, auditLogger);

// Keep vault unlocked during session
let sessionVault = vault;

// Helper: Prompt for input
function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer);
    });
  });
}

// Helper: Prompt for password (hidden input)
function promptPassword(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer);
    });
  });
}

// Helper: Print formatted output
function printOutput(data, format = 'json') {
  if (format === 'json') {
    console.log(JSON.stringify(data, null, 2));
  } else if (format === 'table' && Array.isArray(data)) {
    const headers = Object.keys(data[0] || {});
    console.log(headers.join(' | '));
    console.log(headers.map(() => '---').join(' | '));
    data.forEach(row => {
      console.log(headers.map(h => String(row[h] || '')).join(' | '));
    });
  }
}

const program = new Command();

program
  .name('keyvault')
  .description('Secure, auditable storage for API keys with automatic rotation and usage monitoring')
  .version('1.0.0');

// Initialize vault
program
  .command('init')
  .description('Initialize a new vault')
  .action(async () => {
    try {
      const passphrase = await promptPassword('Enter master passphrase: ');
      const confirm = await promptPassword('Confirm passphrase: ');
      
      if (passphrase !== confirm) {
        console.error('Passphrases do not match');
        process.exit(1);
      }

      if (vault.exists()) {
        console.error('Vault already exists. Use "keyvault unlock" to open it.');
        process.exit(1);
      }

      const result = await vault.init(passphrase);
      console.log(result.message);
      await auditLogger.logVaultUnlocked({ action: 'init' });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Unlock vault
program
  .command('unlock')
  .description('Unlock the vault with master passphrase')
  .action(async () => {
    try {
      if (!vault.exists()) {
        console.error('Vault does not exist. Run "keyvault init" first.');
        process.exit(1);
      }

      const passphrase = await promptPassword('Enter master passphrase: ');
      await vault.unlock(passphrase);
      sessionVault = vault;
      console.log('Vault unlocked successfully');
      await auditLogger.logVaultUnlocked({ action: 'unlock' });
    } catch (error) {
      console.error('Error:', error.message);
      await auditLogger.logAuthFailure({ action: 'unlock', error: error.message });
      process.exit(1);
    }
  });

// Lock vault
program
  .command('lock')
  .description('Lock the vault')
  .action(async () => {
    try {
      vault.lock();
      console.log('Vault locked');
      await auditLogger.logVaultLocked({ action: 'lock' });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Add a key
program
  .command('add')
  .description('Add a new API key to the vault')
  .requiredOption('-n, --name <name>', 'Key name')
  .requiredOption('-k, --key <key>', 'API key value')
  .option('-s, --service <service>', 'Service name', 'default')
  .option('-r, --rotation <days>', 'Rotation period in days', '90')
  .option('-t, --tags <tags>', 'Comma-separated tags')
  .action(async (options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const keyData = {
        name: options.name,
        key: options.key,
        service: options.service,
        rotationDays: parseInt(options.rotation),
        tags: options.tags ? options.tags.split(',').map(t => t.trim()) : []
      };

      const result = await vault.addKey(keyData);
      console.log('API key added successfully:');
      console.log(`  ID: ${result.id}`);
      console.log(`  Name: ${result.name}`);
      console.log(`  Key: ${result.key} (shown once)`);
      console.log(`  Service: ${result.service}`);
      console.log(`  Rotation: Every ${result.rotationDays} days`);

      await auditLogger.logKeyCreated(result);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Get a key
program
  .command('get <id>')
  .description('Get an API key by ID')
  .action(async (id) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const key = await vault.getKey(id);
      console.log('API Key:');
      console.log(`  ID: ${key.id}`);
      console.log(`  Name: ${key.name}`);
      console.log(`  Service: ${key.service}`);
      console.log(`  Key: ${key.key}`);
      console.log(`  Enabled: ${key.enabled}`);
      console.log(`  Rotation: Every ${key.rotationDays} days`);
      console.log(`  Last Rotated: ${key.lastRotated}`);
      console.log(`  Next Rotation: ${key.nextRotation}`);
      console.log(`  Usage Count: ${key.usageCount}`);
      console.log(`  Last Used: ${key.lastUsed || 'Never'}`);

      await auditLogger.logKeyAccessed({ id: key.id, name: key.name, service: key.service });
      await vault.recordUsage(id, { action: 'cli_get' });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// List keys
program
  .command('list')
  .description('List all API keys (metadata only)')
  .option('-s, --service <service>', 'Filter by service')
  .option('-f, --format <format>', 'Output format (json, table)', 'json')
  .action(async (options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      let keys = await vault.listKeys();
      
      if (options.service) {
        keys = keys.filter(k => k.service === options.service);
      }

      printOutput(keys, options.format);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Update a key
program
  .command('update <id>')
  .description('Update an API key')
  .option('-n, --name <name>', 'Key name')
  .option('-s, --service <service>', 'Service name')
  .option('-r, --rotation <days>', 'Rotation period in days')
  .option('-k, --key <key>', 'New API key value')
  .option('--enable', 'Enable the key')
  .option('--disable', 'Disable the key')
  .action(async (id, options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const updates = {};
      if (options.name) updates.name = options.name;
      if (options.service) updates.service = options.service;
      if (options.rotation) updates.rotationDays = parseInt(options.rotation);
      if (options.key) updates.key = options.key;
      if (options.enable) updates.enabled = true;
      if (options.disable) updates.enabled = false;

      const result = await vault.updateKey(id, updates);
      console.log(result.message);
      
      await auditLogger.logKeyUpdated({ id, changes: Object.keys(updates) });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Delete a key
program
  .command('delete <id>')
  .description('Delete an API key')
  .option('-f, --force', 'Skip confirmation')
  .action(async (id, options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      if (!options.force) {
        const confirm = await prompt(`Are you sure you want to delete key ${id}? (yes/no): `);
        if (confirm.toLowerCase() !== 'yes') {
          console.log('Cancelled');
          process.exit(0);
        }
      }

      const key = await vault.getKeyMeta(id);
      const result = await vault.deleteKey(id);
      console.log(result.message);
      
      await auditLogger.logKeyDeleted({ id, name: key.name, service: key.service });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Rotate a key
program
  .command('rotate <id>')
  .description('Rotate an API key')
  .option('-k, --key <key>', 'New key value (generated if not provided)')
  .action(async (id, options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const result = await vault.rotateKey(id, options.key);
      console.log('Key rotated successfully:');
      console.log(`  ID: ${result.id}`);
      console.log(`  Name: ${result.name}`);
      console.log(`  New Key: ${result.key}`);
      console.log(`  Last Rotated: ${result.lastRotated}`);
      console.log(`  Next Rotation: ${result.nextRotation}`);

      await auditLogger.logKeyRotated({ id: result.id, name: result.name, reason: 'manual' });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Check rotation status
program
  .command('rotate:check')
  .description('Check keys that need rotation')
  .option('--dry-run', 'Show what would be rotated without rotating')
  .action(async (options) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const status = await rotationService.getRotationStatus();
      
      if (status.length === 0) {
        console.log('All keys are healthy');
        return;
      }

      console.log('Keys needing attention:');
      status.forEach(key => {
        console.log(`  ${key.name} (${key.service}): ${key.daysUntilRotation} days until rotation`);
        if (key.needsRotation) console.log(`    ⚠️ Needs rotation now!`);
        if (key.rotationOverdue) console.log(`    🚨 Rotation overdue!`);
      });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Generate rotation report
program
  .command('rotate:report')
  .description('Generate rotation report')
  .action(async () => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const report = await rotationService.generateReport();
      console.log('=== Rotation Report ===');
      console.log(`Total Keys: ${report.totalKeys}`);
      console.log(`Keys Needing Rotation: ${report.keysNeedingRotation}`);
      console.log(`Keys Healthy: ${report.keysHealthy}`);
      console.log(`Keys Disabled: ${report.keysDisabled}`);
      console.log('');
      
      if (report.byRotationStatus.overdue.length > 0) {
        console.log('Overdue:');
        report.byRotationStatus.overdue.forEach(k => {
          console.log(`  - ${k.name}: ${k.daysOverdue} days overdue`);
        });
      }
      
      if (report.byRotationStatus.dueSoon.length > 0) {
        console.log('Due Soon (within 7 days):');
        report.byRotationStatus.dueSoon.forEach(k => {
          console.log(`  - ${k.name}: ${k.daysUntil} days`);
        });
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Usage commands
program
  .command('usage <id>')
  .description('Get usage statistics for a key')
  .action(async (id) => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const usage = await usageMonitor.getKeyUsage(id);
      console.log('=== Usage Statistics ===');
      console.log(`Key: ${usage.name}`);
      console.log(`Total Usage: ${usage.usageCount}`);
      console.log(`Last Used: ${usage.lastUsed || 'Never'}`);
      
      if (usage.usageHistory && usage.usageHistory.length > 0) {
        console.log('Recent Usage:');
        usage.usageHistory.slice(-5).forEach(h => {
          console.log(`  ${h.timestamp}: ${h.action}`);
        });
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Health check
program
  .command('health')
  .description('Get vault health status')
  .action(async () => {
    try {
      if (!vault.isVaultUnlocked()) {
        console.error('Vault is locked. Run "keyvault unlock" first.');
        process.exit(1);
      }

      const health = await usageMonitor.getVaultHealth();
      console.log('=== Vault Health ===');
      console.log(`Overall Score: ${health.overallScore}/100 (${health.status})`);
      console.log(`Total Keys: ${health.keyCount}`);
      console.log(`Healthy: ${health.keysByStatus.healthy}`);
      console.log(`Warning: ${health.keysByStatus.warning}`);
      console.log(`Critical: ${health.keysByStatus.critical}`);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Audit log commands
program
  .command('audit')
  .description('View audit logs')
  .option('-a, --action <action>', 'Filter by action')
  .option('-l, --limit <limit>', 'Limit number of entries', '20')
  .action(async (options) => {
    try {
      const logs = await auditLogger.getLogs({
        action: options.action,
        limit: parseInt(options.limit)
      });

      console.log('=== Audit Log ===');
      logs.forEach(log => {
        console.log(`[${log.timestamp}] ${log.action} - ${log.success ? '✓' : '✗'}`);
        console.log(`  Target: ${log.target}${log.targetId ? ` (${log.targetId})` : ''}`);
        if (log.details) console.log(`  Details: ${JSON.stringify(log.details)}`);
        console.log('');
      });
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Generate new API key
program
  .command('generate')
  .description('Generate a new random API key')
  .option('-l, --length <length>', 'Key length', '32')
  .action(async (options) => {
    const crypto = require('./utils/crypto');
    const key = crypto.generateApiKey(parseInt(options.length));
    console.log('Generated API Key:');
    console.log(key);
  });

program.parse(process.argv);
