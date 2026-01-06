import React, { useState } from 'react';
import './Login.css';
import msLogo from './mark_solution_logo.png';

function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = (e) => {
        e.preventDefault();

        // Mock Authentication Logic
        // In production, this would hit an API endpoint.
        // In production, this would hit an API endpoint.
        const user = username.trim().toLowerCase();
        let role = null;
        let branch = null;

        if (user === 'admin') { role = 'ADMIN'; branch = 'ALL'; }
        else if (user === 'owner') { role = 'BUSINESS_OWNER'; branch = 'ALL'; }

        // Dynamic Branch Binding based on Username suffix
        else if (user.startsWith('manager')) {
            role = 'MANAGER';
            branch = user.includes('br2') ? '2' : '1'; // Default: 1, manager_br2: 2
        }
        else if (user.startsWith('staff')) {
            role = 'STAFF';
            branch = user.includes('br1') ? '1' : '2'; // Default: 2, staff_br1: 1
        }

        if (role) {
            onLogin({ name: username, role: role, branch: branch });
        } else {
            setError('Invalid credentials. Try: admin, manager_br1, staff_br2');
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="login-header">
                    <img src={msLogo} alt="MarkSolution" className="login-logo" />
                    <h2>Enterprise Assistant</h2>
                    <p>Secure Business Intelligence Access</p>
                </div>

                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                        />
                    </div>

                    {error && <div className="error-msg">{error}</div>}

                    <button type="submit" className="login-btn">Secure Login</button>

                    <div className="demo-hint">
                        <small>Demo: admin / manager_br1 / manager_br2</small>
                    </div>
                </form>
            </div>
            <div className="login-footer">
                Powered by Mark Solutions
            </div>
        </div>
    );
}

export default Login;
