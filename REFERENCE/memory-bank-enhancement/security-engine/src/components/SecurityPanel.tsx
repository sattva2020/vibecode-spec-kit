// Security Panel React Component
import React, { useState, useEffect } from "react";
import { SecurityStatus, SecurityLevel, Vulnerability, ComplianceStatus } from "../types/SecurityTypes";
import { SecurityEngine } from "../core/SecurityEngine";

interface SecurityPanelProps {
  isVisible: boolean;
  onToggle: () => void;
}

export const SecurityPanel: React.FC<SecurityPanelProps> = ({ isVisible, onToggle }) => {
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [securityEngine] = useState(() => new SecurityEngine());

  useEffect(() => {
    // Add status listener
    const handleStatusUpdate = (status: SecurityStatus) => {
      setSecurityStatus(status);
      setIsScanning(false);
    };

    securityEngine.addStatusListener(handleStatusUpdate);

    // Initial status
    setSecurityStatus(securityEngine.getCurrentStatus());

    return () => {
      securityEngine.removeStatusListener(handleStatusUpdate);
    };
  }, [securityEngine]);

  const handleScanNow = async () => {
    setIsScanning(true);
    await securityEngine.performSecurityScan();
  };

  const getStatusColor = (level: SecurityLevel): string => {
    switch (level) {
      case SecurityLevel.LOW: return "text-green-600 bg-green-100";
      case SecurityLevel.MEDIUM: return "text-yellow-600 bg-yellow-100";
      case SecurityLevel.HIGH: return "text-orange-600 bg-orange-100";
      case SecurityLevel.CRITICAL: return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    if (score >= 40) return "text-orange-600";
    return "text-red-600";
  };

  if (!isVisible) {
    return (
      <button
        onClick={onToggle}
        className="fixed top-4 right-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
      >
        🔒 Security
      </button>
    );
  }

  return (
    <div className="fixed top-0 right-0 w-96 h-full bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Security Panel</h2>
          <button
            onClick={onToggle}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Security Status */}
        {securityStatus && (
          <div className="space-y-4">
            {/* Overall Status */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">Overall Security</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(securityStatus.level)}`}>
                  {securityStatus.level.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${getScoreColor(securityStatus.score)}`}
                    style={{ width: `${securityStatus.score}%`, backgroundColor: securityStatus.score >= 80 ? "#10b981" : securityStatus.score >= 60 ? "#f59e0b" : securityStatus.score >= 40 ? "#f97316" : "#ef4444" }}
                  />
                </div>
                <span className={`text-sm font-medium ${getScoreColor(securityStatus.score)}`}>
                  {securityStatus.score}/100
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Last checked: {securityStatus.lastChecked.toLocaleString()}
              </p>
            </div>

            {/* Scan Button */}
            <button
              onClick={handleScanNow}
              disabled={isScanning}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isScanning ? "🔍 Scanning..." : "🔍 Scan Now"}
            </button>

            {/* Vulnerabilities */}
            {securityStatus.vulnerabilities.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">Vulnerabilities ({securityStatus.vulnerabilities.length})</h4>
                {securityStatus.vulnerabilities.map((vuln) => (
                  <div key={vuln.id} className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <h5 className="font-medium text-red-900">{vuln.title}</h5>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(vuln.severity)}`}>
                        {vuln.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-red-700 mb-2">{vuln.description}</p>
                    <p className="text-xs text-red-600">
                      💡 {vuln.fixRecommendation}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Compliance Status */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Compliance</h4>
              <div className="grid grid-cols-1 gap-2">
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700">GDPR</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.gdpr ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                    {securityStatus.compliance.gdpr ? "✅ Compliant" : "❌ Non-compliant"}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700">ISO 27001</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.iso27001 ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                    {securityStatus.compliance.iso27001 ? "✅ Compliant" : "❌ Non-compliant"}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700">SOC 2</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${securityStatus.compliance.soc2 ? "text-green-600 bg-green-100" : "text-red-600 bg-red-100"}`}>
                    {securityStatus.compliance.soc2 ? "✅ Compliant" : "❌ Non-compliant"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityPanel;
