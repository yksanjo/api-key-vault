/**
 * Rotation Service - Automatic key rotation system
 */

const crypto = require('../utils/crypto');

class RotationService {
  constructor(vault, auditLogger) {
    this.vault = vault;
    this.auditLogger = auditLogger;
    this.rotationHandlers = [];
  }

  /**
   * Register a rotation handler (callback for when keys are rotated)
   * @param {Function} handler - Handler function
   */
  registerRotationHandler(handler) {
    this.rotationHandlers.push(handler);
  }

  /**
   * Rotate a specific key
   * @param {string} keyId - Key ID to rotate
   * @param {Object} options - Rotation options
   */
  async rotateKey(keyId, options = {}) {
    const { newKey, reason = 'manual', notify = true } = options;

    // Get current key info for audit
    const currentKey = await this.vault.getKeyMeta(keyId);
    
    // Perform rotation
    const result = await this.vault.rotateKey(keyId, newKey);
    
    // Log the rotation
    await this.auditLogger.logKeyRotated({
      id: result.id,
      name: result.name,
      reason
    });

    // Notify handlers
    if (notify) {
      for (const handler of this.rotationHandlers) {
        try {
          await handler({
            type: 'rotation',
            keyId: result.id,
            name: result.name,
            newKey: result.key,
            previousKeyId: currentKey.keyHash,
            reason,
            rotatedAt: result.lastRotated,
            nextRotation: result.nextRotation
          });
        } catch (e) {
          console.error('Rotation handler error:', e.message);
        }
      }
    }

    return result;
  }

  /**
   * Check and rotate keys that need rotation
   * @param {Object} options - Options
   */
  async checkAndRotate(options = {}) {
    const { autoRotate = false, dryRun = false } = options;

    const keysNeedingRotation = await this.vault.getKeysNeedingRotation();
    const results = {
      checked: keysNeedingRotation.length,
      rotated: [],
      failed: [],
      skipped: []
    };

    for (const key of keysNeedingRotation) {
      try {
        if (dryRun) {
          results.skipped.push({
            id: key.id,
            name: key.name,
            reason: 'dry run'
          });
          continue;
        }

        if (autoRotate) {
          const result = await this.rotateKey(key.id, { reason: 'scheduled' });
          results.rotated.push(result);
        } else {
          results.skipped.push({
            id: key.id,
            name: key.name,
            nextRotation: key.nextRotation,
            reason: 'auto-rotate disabled'
          });
        }
      } catch (e) {
        results.failed.push({
          id: key.id,
          name: key.name,
          error: e.message
        });
      }
    }

    return results;
  }

  /**
   * Get rotation status for all keys
   */
  async getRotationStatus() {
    const keys = await this.vault.listKeys();
    const now = new Date();

    return keys.map(key => {
      const nextRotation = new Date(key.nextRotation);
      const daysUntilRotation = Math.ceil((nextRotation - now) / (1000 * 60 * 60 * 24));
      
      return {
        id: key.id,
        name: key.name,
        service: key.service,
        enabled: key.enabled,
        lastRotated: key.lastRotated,
        nextRotation: key.nextRotation,
        daysUntilRotation,
        needsRotation: daysUntilRotation <= 0,
        rotationOverdue: daysUntilRotation < -7
      };
    });
  }

  /**
   * Set up automatic rotation check schedule
   * @param {number} intervalHours - Check interval in hours
   */
  startAutoRotation(intervalHours = 24) {
    const intervalMs = intervalHours * 60 * 60 * 1000;
    
    console.log(`Auto-rotation scheduled every ${intervalHours} hours`);
    
    setInterval(async () => {
      try {
        console.log('Running automatic rotation check...');
        const results = await this.checkAndRotate({ autoRotate: true });
        console.log(`Rotation check complete: ${results.rotated.length} rotated, ${results.failed.length} failed`);
      } catch (e) {
        console.error('Auto-rotation error:', e.message);
      }
    }, intervalMs);

    return {
      intervalHours,
      nextCheck: new Date(Date.now() + intervalMs).toISOString()
    };
  }

  /**
   * Generate rotation report
   */
  async generateReport() {
    const keys = await this.vault.listKeys();
    const now = new Date();

    const report = {
      generatedAt: now.toISOString(),
      totalKeys: keys.length,
      keysNeedingRotation: 0,
      keysHealthy: 0,
      keysDisabled: 0,
      byService: {},
      byRotationStatus: {
        current: [],
        dueSoon: [],
        overdue: [],
        disabled: []
      }
    };

    for (const key of keys) {
      if (!key.enabled) {
        report.keysDisabled++;
        report.byRotationStatus.disabled.push({
          id: key.id,
          name: key.name,
          service: key.service
        });
        continue;
      }

      const nextRotation = new Date(key.nextRotation);
      const daysUntil = Math.ceil((nextRotation - now) / (1000 * 60 * 60 * 24));

      // Group by service
      if (!report.byService[key.service]) {
        report.byService[key.service] = {
          total: 0,
          needsRotation: 0
        };
      }
      report.byService[key.service].total++;

      // Group by rotation status
      if (daysUntil <= 0) {
        report.keysNeedingRotation++;
        report.byRotationStatus.overdue.push({
          id: key.id,
          name: key.name,
          service: key.service,
          daysOverdue: Math.abs(daysUntil)
        });
        report.byService[key.service].needsRotation++;
      } else if (daysUntil <= 7) {
        report.keysHealthy++;
        report.byRotationStatus.dueSoon.push({
          id: key.id,
          name: key.name,
          service: key.service,
          daysUntil
        });
      } else {
        report.keysHealthy++;
        report.byRotationStatus.current.push({
          id: key.id,
          name: key.name,
          service: key.service,
          daysUntil
        });
      }
    }

    return report;
  }
}

module.exports = RotationService;
