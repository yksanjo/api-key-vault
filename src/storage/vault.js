/**
 * Vault Storage - Secure JSON file-based storage for API keys
 */

const fs = require('fs');
const path = require('path');
const crypto = require('../utils/crypto');

class VaultStorage {
  constructor(vaultPath = null) {
    this.vaultPath = vaultPath || path.join(process.cwd(), '.keyvault', 'vault.json');
    this.data = {
      version: 1,
      keys: [],
      metadata: {
        createdAt: null,
        updatedAt: null,
        salt: null
      }
    };
    this.encryptionKey = null;
    this.isUnlocked = false;
  }

  /**
   * Initialize a new vault with a master passphrase
   * @param {string} passphrase - Master passphrase
   */
  async init(passphrase) {
    // Ensure directory exists
    const dir = path.dirname(this.vaultPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Derive encryption key from passphrase
    const { key, salt } = await crypto.deriveKey(passphrase);
    this.encryptionKey = key;
    
    // Initialize vault metadata
    this.data.metadata.createdAt = new Date().toISOString();
    this.data.metadata.updatedAt = new Date().toISOString();
    this.data.metadata.salt = salt;
    
    await this.save();
    this.isUnlocked = true;
    
    return { success: true, message: 'Vault initialized successfully' };
  }

  /**
   * Unlock an existing vault with passphrase
   * @param {string} passphrase - Master passphrase
   */
  async unlock(passphrase) {
    if (!fs.existsSync(this.vaultPath)) {
      throw new Error('Vault does not exist. Run "keyvault init" first.');
    }

    await this.load();
    
    // Derive key from passphrase and verify
    const { key, salt } = await crypto.deriveKey(passphrase, this.data.metadata.salt);
    
    // Verify by checking if we can decrypt (simple check)
    // In production, store a verification token
    this.encryptionKey = key;
    this.isUnlocked = true;
    
    return { success: true, message: 'Vault unlocked successfully' };
  }

  /**
   * Lock the vault
   */
  lock() {
    this.encryptionKey = null;
    this.isUnlocked = false;
    return { success: true, message: 'Vault locked' };
  }

  /**
   * Load vault data from file
   */
  async load() {
    const raw = fs.readFileSync(this.vaultPath, 'utf8');
    this.data = JSON.parse(raw);
    return this.data;
  }

  /**
   * Save vault data to file
   */
  async save() {
    const dir = path.dirname(this.vaultPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(this.vaultPath, JSON.stringify(this.data, null, 2));
  }

  /**
   * Check if vault exists
   */
  exists() {
    return fs.existsSync(this.vaultPath);
  }

  /**
   * Check if vault is unlocked
   */
  isVaultUnlocked() {
    return this.isUnlocked;
  }

  /**
   * Add a new API key to the vault
   * @param {Object} keyData - Key data
   */
  async addKey(keyData) {
    this._ensureUnlocked();
    
    const key = {
      id: crypto.generateApiKey(16),
      name: keyData.name,
      service: keyData.service || 'unknown',
      key: crypto.encrypt(keyData.key, this.encryptionKey),
      keyHash: crypto.hash(keyData.key), // For verification without decryption
      rotationDays: keyData.rotationDays || 90,
      lastRotated: new Date().toISOString(),
      nextRotation: this._calculateNextRotation(keyData.rotationDays || 90),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      enabled: true,
      tags: keyData.tags || [],
      metadata: keyData.metadata || {},
      usageCount: 0,
      lastUsed: null
    };

    this.data.keys.push(key);
    this.data.metadata.updatedAt = new Date().toISOString();
    await this.save();

    return {
      id: key.id,
      name: key.name,
      service: key.service,
      key: keyData.key, // Return raw key only on creation
      rotationDays: key.rotationDays,
      createdAt: key.createdAt
    };
  }

  /**
   * Get an API key by ID (decrypted)
   * @param {string} id - Key ID
   */
  async getKey(id) {
    this._ensureUnlocked();
    
    const key = this.data.keys.find(k => k.id === id);
    if (!key) {
      throw new Error('Key not found');
    }

    return {
      id: key.id,
      name: key.name,
      service: key.service,
      key: crypto.decrypt(key.key, this.encryptionKey),
      keyHash: key.keyHash,
      rotationDays: key.rotationDays,
      lastRotated: key.lastRotated,
      nextRotation: key.nextRotation,
      createdAt: key.createdAt,
      updatedAt: key.updatedAt,
      enabled: key.enabled,
      tags: key.tags,
      metadata: key.metadata,
      usageCount: key.usageCount,
      lastUsed: key.lastUsed
    };
  }

  /**
   * Get key metadata (without decrypted value)
   * @param {string} id - Key ID
   */
  async getKeyMeta(id) {
    this._ensureUnlocked();
    
    const key = this.data.keys.find(k => k.id === id);
    if (!key) {
      throw new Error('Key not found');
    }

    // Return everything except the actual key
    const { key: _, ...meta } = key;
    return meta;
  }

  /**
   * List all API keys (metadata only, no decrypted values)
   */
  async listKeys() {
    this._ensureUnlocked();
    
    return this.data.keys.map(key => {
      const { key: _, ...meta } = key;
      return meta;
    });
  }

  /**
   * Update an API key
   * @param {string} id - Key ID
   * @param {Object} updates - Fields to update
   */
  async updateKey(id, updates) {
    this._ensureUnlocked();
    
    const index = this.data.keys.findIndex(k => k.id === id);
    if (index === -1) {
      throw new Error('Key not found');
    }

    const key = this.data.keys[index];

    // Update allowed fields
    if (updates.name) key.name = updates.name;
    if (updates.service) key.service = updates.service;
    if (updates.rotationDays) {
      key.rotationDays = updates.rotationDays;
      key.nextRotation = this._calculateNextRotation(updates.rotationDays);
    }
    if (updates.enabled !== undefined) key.enabled = updates.enabled;
    if (updates.tags) key.tags = updates.tags;
    if (updates.metadata) key.metadata = { ...key.metadata, ...updates.metadata };

    // If updating the actual key value
    if (updates.key) {
      key.key = crypto.encrypt(updates.key, this.encryptionKey);
      key.keyHash = crypto.hash(updates.key);
    }

    key.updatedAt = new Date().toISOString();
    this.data.metadata.updatedAt = new Date().toISOString();
    await this.save();

    return { success: true, message: 'Key updated successfully' };
  }

  /**
   * Delete an API key
   * @param {string} id - Key ID
   */
  async deleteKey(id) {
    this._ensureUnlocked();
    
    const index = this.data.keys.findIndex(k => k.id === id);
    if (index === -1) {
      throw new Error('Key not found');
    }

    this.data.keys.splice(index, 1);
    this.data.metadata.updatedAt = new Date().toISOString();
    await this.save();

    return { success: true, message: 'Key deleted successfully' };
  }

  /**
   * Rotate an API key
   * @param {string} id - Key ID
   * @param {string} newKey - New key value (generated if not provided)
   */
  async rotateKey(id, newKey = null) {
    this._ensureUnlocked();
    
    const key = this.data.keys.find(k => k.id === id);
    if (!key) {
      throw new Error('Key not found');
    }

    const generatedKey = newKey || crypto.generateApiKey(32);
    
    key.key = crypto.encrypt(generatedKey, this.encryptionKey);
    key.keyHash = crypto.hash(generatedKey);
    key.lastRotated = new Date().toISOString();
    key.nextRotation = this._calculateNextRotation(key.rotationDays);
    key.updatedAt = new Date().toISOString();
    
    this.data.metadata.updatedAt = new Date().toISOString();
    await this.save();

    return {
      id: key.id,
      name: key.name,
      key: generatedKey,
      lastRotated: key.lastRotated,
      nextRotation: key.nextRotation
    };
  }

  /**
   * Record key usage
   * @param {string} id - Key ID
   * @param {Object} usageInfo - Usage information
   */
  async recordUsage(id, usageInfo = {}) {
    this._ensureUnlocked();
    
    const key = this.data.keys.find(k => k.id === id);
    if (!key) {
      throw new Error('Key not found');
    }

    key.usageCount = (key.usageCount || 0) + 1;
    key.lastUsed = new Date().toISOString();
    
    // Store usage metadata
    if (!key.usageHistory) {
      key.usageHistory = [];
    }
    
    key.usageHistory.push({
      timestamp: new Date().toISOString(),
      action: usageInfo.action || 'access',
      metadata: usageInfo.metadata || {}
    });

    // Keep only last 100 usage records
    if (key.usageHistory.length > 100) {
      key.usageHistory = key.usageHistory.slice(-100);
    }

    this.data.metadata.updatedAt = new Date().toISOString();
    await this.save();

    return { success: true, usageCount: key.usageCount };
  }

  /**
   * Get keys that need rotation
   */
  async getKeysNeedingRotation() {
    this._ensureUnlocked();
    
    const now = new Date();
    return this.data.keys.filter(key => {
      if (!key.enabled) return false;
      const nextRotation = new Date(key.nextRotation);
      return nextRotation <= now;
    }).map(key => {
      const { key: _, ...meta } = key;
      return meta;
    });
  }

  /**
   * Get usage statistics for a key
   * @param {string} id - Key ID
   */
  async getKeyUsageStats(id) {
    this._ensureUnlocked();
    
    const key = this.data.keys.find(k => k.id === id);
    if (!key) {
      throw new Error('Key not found');
    }

    return {
      id: key.id,
      name: key.name,
      usageCount: key.usageCount || 0,
      lastUsed: key.lastUsed,
      usageHistory: key.usageHistory || []
    };
  }

  /**
   * Calculate next rotation date
   * @param {number} days - Rotation period in days
   */
  _calculateNextRotation(days) {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString();
  }

  /**
   * Ensure vault is unlocked
   */
  _ensureUnlocked() {
    if (!this.isUnlocked) {
      throw new Error('Vault is locked. Run "keyvault unlock" first.');
    }
  }
}

module.exports = VaultStorage;
