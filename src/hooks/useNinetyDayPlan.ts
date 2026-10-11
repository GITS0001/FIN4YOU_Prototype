import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import { useFinancialProfile } from './useFinancialProfile';
import { useFinancialState } from './useFinancialState';

export interface PlanActionItem {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}

export interface PlanPhase {
  phase_number: number;
  name: string;
  days: string;
  target_savings: number;
  cumulative_target: number;
  focus: string;
  advice: string[];
  actions: PlanActionItem[];
}

export interface FinancialTerm {
  term: string;
  key: string;
  your_metric: string;
  status: string;
  definition: string;
  why_it_matters: string;
}

export interface NinetyDayPlanData {
  user_id: string;
  currency: string;
  dataset_summary: {
    monthly_income: number;
    monthly_expenses: number;
    monthly_cash_flow: number;
    available_balance: number;
    minimum_buffer: number;
    essential_expenses: number;
    discretionary_expenses: number;
    emi_burden: number;
    liquidity_runway_months: number;
    savings_rate_pct: number;
    discretionary_ratio_pct: number;
    emi_ratio_pct: number;
  };
  total_90_day_savings_target: number;
  projected_end_balance: number;
  phases: PlanPhase[];
  financial_terms: FinancialTerm[];
}

const STORAGE_KEY = 'fin4you_90day_completed_actions';

