# SmartChat Mobile App 📱💰

A Cordova-based mobile application for financial assistance with AI-powered chat capabilities.

## 🚀 Features

- **Financial Chat Assistant** - AI-powered financial advice and Q&A
- **Account Management** - View balances and transaction history  
- **Cross-Platform** - Runs on Android, iOS, and web browsers
- **Secure Authentication** - Token-based user authentication
- **Real-time Chat** - Integrated with Rasa AI chatbot

## 🛠 Tech Stack

### Frontend
- **Cordova** - Mobile app framework
- **Vanilla JavaScript** - Frontend logic
- **HTML5/CSS3** - UI components with Apple-style design
- **FrontController Pattern** - Custom MVC architecture

### Backend
- **Python Flask** - REST API server
- **Rasa** - AI chatbot framework
- **SQLite/PostgreSQL** - Database management
- **JWT** - Authentication tokens

## 📋 Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- Android Studio (for Android builds)
- Java JDK 8+

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/undextrois/smartchat-mobile-app.git
cd smartchat-mobile-app
```

### 2. Install Cordova Dependencies
```bash
npm install -g cordova
npm install
```

### 3. Add Android Platform
```bash
cordova platform add android
```

### 4. Install Python Dependencies
```bash
cd ../smartchat-backend  # Navigate to your backend
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

### Start Backend Server https://github.com/Robotronut/SmartChat


### Build and Run Mobile App
```bash
cd smartchat-mobile-app
cordova run android
```

### For Web Development
```bash
# Use any local server, e.g.:
python -m http.server 8000
# Then open http://localhost:8000
```

## 🔧 Configuration

### Network Configuration
The app automatically detects environment and uses appropriate API URLs:

- **Android Emulator**: `http://10.0.2.2:5000/api`
- **Physical Device**: `http://[YOUR_IP]:5000/api` 
- **Web Browser**: `http://localhost:5000/api`

### Android Network Security
For Cordova Android builds, ensure `platforms/android/app/src/main/AndroidManifest.xml` contains:
```xml
<application
    android:usesCleartextTraffic="true"
    android:networkSecurityConfig="@xml/network_security_config">
```

## 🗂 Project Structure
```
smartchat-mobile-app/
├── www/
│   ├── index.html          # Main app entry point
│   ├── js/
│   │   ├── config.js       # Environment configuration
│   │   └── index.js        # Main application logic
│   └── css/
│       └── index.css       # Stylesheets
├── platforms/              # Cordova platform builds
├── plugins/               # Cordova plugins
├── config.xml            # Cordova configuration
└── package.json          # Node.js dependencies
```

## 🎯 Key Components

### FrontController Class
- Manages routing and navigation
- Handles API communication
- Provides validation utilities
- Manages application state

### Authentication Flow
1. User login with username/password
2. JWT token generation
3. Automatic token refresh
4. Secure API calls with Authorization headers

### Chat System
- Real-time messaging with Rasa AI
- Session management
- Chat history persistence
- Fallback responses when AI is unavailable

## 🔐 Security Features

- JWT token-based authentication
- Automatic token refresh
- Input validation and sanitization
- Secure API communication
- CORS configuration for cross-origin requests

## 🐛 Troubleshooting

### Common Issues

**Network Connection Errors in Android Emulator**
- Ensure Flask server runs on `0.0.0.0:5000`
- Verify `android:usesCleartextTraffic="true"` in AndroidManifest
- Check network security configuration

**CORS Errors**
- Verify Flask CORS configuration
- Ensure no duplicate CORS headers
- Check preflight request handling

**Build Issues**
- Clear platform and re-add: `cordova platform remove android && cordova platform add android`
- Check Android SDK installation
- Verify Java JDK version

## 📱 Building for Production

### Android APK
```bash
cordova build android --release
```

### iOS (Requires macOS)
```bash
cordova platform add ios
cordova build ios
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Rasa Open Source for chatbot capabilities
- Cordova community for mobile framework
- Flask for lightweight backend API

---

**Developed with ❤️ by [undextrois](https://github.com/undextrois)**

For support or questions, please open an issue on GitHub.
