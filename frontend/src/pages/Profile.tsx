import React, { useState, useEffect } from 'react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { ErrorState } from '../components/shared/ErrorState';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { formatCurrency, formatCategory } from '../utils/format';
import { User, Shield, CreditCard, Wallet, Tag, AlertCircle, Edit2, Check, X } from 'lucide-react';
import type { FinancialProfile } from '../types';

interface PersonalContext {
  name: string;
  age: string;
  maritalStatus: string;
  dependents: string;
  occupation: string;
  cityTier: string;
}

export const Profile: React.FC = () => {
  const { data: profile, status, error, refetch, update } = useFinancialProfile();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editProfile, setEditProfile] = useState<FinancialProfile | null>(null);
  
  const [personalContext, setPersonalContext] = useState<PersonalContext>({
    name: 'Aditya',
    age: '32',
    maritalStatus: 'Single',
    dependents: '0',
    occupation: 'Software Engineer',
    cityTier: 'Tier 1'
  });
  
  useEffect(() => {
    const savedContext = localStorage.getItem('personal_context');
    if (savedContext) {
      try {
        setPersonalContext(JSON.parse(savedContext));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  useEffect(() => {
    if (profile && !isEditing) {
      setEditProfile(profile);
    }
  }, [profile, isEditing]);

  if (status === 'error') {
    return <ErrorState type="data" message={error?.message} onRetry={refetch} />;
  }

  const isLoading = status === 'loading' || !profile || !editProfile;

  const handleSave = async () => {
    if (editProfile) {
      await update(editProfile);
      localStorage.setItem('personal_context', JSON.stringify(personalContext));
      setIsEditing(false);
      window.location.reload(); // Hard reload to refresh all other contexts/hooks
    }
  };

  const parseList = (str: string) => str.split('|').map(s => s.trim()).filter(Boolean);
  const joinList = (arr: string[]) => arr.join(' | ');

  if (isLoading && !isEditing) {
    return (
      <div className="space-y-6 max-w-2xl">
        <LoadingSkeleton height="h-14" className="w-full" />
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="space-y-6 max-w-2xl pb-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-primary-accent rounded-2xl flex items-center justify-center">
            <User size={24} className="text-white" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-primary-dark">
              {isEditing ? (
                <input 
                  type="text" 
                  value={personalContext.name}
                  onChange={e => setPersonalContext({...personalContext, name: e.target.value})}
                  className="bg-gray-50 border border-gray-300 rounded px-2 py-1 text-lg font-bold w-48"
                />
              ) : personalContext.name}
            </h1>
            <p className="text-muted text-sm mt-0.5">
              {profile?.user_id} · {profile?.home_currency}
            </p>
          </div>
        </div>
        
        {!isEditing ? (
          <button 
            onClick={() => setIsEditing(true)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 shadow-sm rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
          >
            <Edit2 size={16} /> Edit Profile
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <button 
              onClick={() => {
                setIsEditing(false);
                setEditProfile(profile);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 shadow-sm rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            >
              <X size={16} /> Cancel
            </button>
            <button 
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 bg-primary-accent text-white shadow-sm rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <Check size={16} /> Save Changes
            </button>
          </div>
        )}
      </div>

      {isEditing ? (
        <div className="space-y-6">
          {/* Edit Mode */}
          <section className="card p-5 border-l-4 border-l-gray-400">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Personal Information <span className="text-xs font-normal text-gray-500 ml-2 bg-gray-100 px-2 py-1 rounded">(Personal context)</span></h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Age</label>
                <input 
                  type="text" value={personalContext.age} 
                  onChange={e => setPersonalContext({...personalContext, age: e.target.value})}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Marital Status</label>
                <input 
                  type="text" value={personalContext.maritalStatus} 
                  onChange={e => setPersonalContext({...personalContext, maritalStatus: e.target.value})}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Dependents</label>
                <input 
                  type="text" value={personalContext.dependents} 
                  onChange={e => setPersonalContext({...personalContext, dependents: e.target.value})}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Occupation</label>
                <input 
                  type="text" value={personalContext.occupation} 
                  onChange={e => setPersonalContext({...personalContext, occupation: e.target.value})}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">City Tier</label>
                <input 
                  type="text" value={personalContext.cityTier} 
                  onChange={e => setPersonalContext({...personalContext, cityTier: e.target.value})}
                  className="w-full bg-gray-50 border border-gray-300 rounded p-2 text-sm"
                />
              </div>
            </div>
          </section>

          <section className="card p-5 border-l-4 border-l-blue-500 bg-blue-50/20">
            <h2 className="text-lg font-semibold mb-4 text-primary-dark">Financial Information <span className="text-xs font-normal text-blue-600 bg-blue-100 ml-2 px-2 py-1 rounded">(Used in financial calculations)</span></h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Current Available Balance ({profile?.home_currency})</label>
                <input 
                  type="number" step="0.01" 
                  value={editProfile?.current_available_balance} 
                  onChange={e => setEditProfile({...editProfile!, current_available_balance: parseFloat(e.target.value) || 0})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Minimum Balance Buffer ({profile?.home_currency})</label>
                <input 
                  type="number" step="0.01" 
                  value={editProfile?.minimum_balance_to_keep} 
                  onChange={e => setEditProfile({...editProfile!, minimum_balance_to_keep: parseFloat(e.target.value) || 0})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Financial Priorities (pipe-separated `|`)</label>
                <input 
                  type="text"
                  value={joinList(editProfile?.financial_priorities || [])} 
                  onChange={e => setEditProfile({...editProfile!, financial_priorities: parseList(e.target.value)})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                  placeholder="e.g. emergency_savings | housing"
                />
              </div>
            </div>
          </section>

          <section className="card p-5 border-l-4 border-l-blue-500 bg-blue-50/20">
            <h2 className="text-lg font-semibold mb-4 text-primary-dark">Spending Preferences <span className="text-xs font-normal text-blue-600 bg-blue-100 ml-2 px-2 py-1 rounded">(Used in financial calculations)</span></h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Protected Categories</label>
                <input 
                  type="text"
                  value={joinList(editProfile?.expense_categories_to_protect || [])} 
                  onChange={e => setEditProfile({...editProfile!, expense_categories_to_protect: parseList(e.target.value)})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Reducible Categories</label>
                <input 
                  type="text"
                  value={joinList(editProfile?.expense_categories_user_is_willing_to_reduce || [])} 
                  onChange={e => setEditProfile({...editProfile!, expense_categories_user_is_willing_to_reduce: parseList(e.target.value)})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Stoppable Categories</label>
                <input 
                  type="text"
                  value={joinList(editProfile?.expense_categories_user_is_willing_to_stop || [])} 
                  onChange={e => setEditProfile({...editProfile!, expense_categories_user_is_willing_to_stop: parseList(e.target.value)})}
                  className="w-full bg-white border border-gray-300 rounded p-2 text-sm"
                />
              </div>
            </div>
          </section>
        </div>
      ) : (
        <>
          {/* Read Mode */}
          <section className="card p-5">
            <div className="flex items-center gap-2 mb-4">
              <User size={16} className="text-muted" aria-hidden="true" />
              <h2 className="section-title">Personal Information <span className="text-xs font-normal text-gray-400 ml-2">(Personal context)</span></h2>
            </div>
            <div className="grid grid-cols-2 gap-y-3">
              <div>
                <p className="text-xs text-muted">Age</p>
                <p className="text-sm font-semibold text-primary-dark">{personalContext.age}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Marital Status</p>
                <p className="text-sm font-semibold text-primary-dark">{personalContext.maritalStatus}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Dependents</p>
                <p className="text-sm font-semibold text-primary-dark">{personalContext.dependents}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Occupation</p>
                <p className="text-sm font-semibold text-primary-dark">{personalContext.occupation}</p>
              </div>
              <div>
                <p className="text-xs text-muted">City Tier</p>
                <p className="text-sm font-semibold text-primary-dark">{personalContext.cityTier}</p>
              </div>
            </div>
          </section>

          <section className="card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Wallet size={16} className="text-muted" aria-hidden="true" />
              <h2 className="section-title">Financial Information <span className="text-xs font-normal text-blue-600 bg-blue-50 px-2 py-0.5 rounded ml-2">Used in calculations</span></h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-border">
                <p className="text-sm text-muted">Available Balance</p>
                <p className="text-sm font-semibold text-primary-dark">{formatCurrency(profile.current_available_balance, profile.home_currency)}</p>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border">
                <p className="text-sm text-muted">Minimum Balance Buffer</p>
                <p className="text-sm font-semibold text-primary-dark">{formatCurrency(profile.minimum_balance_to_keep, profile.home_currency)}</p>
              </div>
            </div>
            
            <div className="mt-4">
              <p className="text-sm text-muted mb-2">Financial Priorities</p>
              <div className="flex flex-wrap gap-2">
                {profile.financial_priorities.map(item => (
                  <span key={item} className="badge-neutral">{formatCategory(item)}</span>
                ))}
              </div>
            </div>
          </section>

          <section className="card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Tag size={16} className="text-muted" aria-hidden="true" />
              <h2 className="section-title">Spending Preferences <span className="text-xs font-normal text-blue-600 bg-blue-50 px-2 py-0.5 rounded ml-2">Used in calculations</span></h2>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted mb-2">Protected Categories <span className="text-xs">(Will not be reduced in recommendations)</span></p>
                <div className="flex flex-wrap gap-2">
                  {profile.expense_categories_to_protect?.length ? profile.expense_categories_to_protect.map(item => (
                    <span key={item} className="badge-neutral">{formatCategory(item)}</span>
                  )) : <p className="text-sm text-muted">None</p>}
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-2">Reducible Categories <span className="text-xs">(Open to reducing spending)</span></p>
                <div className="flex flex-wrap gap-2">
                  {profile.expense_categories_user_is_willing_to_reduce?.length ? profile.expense_categories_user_is_willing_to_reduce.map(item => (
                    <span key={item} className="badge-neutral">{formatCategory(item)}</span>
                  )) : <p className="text-sm text-muted">None</p>}
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-2">Stoppable Categories <span className="text-xs">(Willing to stop spending)</span></p>
                <div className="flex flex-wrap gap-2">
                  {profile.expense_categories_user_is_willing_to_stop?.length ? profile.expense_categories_user_is_willing_to_stop.map(item => (
                    <span key={item} className="badge-neutral">{formatCategory(item)}</span>
                  )) : <p className="text-sm text-muted">None</p>}
                </div>
              </div>
            </div>
          </section>
        </>
      )}

      <p className="text-xs text-muted/70 text-center pb-4">
        {isEditing ? "Editing Demo Profile for Testing Purposes" : "Profile data is read from the FIN4YOU data directory."}
      </p>
    </div>
  );
};
