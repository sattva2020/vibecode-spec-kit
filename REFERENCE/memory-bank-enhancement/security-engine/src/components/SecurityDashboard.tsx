// Security Dashboard Component
import React, { useState, useEffect } from "react";
import { SecurityStatus, SecurityMetrics, SecurityLevel } from "../types/SecurityTypes";
import { SecurityEngine } from "../core/SecurityEngine";

export const SecurityDashboard: React.FC = () => {
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [securityMetrics, setSecurityMetrics] = useState<SecurityMetrics | null>(null);
  const [securityEngine] = useState(() => new SecurityEngine());

  useEffect(() => {
    const handleStatusUpdate = (status: SecurityStatus) => {
      setSecurityStatus(status);
      setSecurityMetrics(securityEngine.getSecurityMetrics());
    };

    securityEngine.addStatusListener(handleStatusUpdate);
    
    // Initial load
    setSecurityStatus(securityEngine.getCurrentStatus());
    setSecurityMetrics(securityEngine.getSecurityMetrics());

    return () => {
      securityEngine.removeStatusListener(handleStatusUpdate);
    };
  }, [securityEngine]);

  const getStatusColor = (level: SecurityLevel): string => {
    switch (level) {
      case SecurityLevel.LOW: return "text-green-600 bg-green-100";
      case SecurityLevel.MEDIUM: return "text-yellow-600 bg-yellow-100";
      case SecurityLevel.HIGH: return "text-orange-600 bg-orange-100";
      case SecurityLevel.CRITICAL: return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case "improving": return "📈";
      case "stable": return "➡️";
      case "declining": return "📉";
      default: return "➡️";
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Security Dashboard</h1>
        <p className="text-gray-600">Comprehensive security monitoring and analytics</p>
      </div>

      {/* Security Overview */}
      {securityStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Overall Score */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Security Score</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(securityStatus.level)}`}>
                {securityStatus.level.toUpperCase()}
              </span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {securityStatus.score}/100
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${securityStatus.score}%`,
                  backgroundColor: securityStatus.score >= 80 ? "#10b981" : securityStatus.score >= 60 ? "#f59e0b" : securityStatus.score >= 40 ? "#f97316" : "#ef4444"
                }}
              />
            </div>
          </div>

          {/* Vulnerabilities */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Vulnerabilities</h3>
            <div className="text-3xl font-bold text-red-600 mb-2">
              {securityStatus.vulnerabilities.length}
            </div>
            <p className="text-sm text-gray-600">
              {securityStatus.vulnerabilities.length === 0 ? "No vulnerabilities found" : "Active vulnerabilities"}
            </p>
          </div>

          {/* Compliance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">GDPR</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.gdpr ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                  {securityStatus.compliance.gdpr ? "✅" : "❌"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">ISO 27001</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.iso27001 ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                  {securityStatus.compliance.iso27001 ? "✅" : "❌"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">SOC 2</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.soc2 ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                  {securityStatus.compliance.soc2 ? "✅" : "❌"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Metrics */}
      {securityMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Total Checks</h3>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {securityMetrics.totalChecks}
            </div>
            <p className="text-sm text-gray-600">Security rules executed</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Passed</h3>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {securityMetrics.passedChecks}
            </div>
            <p className="text-sm text-gray-600">Successful checks</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Failed</h3>
            <div className="text-3xl font-bold text-red-600 mb-2">
              {securityMetrics.failedChecks}
            </div>
            <p className="text-sm text-gray-600">Failed checks</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trend</h3>
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-2xl">{getTrendIcon(securityMetrics.trend)}</span>
              <span className="text-lg font-semibold text-gray-900 capitalize">
                {securityMetrics.trend}
              </span>
            </div>
            <p className="text-sm text-gray-600">
              {securityMetrics.currentWeekScore} vs {securityMetrics.lastWeekScore} last week
            </p>
          </div>
        </div>
      )}

      {/* Vulnerability Details */}
      {securityStatus && securityStatus.vulnerabilities.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Vulnerability Details</h3>
          <div className="space-y-4">
            {securityStatus.vulnerabilities.map((vuln) => (
              <div key={vuln.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{vuln.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(vuln.severity)}`}>
                    {vuln.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{vuln.description}</p>
                <p className="text-xs text-blue-600">
                  💡 {vuln.fixRecommendation}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Detected: {vuln.detectedAt.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityDashboard;
