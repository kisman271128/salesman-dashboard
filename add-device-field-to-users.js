// add-device-field-to-users.js
// Script untuk menambahkan field "device: null" ke semua users yang belum punya field device
// Jalankan sekali saja di Console setelah login

async function addDeviceFieldToAllUsers() {
    console.log('🔄 Starting to add device field to all users...');
    
    try {
        // Check if Firebase is available
        if (typeof database === 'undefined') {
            console.error('❌ Firebase database not available!');
            alert('❌ Firebase not initialized. Please make sure you are logged in.');
            return;
        }
        
        // Get all users from Firebase
        const usersRef = database.ref('users');
        const snapshot = await usersRef.once('value');
        const usersData = snapshot.val();
        
        if (!usersData) {
            console.log('ℹ️ No users found in Firebase');
            alert('ℹ️ No users found');
            return;
        }
        
        console.log('📋 Found users:', Object.keys(usersData));
        
        // Prepare updates
        const updates = {};
        let count = 0;
        
        for (const nik in usersData) {
            const user = usersData[nik];
            
            // Check if user already has device field
            if (!user.hasOwnProperty('device')) {
                // Add device field as null
                updates[`${nik}/device`] = null;
                count++;
                console.log(`➕ Adding device field to ${nik} (${user.name || 'Unknown'})`);
            } else {
                console.log(`✓ ${nik} already has device field:`, user.device);
            }
        }
        
        if (count === 0) {
            console.log('✅ All users already have device field');
            alert('✅ All users already have device field. No changes needed.');
            return;
        }
        
        console.log(`📊 Adding device field to ${count} users...`);
        
        // Apply all updates at once
        await usersRef.update(updates);
        
        console.log(`✅ Successfully added device field to ${count} users!`);
        alert(`✅ Success!\n\nAdded device field (null) to ${count} users.\n\nAll users can now login from any device.`);
        
        // Show updated structure
        console.log('📋 Updated users structure:');
        const updatedSnapshot = await usersRef.once('value');
        console.log(updatedSnapshot.val());
        
    } catch (error) {
        console.error('❌ Error adding device field:', error);
        alert(`❌ Error: ${error.message}`);
    }
}

// Run the function
console.log('📱 Add Device Field Script Loaded');
console.log('💡 To add device field to all users, run: addDeviceFieldToAllUsers()');

// Uncomment to run automatically:
// addDeviceFieldToAllUsers();
