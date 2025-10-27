// ========================================
// DEVICE FINGERPRINTING & VALIDATION SYSTEM
// ========================================

const DeviceAuth = {
    // Storage keys
    STORAGE_KEY: 'device_fingerprint',
    REGISTERED_DEVICES_KEY: 'registered_devices',
    DEVICE_INFO_KEY: 'device_info',
    
    // Generate unique device fingerprint
    generateFingerprint: function() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('Device ID', 2, 2);
        const canvasData = canvas.toDataURL();
        
        const fingerprint = {
            userAgent: navigator.userAgent,
            language: navigator.language,
            languages: navigator.languages ? navigator.languages.join(',') : '',
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency || 0,
            deviceMemory: navigator.deviceMemory || 0,
            screenWidth: screen.width,
            screenHeight: screen.height,
            screenColorDepth: screen.colorDepth,
            screenPixelDepth: screen.pixelDepth,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timezoneOffset: new Date().getTimezoneOffset(),
            canvas: this.hashCode(canvasData),
            touchSupport: 'ontouchstart' in window,
            maxTouchPoints: navigator.maxTouchPoints || 0,
            vendor: navigator.vendor,
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack,
            plugins: this.getPlugins(),
            battery: 'getBattery' in navigator
        };
        
        // Create a unique hash from all fingerprint data
        const fingerprintString = JSON.stringify(fingerprint);
        const hash = this.hashCode(fingerprintString);
        
        return {
            id: hash,
            data: fingerprint,
            generated: new Date().toISOString()
        };
    },
    
    // Simple hash function
    hashCode: function(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash).toString(36);
    },
    
    // Get browser plugins
    getPlugins: function() {
        if (!navigator.plugins) return '';
        const plugins = [];
        for (let i = 0; i < navigator.plugins.length; i++) {
            plugins.push(navigator.plugins[i].name);
        }
        return plugins.join(',');
    },
    
    // Get or create device fingerprint
    getDeviceFingerprint: function() {
        let stored = localStorage.getItem(this.STORAGE_KEY);
        
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.warn('Invalid stored fingerprint, generating new one');
            }
        }
        
        const fingerprint = this.generateFingerprint();
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(fingerprint));
        
        console.log('🔐 Device Fingerprint Generated:', fingerprint.id);
        return fingerprint;
    },
    
    // Register device for a user
    registerDevice: function(username) {
        const fingerprint = this.getDeviceFingerprint();
        const registeredDevices = this.getRegisteredDevices();
        
        // Check if user already has a registered device
        const existingDevice = registeredDevices[username];
        
        if (existingDevice && existingDevice.id !== fingerprint.id) {
            return {
                success: false,
                message: 'User sudah terdaftar di device lain',
                existingDevice: existingDevice,
                currentDevice: fingerprint
            };
        }
        
        // Register this device
        registeredDevices[username] = {
            id: fingerprint.id,
            deviceInfo: this.getReadableDeviceInfo(fingerprint.data),
            registeredAt: new Date().toISOString(),
            lastAccess: new Date().toISOString()
        };
        
        localStorage.setItem(this.REGISTERED_DEVICES_KEY, JSON.stringify(registeredDevices));
        
        console.log('✅ Device registered for user:', username);
        return {
            success: true,
            message: 'Device berhasil didaftarkan',
            device: registeredDevices[username]
        };
    },
    
    // Validate device for a user
    validateDevice: function(username) {
        const currentFingerprint = this.getDeviceFingerprint();
        const registeredDevices = this.getRegisteredDevices();
        
        const registeredDevice = registeredDevices[username];
        
        // If no device registered yet, auto-register
        if (!registeredDevice) {
            console.log('📱 No device registered, auto-registering...');
            return this.registerDevice(username);
        }
        
        // Check if current device matches
        if (registeredDevice.id === currentFingerprint.id) {
            // Update last access
            registeredDevice.lastAccess = new Date().toISOString();
            registeredDevices[username] = registeredDevice;
            localStorage.setItem(this.REGISTERED_DEVICES_KEY, JSON.stringify(registeredDevices));
            
            console.log('✅ Device validated for user:', username);
            return {
                success: true,
                message: 'Device tervalidasi',
                device: registeredDevice
            };
        } else {
            console.warn('❌ Device mismatch for user:', username);
            return {
                success: false,
                message: 'Device tidak terdaftar. Hubungi administrator.',
                registeredDevice: registeredDevice,
                currentDevice: {
                    id: currentFingerprint.id,
                    info: this.getReadableDeviceInfo(currentFingerprint.data)
                }
            };
        }
    },
    
    // Get all registered devices
    getRegisteredDevices: function() {
        const stored = localStorage.getItem(this.REGISTERED_DEVICES_KEY);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.warn('Invalid registered devices data');
            }
        }
        return {};
    },
    
    // Get readable device info
    getReadableDeviceInfo: function(deviceData) {
        const ua = deviceData.userAgent.toLowerCase();
        let browser = 'Unknown';
        let os = 'Unknown';
        let device = 'Unknown';
        
        // Detect Browser
        if (ua.includes('chrome') && !ua.includes('edg')) browser = 'Chrome';
        else if (ua.includes('firefox')) browser = 'Firefox';
        else if (ua.includes('safari') && !ua.includes('chrome')) browser = 'Safari';
        else if (ua.includes('edg')) browser = 'Edge';
        else if (ua.includes('opera') || ua.includes('opr')) browser = 'Opera';
        
        // Detect OS
        if (ua.includes('android')) os = 'Android';
        else if (ua.includes('iphone') || ua.includes('ipad')) os = 'iOS';
        else if (ua.includes('windows')) os = 'Windows';
        else if (ua.includes('mac')) os = 'MacOS';
        else if (ua.includes('linux')) os = 'Linux';
        
        // Detect Device Type
        if (deviceData.touchSupport && deviceData.maxTouchPoints > 0) {
            if (deviceData.screenWidth < 768) device = 'Mobile';
            else device = 'Tablet';
        } else {
            device = 'Desktop';
        }
        
        return {
            browser: browser,
            os: os,
            device: device,
            screen: `${deviceData.screenWidth}x${deviceData.screenHeight}`,
            language: deviceData.language,
            timezone: deviceData.timezone
        };
    },
    
    // Unregister device for a user (admin function)
    unregisterDevice: function(username) {
        const registeredDevices = this.getRegisteredDevices();
        if (registeredDevices[username]) {
            delete registeredDevices[username];
            localStorage.setItem(this.REGISTERED_DEVICES_KEY, JSON.stringify(registeredDevices));
            console.log('🗑️ Device unregistered for user:', username);
            return true;
        }
        return false;
    },
    
    // Get device info summary
    getDeviceSummary: function() {
        const fingerprint = this.getDeviceFingerprint();
        const info = this.getReadableDeviceInfo(fingerprint.data);
        
        return {
            id: fingerprint.id,
            ...info,
            generated: fingerprint.generated
        };
    },
    
    // Check if admin mode (bypass device check)
    isAdminMode: function(username) {
        return username === 'admin';
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Device Auth System Initialized');
    const deviceSummary = DeviceAuth.getDeviceSummary();
    console.log('📱 Device Info:', deviceSummary);
});
