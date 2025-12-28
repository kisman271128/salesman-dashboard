// Device Authentication System - Firebase Version
// Manages device registration and validation using Firebase Realtime Database

const DeviceAuth = {
    // Firebase reference (will be initialized from index.html)
    firebase: null,
    
    // Initialize Firebase reference
    init(firebaseRef) {
        this.firebase = firebaseRef;
        console.log('🔐 DeviceAuth: Firebase initialized');
    },
    
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
    
    // Validate device for a user (Firebase version)
    async validateDevice(userId, userRole = null) {
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
        
        if (!this.firebase) {
            console.warn('⚠️ Firebase not initialized, falling back to localStorage');
            return this.validateDeviceLocalStorage(userId);
        }
        
        try {
            const currentFingerprint = this.getDeviceFingerprint();
            const deviceInfo = this.getDeviceInfo();
            
            console.log(`🔑 Current device fingerprint: ${currentFingerprint}`);
            console.log(`📱 Device info:`, deviceInfo);
            
            // Get user data from Firebase
            const userRef = this.firebase.ref(`users/${userId}`);
            const snapshot = await userRef.once('value');
            const userData = snapshot.val();
            
            if (!userData) {
                console.error('❌ User not found in Firebase');
                return {
                    success: false,
                    message: 'User not found'
                };
            }
            
            const registeredDevice = userData.device;
            
            if (!registeredDevice || registeredDevice === null) {
                // No device registered yet - register this device
                console.log('📝 No device registered, registering current device in Firebase...');
                const deviceData = {
                    fingerprint: currentFingerprint,
                    info: deviceInfo,
                    registeredAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString()
                };
                
                // Save to Firebase
                await userRef.update({ device: deviceData });
                console.log('✅ Device registered in Firebase successfully');
                
                return {
                    success: true,
                    message: 'Device registered successfully',
                    isNewRegistration: true,
                    currentDevice: deviceData
                };
            }
            
            console.log(`📋 Registered device fingerprint: ${registeredDevice.fingerprint}`);
            
            // Check if fingerprints match
            if (registeredDevice.fingerprint === currentFingerprint) {
                // Update last used time in Firebase
                const updatedDevice = {
                    ...registeredDevice,
                    lastUsed: new Date().toISOString()
                };
                await userRef.update({ device: updatedDevice });
                
                console.log('✅ Device validated successfully (Firebase)');
                return {
                    success: true,
                    message: 'Device validated successfully',
                    isNewRegistration: false,
                    currentDevice: updatedDevice
                };
            } else {
                // Different device detected
                console.warn('❌ Device mismatch detected');
                return {
                    success: false,
                    message: 'Device not registered. This account is registered on another device.',
                    registeredDevice: registeredDevice,
                    currentDevice: {
                        fingerprint: currentFingerprint,
                        info: deviceInfo
                    }
                };
            }
            
        } catch (error) {
            console.error('❌ DeviceAuth Firebase error:', error);
            
            // On error, fallback to localStorage
            console.log('⚠️ Falling back to localStorage validation');
            return this.validateDeviceLocalStorage(userId);
        }
    },
    
    // Fallback: localStorage validation (for backward compatibility)
    validateDeviceLocalStorage(userId) {
        try {
            const currentFingerprint = this.getDeviceFingerprint();
            const deviceInfo = this.getDeviceInfo();
            const storageKey = `device_${userId}`;
            
            const registeredDevice = localStorage.getItem(storageKey);
            
            if (!registeredDevice) {
                const deviceData = {
                    fingerprint: currentFingerprint,
                    info: deviceInfo,
                    registeredAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString()
                };
                
                localStorage.setItem(storageKey, JSON.stringify(deviceData));
                
                return {
                    success: true,
                    message: 'Device registered successfully (localStorage)',
                    isNewRegistration: true,
                    currentDevice: deviceData
                };
            }
            
            const deviceData = JSON.parse(registeredDevice);
            
            if (deviceData.fingerprint === currentFingerprint) {
                deviceData.lastUsed = new Date().toISOString();
                localStorage.setItem(storageKey, JSON.stringify(deviceData));
                
                return {
                    success: true,
                    message: 'Device validated successfully (localStorage)',
                    isNewRegistration: false,
                    currentDevice: deviceData
                };
            } else {
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
            console.error('❌ DeviceAuth localStorage error:', error);
            return {
                success: true,
                message: 'Device validation skipped due to error',
                error: error.message
            };
        }
    },
    
    // Reset device registration in Firebase
    async resetDevice(userId) {
        if (!this.firebase) {
            console.warn('⚠️ Firebase not initialized, using localStorage');
            const storageKey = `device_${userId}`;
            localStorage.removeItem(storageKey);
            console.log(`🗑️ Device registration reset for user: ${userId} (localStorage)`);
            return { success: true, message: 'Device registration reset successfully (localStorage)' };
        }
        
        try {
            const userRef = this.firebase.ref(`users/${userId}`);
            await userRef.update({ device: null });
            
            console.log(`🗑️ Device registration reset for user: ${userId} (Firebase)`);
            return { success: true, message: 'Device registration reset successfully (Firebase)' };
        } catch (error) {
            console.error('❌ Error resetting device:', error);
            return { success: false, message: 'Failed to reset device', error: error.message };
        }
    },
    
    // Get registered device info from Firebase
    async getRegisteredDevice(userId) {
        if (!this.firebase) {
            const storageKey = `device_${userId}`;
            const registeredDevice = localStorage.getItem(storageKey);
            return registeredDevice ? JSON.parse(registeredDevice) : null;
        }
        
        try {
            const userRef = this.firebase.ref(`users/${userId}`);
            const snapshot = await userRef.once('value');
            const userData = snapshot.val();
            
            return userData ? userData.device : null;
        } catch (error) {
            console.error('❌ Error getting registered device:', error);
            return null;
        }
    },
    
    // Check if device is registered in Firebase
    async isDeviceRegistered(userId) {
        const device = await this.getRegisteredDevice(userId);
        return device !== null && device !== undefined;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceAuth;
}

console.log('🔐 DeviceAuth module loaded successfully (Firebase version)');