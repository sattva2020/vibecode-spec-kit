// Security Engine Core Service
import { SecurityStatus, SecurityLevel, Vulnerability, ComplianceStatus, SecurityRule, SecurityCheckResult, SecurityMetrics } from "../types/SecurityTypes";

export class SecurityEngine {
  private status: SecurityStatus;
  private rules: SecurityRule[] = [];
  private listeners: Array<(status: SecurityStatus) => void> = [];

  constructor() {
    this.status = this.initializeDefaultStatus();
    this.initializeDefaultRules();
  }

  private initializeDefaultStatus(): SecurityStatus {
    return {
      level: SecurityLevel.MEDIUM,
      score: 75,
      lastChecked: new Date(),
      vulnerabilities: [],
      compliance: {
        gdpr: true,
        iso27001: false,
        soc2: false,
        lastAudit: new Date(),
        issues: []
      }
    };
  }

  private initializeDefaultRules(): void {
    this.rules = [
      {
        id: "file-permissions",
        name: "File Permissions Check",
        description: "Check file permissions for sensitive files",
        severity: SecurityLevel.HIGH,
        enabled: true,
        checkFunction: this.checkFilePermissions.bind(this)
      },
      {
        id: "dependency-vulnerabilities",
        name: "Dependency Vulnerabilities",
        description: "Scan for known vulnerabilities in dependencies",
        severity: SecurityLevel.CRITICAL,
        enabled: true,
        checkFunction: this.checkDependencyVulnerabilities.bind(this)
      },
      {
        id: "secrets-detection",
        name: "Secrets Detection",
        description: "Scan for hardcoded secrets and credentials",
        severity: SecurityLevel.CRITICAL,
        enabled: true,
        checkFunction: this.checkSecretsDetection.bind(this)
      },
      {
        id: "code-quality",
        name: "Code Quality Security",
        description: "Check for security-related code quality issues",
        severity: SecurityLevel.MEDIUM,
        enabled: true,
        checkFunction: this.checkCodeQuality.bind(this)
      }
    ];
  }

  async performSecurityScan(): Promise<SecurityStatus> {
    console.log("🔍 Starting security scan...");
    
    const vulnerabilities: Vulnerability[] = [];
    let totalScore = 100;
    let criticalIssues = 0;

    // Run all enabled security rules
    for (const rule of this.rules) {
      if (rule.enabled) {
        try {
          const result = await rule.checkFunction();
          
          if (!result.passed) {
            vulnerabilities.push({
              id: `${rule.id}-${Date.now()}`,
              title: rule.name,
              severity: rule.severity,
              description: result.issues.join(", "),
              affectedFiles: [],
              fixRecommendation: result.recommendations.join(", "),
              detectedAt: new Date()
            });

            // Calculate score impact
            const scoreImpact = this.getScoreImpact(rule.severity);
            totalScore -= scoreImpact;
            
            if (rule.severity === SecurityLevel.CRITICAL) {
              criticalIssues++;
            }
          }
        } catch (error) {
          console.error(`Security rule ${rule.id} failed:`, error);
        }
      }
    }

    // Update security status
    this.status = {
      level: this.calculateSecurityLevel(totalScore, criticalIssues),
      score: Math.max(0, totalScore),
      lastChecked: new Date(),
      vulnerabilities,
      compliance: this.updateComplianceStatus(vulnerabilities)
    };

    // Notify listeners
    this.notifyListeners();

    console.log(`✅ Security scan completed. Score: ${this.status.score}, Level: ${this.status.level}`);
    return this.status;
  }

  private calculateSecurityLevel(score: number, criticalIssues: number): SecurityLevel {
    if (criticalIssues > 0 || score < 30) {
      return SecurityLevel.CRITICAL;
    } else if (score < 50) {
      return SecurityLevel.HIGH;
    } else if (score < 75) {
      return SecurityLevel.MEDIUM;
    } else {
      return SecurityLevel.LOW;
    }
  }

  private getScoreImpact(severity: SecurityLevel): number {
    switch (severity) {
      case SecurityLevel.CRITICAL: return 30;
      case SecurityLevel.HIGH: return 20;
      case SecurityLevel.MEDIUM: return 10;
      case SecurityLevel.LOW: return 5;
      default: return 0;
    }
  }

  private updateComplianceStatus(vulnerabilities: Vulnerability[]): ComplianceStatus {
    const criticalVulns = vulnerabilities.filter(v => v.severity === SecurityLevel.CRITICAL);
    
    return {
      gdpr: criticalVulns.length === 0,
      iso27001: this.status.score >= 80,
      soc2: this.status.score >= 85,
      lastAudit: new Date(),
      issues: criticalVulns.map(v => ({
        id: v.id,
        standard: "ISO27001",
        requirement: "Vulnerability Management",
        status: "fail" as const,
        description: v.description
      }))
    };
  }

  // Security rule implementations
  private async checkFilePermissions(): Promise<SecurityCheckResult> {
    // Simulate file permissions check
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      passed: true,
      score: 100,
      issues: [],
      recommendations: ["Ensure sensitive files have restricted permissions"]
    };
  }

  private async checkDependencyVulnerabilities(): Promise<SecurityCheckResult> {
    // Simulate dependency vulnerability check
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return {
      passed: true,
      score: 95,
      issues: [],
      recommendations: ["Regularly update dependencies", "Use automated vulnerability scanning"]
    };
  }

  private async checkSecretsDetection(): Promise<SecurityCheckResult> {
    // Simulate secrets detection
    await new Promise(resolve => setTimeout(resolve, 150));
    
    return {
      passed: true,
      score: 100,
      issues: [],
      recommendations: ["Use environment variables for secrets", "Implement secret scanning"]
    };
  }

  private async checkCodeQuality(): Promise<SecurityCheckResult> {
    // Simulate code quality security check
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      passed: true,
      score: 90,
      issues: [],
      recommendations: ["Implement input validation", "Use secure coding practices"]
    };
  }

  // Event handling
  addStatusListener(listener: (status: SecurityStatus) => void): void {
    this.listeners.push(listener);
  }

  removeStatusListener(listener: (status: SecurityStatus) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.status);
      } catch (error) {
        console.error("Error notifying security status listener:", error);
      }
    });
  }

  // Getters
  getCurrentStatus(): SecurityStatus {
    return this.status;
  }

  getSecurityMetrics(): SecurityMetrics {
    const totalChecks = this.rules.length;
    const passedChecks = this.status.vulnerabilities.length === 0 ? totalChecks : totalChecks - this.status.vulnerabilities.length;
    
    return {
      totalChecks,
      passedChecks,
      failedChecks: this.status.vulnerabilities.length,
      averageScore: this.status.score,
      trend: this.status.score >= 80 ? "improving" : this.status.score >= 60 ? "stable" : "declining",
      lastWeekScore: this.status.score - 5, // Simulated
      currentWeekScore: this.status.score
    };
  }

  // Rule management
  addSecurityRule(rule: SecurityRule): void {
    this.rules.push(rule);
  }

  updateSecurityRule(ruleId: string, updates: Partial<SecurityRule>): void {
    const ruleIndex = this.rules.findIndex(rule => rule.id === ruleId);
    if (ruleIndex !== -1) {
      this.rules[ruleIndex] = { ...this.rules[ruleIndex], ...updates };
    }
  }

  removeSecurityRule(ruleId: string): void {
    this.rules = this.rules.filter(rule => rule.id !== ruleId);
  }
}
