import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, Mail, ArrowRight, AlertTriangle } from 'lucide-react';
import fin4youLogo from '../assets/fin4you_logo.jpg';
import { motion } from 'framer-motion';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Invalid email or password');
      }

      const data = await response.json();
      login(data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary-accent/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple/10 blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md bg-card-bg border border-border rounded-2xl shadow-2xl overflow-hidden relative z-10"
      >
        <div className="p-8 pb-6 text-center border-b border-border/50">
          <div className="w-16 h-16 mx-auto rounded-2xl overflow-hidden bg-primary-dark shadow-md flex items-center justify-center mb-4">
            <img src={fin4youLogo} alt="FIN4YOU Logo" className="w-full h-full object-cover" />
          </div>
          <h1 className="text-2xl font-bold text-primary-dark tracking-tight">Welcome back</h1>
          <p className="text-muted mt-2 text-sm">Sign in to your financial intelligence dashboard</p>
        </div>

        <div className="p-8 pt-6">
          {errorMsg && (
            <div className="mb-4 p-3 bg-danger/10 border border-danger/20 rounded-lg flex items-center gap-2 text-danger text-sm font-medium">
              <AlertTriangle size={16} />
              {errorMsg}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-primary-dark mb-1.5" htmlFor="email">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail size={18} className="text-muted/70" />
                </div>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-1 border border-border rounded-lg text-primary-dark focus:outline-none focus:ring-2 focus:ring-primary-accent focus:border-transparent transition-all placeholder:text-muted/50 text-sm"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-sm font-medium text-primary-dark" htmlFor="password">Password</label>
                <a href="#" className="text-xs text-primary-accent hover:text-primary-accent/80 font-medium transition-colors">Forgot password?</a>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock size={18} className="text-muted/70" />
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-1 border border-border rounded-lg text-primary-dark focus:outline-none focus:ring-2 focus:ring-primary-accent focus:border-transparent transition-all placeholder:text-muted/50 text-sm"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email || !password}
              className="w-full flex items-center justify-center gap-2 bg-primary-accent text-white py-2.5 rounded-lg font-medium hover:bg-primary-accent/90 focus:outline-none focus:ring-2 focus:ring-primary-accent focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-primary-accent/20 mt-6"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In <ArrowRight size={18} />
                </>
              )}
            </button>
            <div className="text-center mt-4">
              <Link to="/register" className="text-sm text-primary-accent font-medium hover:underline">
                Don't have an account? Sign Up
              </Link>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};
