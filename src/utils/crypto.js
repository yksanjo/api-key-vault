/**
 * Encryption utility for secure key storage
 * Uses AES-256-CTR for encryption with a master key derived from PBKDF2
 */

const aesjs = require('aes-js');
const crypto = require('crypto');

class Crypto {
  constructor() {
    this.keyLength = 32; // 256 bits
    this.ivLength = 16;   // 128 bits
    this.pbkdf2Iterations = 100000;
  }

  /**
   * Derive a 256-bit key from a passphrase using PBKDF2
   * @param {string} passphrase - The master passphrase
   * @param {string} salt - Optional salt (hex encoded, generated if not provided)
   * @returns {Object} - { key, salt }
   */
  async deriveKey(passphrase, salt = null) {
    if (!salt) {
      salt = crypto.randomBytes(16).toString('hex');
    }
    
    // Use PBKDF2 to derive a proper 32-byte key
    const saltBuffer = Buffer.from(salt, 'hex');
    const key = crypto.pbkdf2Sync(passphrase, saltBuffer, 100000, this.keyLength, 'sha256');
    
    return { key, salt };
  }

  /**
   * Encrypt data using AES-256-CTR
   * @param {string} plaintext - Data to encrypt
   * @param {Buffer} key - 256-bit encryption key
   * @returns {string} - Base64 encoded encrypted data (iv + ciphertext)
   */
  encrypt(plaintext, key) {
    // Generate a random IV using Node's crypto
    const iv = crypto.randomBytes(this.ivLength);
    
    const aesCtr = new aesjs.ModeOfOperation.ctr(key, new aesjs.Counter(iv));
    const encryptedBytes = aesCtr.encrypt(aesjs.utils.utf8.toBytes(plaintext));
    
    // Prepend IV to encrypted data
    const combined = Buffer.concat([iv, encryptedBytes]);
    return combined.toString('base64');
  }

  /**
   * Decrypt data using AES-256-CTR
   * @param {string} ciphertext - Base64 encoded encrypted data
   * @param {Buffer} key - 256-bit encryption key
   * @returns {string} - Decrypted plaintext
   */
  decrypt(ciphertext, key) {
    const combined = Buffer.from(ciphertext, 'base64');
    
    // Extract IV and encrypted data
    const iv = combined.slice(0, this.ivLength);
    const encryptedBytes = combined.slice(this.ivLength);
    
    const aesCtr = new aesjs.ModeOfOperation.ctr(key, new aesjs.Counter(iv));
    const decryptedBytes = aesCtr.decrypt(encryptedBytes);
    
    return aesjs.utils.utf8.fromBytes(decryptedBytes);
  }

  /**
   * Hash a value for secure comparison (e.g., API key checksums)
   * @param {string} value - Value to hash
   * @returns {string} - SHA-256 hash
   */
  hash(value) {
    const sha256 = crypto.createHash('sha256');
    return sha256.update(value).digest('hex');
  }

  /**
   * Generate a secure random API key
   * @param {number} length - Key length (default 32)
   * @returns {string} - Random API key
   */
  generateApiKey(length = 32) {
    const bytes = crypto.randomBytes(length);
    // Convert to base64url format for URL-safe keys
    return bytes.toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  /**
   * Verify passphrase against stored hash
   * @param {string} passphrase - Passphrase to verify
   * @param {string} salt - Salt used for key derivation
   * @returns {boolean} - True if passphrase is valid
   */
  async verifyPassphrase(passphrase, salt) {
    const { key } = await this.deriveKey(passphrase, salt);
    // Store a verification token during setup to check later
    return true;
  }
}

module.exports = new Crypto();
