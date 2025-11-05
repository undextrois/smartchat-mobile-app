    // ============================================
    // FRONT CONTROLLER CLASS
    // ============================================
class FrontController 
{
    constructor(config = {}) 
    {
        this.routes = new Map();
        this.currentRoute = null;
        this.appElement = document.getElementById(config.appElementId || 'app');
        this.logHistory = [];
        this.maxLogs = config.maxLogs || 100;
        this.validators = this.initializeValidators();
        this.middleware = [];
        this.apiBaseUrl = config.apiBaseUrl || 'http://localhost:5000/api';
        this.log('info', 'FrontController initialized');
        this.initializeRouting();
    }

    registerRoute(path, handler, middleware = []) 
    {
        this.routes.set(path, { handler, middleware });
        this.log('info', `Route registered: ${path}`);
    }

    initializeRouting() 
    {
        window.addEventListener('hashchange', () => this.handleRouteChange());
        window.addEventListener('load', () => this.handleRouteChange());
    }

    navigate(path, state = {}) 
    {
        this.log('info', `Navigating to: ${path}`);
        window.location.hash = path;
        this.currentRoute = { path, state };
    }

    handleRouteChange() 
    {
        const path = window.location.hash.slice(1) || '/';
        const route = this.routes.get(path);

        if (!route) {
          this.log('error', `Route not found: ${path}`);
          this.navigate('/');
          return;
        }

        for (const mw of [...this.middleware, ...route.middleware]) {
          const result = mw(path);
          if (result === false) {
            this.log('warn', `Middleware blocked navigation to: ${path}`);
            return;
          }
        }

        this.clearView();
        route.handler(this.currentRoute?.state || {});
    }

    clearView() 
    {
        this.appElement.innerHTML = '';
    }

    initializeValidators() 
    {
        return {
          required: (value) => {
            return value && value.trim() !== '' 
              ? { valid: true } 
              : { valid: false, message: 'This field is required' };
          },
          email: (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(value)
              ? { valid: true }
              : { valid: false, message: 'Please enter a valid email address' };
          },
          minLength: (min) => (value) => {
            return value.length >= min
              ? { valid: true }
              : { valid: false, message: `Must be at least ${min} characters` };
          },
          maxLength: (max) => (value) => {
            return value.length <= max
              ? { valid: true }
              : { valid: false, message: `Must be no more than ${max} characters` };
          },
          pattern: (regex, message) => (value) => {
            return regex.test(value)
              ? { valid: true }
              : { valid: false, message };
          }
        };
    }

    validateField(value, rules) 
    {
        for (const rule of rules) {
          const result = rule(value);
          if (!result.valid) {
            return result;
          }
        }
        return { valid: true };
    }

    validateForm(formData, rules) 
    {
        const errors = {};
        let isValid = true;

        for (const [field, fieldRules] of Object.entries(rules)) {
          const result = this.validateField(formData[field] || '', fieldRules);
          if (!result.valid) {
            errors[field] = result.message;
            isValid = false;
          }
        }

        return { isValid, errors };
    }

