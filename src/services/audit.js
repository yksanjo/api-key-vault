/**
 * Audit Logger - Comprehensive audit logging for all vault operations
 */

const fs = require('fs');
const path = require('path');
const crypto = require('../utils/crypto');

class AuditLogger {
  constructor(logPath = null) {
    this.logPath = logPath || path.join(process.cwd(), '.keyvault', 'audit.log');
    this.maxLogSize = 10 * 1024 * 1024; // 10MB
  }

  /**
   * Log an audit event
   * @param {Object} event - Audit event data
   */
  async log(event) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      eventId: crypto.generateApiKey(8),
      action: event.action,
      target: event.target,
      targetId: event.targetId,
      user: event.user || 'system',
      ip: event.ip || 'local',
      success: event.success !== false,
      details: event.details || {},
      metadata: event.metadata || {}
    };

    // Ensure directory exists
    const dir = path.dirname(this.logPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Append to log file
    const logLine = JSON.stringify(logEntry) + '\n';
    fs.appendFileSync(this.logPath, logLine);

    // Rotate log if too large
    await this._rotateIfNeeded();

    return logEntry;
  }

  /**
   * Log key creation
   */
  async logKeyCreated(data) {
    return this.log({
      action: 'KEY_CREATED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        service: data.service,
        rotationDays: data.rotationDays
      }
    });
  }

  /**
   * Log key access
   */
  async logKeyAccessed(data) {
    return this.log({
      action: 'KEY_ACCESSED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        service: data.service
      }
    });
  }

  /**
   * Log key update
   */
  async logKeyUpdated(data) {
    return this.log({
      action: 'KEY_UPDATED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        changes: data.changes
      }
    });
  }

  /**
   * Log key deletion
   */
  async logKeyDeleted(data) {
    return this.log({
      action: 'KEY_DELETED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        service: data.service
      }
    });
  }

  /**
   * Log key rotation
   */
  async logKeyRotated(data) {
    return this.log({
      action: 'KEY_ROTATED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        reason: data.reason || 'scheduled'
      }
    });
  }

  /**
   * Log key usage
   */
  async logKeyUsed(data) {
    return this.log({
      action: 'KEY_USED',
      target: 'api_key',
      targetId: data.id,
      details: {
        name: data.name,
        action: data.action,
        metadata: data.metadata
      }
    });
  }

  /**
   * Log vault unlock
   */
  async logVaultUnlocked(data) {
    return this.log({
      action: 'VAULT_UNLOCKED',
      target: 'vault',
      details: data
    });
  }

  /**
   * Log vault lock
   */
  async logVaultLocked(data) {
    return this.log({
      action: 'VAULT_LOCKED',
      target: 'vault',
      details: data
    });
  }

  /**
   * Log failed authentication attempt
   */
  async logAuthFailure(data) {
    return this.log({
      action: 'AUTH_FAILURE',
      target: 'vault',
      success: false,
      details: data
    });
  }

  /**
   * Get audit logs with filtering
   * @param {Object} filters - Filter options
   */
  async getLogs(filters = {}) {
    if (!fs.existsSync(this.logPath)) {
      return [];
    }

    const logs = [];
    const content = fs.readFileSync(this.logPath, 'utf8');
    const lines = content.split('\n').filter(line => line.trim());

    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        
        // Apply filters
        if (filters.action && entry.action !== filters.action) continue;
        if (filters.targetId && entry.targetId !== filters.targetId) continue;
        if (filters.startDate && new Date(entry.timestamp) < new Date(filters.startDate)) continue;
        if (filters.endDate && new Date(entry.timestamp) > new Date(filters.endDate)) continue;
        if (filters.success !== undefined && entry.success !== filters.success) continue;
        
        logs.push(entry);
      } catch (e) {
        // Skip invalid lines
      }
    }

    // Sort by timestamp descending (newest first)
    logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // Apply limit
    if (filters.limit) {
      return logs.slice(0, filters.limit);
    }

    return logs;
  }

  /**
   * Rotate log file if too large
   */
  async _rotateIfNeeded() {
    if (!fs.existsSync(this.logPath)) return;

    const stats = fs.statSync(this.logPath);
    if (stats.size > this.maxLogSize) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const rotatedPath = `${this.logPath}.${timestamp}`;
      fs.renameSync(this.logPath, rotatedPath);
    }
  }

  /**
   * Get log statistics
   */
  async getStats() {
    if (!fs.existsSync(this.logPath)) {
      return {
        totalEvents: 0,
        fileSize: 0
      };
    }

    const stats = fs.statSync(this.logPath);
    const content = fs.readFileSync(this.logPath, 'utf8');
    const lines = content.split('\n').filter(line => line.trim());

    const actionCounts = {};
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        actionCounts[entry.action] = (actionCounts[entry.action] || 0) + 1;
      } catch (e) {}
    }

    return {
      totalEvents: lines.length,
      fileSize: stats.size,
      actionCounts
    };
  }
}

module.exports = AuditLogger;
