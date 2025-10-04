// Security Engine Types
export interface SecurityStatus {
  level: SecurityLevel;
  score: number;
  lastChecked: Date;
  vulnerabilities: Vulnerability[];
  compliance: ComplianceStatus;
}

export enum SecurityLevel {
  LOW = "low",
  MEDIUM = "medium", 
  HIGH = "high",
  CRITICAL = "critical"
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: SecurityLevel;
  description: string;
  affectedFiles: string[];
  fixRecommendation: string;
  detectedAt: Date;
}

export interface ComplianceStatus {
  gdpr: boolean;
  iso27001: boolean;
  soc2: boolean;
  lastAudit: Date;
  issues: ComplianceIssue[];
}

export interface ComplianceIssue {
  id: string;
  standard: string;
  requirement: string;
  status: "pass" | "fail" | "warning";
  description: string;
}

export interface SecurityRule {
  id: string;
  name: string;
  description: string;
  severity: SecurityLevel;
  enabled: boolean;
  checkFunction: () => Promise<SecurityCheckResult>;
}

export interface SecurityCheckResult {
  passed: boolean;
  score: number;
  issues: string[];
  recommendations: string[];
}

export interface SecurityMetrics {
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  averageScore: number;
  trend: "improving" | "stable" | "declining";
  lastWeekScore: number;
  currentWeekScore: number;
}
