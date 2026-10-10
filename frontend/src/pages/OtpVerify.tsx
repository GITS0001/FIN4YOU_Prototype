import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, ArrowRight, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';

export const OtpVerify: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [otp, setOtp] = useState(location.state?.mock_otp || '');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const email = location.state?.email;

  if (!email) {
    navigate('/register');
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, otp }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      const data = await response.json();
      login(data.access_token);
      navigate('/');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to verify OTP');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center mb-6">
          <div className="bg-primary/10 p-3 rounded-full">
            <ShieldCheck size={32} className="text-primary-accent" />
          </div>
        </div>
        <h2 className="text-center text-3xl font-extrabold text-primary-dark">Verify your account</h2>
        <p className="mt-2 text-center text-sm text-muted">
          We've sent a code to <span className="font-semibold">{email}</span>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {errorMsg && (
              <div className="bg-negative/10 border border-negative/20 p-3 rounded-lg flex items-start gap-2">
                <p className="text-sm text-negative font-medium">{errorMsg}</p>
              </div>
            )}

            {location.state?.mock_otp && (
              <div className="bg-positive/10 border border-positive/20 p-3 rounded-lg">
                <p className="text-xs text-positive font-medium mb-1">PROTOTYPE MODE: Auto-filled OTP</p>
                <p className="text-sm font-mono text-positive">{location.state.mock_otp}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-primary-dark mb-1.5" htmlFor="otp">6-Digit Code</label>
              <div className="relative">
                <input
                  id="otp"
                  type="text"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="w-full px-4 py-3 bg-background border border-border rounded-xl text-primary-dark focus:ring-2 focus:ring-primary-accent focus:border-transparent outline-none transition-all text-center tracking-widest text-2xl"
                  placeholder="------"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || otp.length < 6}
              className="w-full btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <>
                  Verify & Continue
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
