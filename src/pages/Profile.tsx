import React, { useState, useEffect } from 'react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { ErrorState } from '../components/shared/ErrorState';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { formatCurrency, formatCategory } from '../utils/format';
import { User, Shield, CreditCard, Wallet, Tag, AlertCircle, Edit2, Check, X } from 'lucide-react';
import { PlaidLinkButton } from '../components/PlaidLinkButton';
import type { FinancialProfile } from '../types';

export const Profile: React.FC = () => {
  const { data: profile, status, error, refetch, update } = useFinancialProfile();

  const [isEditing, setIsEditing] = useState(false);
  const [editProfile, setEditProfile] = useState<FinancialProfile | null>(null);

  useEffect(() => {
    if (profile && !isEditing) {
      setEditProfile(profile);
    }
  }, [profile, isEditing]);

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
      setIsEditing(false);
      refetch();
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
    <div className="space-y-6 max-w-4xl pb-10">
      {/* Header Banner */}
      <div className="card p-6 bg-gradient-to-r from-sidebar-bg via-slate-900 to-indigo-950 text-white relative overflow-hidden shadow-xl border border-white/10">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-tr from-primary-accent to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 border border-white/20">
              <User size={28} className="text-white" aria-hidden="true" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-2xs font-extrabold bg-[#CCFF00] text-black shadow-xs tracking-wider uppercase">
                  ACTIVE PROFILE
                </span>
                <span className="text-2xs text-white/60 font-medium">{profile?.home_currency} Base Currency</span>
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                {isEditing ? (
                  <input
                    type="text"
                    value={editProfile?.full_name || ''}
                    onChange={e => setEditProfile({...editProfile!, full_name: e.target.value})}
                    className="bg-white/10 border border-white/30 rounded-lg px-3 py-1 text-lg font-bold text-white w-52 focus:outline-none focus:ring-2 focus:ring-primary-accent"
                  />
                ) : (
                  `${profile?.full_name || 'Demo User'} (${profile?.user_id})`
                )}
              </h1>
              <p className="text-white/70 text-xs mt-0.5">
                Financial decision constraints &amp; spending risk preferences portal
              </p>
            </div>
          </div>

          {!isEditing ? (
            <div className="flex items-center gap-2">
              <PlaidLinkButton />
              <button
                onClick={() => setIsEditing(true)}
                className="btn-primary flex items-center gap-2 shadow-lg shadow-blue-500/30"
              >
                <Edit2 size={16} /> Edit Settings
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setIsEditing(false);
                  setEditProfile(profile);
                }}
                className="btn-secondary text-white border-white/20 hover:bg-white/10 flex items-center gap-2"
              >
                <X size={16} /> Cancel
              </button>
              <button
                onClick={handleSave}
                className="btn-primary flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 shadow-emerald-500/30 border-none"
              >
                <Check size={16} /> Save Settings
              </button>
            </div>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="space-y-6">
          {/* Personal Context Section */}
          <section className="card p-6 border-t-4 border-t-primary-accent">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-primary-accent/10 text-primary-accent flex items-center justify-center">
                  <User size={18} />
                </div>
                <div>
                  <h2 className="text-base font-bold text-primary-dark">Personal Context</h2>
                  <p className="text-2xs text-muted">Used for demographic context &amp; benchmark comparison</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Age</label>
                <input
                  type="text" value={editProfile?.age || ''}
                  onChange={e => setEditProfile({...editProfile!, age: e.target.value})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Marital Status</label>
                <input
                  type="text" value={editProfile?.marital_status || ''}
                  onChange={e => setEditProfile({...editProfile!, marital_status: e.target.value})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Dependents</label>
                <input
                  type="text" value={editProfile?.dependents || ''}
                  onChange={e => setEditProfile({...editProfile!, dependents: e.target.value})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Occupation</label>
                <input
                  type="text" value={editProfile?.occupation || ''}
                  onChange={e => setEditProfile({...editProfile!, occupation: e.target.value})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">City Tier</label>
                <input
                  type="text" value={editProfile?.city_tier || ''}
                  onChange={e => setEditProfile({...editProfile!, city_tier: e.target.value})}
                  className="form-input shadow-xs"
                />
              </div>
            </div>
          </section>

          {/* Financial Calculation Constraints */}
          <section className="card p-6 border-t-4 border-t-emerald-500 bg-emerald-50/10">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                <Wallet size={18} />
              </div>
              <div>
                <h2 className="text-base font-bold text-primary-dark">Financial Calculation Constraints</h2>
                <p className="text-2xs text-muted">Directly influences cash flow models &amp; buffer safety checks</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-primary-dark mb-1">
                  Current Available Balance ({profile?.home_currency})
                </label>
                <input
                  type="number" step="0.01"
                  value={editProfile?.current_available_balance}
                  onChange={e => setEditProfile({...editProfile!, current_available_balance: parseFloat(e.target.value) || 0})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-primary-dark mb-1">
                  Minimum Balance Buffer ({profile?.home_currency})
                </label>
                <input
                  type="number" step="0.01"
                  value={editProfile?.minimum_balance_to_keep}
                  onChange={e => setEditProfile({...editProfile!, minimum_balance_to_keep: parseFloat(e.target.value) || 0})}
                  className="form-input shadow-xs"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-primary-dark mb-1">
                  Financial Priorities (pipe-separated `|`)
                </label>
                <input
                  type="text"
                  value={joinList(editProfile?.financial_priorities || [])}
                  onChange={e => setEditProfile({...editProfile!, financial_priorities: parseList(e.target.value)})}
                  className="form-input shadow-xs"
                  placeholder="e.g. emergency_savings | housing | debt_reduction"
                />
              </div>
            </div>
          </section>

          {/* Spending Flexibility */}
          <section className="card p-6 border-t-4 border-t-purple-500 bg-purple-50/10">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-600 flex items-center justify-center">
                <Tag size={18} />
              </div>
              <div>
                <h2 className="text-base font-bold text-primary-dark">Spending Category Flexibility</h2>
                <p className="text-2xs text-muted">Configures What-If recommendations and discretionary reduction targets</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-primary-dark mb-1">Protected Categories (Cannot be reduced)</label>
                <input
                  type="text"
                  value={joinList(editProfile?.expense_categories_to_protect || [])}
                  onChange={e => setEditProfile({...editProfile!, expense_categories_to_protect: parseList(e.target.value)})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-primary-dark mb-1">Reducible Categories (Open to spend cutbacks)</label>
                <input
                  type="text"
                  value={joinList(editProfile?.expense_categories_user_is_willing_to_reduce || [])}
                  onChange={e => setEditProfile({...editProfile!, expense_categories_user_is_willing_to_reduce: parseList(e.target.value)})}
                  className="form-input shadow-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-primary-dark mb-1">Stoppable Categories (Willing to pause completely)</label>
                <input
                  type="text"
                  value={joinList(editProfile?.expense_categories_user_is_willing_to_stop || [])}
                  onChange={e => setEditProfile({...editProfile!, expense_categories_user_is_willing_to_stop: parseList(e.target.value)})}
                  className="form-input shadow-xs"
                />
              </div>
            </div>
          </section>
        </div>
      ) : (
        <>
          {/* Read View */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <User size={18} className="text-primary-accent" aria-hidden="true" />
                  <h2 className="section-title">Personal Demographics</h2>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-background p-3 rounded-xl border border-border shadow-sm">
                    <p className="text-2xs text-muted uppercase font-semibold">Age</p>
                    <p className="text-sm font-bold text-primary-dark">{profile.age}</p>
                  </div>
                  <div className="bg-background p-3 rounded-xl border border-border shadow-sm">
                    <p className="text-2xs text-muted uppercase font-semibold">Marital Status</p>
                    <p className="text-sm font-bold text-primary-dark">{profile.marital_status}</p>
                  </div>
                  <div className="bg-background p-3 rounded-xl border border-border shadow-sm">
                    <p className="text-2xs text-muted uppercase font-semibold">Dependents</p>
                    <p className="text-sm font-bold text-primary-dark">{profile.dependents}</p>
                  </div>
                  <div className="bg-background p-3 rounded-xl border border-border shadow-sm">
                    <p className="text-2xs text-muted uppercase font-semibold">Occupation</p>
                    <p className="text-sm font-bold text-primary-dark">{profile.occupation}</p>
                  </div>
                  <div className="bg-background p-3 rounded-xl border border-border shadow-sm col-span-2">
                    <p className="text-2xs text-muted uppercase font-semibold">City Tier</p>
                    <p className="text-sm font-bold text-primary-dark">{profile.city_tier}</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Wallet size={18} className="text-emerald-600" aria-hidden="true" />
                    <h2 className="section-title">Buffer &amp; Balance Security</h2>
                  </div>
                  <span className="text-2xs font-bold text-emerald-600 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
                    ENGINE ACTIVE
                  </span>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-background rounded-xl border border-border shadow-sm">
                    <p className="text-xs text-muted font-medium">Available Cash Balance</p>
                    <p className="text-base font-bold text-primary-dark">{formatCurrency(profile.current_available_balance, profile.home_currency)}</p>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-background rounded-xl border border-border shadow-sm">
                    <p className="text-xs text-muted font-medium">Required Buffer Security</p>
                    <p className="text-base font-bold text-emerald-600">{formatCurrency(profile.minimum_balance_to_keep, profile.home_currency)}</p>
                  </div>
                </div>

                <div className="mt-4">
                  <p className="text-2xs uppercase tracking-wider text-muted font-semibold mb-2">Financial Priorities</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.financial_priorities.map(item => (
                      <span key={item} className="text-xs font-semibold px-2.5 py-1 bg-primary-accent/10 text-primary-accent border border-primary-accent/20 rounded-lg">{formatCategory(item)}</span>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>

          <section className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Tag size={18} className="text-purple-600" aria-hidden="true" />
              <h2 className="section-title">Category Spending Risk Flexibility</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-background p-4 rounded-xl border border-border shadow-sm">
                <p className="text-xs font-bold text-primary-dark mb-2">🛡️ Protected Categories</p>
                <div className="flex flex-wrap gap-1.5">
                  {profile.expense_categories_to_protect?.length ? profile.expense_categories_to_protect.map(item => (
                    <span key={item} className="text-2xs font-semibold px-2 py-0.5 bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 rounded-md">{formatCategory(item)}</span>
                  )) : <p className="text-xs text-muted">None specified</p>}
                </div>
              </div>

              <div className="bg-background p-4 rounded-xl border border-border shadow-sm">
                <p className="text-xs font-bold text-primary-dark mb-2">✂️ Reducible Categories</p>
                <div className="flex flex-wrap gap-1.5">
                  {profile.expense_categories_user_is_willing_to_reduce?.length ? profile.expense_categories_user_is_willing_to_reduce.map(item => (
                    <span key={item} className="text-2xs font-semibold px-2 py-0.5 bg-warning/10 text-warning-dark border border-warning/20 rounded-md">{formatCategory(item)}</span>
                  )) : <p className="text-xs text-muted">None specified</p>}
                </div>
              </div>

              <div className="bg-background p-4 rounded-xl border border-border shadow-sm">
                <p className="text-xs font-bold text-primary-dark mb-2">🚫 Stoppable Categories</p>
                <div className="flex flex-wrap gap-1.5">
                  {profile.expense_categories_user_is_willing_to_stop?.length ? profile.expense_categories_user_is_willing_to_stop.map(item => (
                    <span key={item} className="text-2xs font-semibold px-2 py-0.5 bg-rose-500/10 text-rose-600 border border-rose-500/20 rounded-md">{formatCategory(item)}</span>
                  )) : <p className="text-xs text-muted">None specified</p>}
                </div>
              </div>
            </div>
          </section>
        </>
      )}

      <p className="text-xs text-muted/70 text-center pb-4">
        {isEditing ? "Editing Demo Settings for Testing Purposes" : "Profile constraints ground all Artha AI recommendations & simulations."}
      </p>
    </div>
  );
};
