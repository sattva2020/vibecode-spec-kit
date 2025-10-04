// Main Security Engine Entry Point
export { SecurityEngine } from "./core/SecurityEngine";
export { SecurityPanel } from "./components/SecurityPanel";
export { SecurityDashboard } from "./components/SecurityDashboard";
export * from "./types/SecurityTypes";

// Main Security Engine class for easy integration
import { SecurityEngine } from "./core/SecurityEngine";

export class MemoryBankSecurityEngine {
  private securityEngine: SecurityEngine;
  
  constructor() {
    this.securityEngine = new SecurityEngine();
  }

  // Initialize security engine
  async initialize(): Promise<void> {
    console.log("🔒 Initializing Memory Bank Security Engine...");
    await this.securityEngine.performSecurityScan();
    console.log("✅ Security Engine initialized successfully");
  }

  // Get security status
  getSecurityStatus() {
    return this.securityEngine.getCurrentStatus();
  }

  // Perform security scan
  async performSecurityScan() {
    return await this.securityEngine.performSecurityScan();
  }

  // Get security metrics
  getSecurityMetrics() {
    return this.securityEngine.getSecurityMetrics();
  }

  // Add security status listener
  addStatusListener(listener: (status: any) => void) {
    this.securityEngine.addStatusListener(listener);
  }

  // Remove security status listener
  removeStatusListener(listener: (status: any) => void) {
    this.securityEngine.removeStatusListener(listener);
  }
}

// Default export
export default MemoryBankSecurityEngine;
