/*
 * Application Configuration
 * Handles different API endpoints for various environments
 */

window.APP_CONFIG = (function() {
    'use strict';
    
    // Detect if running in Cordova
    function isCordovaApp() {
        return typeof cordova !== 'undefined' || document.URL.indexOf('http://') === -1 && document.URL.indexOf('https://') === -1;
    }
    
    // Detect if running in Android
    function isAndroid() {
        return /Android/i.test(navigator.userAgent);
    }
    
    // Detect if running in iOS
    function isIOS() {
        return /iPhone|iPad|iPod/i.test(navigator.userAgent);
    }
    
    // Get the appropriate API base URL
    function getApiBaseUrl() {
        // If running in Cordova app
        if (isCordovaApp()) {
            console.log('Running in Cordova environment');
            
            // Android emulator uses 10.0.2.2 to access host machine's localhost
            if (isAndroid()) {
                console.log('Detected Android - using 10.0.2.2');
                return 'http://10.0.2.2:5000/api';
            }
            
            // iOS simulator can use localhost
            if (isIOS()) {
                console.log('Detected iOS - using localhost');
                return 'http://localhost:5000/api';
            }
            
            // Default for other platforms
            return 'http://10.0.2.2:5000/api';
        }
        
        // For web browser during development
        console.log('Running in web browser');
        return 'http://localhost:5000/api';
    }
    
    const config = {
        apiBaseUrl: getApiBaseUrl(),
        version: '1.0.0',
        appName: 'SmartChat Financial Assistant',
        environment: isCordovaApp() ? 'mobile' : 'web',
        platform: isAndroid() ? 'android' : (isIOS() ? 'ios' : 'web')
    };
    
    console.log('App Config loaded:', config);
    
    return config;
})();