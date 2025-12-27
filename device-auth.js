// Device Authentication System
// Manages device registration and validation

const DeviceAuth = {
    // Generate unique device fingerprint
    getDeviceFingerprint() {
        const userAgent = navigator.userAgent;
        const platform = navigator.platform;
        const language = navigator.language;
        const screenResolution = `${screen.width}x${screen.height}`;
        const colorDepth = screen.colorDepth;
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        
        // Create a unique string from device characteristics
        const fingerprintString = `${userAgent}|${platform}|${language}|${screenResolution}|${colorDepth}|${timezone}`;
        
        // Simple hash function (for demo - use crypto.subtle.digest in production)
        let hash = 0;
        for (let i = 0; i < fingerprintString.length; i++) {
            const char = fingerprintString.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        
        return Math.abs(hash).toString(36);
    },
    
    // Get readable device info
    getDeviceInfo() {
        const ua = navigator.userAgent;
        let device = 'Unknown Device';
        let browser = 'Unknown Browser';
        let os = 'Unknown OS';
        
        // Detect OS
        if (ua.indexOf('Win') !== -1) os = 'Windows';
        else if (ua.indexOf('Mac') !== -1) os = 'MacOS';
        else if (ua.indexOf('Linux') !== -1) os = 'Linux';
        else if (ua.indexOf('Android') !== -1) os = 'Android';
        else if (ua.indexOf('iOS') !== -1 || ua.indexOf('iPhone') !== -1 || ua.indexOf('iPad') !== -1) os = 'iOS';
        
        // Detect Browser
        if (ua.indexOf('Firefox') !== -1) browser = 'Firefox';
        else if (ua.indexOf('Chrome') !== -1) browser = 'Chrome';
        else if (ua.indexOf('Safari') !== -1) browser = 'Safari';
        else if (ua.indexOf('Edge') !== -1) browser = 'Edge';
        else if (ua.indexOf('Opera') !== -1 || ua.indexOf('OPR') !== -1) browser = 'Opera';
        
        // Detect Device Type
        if (/Mobile|Android|iPhone|iPad|iPod/.test(ua)) {
            device = /iPad|Tablet/.test(ua) ? 'Tablet' : 'Mobile Phone';
        } else {
            device = 'Desktop/Laptop';
        }
        
        return { device, browser, os };
    },
    
    // Validate device for a user
    validateDevice(userId, userRole = null) {
        console.log(`🔐 DeviceAuth: Validating device for user: ${userId} (role: ${userRole})`);
        
        // BYPASS device authentication for admin
        if (userId === 'admin' || userRole === 'admin') {
            console.log('👑 Admin user detected - bypassing device authentication');
            return {
                success: true,
                message: 'Admin access - device authentication bypassed',
                isNewRegistration: false,
                isBypass: true,
                bypassReason: 'Admin role'
            };
        }
        
        try {
            const currentFingerprint = this.getDeviceFingerprint();
            const deviceInfo = this.getDeviceInfo();
            const storageKey = `device_${userId}`;
            
            console.log(`🔑 Current device fingerprint: ${currentFingerprint}`);
            console.log(`📱 Device info:`, deviceInfo);
            
            // Get registered device from localStorage
            const registeredDevice = localStorage.getItem(storageKey);
            
            if (!registeredDevice) {
                // No device registered yet - register this device
                console.log('📝 No device registered, registering current device...');
                const deviceData = {
                    fingerprint: currentFingerprint,
                    info: deviceInfo,
                    registeredAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString()
                };
                
                localStorage.setItem(storageKey, JSON.stringify(deviceData));
                
                return {
                    success: true,
                    message: 'Device registered successfully',
                    isNewRegistration: true,
                    currentDevice: deviceData
                };
            }
            
            // Parse registered device
            const deviceData = JSON.parse(registeredDevice);
            console.log(`📋 Registered device fingerprint: ${deviceData.fingerprint}`);
            
            // Check if fingerprints match
            if (deviceData.fingerprint === currentFingerprint) {
                // Update last used time
                deviceData.lastUsed = new Date().toISOString();
                localStorage.setItem(storageKey, JSON.stringify(deviceData));
                
                console.log('✅ Device validated successfully');
                return {
                    success: true,
                    message: 'Device validated successfully',
                    isNewRegistration: false,
                    currentDevice: deviceData
                };
            } else {
                // Different device detected
                console.warn('❌ Device mismatch detected');
                return {
                    success: false,
                    message: 'Device not registered. This account is registered on another device.',
                    registeredDevice: deviceData,
                    currentDevice: {
                        fingerprint: currentFingerprint,
                        info: deviceInfo
                    }
                };
            }
            
        } catch (error) {
            console.error('❌ DeviceAuth error:', error);
            
            // On error, allow login (fail-open for better UX)
            return {
                success: true,
                message: 'Device validation skipped due to error',
                error: error.message
            };
        }
    },
    
    // Reset device registration (for admin)
    resetDevice(userId) {
        const storageKey = `device_${userId}`;
        localStorage.removeItem(storageKey);
        console.log(`🗑️ Device registration reset for user: ${userId}`);
        return { success: true, message: 'Device registration reset successfully' };
    },
    
    // Get registered device info
    getRegisteredDevice(userId) {
        const storageKey = `device_${userId}`;
        const registeredDevice = localStorage.getItem(storageKey);
        
        if (!registeredDevice) {
            return null;
        }
        
        return JSON.parse(registeredDevice);
    },
    
    // Check if device is registered
    isDeviceRegistered(userId) {
        const storageKey = `device_${userId}`;
        return localStorage.getItem(storageKey) !== null;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceAuth;
}

console.log('🔐 DeviceAuth module loaded successfully');
