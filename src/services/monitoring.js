/**
 * Usage Monitoring Service - Track and analyze API key usage
 */

class UsageMonitor {
  constructor(vault, auditLogger) {
    this.vault = vault;
    this.auditLogger = auditLogger;
  }

  /**
   * Record key usage
   * @param {string} keyId - Key ID
   * @param {Object} usageInfo - Usage information
   */
  async recordUsage(keyId, usageInfo = {}) {
    const { action = 'access', metadata = {} } = usageInfo;

    // Record in vault
    const result = await this.vault.recordUsage(keyId, { action, metadata });

    // Log to audit
    const key = await this.vault.getKeyMeta(keyId);
    await this.auditLogger.logKeyUsed({
      id: keyId,
      name: key.name,
      action,
      metadata
    });

    return result;
  }

  /**
   * Get usage statistics for a key
   * @param {string} keyId - Key ID
   */
  async getKeyUsage(keyId) {
    return this.vault.getKeyUsageStats(keyId);
  }

  /**
   * Get usage summary for all keys
   */
  async getUsageSummary() {
    const keys = await this.vault.listKeys();
    
    const summary = {
      totalKeys: keys.length,
      totalUsage: 0,
      activeKeys: 0,
      unusedKeys: 0,
      byService: {},
      recentlyUsed: [],
      unusedList: []
    };

    for (const key of keys) {
      summary.totalUsage += key.usageCount || 0;
      
      if (key.enabled) {
        summary.activeKeys++;
      }

      // Group by service
      if (!summary.byService[key.service]) {
        summary.byService[key.service] = {
          totalKeys: 0,
          totalUsage: 0
        };
      }
      summary.byService[key.service].totalKeys++;
      summary.byService[key.service].totalUsage += key.usageCount || 0;

      // Track unused keys
      if (!key.lastUsed) {
        summary.unusedKeys++;
        summary.unusedList.push({
          id: key.id,
          name: key.name,
          service: key.service,
          createdAt: key.createdAt
        });
      } else {
        // Track recently used (last 7 days)
        const lastUsed = new Date(key.lastUsed);
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        
        if (lastUsed >= sevenDaysAgo) {
          summary.recentlyUsed.push({
            id: key.id,
            name: key.name,
            service: key.service,
            usageCount: key.usageCount,
            lastUsed: key.lastUsed
          });
        }
      }
    }

    return summary;
  }

  /**
   * Get usage by time period
   * @param {string} keyId - Key ID
   * @param {Object} period - Time period
   */
  async getUsageByPeriod(keyId, period = { days: 30 }) {
    const stats = await this.vault.getKeyUsageStats(keyId);
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - period.days);

    const history = (stats.usageHistory || []).filter(entry => {
      return new Date(entry.timestamp) >= cutoff;
    });

    // Group by day
    const byDay = {};
    for (const entry of history) {
      const date = entry.timestamp.split('T')[0];
      if (!byDay[date]) {
        byDay[date] = { count: 0, actions: {} };
      }
      byDay[date].count++;
      byDay[date].actions[entry.action] = (byDay[date].actions[entry.action] || 0) + 1;
    }