export function useNinetyDayPlan() {
  const { data: profile } = useFinancialProfile();
  const { data: state } = useFinancialState();

  const [data, setData] = useState<NinetyDayPlanData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [completedActions, setCompletedActions] = useState<Record<string, boolean>>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });

  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.get('/api/users/planner/90-day-plan');
      if (res.data) {
        setData(res.data);
        setLoading(false);
        return;
      }
    } catch (err: any) {
      console.warn('API fetch for 90-day plan fell back to client dataset derivation:', err);
    }

    // Client-side fallback derivation based on loaded profile and state dataset
    const currency = profile?.home_currency || 'INR';
    const balance = Number(profile?.current_available_balance || 0);
    const buffer = Number(profile?.minimum_balance_to_keep || 0);
    const income = Number(state?.income || 0);
    const expenses = Number(state?.expenses || 0);
    const essential = Number(state?.essential_expenses || expenses * 0.65);
    const discretionary = Number(state?.discretionary_expenses || expenses * 0.35);
    const emi = Number(state?.emi_burden || 0);
    const cashFlow = Number(state?.cash_flow ?? (income - expenses));

    const monthlySavings = cashFlow > 0 ? cashFlow : (income > 0 ? Math.max(1000, income * 0.15) : 5000);
    const totalSavings = Math.round(monthlySavings * 3);
    const projectedBalance = Math.round(balance + totalSavings);

    const essentialBurn = Math.max(1, essential > 0 ? essential : (expenses > 0 ? expenses : 20000));
    const runway = Number((balance / essentialBurn).toFixed(1));
    const incomeBase = Math.max(1, income);
    const discPct = Number(((discretionary / incomeBase) * 100).toFixed(1));
    const savPct = Number(((monthlySavings / incomeBase) * 100).toFixed(1));
    const emiPct = Number(((emi / incomeBase) * 100).toFixed(1));

    let topCat = 'Dining & Discretionary';
    if (state?.category_spending && state.category_spending.length > 0) {
      const sortedCats = [...state.category_spending].sort((a, b) => (b.total_amount || 0) - (a.total_amount || 0));
      if (sortedCats[0]?.category && sortedCats[0].category !== 'unknown') {
        topCat = sortedCats[0].category.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
      }
    }

    const fallbackData: NinetyDayPlanData = {
      user_id: profile?.user_id || 'user',
      currency,
      dataset_summary: {
        monthly_income: income,
        monthly_expenses: expenses,
        monthly_cash_flow: cashFlow,
        available_balance: balance,
        minimum_buffer: buffer,
        essential_expenses: essential,
        discretionary_expenses: discretionary,
        emi_burden: emi,
        liquidity_runway_months: runway,
        savings_rate_pct: savPct,
        discretionary_ratio_pct: discPct,
        emi_ratio_pct: emiPct,
      },
      total_90_day_savings_target: totalSavings,
      projected_end_balance: projectedBalance,
      phases: [
        {
          phase_number: 1,
          name: 'Phase 1: Liquidity & Leakage Plugging',
          days: 'Days 1–30',
          target_savings: Math.round(monthlySavings),
          cumulative_target: Math.round(monthlySavings),
          focus: 'Establish baseline cash discipline, curtail flexible leakage, and automate savings.',
          advice: [
            `Set up an automated standing instruction on salary credit day for ${currency} ${Math.round(monthlySavings).toLocaleString()} directly into your reserve account.`,
            `Cap flexible spending in ${topCat} by 15–20% to prevent unexpected mid-month cash crunches.`,
            'Conduct a zero-delay audit of all active debit mandates and recurring app subscriptions to eliminate unused services.',
          ],
          actions: [
            { id: 'act_1_1', title: 'Automate Salary Day Transfer', description: `Schedule auto-deposit of ${currency} ${Math.round(monthlySavings).toLocaleString()} right when income hits.`, completed: false },
            { id: 'act_1_2', title: `Curtail ${topCat} Leakage`, description: 'Set a weekly discretionary card cap to avoid exceeding monthly budget.', completed: false },
            { id: 'act_1_3', title: 'Audit Recurring Subscriptions', description: 'Identify and cancel unused entertainment or cloud memberships.', completed: false },
          ],
        },
        {
          phase_number: 2,
          name: 'Phase 2: Buffer Fortification & Category Optimization',
          days: 'Days 31–60',
          target_savings: Math.round(monthlySavings),
          cumulative_target: Math.round(monthlySavings * 2),
          focus: 'Fortify emergency reserve buffer and renegotiate recurring utility/debt costs.',
          advice: [
            `Fortify cash balance toward your safety buffer of ${currency} ${Math.round(buffer).toLocaleString()} so unexpected shocks never require high-interest loans.`,
            'Compare flexible utility, insurance, and telecom plans to unlock permanent recurring cost reductions.',
            'Review credit card and short-term debt billing cycles to ensure zero interest or penalty accruals.',
          ],
          actions: [
            { id: 'act_2_1', title: 'Reach Halfway Savings Milestone', description: `Accumulate cumulative ${currency} ${Math.round(monthlySavings * 2).toLocaleString()} in liquid buffer.`, completed: false },
            { id: 'act_2_2', title: 'Essential Utility Review', description: 'Optimize electricity, wifi, and grocery spending baskets.', completed: false },
            { id: 'act_2_3', title: 'Zero-Fee Debt Clearance', description: 'Ensure full payment on credit balances to protect credit score.', completed: false },
          ],
        },
        {
          phase_number: 3,
          name: 'Phase 3: Resiliency, Compounding & Surplus Allocation',
          days: 'Days 61–90',
          target_savings: Math.round(monthlySavings),
          cumulative_target: totalSavings,
          focus: 'Lock in compounding resilience and allocate surplus capital beyond buffer.',
          advice: [
            `Achieve the full 90-day savings milestone of ${currency} ${totalSavings.toLocaleString()}, bringing projected liquid balance to ${currency} ${projectedBalance.toLocaleString()}.`,
            `Deploy any surplus above the ${currency} ${Math.round(buffer).toLocaleString()} reserve buffer into low-risk liquid yields or short-term deposits.`,
            `Standardize your ${savPct}% net savings rate as your permanent household operational benchmark.`,
          ],
          actions: [
            { id: 'act_3_1', title: 'Complete 90-Day Savings Goal', description: `Hit the ${currency} ${totalSavings.toLocaleString()} cumulative milestone.`, completed: false },
            { id: 'act_3_2', title: 'Deploy Buffer Surplus', description: 'Move funds exceeding emergency reserve into interest-bearing liquid assets.', completed: false },
            { id: 'act_3_3', title: 'Review 90-Day Run-Rate', description: 'Re-run Artha AI diagnostic to set the subsequent quarter’s financial goals.', completed: false },
          ],
        },
      ],
      financial_terms: [
        {
          term: 'Emergency Reserve Buffer (ERB)',
          key: 'erb',
          your_metric: `${currency} ${Math.round(buffer).toLocaleString()}`,
          status: balance >= buffer ? 'Healthy' : 'Needs Fortification',
          definition: 'The non-negotiable cash baseline kept in liquid form to insulate your household against sudden medical emergencies or income shocks.',
          why_it_matters: 'Prevents forced liquidations of long-term investments or recourse to predatory credit when unexpected expenses arise.',
        },
        {
          term: 'Liquidity Runway',
          key: 'runway',
          your_metric: `${runway} Months`,
          status: runway >= 3.0 ? 'Strong' : 'Caution',
          definition: 'The exact duration your existing liquid balance can sustain essential baseline expenditures if all income ceased today.',
          why_it_matters: 'A runway of 3 to 6 months provides career resilience, peace of mind, and financial independence.',
        },
        {
          term: 'Discretionary Expense Ratio (DER)',
          key: 'der',
          your_metric: `${discPct}%`,
          status: discPct <= 30 ? 'Optimal' : 'High',
          definition: 'The percentage of gross monthly earnings spent on flexible lifestyle choices, dining, entertainment, and non-essential wants.',
          why_it_matters: 'Maintaining DER below 30% guarantees sufficient monthly surplus to feed savings and investment goals.',
        },
        {
          term: 'Debt-to-Income / EMI Burden',
          key: 'dti',
          your_metric: `${emiPct}%`,
          status: emiPct <= 35 ? 'Safe' : 'Elevated',
          definition: 'The fraction of monthly earnings committed to fixed debt repayments, loan EMIs, and credit servicing.',
          why_it_matters: 'A low burden (< 35%) ensures high discretionary flexibility and protects against default during income interruptions.',
        },
        {
          term: 'Net Savings Yield (Savings Rate)',
          key: 'savings_rate',
          your_metric: `${savPct}%`,
          status: savPct >= 25 ? 'High Velocity' : 'Moderate',
          definition: 'The portion of total monthly income retained as net unspent surplus after meeting all living costs.',
          why_it_matters: 'This single metric dictates how rapidly your net worth compounds and how fast your 90-day roadmap succeeds.',
        },
      ],
    };

    setData(fallbackData);
    setLoading(false);
  }, [profile, state]);

  useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  const toggleAction = useCallback((actionId: string) => {
    setCompletedActions((prev) => {
      const updated = { ...prev, [actionId]: !prev[actionId] };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // ignore
      }
      return updated;
    });
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchPlan,
    completedActions,
    toggleAction,
  };
}
