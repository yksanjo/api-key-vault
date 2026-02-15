/**
 * Basic tests for API Key Vault
 */

const VaultStorage = require('../src/storage/vault');
const crypto = require('../src/utils/crypto');
const fs = require('fs');
const path = require('path');

// Test vault path
const TEST_VAULT_PATH = path.join(__dirname, '.test-vault', 'vault.json');

describe('Crypto Utils', () => {
  test('should generate a random API key', () => {
    const key = crypto.generateApiKey(32);
    expect(key).toBeDefined();
    expect(key.length).toBeGreaterThan(0);
  });

  test('should hash a value', () => {
    const hash = crypto.hash('test-value');
    expect(hash).toBeDefined();
    expect(hash.length).toBe(64); // SHA-256 produces 64 hex characters
  });

  test('should derive key from passphrase', async () => {
    const { key, salt } = await crypto.deriveKey('test-passphrase');
    expect(key).toBeDefined();
    expect(salt).toBeDefined();
  });

  test('should encrypt and decrypt data', async () => {
    const { key } = await crypto.deriveKey('test-passphrase');
    const plaintext = 'secret-api-key';
    
    const encrypted = crypto.encrypt(plaintext, key);
    const decrypted = crypto.decrypt(encrypted, key);
    
    expect(decrypted).toBe(plaintext);
  });
});

describe('Vault Storage', () => {
  let vault;

  beforeEach(() => {
    vault = new VaultStorage(TEST_VAULT_PATH);
  });

  afterEach(async () => {
    // Clean up test vault
    try {
      fs.unlinkSync(TEST_VAULT_PATH);
    } catch (e) {}
    
    // Clean up test directory
    try {
      fs.rmdirSync(path.dirname(TEST_VAULT_PATH));
    } catch (e) {}
  });

  test('should initialize a new vault', async () => {
    await vault.init('test-passphrase');
    expect(vault.exists()).toBe(true);
    expect(vault.isVaultUnlocked()).toBe(true);
  });

  test('should add a key', async () => {
    await vault.init('test-passphrase');
    
    const result = await vault.addKey({
      name: 'Test Key',
      key: 'api-key-value',
      service: 'test-service',
      rotationDays: 30
    });

    expect(result.id).toBeDefined();
    expect(result.name).toBe('Test Key');
    expect(result.key).toBe('api-key-value');
  });

  test('should get a key', async () => {
    await vault.init('test-passphrase');
    
    const added = await vault.addKey({
      name: 'Test Key',
      key: 'api-key-value',
      service: 'test-service'
    });

    const retrieved = await vault.getKey(added.id);
    expect(retrieved.key).toBe('api-key-value');
  });

  test('should list keys', async () => {
    await vault.init('test-passphrase');
    
    await vault.addKey({
      name: 'Key 1',
      key: 'key1',
      service: 'service1'
    });
    
    await vault.addKey({
      name: 'Key 2',
      key: 'key2',
      service: 'service2'
    });

    const keys = await vault.listKeys();
    expect(keys.length).toBe(2);
    // Keys should not include decrypted values
    expect(keys[0].key).toBeUndefined();
  });

  test('should delete a key', async () => {
    await vault.init('test-passphrase');
    
    const added = await vault.addKey({
      name: 'Test Key',
      key: 'api-key-value'
    });

    await vault.deleteKey(added.id);
    
    const keys = await vault.listKeys();
    expect(keys.length).toBe(0);
  });

  test('should rotate a key', async () => {
    await vault.init('test-passphrase');
    
    const added = await vault.addKey({
      name: 'Test Key',
      key: 'old-key'
    });

    const rotated = await vault.rotateKey(added.id);
    expect(rotated.key).not.toBe('old-key');
    expect(rotated.lastRotated).toBeDefined();
  });

  test('should record usage', async () => {
    await vault.init('test-passphrase');
    
    const added = await vault.addKey({
      name: 'Test Key',
      key: 'api-key'
    });

    await vault.recordUsage(added.id, { action: 'test', metadata: { foo: 'bar' } });
    
    const stats = await vault.getKeyUsageStats(added.id);
    expect(stats.usageCount).toBe(1);
  });
});