    return {
      period: period.days,
      totalUsage: history.length,
      byDay,
      uniqueActions: [...new Set(history.map(h => h.action))]
    };
  }

  /**
   * Detect anomalous usage patterns
   * @param {string} keyId - Key ID
   */
  async detectAnomalies(keyId) {
    const stats = await this.vault.getKeyUsageStats(keyId);
    const history = stats.usageHistory || [];

    if (history.length < 10) {
      return {
        hasAnomalies: false,
        reason: 'Insufficient data for analysis'
      };
    }

    const anomalies = [];
    
    // Calculate average usage
    const usageTimes = history.map(h => new Date(h.timestamp).getTime());
    const avgGap = (usageTimes[0] - usageTimes[usageTimes.length - 1]) / usageTimes.length;
    
    // Check for unusual frequency
    const recentHistory = history.slice(-10);
    const recentGaps = [];
    for (let i = 1; i < recentHistory.length; i++) {
      recentGaps.push(
        new Date(recentHistory[i - 1].timestamp).getTime() - 
        new Date(recentHistory[i].timestamp).getTime()
      );
    }
    
    if (recentGaps.length > 0) {
      const avgRecentGap = recentGaps.reduce((a, b) => a + b, 0) / recentGaps.length;
      
      if (avgRecentGap < avgGap * 0.1) {
        anomalies.push({
          type: 'high_frequency',
          message: 'Unusually high usage frequency detected'
        });
      }
    }

    // Check for irregular hours
    const hours = recentHistory.map(h => new Date(h.timestamp).getHours());
    const nightUsage = hours.filter(h => h >= 0 && h < 6).length;
    if (nightUsage > recentHistory.length * 0.3) {
      anomalies.push({
        type: 'unusual_hours',
        message: 'Significant usage during unusual hours (midnight-6am)'
      });
    }

    return {
      hasAnomalies: anomalies.length > 0,
      anomalies,
      analysis: {
        averageGapMs: avgGap,
        totalEvents: history.length,
        lastUsed: stats.lastUsed
      }
    };
  }

  /**
   * Get health score for a key
   * @param {string} keyId - Key ID
   */
  async getHealthScore(keyId) {
    const key = await this.vault.getKeyMeta(keyId);
    const stats = await this.vault.getKeyUsageStats(keyId);
    
    let score = 100;
    const issues = [];

    // Check if enabled
    if (!key.enabled) {
      score -= 50;
      issues.push('Key is disabled');
    }

    // Check rotation status
    const now = new Date();
    const nextRotation = new Date(key.nextRotation);
    const daysUntilRotation = Math.ceil((nextRotation - now) / (1000 * 60 * 60 * 24));

    if (daysUntilRotation < 0) {
      score -= 30;
      issues.push(`Rotation overdue by ${Math.abs(daysUntilRotation)} days`);
    } else if (daysUntilRotation < 7) {
      score -= 10;
      issues.push(`Rotation due in ${daysUntilRotation} days`);
    }

    // Check usage activity
    if (!key.lastUsed) {
      score -= 20;
      issues.push('Key has never been used');
    } else {
      const lastUsed = new Date(key.lastUsed);
      const daysSinceUse = Math.ceil((now - lastUsed) / (1000 * 60 * 60 * 24));
      
      if (daysSinceUse > 90) {
        score -= 25;
        issues.push(`Key unused for ${daysSinceUse} days`);
      } else if (daysSinceUse > 30) {
        score -= 10;
        issues.push(`Key unused for ${daysSinceUse} days`);
      }
    }

    // Check usage count
    if (key.usageCount === 0) {
      score -= 15;
      issues.push('Key has zero usage count');
    }

    return {
      score: Math.max(0, score),
      status: score >= 80 ? 'healthy' : score >= 50 ? 'warning' : 'critical',
      issues,
      details: {
        rotation: {
          nextRotation: key.nextRotation,
          daysUntilRotation,
          lastRotated: key.lastRotated
        },
        usage: {
          usageCount: key.usageCount,
          lastUsed: key.lastUsed
        }
      }
    };
  }

  /**
   * Get overall vault health
   */
  async getVaultHealth() {
    const keys = await this.vault.listKeys();
    const healthScores = [];

    for (const key of keys) {
      const health = await this.getHealthScore(key.id);
      healthScores.push({
        id: key.id,
        name: key.name,
        ...health
      });
    }

    const avgScore = healthScores.length > 0
      ? healthScores.reduce((sum, h) => sum + h.score, 0) / healthScores.length
      : 100;

    return {
      overallScore: Math.round(avgScore),
      status: avgScore >= 80 ? 'healthy' : avgScore >= 50 ? 'warning' : 'critical',
      keyCount: keys.length,
      keysByStatus: {
        healthy: healthScores.filter(h => h.status === 'healthy').length,
        warning: healthScores.filter(h => h.status === 'warning').length,
        critical: healthScores.filter(h => h.status === 'critical').length
      },
      keys: healthScores
    };
  }
}

module.exports = UsageMonitor;
