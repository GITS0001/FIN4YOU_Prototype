import React, { useState } from 'react';
import {
  Calendar,
  CheckCircle2,
  Circle,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  HelpCircle,
  ChevronRight,
  ArrowUpRight,
  Target,
  BookOpen,
  PieChart,
} from 'lucide-react';
import { useNinetyDayPlan, PlanPhase, FinancialTerm } from '../../hooks/useNinetyDayPlan';
import { formatCurrency, formatCurrencyCompact } from '../../utils/format';
import { useNavigate } from 'react-router-dom';

interface NinetyDayPlanCardProps {
  currency?: string;
}

export const NinetyDayPlanCard: React.FC<NinetyDayPlanCardProps> = ({ currency = 'INR' }) => {
  const navigate = useNavigate();
  const { data: plan, loading, completedActions, toggleAction } = useNinetyDayPlan();
  const [activeTab, setActiveTab] = useState<'phases' | 'terms'>('phases');
  const [selectedPhase, setSelectedPhase] = useState<number>(1);

  if (loading && !plan) {
    return (
      <div className="card p-6 border border-border shadow-sm animate-pulse space-y-4">
        <div className="h-6 bg-surface-2 rounded-lg w-1/3"></div>
        <div className="h-4 bg-surface-2 rounded w-1/2"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
          <div className="h-32 bg-surface-2 rounded-xl"></div>
          <div className="h-32 bg-surface-2 rounded-xl"></div>
          <div className="h-32 bg-surface-2 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!plan) return null;

  // Calculate total completed tasks across all phases
  let totalTasks = 0;
  let finishedTasks = 0;
  plan.phases.forEach((p) => {
    p.actions.forEach((a) => {
      totalTasks++;
      if (completedActions[a.id]) finishedTasks++;
    });
  });
  const overallProgressPercent = totalTasks > 0 ? Math.round((finishedTasks / totalTasks) * 100) : 0;

  const currentPhaseData = plan.phases.find((p) => p.phase_number === selectedPhase) || plan.phases[0];

  return (
    <div className="card p-6 sm:p-7 border border-border/80 shadow-md bg-card-bg relative overflow-hidden transition-all">
      {/* Background ambient accent */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-primary-accent/5 via-purple/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Top Header & Strategy Executive Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pb-6 border-b border-border/70 relative z-10">
        <div>
          <div className="flex items-center gap-2.5 mb-1.5">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-primary-accent bg-primary-accent/10 px-2.5 py-1 rounded-full border border-primary-accent/20">
              <Calendar size={13} />
              90-Day Strategy Playbook
            </span>
            <span className="text-2xs text-muted font-medium bg-surface-2 px-2 py-0.5 rounded-md border border-border/50">
              Data-Driven
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-primary-dark tracking-tight">
            90-Day Financial Roadmap & Savings Engine
          </h2>
          <p className="text-xs sm:text-sm text-muted mt-1 max-w-2xl leading-relaxed">
            Formulated from your cash flow, recurring obligations, and safety buffer to steadily build financial resilience.
          </p>
        </div>

        {/* Milestone Targets summary & AI CTA */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-3">
          <div className="bg-surface-2/70 border border-border/80 rounded-xl px-4 py-2.5 text-left">
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">90-Day Target Savings</p>
            <p className="text-base sm:text-lg font-bold text-positive">
              +{formatCurrencyCompact(plan.total_90_day_savings_target, currency)}
            </p>
          </div>

          <div className="bg-surface-2/70 border border-border/80 rounded-xl px-4 py-2.5 text-left">
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Target Balance</p>
            <p className="text-base sm:text-lg font-bold text-primary-dark">
              {formatCurrencyCompact(plan.projected_end_balance, currency)}
            </p>
          </div>

          <button
            onClick={() => navigate('/copilot')}
            className="btn-primary flex items-center gap-2 text-xs font-semibold px-4 py-2.5 shadow-sm whitespace-nowrap"
            title="Ask Artha AI to analyze or tailor your 90-day plan"
          >
            <Sparkles size={14} className="text-yellow-300" />
            <span>Consult Artha AI</span>
            <ArrowUpRight size={14} className="opacity-70" />
          </button>
        </div>
      </div>

      {/* Navigation Segment Tabs */}
      <div className="flex items-center justify-between mt-5 mb-6 relative z-10 flex-wrap gap-3">
        <div className="flex items-center gap-1.5 p-1 bg-surface-2/80 rounded-xl border border-border/60 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('phases')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'phases'
                ? 'bg-card-bg text-primary-dark shadow-xs font-bold border border-border/50'
                : 'text-muted hover:text-primary-dark'
            }`}
          >
            <Target size={14} className={activeTab === 'phases' ? 'text-primary-accent' : 'text-muted'} />
            <span>3-Phase Action Roadmap</span>
          </button>
          <button
            onClick={() => setActiveTab('terms')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'terms'
                ? 'bg-card-bg text-primary-dark shadow-xs font-bold border border-border/50'
                : 'text-muted hover:text-primary-dark'
            }`}
          >
            <BookOpen size={14} className={activeTab === 'terms' ? 'text-primary-accent' : 'text-muted'} />
            <span>Financial Terms Guide</span>
          </button>
        </div>

        {/* Global Progress Indicator */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted">
            Checklist Progress: <strong className="text-primary-dark">{finishedTasks}/{totalTasks}</strong>
          </span>
          <div className="w-24 bg-surface-2 rounded-full h-2 overflow-hidden border border-border/60">
            <div
              className="h-full bg-gradient-to-r from-primary-accent to-positive rounded-full transition-all duration-500"
              style={{ width: `${overallProgressPercent}%` }}
            />
          </div>
          <span className="text-xs font-bold text-primary-accent">{overallProgressPercent}%</span>
        </div>
      </div>

      {/* CONTENT TAB 1: 3-PHASE ROADMAP */}
      {activeTab === 'phases' && (
        <div className="space-y-6 relative z-10 animate-fade-in">
          {/* Phase Selector Chips */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {plan.phases.map((phase) => {
              const isSelected = selectedPhase === phase.phase_number;
              const phaseDoneCount = phase.actions.filter((a) => completedActions[a.id]).length;
              return (
                <button
                  key={phase.phase_number}
                  onClick={() => setSelectedPhase(phase.phase_number)}
                  className={`text-left p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                    isSelected
                      ? 'border-primary-accent bg-primary-accent/5 ring-1 ring-primary-accent/30 shadow-xs'
                      : 'border-border/70 bg-surface-2/40 hover:bg-surface-2 hover:border-border'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-xs font-bold ${isSelected ? 'text-primary-accent' : 'text-muted'}`}>
                      {phase.days}
                    </span>
                    <span className="text-2xs font-semibold text-positive bg-positive/10 px-2 py-0.5 rounded-full">
                      +{formatCurrencyCompact(phase.target_savings, currency)}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-primary-dark truncate">{phase.name}</h4>
                  <div className="flex items-center justify-between text-2xs text-muted mt-2">
                    <span>Target: {formatCurrency(phase.cumulative_target, currency)}</span>
                    <span>{phaseDoneCount}/{phase.actions.length} Done</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active Phase Details Container */}
          <div className="bg-surface-2/40 border border-border/80 rounded-2xl p-5 sm:p-6 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/70">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-primary-dark">{currentPhaseData.name}</h3>
                  <span className="text-xs font-semibold text-primary-accent bg-primary-accent/10 px-2 py-0.5 rounded-full">
                    {currentPhaseData.days}
                  </span>
                </div>
                <p className="text-xs text-muted mt-0.5">{currentPhaseData.focus}</p>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-auto bg-card-bg px-3.5 py-1.5 rounded-lg border border-border/70 shadow-2xs">
                <TrendingUp size={14} className="text-positive" />
                <span className="text-xs text-muted font-medium">Phase Savings:</span>
                <span className="text-xs font-bold text-positive">+{formatCurrency(currentPhaseData.target_savings, currency)}</span>
              </div>
            </div>

            {/* Strategic Advice */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-primary-dark mb-2.5 flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-primary-accent" />
                Key Strategic Advice & Financial Discipline
              </h4>
              <ul className="space-y-2">
                {currentPhaseData.advice.map((adv, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-primary-dark/90 leading-relaxed bg-card-bg/60 p-2.5 rounded-lg border border-border/40">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary-accent mt-1.5 flex-shrink-0" />
                    <span>{adv}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Action Items Checklist */}
            <div className="pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-primary-dark mb-2.5 flex items-center gap-1.5">
                <CheckCircle2 size={14} className="text-positive" />
                Actionable Checklist (Mark completed as you progress)
              </h4>
              <div className="space-y-2.5">
                {currentPhaseData.actions.map((action) => {
                  const isDone = !!completedActions[action.id];
                  return (
                    <div
                      key={action.id}
                      onClick={() => toggleAction(action.id)}
                      className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                        isDone
                          ? 'bg-positive/5 border-positive/30 text-muted'
                          : 'bg-card-bg border-border/80 hover:border-primary-accent/40 shadow-2xs'
                      }`}
                    >
                      <button
                        type="button"
                        aria-label={isDone ? `Mark ${action.title} incomplete` : `Mark ${action.title} complete`}
                        className="mt-0.5 flex-shrink-0 text-muted hover:text-primary-dark transition-colors"
                      >
                        {isDone ? (
                          <CheckCircle2 size={18} className="text-positive fill-positive/20" />
                        ) : (
                          <Circle size={18} className="text-muted/60" />
                        )}
                      </button>
                      <div className="min-w-0 flex-1">
                        <p className={`text-sm font-bold ${isDone ? 'line-through text-muted' : 'text-primary-dark'}`}>
                          {action.title}
                        </p>
                        <p className={`text-xs mt-0.5 leading-relaxed ${isDone ? 'text-muted/70' : 'text-muted'}`}>
                          {action.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CONTENT TAB 2: FINANCIAL TERMS & HEALTH PLAYBOOK */}
      {activeTab === 'terms' && (
        <div className="space-y-4 relative z-10 animate-fade-in">
          <div className="p-4 bg-primary-accent/5 rounded-xl border border-primary-accent/20 flex items-start gap-3">
            <HelpCircle size={18} className="text-primary-accent flex-shrink-0 mt-0.5" />
            <p className="text-xs text-primary-dark leading-relaxed">
              Managing your money for 90 days requires understanding key financial concepts. Here is your personalized glossary
              calculated from your actual data, with practical guidelines to maintain stability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plan.financial_terms.map((item, idx) => (
              <div
                key={idx}
                className="bg-surface-2/40 border border-border/80 hover:border-border rounded-xl p-4 flex flex-col justify-between transition-colors shadow-2xs"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="text-sm font-bold text-primary-dark">{item.term}</h4>
                    <span
                      className={`text-2xs font-bold px-2 py-0.5 rounded-full border ${
                        item.status === 'Healthy' || item.status === 'Strong' || item.status === 'Optimal' || item.status === 'Safe' || item.status === 'High Velocity'
                          ? 'bg-positive/10 text-positive border-positive/20'
                          : 'bg-warning/10 text-warning-dark border-warning/30'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <div className="mb-3 flex items-baseline gap-2">
                    <span className="text-2xs uppercase tracking-wider text-muted font-bold">Your Calculated Value:</span>
                    <span className="text-sm font-black text-primary-dark">{item.your_metric}</span>
                  </div>

                  <p className="text-xs text-muted leading-relaxed mb-3">
                    {item.definition}
                  </p>
                </div>

                <div className="pt-3 border-t border-border/60">
                  <p className="text-2xs text-primary-dark/80 font-medium leading-relaxed">
                    <strong className="text-primary-accent">90-Day Impact:</strong> {item.why_it_matters}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
