"""
90-Day Forward Liquidity Simulation & Affordability Decision Engine.
Implements Sections 8, 10, and 11 of formula_sheet.docx.
Simulates day-by-day cash balance under full payment, installment options, and waiting schedules.
"""

from datetime import datetime, timedelta
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

class AffordabilitySimulator:
    """
    Simulates multi-scenario forward cash flows to determine safe affordability
    and optimal payment methods according to FIN4YOU rules.
    """
    
    def __init__(
        self,
        horizon_days: int = 90
    ):
        self.horizon_days = horizon_days
        
    def _extract_recurring_profile(
        self,
        df_events: pd.DataFrame,
        request_date: datetime,
        messages_df: Optional[pd.DataFrame] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract recurring income cadence, fixed contractual obligations,
        and daily variable burn rate from past transaction history.
        """
        # Filter prior events
        past_events = df_events[pd.to_datetime(df_events['event_date']) <= request_date].copy()
        
        # 1. Income schedule
        income_events = past_events[past_events['direction'] == 'credit'].sort_values('event_date')
        if not income_events.empty:
            regular_salary = income_events[income_events['category'] == 'salary']
            if not regular_salary.empty:
                last_salary = regular_salary.iloc[-1]
                salary_amount = float(last_salary['amount'])
                last_salary_date = pd.to_datetime(last_salary['event_date'])
                
                # Check cadence (weekly 7d, bi-weekly 14d, or monthly 30d)
                if len(regular_salary) > 1:
                    intervals = regular_salary['event_date'].diff().dt.days.dropna()
                    median_interval = float(intervals.median())
                else:
                    median_interval = 30.0
            else:
                salary_amount = float(income_events['amount'].median())
                last_salary_date = pd.to_datetime(income_events['event_date'].iloc[-1])
                median_interval = 30.0
        else:
            salary_amount = 0.0
            last_salary_date = request_date
            median_interval = 30.0

        # Check messages for salary adjustments or contract termination
        contract_ended = False
        salary_adjustment = None
        if messages_df is not None and not messages_df.empty and user_id:
            user_msgs = messages_df[messages_df['user_id'] == user_id]
            for _, msg in user_msgs.iterrows():
                txt = str(msg.get('message_text', ''))
                # Contract ended
                if 'contract has ended' in txt.lower() or 'no off-season income' in txt.lower():
                    contract_ended = True
                # Raised salary / updated salary
                elif 'gaji bulanan anda naik menjadi idr' in txt.lower():
                    import re
                    match = re.search(r'idr\s*([\d\.\,]+)', txt.lower())
                    if match:
                        salary_amount = float(match.group(1).replace('.', '').replace(',', ''))
                elif 'faktur sebesar idr' in txt.lower():
                    # Approved invoice
                    import re
                    match = re.search(r'idr\s*([\d\.\,]+)', txt.lower())
                    if match:
                        salary_adjustment = {
                            "date": request_date + timedelta(days=12),
                            "amount": float(match.group(1).replace('.', '').replace(',', ''))
                        }

        if contract_ended:
            salary_amount = 0.0

        # 2. Fixed recurring debits (rent, utilities, debt repayment, subscriptions, etc.)
        fixed_debits = past_events[
            (past_events['direction'] == 'debit') & 
            (past_events['flexibility'] == 'fixed')
        ]
        recurring_bills = []
        for cat, grp in fixed_debits.groupby('category'):
            recent = grp.tail(2)
            avg_amount = float(recent['amount'].mean())
            days_of_month = grp['event_date'].dt.day.mode().tolist()
            dom = days_of_month[0] if days_of_month else 1
            recurring_bills.append({
                "category": cat,
                "amount": avg_amount,
                "day_of_month": dom
            })
            
        # 3. Variable daily burn rate (groceries, transport, dining)
        variable_debits = past_events[
            (past_events['direction'] == 'debit') & 
            (past_events['flexibility'] != 'fixed')
        ]
        total_days = max(30, (request_date - past_events['event_date'].min()).days)
        daily_variable_rate = float(variable_debits['amount'].sum()) / total_days if total_days > 0 else 0.0

        return {
            "salary_amount": salary_amount,
            "salary_interval_days": median_interval,
            "last_salary_date": last_salary_date,
            "recurring_bills": recurring_bills,
            "daily_variable_rate": daily_variable_rate,
            "salary_adjustment": salary_adjustment
        }

    def simulate_trajectory(
        self,
        starting_balance: float,
        request_date: datetime,
        recurring_profile: Dict[str, Any],
        pending_events: List[Dict[str, Any]],
        additional_payments: List[Dict[str, Any]]
    ) -> Tuple[List[float], List[datetime], float]:
        """
        Simulate day-by-day cash balance from day 0 to horizon_days.
        Returns:
            trajectory: list of balances for days 0..horizon_days
            dates: list of corresponding datetime objects
            min_balance: lowest balance encountered
        """
        curr_balance = float(starting_balance)
        # Pre-index additional payments by date
        pmt_by_date = {}

        for p in additional_payments:
            p_date = pd.to_datetime(p['date']).date()
            pmt_by_date[p_date] = pmt_by_date.get(p_date, 0.0) + float(p['amount'])
            
        # Pre-index pending events by settlement date
        pending_by_date = {}
        for pe in pending_events:
            s_date = pd.to_datetime(pe['settlement_date']).date()
            direction = pe.get('direction', 'debit')
            signed_amount = float(pe['amount']) if direction == 'credit' else -float(pe['amount'])
            pending_by_date[s_date] = pending_by_date.get(s_date, 0.0) + signed_amount

        req_d = request_date.date()
        if req_d in pmt_by_date:
            curr_balance -= pmt_by_date[req_d]
        if req_d in pending_by_date:
            curr_balance += pending_by_date[req_d]

        trajectory = [curr_balance]
        dates = [request_date]

        salary_amt = recurring_profile['salary_amount']
        interval = recurring_profile['salary_interval_days']
        last_sal = recurring_profile['last_salary_date']
        daily_var = recurring_profile['daily_variable_rate']
        bills = recurring_profile['recurring_bills']
        adj = recurring_profile.get('salary_adjustment')


        for d in range(1, self.horizon_days + 1):
            day_date = (request_date + timedelta(days=d)).date()
            dt_obj = request_date + timedelta(days=d)
            
            # 1. Salary credit
            if salary_amt > 0:
                if interval <= 10:  # Weekly
                    if (dt_obj - last_sal).days % 7 == 0:
                        curr_balance += salary_amt
                elif interval <= 18:  # Bi-weekly
                    if (dt_obj - last_sal).days % 14 == 0:
                        curr_balance += salary_amt
                else:  # Monthly (e.g. 15th of each month)
                    if dt_obj.day == 15:
                        curr_balance += salary_amt
                        
            # One-time salary adjustment if present
            if adj and pd.to_datetime(adj['date']).date() == day_date:
                curr_balance += float(adj['amount'])
                
            # 2. Pending float settlements
            if day_date in pending_by_date:
                curr_balance += pending_by_date[day_date]
                
            # 3. Fixed recurring bills
            for b in bills:
                if dt_obj.day == b['day_of_month']:
                    curr_balance -= b['amount']
                    
            # 4. Daily variable burn rate
            curr_balance -= daily_var
            
            # 5. Candidate transaction payment schedule
            if day_date in pmt_by_date:
                curr_balance -= pmt_by_date[day_date]
                
            trajectory.append(curr_balance)
            dates.append(dt_obj)
            
        min_balance = min(trajectory)
        return trajectory, dates, min_balance

    def evaluate_request(
        self,
        user_id: str,
        request_id: str,
        request_date: datetime,
        requested_amount: float,
        profile: pd.DataFrame,
        events: pd.DataFrame,
        options: pd.DataFrame,
        messages: Optional[pd.DataFrame] = None,
        desired_completion_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Full evaluation of an affordability request against FIN4YOU rules.
        """
        u_prof = profile[profile['user_id'] == user_id].iloc[0]
        curr_balance = float(u_prof['current_available_balance'])
        min_balance_keep = float(u_prof['minimum_balance_to_keep'])
        currency = u_prof.get('home_currency', 'USD')
        
        # Pending events for this user
        user_events = events[events['user_id'] == user_id]
        pending_df = user_events[user_events['status'] == 'pending']
        pending_list = pending_df.to_dict('records')
        
        # Recurring profile
        recurring_prof = self._extract_recurring_profile(user_events, request_date, messages, user_id)
        
        # Base trajectory without requested payment
        base_traj, base_dates, base_min = self.simulate_trajectory(
            curr_balance, request_date, recurring_prof, pending_list, []
        )
        
        # Profile constraints
        raw_methods = str(u_prof.get('payment_methods_user_will_consider', ''))
        allowed_methods = [m.strip() for m in raw_methods.split('|') if m.strip()] if raw_methods else ['full_payment', 'installments']
        max_install_months = float(u_prof['max_installment_months']) if pd.notnull(u_prof.get('max_installment_months')) else 999.0

        # Calculate amount safe to pay today:
        lowest_headroom = min(b - min_balance_keep for b in base_traj)
        amount_safe_to_pay = max(0.0, lowest_headroom)
        
        # Scenario 1: Test Full Payment Today
        full_payment_traj, _, full_payment_min = self.simulate_trajectory(
            curr_balance, request_date, recurring_prof, pending_list,
            [{"date": request_date, "amount": requested_amount}]
        )
        
        req_options = options[options['request_id'] == request_id] if not options.empty else pd.DataFrame()
        
        can_full_payment = 'full_payment' in allowed_methods
        can_installments = 'installments' in allowed_methods

        # Decision Logic:
        # Check if full payment is both allowed and keeps balance >= min_balance_keep
        if can_full_payment and full_payment_min >= min_balance_keep:
            status = "affordable_now"
            rec_method = "full_payment"
            plan_str = f"{request_date.strftime('%Y-%m-%d')}:{int(requested_amount) if requested_amount.is_integer() else requested_amount}"
            earliest_date = request_date.strftime('%Y-%m-%d')
            amount_safe_to_pay = requested_amount
            lowest_avail = full_payment_min
            explanation = (
                f"Pay {currency} {requested_amount:,.2f} today. "
                f"This leaves at least {currency} {lowest_avail:,.2f} available over the next {self.horizon_days} days."
            )
            selected_traj = full_payment_traj
            selected_dates = base_dates
        else:
            # Check Candidate Installment Options
            valid_installment_option = None
            best_opt_traj = None
            
            if can_installments and not req_options.empty:
                installment_opts = req_options[req_options['payment_method'] == 'installments']
                for _, opt in installment_opts.iterrows():
                    num_pmts = int(opt['number_of_payments'])
                    if num_pmts > max_install_months:
                        continue # Exceeds user maximum installment tenure

                    p_amt = float(opt['payment_amount'])
                    freq = float(opt['payment_frequency_days']) if pd.notnull(opt['payment_frequency_days']) else 30.0
                    first_date = pd.to_datetime(opt['first_payment_date'])
                    
                    # Build installment payments
                    opt_pmts = []
                    for i in range(num_pmts):
                        p_date = first_date + timedelta(days=int(i * freq))
                        opt_pmts.append({"date": p_date, "amount": p_amt})
                        
                    opt_traj, _, opt_min = self.simulate_trajectory(
                        curr_balance, request_date, recurring_prof, pending_list, opt_pmts
                    )
                    
                    if opt_min >= min_balance_keep:
                        valid_installment_option = opt
                        best_opt_traj = opt_traj
                        break
                        
            if valid_installment_option is not None:
                status = "affordable_with_plan"
                rec_method = "installments"
                opt_id = valid_installment_option['payment_option_id']
                p_amt = float(valid_installment_option['payment_amount'])
                num_pmts = int(valid_installment_option['number_of_payments'])
                freq = float(valid_installment_option['payment_frequency_days']) if pd.notnull(valid_installment_option['payment_frequency_days']) else 30.0
                first_d = pd.to_datetime(valid_installment_option['first_payment_date'])
                
                plan_parts = [
                    f"{(first_d + timedelta(days=int(i * freq))).strftime('%Y-%m-%d')}:{p_amt:.2f}"
                    for i in range(num_pmts)
                ]
                plan_str = "|".join(plan_parts)
                earliest_date = first_d.strftime('%Y-%m-%d')
                explanation = (
                    f"Use installment plan ({opt_id}) of {num_pmts} payments starting {first_d.strftime('%Y-%m-%d')}. "
                    f"This leaves at least {currency} {min_balance_keep:,.2f} available."
                )
                selected_traj = best_opt_traj
                selected_dates = base_dates

            else:
                # Test Waiting / Affordable Later
                # Find earliest date where full payment preserves minimum balance
                found_date = None
                max_wait_days = 90
                if desired_completion_date is not None:
                    max_wait_days = min(90, (desired_completion_date - request_date).days)
                    
                for w in range(1, max_wait_days + 1):
                    test_d = request_date + timedelta(days=w)
                    wait_traj, _, wait_min = self.simulate_trajectory(
                        curr_balance, request_date, recurring_prof, pending_list,
                        [{"date": test_d, "amount": requested_amount}]
                    )
                    if wait_min >= min_balance_keep:
                        found_date = test_d
                        break
                        
                if found_date is not None:
                    status = "affordable_later"
                    rec_method = "wait"
                    earliest_date = found_date.strftime('%Y-%m-%d')
                    plan_str = f"{earliest_date}:{requested_amount:.2f}"
                    explanation = (
                        f"Wait until {earliest_date}, then pay {currency} {requested_amount:,.2f} in full. "
                        f"Paying earlier would take balance below the {currency} {min_balance_keep:,.2f} minimum."
                    )
                    selected_traj = base_traj
                    selected_dates = base_dates
                else:
                    status = "not_affordable"
                    rec_method = "not_recommended"
                    earliest_date = None
                    plan_str = "none"
                    explanation = (
                        f"Do not proceed with the {currency} {requested_amount:,.2f} request. "
                        f"None of the candidate payment options keep the {currency} {min_balance_keep:,.2f} minimum balance protected."
                    )
                    selected_traj = base_traj
                    selected_dates = base_dates

        return {
            "request_id": request_id,
            "user_id": user_id,
            "currency": currency,
            "requested_amount": requested_amount,
            "current_balance": curr_balance,
            "minimum_balance_to_keep": min_balance_keep,
            "amount_safe_to_pay": round(amount_safe_to_pay, 2),
            "affordability_status": status,
            "recommended_payment_method": rec_method,
            "payment_plan": plan_str,
            "earliest_date_for_full_payment": earliest_date,
            "spending_changes_needed": "none",
            "decision_explanation": explanation,
            "trajectory_dates": [d.strftime('%Y-%m-%d') for d in selected_dates],
            "trajectory_balances": [round(b, 2) for b in selected_traj]
        }
