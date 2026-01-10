// Device Authentication System - Firebase Version (2 Devices Support)
// Manages device registration and validation using Firebase Realtime Database
// Updated to support up to 2 devices per user

const DeviceAuth = {
    // Firebase reference (will be initialized from index.html)
    firebase: null,
    
    // Maximum devices per user
    MAX_DEVICES: 2,
    
    // Initialize Firebase reference
    init(firebaseRef) {
        this.firebase = firebaseRef;
        console.log('🔐 DeviceAuth: Firebase initialized (Max devices per user: 2)');
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
    
    // Validate device for a user (Firebase version with 2 devices support)
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
            
            // Get registered devices (now supporting multiple devices)
            let registeredDevices = userData.devices || [];
            
            // Convert old single device format to new array format
            if (userData.device && !Array.isArray(userData.device)) {
                console.log('🔄 Converting old single device format to new format...');
                registeredDevices = [userData.device];
                await userRef.update({ 
                    devices: registeredDevices,
                    device: null  // Remove old format
                });
            }
            
            console.log(`📋 Registered devices count: ${registeredDevices.length}/${this.MAX_DEVICES}`);
            
            // Check if current device is already registered
            const existingDeviceIndex = registeredDevices.findIndex(
                dev => dev.fingerprint === currentFingerprint
            );
            
            if (existingDeviceIndex !== -1) {
                // Device already registered - update last used time
                console.log('✅ Device already registered, updating last used time...');
                registeredDevices[existingDeviceIndex].lastUsed = new Date().toISOString();
                
                await userRef.update({ devices: registeredDevices });
                
                return {
                    success: true,
                    message: 'Device validated successfully',
                    isNewRegistration: false,
                    currentDevice: registeredDevices[existingDeviceIndex],
                    deviceNumber: existingDeviceIndex + 1,
                    totalDevices: registeredDevices.length
                };
            }
            
            // Device not registered yet
            if (registeredDevices.length < this.MAX_DEVICES) {
                // Space available - register new device
                console.log(`🆕 Registering new device (${registeredDevices.length + 1}/${this.MAX_DEVICES})...`);
                
                const newDevice = {
                    fingerprint: currentFingerprint,
                    info: deviceInfo,
                    registeredAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString()
                };
                
                registeredDevices.push(newDevice);
                await userRef.update({ devices: registeredDevices });
                
                console.log('✅ New device registered successfully');
                
                return {
                    success: true,
                    message: `Device registered successfully (${registeredDevices.length}/${this.MAX_DEVICES})`,
                    isNewRegistration: true,
                    currentDevice: newDevice,
                    deviceNumber: registeredDevices.length,
                    totalDevices: registeredDevices.length
                };
            } else {
                // Maximum devices reached
                console.warn('❌ Maximum devices limit reached');
                
                return {
                    success: false,
                    message: `Maximum ${this.MAX_DEVICES} devices already registered`,
                    maxDevices: this.MAX_DEVICES,
                    registeredDevices: registeredDevices.map((dev, idx) => ({
                        number: idx + 1,
                        info: dev.info,
                        registeredAt: dev.registeredAt,
                        lastUsed: dev.lastUsed
                    })),
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
    
    // Fallback: localStorage validation with 2 devices support
    validateDeviceLocalStorage(userId) {
        try {
            const currentFingerprint = this.getDeviceFingerprint();
            const deviceInfo = this.getDeviceInfo();
            const storageKey = `devices_${userId}`;
            
            let registeredDevices = [];
            const storedData = localStorage.getItem(storageKey);
            
            if (storedData) {
                try {
                    registeredDevices = JSON.parse(storedData);
                    if (!Array.isArray(registeredDevices)) {
                        registeredDevices = [registeredDevices]; // Convert old format
                    }
                } catch (e) {
                    registeredDevices = [];
                }
            }
            
            // Check if device already registered
            const existingDeviceIndex = registeredDevices.findIndex(
                dev => dev.fingerprint === currentFingerprint
            );
            
            if (existingDeviceIndex !== -1) {
                // Update last used
                registeredDevices[existingDeviceIndex].lastUsed = new Date().toISOString();
                localStorage.setItem(storageKey, JSON.stringify(registeredDevices));
                
                return {
                    success: true,
                    message: 'Device validated successfully (localStorage)',
                    isNewRegistration: false,
                    currentDevice: registeredDevices[existingDeviceIndex],
                    deviceNumber: existingDeviceIndex + 1,
                    totalDevices: registeredDevices.length
                };
            }
            
            // Check if can add new device
            if (registeredDevices.length < this.MAX_DEVICES) {
                const newDevice = {
                    fingerprint: currentFingerprint,
                    info: deviceInfo,
                    registeredAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString()
                };
                
                registeredDevices.push(newDevice);
                localStorage.setItem(storageKey, JSON.stringify(registeredDevices));
                
                return {
                    success: true,
                    message: `Device registered successfully (localStorage) (${registeredDevices.length}/${this.MAX_DEVICES})`,
                    isNewRegistration: true,
                    currentDevice: newDevice,
                    deviceNumber: registeredDevices.length,
                    totalDevices: registeredDevices.length
                };
            } else {
                return {
                    success: false,
                    message: `Maximum ${this.MAX_DEVICES} devices already registered (localStorage)`,
                    maxDevices: this.MAX_DEVICES,
                    registeredDevices: registeredDevices.map((dev, idx) => ({
                        number: idx + 1,
                        info: dev.info,
                        registeredAt: dev.registeredAt,
                        lastUsed: dev.lastUsed
                    })),
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
    
    // Reset ALL device registrations for a user
    async resetAllDevices(userId) {
        if (!this.firebase) {
            console.warn('⚠️ Firebase not initialized, using localStorage');
            const storageKey = `devices_${userId}`;
            localStorage.removeItem(storageKey);
            console.log(`🗑️ All devices reset for user: ${userId} (localStorage)`);
            return { success: true, message: 'All device registrations reset successfully (localStorage)' };
        }
        
        try {
            const userRef = this.firebase.ref(`users/${userId}`);
            await userRef.update({ 
                devices: [],
                device: null  // Also clear old format
            });
            
            console.log(`🗑️ All devices reset for user: ${userId} (Firebase)`);
            return { success: true, message: 'All device registrations reset successfully (Firebase)' };
        } catch (error) {
            console.error('❌ Error resetting devices:', error);
            return { success: false, message: 'Failed to reset devices', error: error.message };
        }
    },
    
    // Remove specific device by fingerprint
    async removeDevice(userId, deviceFingerprint) {
        if (!this.firebase) {
            const storageKey = `devices_${userId}`;
            let registeredDevices = [];
            const storedData = localStorage.getItem(storageKey);
            
            if (storedData) {
                registeredDevices = JSON.parse(storedData);
                registeredDevices = registeredDevices.filter(dev => dev.fingerprint !== deviceFingerprint);
                localStorage.setItem(storageKey, JSON.stringify(registeredDevices));
            }
            
            console.log(`🗑️ Device removed for user: ${userId} (localStorage)`);
            return { success: true, message: 'Device removed successfully (localStorage)' };
        }
        
        try {
            const userRef = this.firebase.ref(`users/${userId}`);
            const snapshot = await userRef.once('value');
            const userData = snapshot.val();
            
            if (userData && userData.devices) {
                const updatedDevices = userData.devices.filter(dev => dev.fingerprint !== deviceFingerprint);
                await userRef.update({ devices: updatedDevices });
                
                console.log(`🗑️ Device removed for user: ${userId} (Firebase)`);
                return { success: true, message: 'Device removed successfully (Firebase)' };
            }
            
            return { success: false, message: 'No devices found' };
        } catch (error) {
            console.error('❌ Error removing device:', error);
            return { success: false, message: 'Failed to remove device', error: error.message };
        }
    },
    
    // Get all registered devices for a user
    async getRegisteredDevices(userId) {
        if (!this.firebase) {
            const storageKey = `devices_${userId}`;
            const storedData = localStorage.getItem(storageKey);
            return storedData ? JSON.parse(storedData) : [];
        }
        
        try {
            const userRef = this.firebase.ref(`users/${userId}`);
            const snapshot = await userRef.once('value');
            const userData = snapshot.val();
            
            return userData && userData.devices ? userData.devices : [];
        } catch (error) {
            console.error('❌ Error getting registered devices:', error);
            return [];
        }
    },
    
    // Check how many devices are registered
    async getDeviceCount(userId) {
        const devices = await this.getRegisteredDevices(userId);
        return devices.length;
    },
    
    // Check if device limit reached
    async isDeviceLimitReached(userId) {
        const count = await this.getDeviceCount(userId);
        return count >= this.MAX_DEVICES;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceAuth;
}

console.log('🔐 DeviceAuth module loaded successfully (Firebase version with 2 devices support)');