    async apiCall(endpoint, options = {}) 
    {
        try {
          const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': session.token ? `Bearer ${session.token}` : '',
              ...options.headers
            },
            ...options
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        } catch (error) {
          this.log('error', `API call failed: ${endpoint}`, error.message);
          throw error;
        }
    }

    log(level, message, data = null) 
    {
        const timestamp = new Date().toISOString();
        const logEntry = { timestamp, level, message, data };
        
        this.logHistory.push(logEntry);
        
        if (this.logHistory.length > this.maxLogs) {
          this.logHistory.shift();
        }

        const styles = {
          info: 'color: #007AFF',
          warn: 'color: #FF9500',
          error: 'color: #FF3B30',
          success: 'color: #34C759'
        };

        console.log(
          `%c[${level.toUpperCase()}] ${timestamp}`,
          styles[level] || 'color: #8E8E93',
          message,
          data || ''
        );
    }

    getLogs(level = null) 
    {
        if (level) {
          return this.logHistory.filter(log => log.level === level);
        }
        return this.logHistory;
    }

    clearLogs() 
    {
        this.logHistory = [];
        this.log('info', 'Log history cleared');
    }

    use(middleware) 
    {
        this.middleware.push(middleware);
    }

    createElement(html) 
    {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    }

    render(html) 
    {
        this.appElement.innerHTML = html;
      }
    }

    // ============================================
    // UI STATE MANAGEMENT
    // ============================================
    const uiState = {
      setLoading: (element, isLoading) => {
        if (isLoading) {
          element.disabled = true;
          element.dataset.originalText = element.textContent;
          element.innerHTML = '<div class="spinner"></div> Loading...';
          element.classList.add('loading');
        } else {
          element.disabled = false;
          element.textContent = element.dataset.originalText;
          element.classList.remove('loading');
        }
      },
      
      showToast: (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
          toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
          toast.classList.remove('show');
          setTimeout(() => toast.remove(), 300);
        }, 3000);
      }
    };

    // ============================================
    // APPLICATION IMPLEMENTATION
    // ============================================
    const app = new FrontController();
    console.log('App created:', app);
    console.log('App element:', app.appElement);
    console.log('Routes:', app.routes);

    // Session management
    const session = {
      user: null,
      token: null,
      isAuthenticated: false,
      rasaAvailable: false,
      sessionId: null,
      accounts: []
    };

    // Check authentication from localStorage
    function loadSession() {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');
      
      if (token && userStr) {
        session.token = token;
        session.user = JSON.parse(userStr);
        session.isAuthenticated = true;
        return true;
      }
      return false;
    }

    // Authentication middleware
    app.use((path) => {
      if (path !== '/' && path !== '/login' && !session.isAuthenticated) {
        app.log('warn', 'Unauthorized access attempt');
        app.navigate('/');
        return false;
      }
      return true;
    });

    // ============================================
    // FORM VALIDATION HELPERS
    // ============================================
    function initializeFormValidation() {
      const inputs = document.querySelectorAll('input[required]');
      inputs.forEach(input => {
        input.addEventListener('blur', (e) => {
          const value = e.target.value.trim();
          const field = e.target.id;
          
          if (field === 'username') {
            const result = app.validateField(value, [app.validators.required]);
            showFieldValidation(e.target, result);
          } else if (field === 'password') {
            const result = app.validateField(value, [app.validators.required, app.validators.minLength(6)]);
            showFieldValidation(e.target, result);
          }
        });
      });
    }

    function showFieldValidation(input, result) {
      const errorEl = document.getElementById(`${input.id}Error`);
      if (!result.valid) {
        input.classList.add('error');
        errorEl.textContent = result.message;
        errorEl.classList.add('show');
      } else {
        input.classList.remove('error');
        errorEl.classList.remove('show');
      }
    }

    // ============================================
    // SECURITY ENHANCEMENTS
    // ============================================
    async function refreshToken() {
      try {
        const response = await fetch(`${app.apiBaseUrl}/refresh`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          session.token = data.token;
          localStorage.setItem('token', data.token);
          app.log('info', 'Token refreshed successfully');
        }
      } catch (error) {
        app.log('error', 'Token refresh failed', error.message);
        logout();
      }
    }

    // Auto-refresh token every 15 minutes
    setInterval(() => {
      if (session.isAuthenticated) {
        refreshToken();
      }
    }, 15 * 60 * 1000);

    // ============================================
    // LOGIN VIEW
    // ============================================
    app.registerRoute('/', () => {
      app.render(`
        <div class="card">
          <div class="logo">💰</div>
          <h1>Financial Assistant</h1>
          <p class="subtitle">Sign in to manage your accounts</p>
          
          <form id="loginForm">
            <div class="form-group">
              <label for="username">Username</label>
              <input type="text" id="username" placeholder="Enter username" autocomplete="username">
              <div class="error-message" id="usernameError"></div>
            </div>
            
            <div class="form-group">
              <label for="password">Password</label>
              <input type="password" id="password" placeholder="Enter password" autocomplete="current-password">
              <div class="error-message" id="passwordError"></div>
            </div>
            
            <button type="submit" class="btn btn-primary" id="loginButton">Sign In</button>
          </form>

          <div class="demo-info">
            <h4>Demo Accounts:</h4>
            <p><strong>demo_user</strong> / password123</p>
            <p><strong>john_doe</strong> / password123</p>
          </div>
        </div>
      `);

      const form = document.getElementById('loginForm');
      const usernameInput = document.getElementById('username');
      const passwordInput = document.getElementById('password');
      const loginButton = document.getElementById('loginButton');

      // Initialize real-time validation
      initializeFormValidation();

      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
          username: usernameInput.value,
          password: passwordInput.value
        };

        const validation = app.validateForm(formData, {
          username: [app.validators.required],
          password: [app.validators.required, app.validators.minLength(6)]
        });

        document.querySelectorAll('.error-message').forEach(el => {
          el.classList.remove('show');
          el.textContent = '';
        });
        document.querySelectorAll('input').forEach(el => {
          el.classList.remove('error');
        });

        if (!validation.isValid) {
          app.log('warn', 'Form validation failed', validation.errors);
          
          for (const [field, message] of Object.entries(validation.errors)) {
            const errorEl = document.getElementById(`${field}Error`);
            const inputEl = document.getElementById(field);
            
            errorEl.textContent = message;
            errorEl.classList.add('show');
            inputEl.classList.add('error');
          }
          return;
        }

        // Attempt login
        uiState.setLoading(loginButton, true);

        try {
          const response = await fetch(`${app.apiBaseUrl}/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
          });

          const data = await response.json();

          if (response.ok) {
            session.user = data.user;
            session.token = data.token;
            session.isAuthenticated = true;

            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            app.log('success', 'Login successful', { username: formData.username });
            uiState.showToast('Login successful!', 'success');
            app.navigate('/dashboard');
          } else {
            throw new Error(data.error || 'Login failed');
          }
        } catch (error) {
          app.log('error', 'Login failed', error.message);
          const errorEl = document.getElementById('passwordError');
          errorEl.textContent = error.message;
          errorEl.classList.add('show');
          passwordInput.classList.add('error');
          uiState.showToast('Login failed. Please try again.', 'error');
        } finally {
          uiState.setLoading(loginButton, false);
        }
      });
    });

    // ============================================
    // DASHBOARD VIEW
    // ============================================
    app.registerRoute('/dashboard', async () => {
      app.render(`
        <div class="card">
          <div class="dashboard-header">
            <div class="welcome-text">Welcome, ${session.user.full_name || session.user.username}!</div>
            <div class="user-email">${session.user.username}</div>
            <div class="status-badge ${session.rasaAvailable ? 'online' : 'offline'}" id="statusBadge">
              <span class="status-dot"></span>
              <span id="statusText">${session.rasaAvailable ? 'System Online' : 'Checking...'}</span>
            </div>
          </div>

          <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
              <div class="stat-value">$0.00</div>
              <div class="stat-label">Total Balance</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">0</div>
              <div class="stat-label">Accounts</div>
            </div>
          </div>

          <div class="recent-transactions">
            <h3>Recent Transactions</h3>
            <div id="recentTransactions">
              <div class="transaction-item">
                <div class="transaction-details">
                  <span class="transaction-description">Loading...</span>
                </div>
              </div>
            </div>
          </div>

          <div class="menu-grid">
            <div class="menu-card" onclick="app.navigate('/chat')">
              <div class="menu-card-icon">💬</div>
              <div class="menu-card-title">Chat Assistant</div>
              <div class="menu-card-subtitle">Ask questions</div>
            </div>
            <div class="menu-card" onclick="showAccountModal()">
              <div class="menu-card-icon">🏦</div>
              <div class="menu-card-title">Accounts</div>
              <div class="menu-card-subtitle">View details</div>
            </div>
            <div class="menu-card">
              <div class="menu-card-icon">📊</div>
              <div class="menu-card-title">Analytics</div>
              <div class="menu-card-subtitle">Coming soon</div>
            </div>
            <div class="menu-card">
              <div class="menu-card-icon">⚙️</div>
              <div class="menu-card-title">Settings</div>
              <div class="menu-card-subtitle">Coming soon</div>
            </div>
          </div>

          <button class="btn btn-secondary" onclick="logout()">Sign Out</button>
        </div>
      `);

      // Check service status
      checkServices();
      
      // Load account data
      loadAccountData();
      loadRecentTransactions();
    });

    // ============================================
    // CHAT VIEW
    // ============================================
    app.registerRoute('/chat', () => {
      app.render(`
        <div class="card">
          <div class="chat-container">
            <div class="chat-header">
              <div class="chat-title">Chat Assistant</div>
              <button class="back-btn" onclick="app.navigate('/dashboard')">← Back</button>
            </div>

            <div class="chat-messages" id="chatMessages">
              <div class="message bot-message">
                <div class="message-content">
                  Hello! I'm your financial assistant. I can help you check balances, view transactions, and provide budget advice. What would you like to know?
                </div>
                <div class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
              </div>
            </div>

            <div class="chat-input-form">
              <input type="text" id="messageInput" placeholder="Type your message..." autocomplete="off">
              <button class="send-btn" onclick="sendMessage()">Send</button>
            </div>

            <div class="typing-indicator" id="typingIndicator">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span>Assistant is typing...</span>
            </div>
          </div>
        </div>
      `);

      // Load chat history
      loadChatHistory();

      // Handle Enter key
      document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          sendMessage();
        }
      });
    });

    // ============================================
    // HELPER FUNCTIONS
    // ============================================

    async function checkServices() {
      try {
        const response = await fetch(`${app.apiBaseUrl}/rasa-status`, {
          headers: {
            'Authorization': `Bearer ${session.token}`
          }
        });

        const data = await response.json();
        session.rasaAvailable = data.status === 'connected';

        const statusBadge = document.getElementById('statusBadge');
        const statusText = document.getElementById('statusText');
        
        if (statusBadge && statusText) {
          if (session.rasaAvailable) {
            statusBadge.className = 'status-badge online';
            statusText.textContent = 'System Online';
          } else {
            statusBadge.className = 'status-badge offline';
            statusText.textContent = 'Limited Mode';
          }
        }

        app.log('info', 'Service status checked', { rasaAvailable: session.rasaAvailable });
      } catch (error) {
        app.log('error', 'Failed to check services', error.message);
        session.rasaAvailable = false;
      }
    }

    async function loadAccountData() {
      try {
        const accounts = await app.apiCall('/user/accounts');
        session.accounts = accounts;
        
        const totalBalance = session.accounts.reduce((sum, acc) => sum + parseFloat(acc.balance), 0);
        
        const statsGrid = document.getElementById('statsGrid');
        if (statsGrid) {
          statsGrid.innerHTML = `
            <div class="stat-card">
              <div class="stat-value">$${totalBalance.toFixed(2)}</div>
              <div class="stat-label">Total Balance</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">${session.accounts.length}</div>
              <div class="stat-label">Accounts</div>
            </div>
          `;
        }

        app.log('success', 'Account data loaded', { accounts: session.accounts.length });
      } catch (error) {
        app.log('error', 'Failed to load account data', error.message);
        uiState.showToast('Failed to load account data', 'error');
      }
    }

    async function loadRecentTransactions() {
      try {
        const transactions = await app.apiCall('/user/transactions?limit=3');
        
        const container = document.getElementById('recentTransactions');
        if (container && transactions.length > 0) {
          container.innerHTML = transactions.map(t => `
            <div class="transaction-item">
              <div class="transaction-details">
                <span class="transaction-description">${t.description}</span>
                <span class="transaction-amount ${t.transaction_type}">$${parseFloat(t.amount).toFixed(2)}</span>
              </div>
              <div class="transaction-date">${new Date(t.transaction_date).toLocaleDateString()}</div>
            </div>
          `).join('');
        } else if (container) {
          container.innerHTML = '<div class="transaction-item"><div class="transaction-details"><span class="transaction-description">No recent transactions</span></div></div>';
        }
      } catch (error) {
        app.log('error', 'Failed to load transactions', error.message);
        const container = document.getElementById('recentTransactions');
        if (container) {
          container.innerHTML = '<div class="transaction-item"><div class="transaction-details"><span class="transaction-description">Unable to load transactions</span></div></div>';
        }
      }
    }

    function saveChatHistory() {
      const chatMessages = document.getElementById('chatMessages');
      if (chatMessages && session.user) {
        const messages = Array.from(chatMessages.children).map(msg => ({
          content: msg.querySelector('.message-content').textContent,
          sender: msg.classList.contains('user-message') ? 'user' : 'bot',
          time: msg.querySelector('.message-time').textContent
        }));
        localStorage.setItem(`chatHistory_${session.user.username}`, JSON.stringify(messages));
      }
    }

    function loadChatHistory() {
      if (!session.user) return;
      
      const saved = localStorage.getItem(`chatHistory_${session.user.username}`);
      if (saved) {
        const messages = JSON.parse(saved);
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
          // Keep the initial welcome message
          const welcomeMessage = chatMessages.innerHTML;
          chatMessages.innerHTML = '';
          
          messages.forEach(msg => {
            addChatMessage(msg.content, msg.sender, msg.time, false);
          });
          
          // If no history, add welcome message back
          if (messages.length === 0) {
            chatMessages.innerHTML = welcomeMessage;
          }
        }
      }
    }

    function addChatMessage(message, sender, customTime = null, saveToHistory = true) {
      const chatMessages = document.getElementById('chatMessages');
      if (!chatMessages) return;

      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${sender}-message`;
      
      const timeString = customTime || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      
      messageDiv.innerHTML = `
        <div class="message-content">
          ${message.replace(/\n/g, '<br>')}
        </div>
        <div class="message-time">${timeString}</div>
      `;
      
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      
      if (saveToHistory) {
        saveChatHistory();
      }
    }

    async function sendMessage() {
      const input = document.getElementById('messageInput');
      const message = input.value.trim();
      
      if (!message) return;

      addChatMessage(message, 'user');
      input.value = '';

      const typingIndicator = document.getElementById('typingIndicator');
      const msg = message.toLowerCase();

      // Check for local commands
      const localCommands = ['balance', 'account', 'transaction'];
      const isLocalCommand = localCommands.some(cmd => msg.includes(cmd));

      // Try Rasa first if available and not a simple local command
      if (session.rasaAvailable && !isLocalCommand) {
        typingIndicator.classList.add('show');

        try {
          const response = await fetch(`${app.apiBaseUrl}/chat`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${session.token}`
            },
            body: JSON.stringify({
              message: message,
              session_id: session.sessionId
            })
          });

          const data = await response.json();

          if (response.ok) {
            session.sessionId = data.session_id;

            if (data.responses && data.responses.length > 0) {
              data.responses.forEach(response => {
                if (response.text) {
                  addChatMessage(response.text, 'bot');
                }
              });
              typingIndicator.classList.remove('show');
              return;
            }
          } else if (response.status === 503) {
            session.rasaAvailable = false;
            uiState.showToast('AI assistant is temporarily unavailable', 'warn');
          }
        } catch (error) {
          app.log('error', 'Chat error', error.message);
          session.rasaAvailable = false;
          uiState.showToast('Connection error', 'error');
        }

        typingIndicator.classList.remove('show');
      }

      // Use local fallback
      await handleLocalCommand(message);
    }

    async function handleLocalCommand(message) {
      const msg = message.toLowerCase();
      
      await new Promise(resolve => setTimeout(resolve, 500));

      if (msg.includes('balance')) {
        try {
          const accounts = await app.apiCall('/user/accounts');
          let total = 0;
          let accountsText = 'Here are your account balances:\n\n';

          accounts.forEach(acc => {
            const balance = parseFloat(acc.balance);
            total += balance;
            const type = acc.account_type.charAt(0).toUpperCase() + acc.account_type.slice(1);
            accountsText += `${type} (${acc.account_number}): $${balance.toFixed(2)}\n`;
          });

          accountsText += `\nTotal Balance: $${total.toFixed(2)}`;
          addChatMessage(accountsText, 'bot');
        } catch (error) {
          addChatMessage('Unable to fetch account information.', 'bot');
        }
      } else if (msg.includes('transaction')) {
        try {
          const transactions = await app.apiCall('/user/transactions?limit=5');

          if (transactions.length === 0) {
            addChatMessage('You have no recent transactions.', 'bot');
            return;
          }

          let transText = 'Here are your recent transactions:\n\n';

          transactions.slice(0, 5).forEach(t => {
            const date = new Date(t.transaction_date).toLocaleDateString();
            const type = t.transaction_type === 'debit' ? '📤' : '📥';
            transText += `${type} ${date} - ${t.description}: $${parseFloat(t.amount).toFixed(2)}\n`;
          });

          addChatMessage(transText, 'bot');
        } catch (error) {
          addChatMessage('Unable to fetch transactions.', 'bot');
        }
      } else if (msg.includes('account')) {
        try {
          const accounts = await app.apiCall('/user/accounts');
          let accountText = 'Here are your accounts:\n\n';

          accounts.forEach(acc => {
            const type = acc.account_type.charAt(0).toUpperCase() + acc.account_type.slice(1);
            accountText += `${type} Account\n`;
            accountText += `Number: ${acc.account_number}\n`;
            accountText += `Balance: $${parseFloat(acc.balance).toFixed(2)}\n\n`;
          });

          addChatMessage(accountText, 'bot');
        } catch (error) {
          addChatMessage('Unable to fetch account information.', 'bot');
        }
      } else if (msg.includes('budget') || msg.includes('advice') || msg.includes('tip')) {
        const adviceOptions = [
          "💡 Try the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings.",
          "💡 Track your spending for a month to identify areas where you can cut back.",
          "💡 Set up automatic transfers to your savings account each payday.",
          "💡 Create an emergency fund covering 3-6 months of expenses.",
          "💡 Review your subscriptions and cancel ones you don't use regularly."
        ];
        const randomAdvice = adviceOptions[Math.floor(Math.random() * adviceOptions.length)];
        addChatMessage(randomAdvice, 'bot');
      } else if (msg.includes('help')) {
        addChatMessage('I can help you with:\n\n• "check my balance" - View account balances\n• "show transactions" - See recent transactions\n• "show my accounts" - Display account details\n• "give me budget advice" - Get financial tips', 'bot');
      } else {
        if (session.rasaAvailable) {
          addChatMessage('I\'m not sure I understood that. Could you try rephrasing?', 'bot');
        } else {
          addChatMessage('I\'m currently in limited mode. Try asking me to:\n• "check my balance"\n• "show transactions"\n• "show my accounts"\n• "give me budget advice"', 'bot');
        }
      }
    }

    function showAccountModal() {
      const modal = document.createElement('div');
      modal.className = 'modal show';
      modal.id = 'accountModal';
      
      let modalContent = '<div class="account-item"><p>Loading accounts...</p></div>';
      
      if (session.accounts.length > 0) {
        let totalBalance = 0;
        let accountsHTML = '';
        
        session.accounts.forEach(account => {
          totalBalance += parseFloat(account.balance);
          const type = account.account_type.charAt(0).toUpperCase() + account.account_type.slice(1);
          accountsHTML += `
            <div class="account-item">
              <h4>${type} Account</h4>
              <p class="account-number">${account.account_number}</p>
              <p class="account-balance">$${parseFloat(account.balance).toFixed(2)}</p>
            </div>
          `;
        });
        
        modalContent = `
          <div class="total-balance">
            <h3>Total Balance: $${totalBalance.toFixed(2)}</h3>
          </div>
          ${accountsHTML}
        `;
      }
      
      modal.innerHTML = `
        <div class="modal-content">
          <div class="modal-header">
            <h3>Account Summary</h3>
            <button class="close-btn" onclick="closeAccountModal()">×</button>
          </div>
          <div class="modal-body">
            ${modalContent}
          </div>
        </div>
      `;
      
      document.body.appendChild(modal);
      
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          closeAccountModal();
        }
      });
    }

    function closeAccountModal() {
      const modal = document.getElementById('accountModal');
      if (modal) {
        modal.remove();
      }
    }

    function logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Clear chat history
      if (session.user) {
        localStorage.removeItem(`chatHistory_${session.user.username}`);
      }
      session.user = null;
      session.token = null;
      session.isAuthenticated = false;
      session.accounts = [];
      app.log('info', 'User logged out');
      uiState.showToast('Logged out successfully', 'success');
      app.navigate('/');
    }

    // ============================================
    // GLOBAL FUNCTION EXPORTS
    // ============================================
    window.app = app;
    window.uiState = uiState;
    window.showAccountModal = showAccountModal;
    window.closeAccountModal = closeAccountModal;
    window.logout = logout;
    window.sendMessage = sendMessage;
    window.initializeFormValidation = initializeFormValidation;

    // ============================================
    // APPLICATION INITIALIZATION
    // ============================================
    app.log('success', 'Application started successfully');

    // Load session from localStorage if exists
    if (loadSession()) {
      app.log('info', 'Session restored from localStorage');
      app.navigate('/dashboard');
    } else {
      // Force navigate to login page
      app.log('info', 'No session found, navigating to login');
      app.navigate('/');
    }