-- =============================================================================
-- FIN4YOU SUPABASE SCHEMA MIGRATION SCRIPT (SAFE & NON-DESTRUCTIVE)
-- =============================================================================
-- This script ensures all 5 required tables and expected columns exist in Supabase.
-- It strictly preserves existing data and tables without dropping or renaming.
-- Note: PostgreSQL identifiers are case-sensitive when quoted.
-- =============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. "Profiles" Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "Profiles" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" TEXT UNIQUE NOT NULL,
    "full_name" TEXT DEFAULT 'Demo User',
    "age" TEXT DEFAULT '30',
    "marital_status" TEXT DEFAULT 'Single',
    "dependents" TEXT DEFAULT '0',
    "occupation" TEXT DEFAULT 'Professional',
    "city_tier" TEXT DEFAULT 'Tier 1',
    "home_currency" VARCHAR(10) DEFAULT 'USD',
    "current_available_balance" NUMERIC(14, 2) DEFAULT 0.0,
    "minimum_balance_to_keep" NUMERIC(14, 2) DEFAULT 0.0,
    "financial_priorities" TEXT DEFAULT '',
    "expense_categories_to_protect" TEXT DEFAULT '',
    "expense_categories_user_is_willing_to_reduce" TEXT DEFAULT '',
    "expense_categories_user_is_willing_to_stop" TEXT DEFAULT '',
    "payment_methods_user_will_consider" TEXT DEFAULT '',
    "max_installment_months" INTEGER DEFAULT 12,
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure optional columns exist if table was already created with minimal schema
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "user_id" TEXT;
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "full_name" TEXT DEFAULT 'Demo User';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "age" TEXT DEFAULT '30';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "marital_status" TEXT DEFAULT 'Single';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "dependents" TEXT DEFAULT '0';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "occupation" TEXT DEFAULT 'Professional';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "city_tier" TEXT DEFAULT 'Tier 1';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "home_currency" VARCHAR(10) DEFAULT 'USD';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "current_available_balance" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "minimum_balance_to_keep" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "financial_priorities" TEXT DEFAULT '';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "expense_categories_to_protect" TEXT DEFAULT '';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "expense_categories_user_is_willing_to_reduce" TEXT DEFAULT '';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "expense_categories_user_is_willing_to_stop" TEXT DEFAULT '';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "payment_methods_user_will_consider" TEXT DEFAULT '';
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "max_installment_months" INTEGER DEFAULT 12;
ALTER TABLE "Profiles" ADD COLUMN IF NOT EXISTS "updated_at" TIMESTAMPTZ DEFAULT NOW();

CREATE INDEX IF NOT EXISTS "ix_profiles_user_id" ON "Profiles" ("user_id");

-- -----------------------------------------------------------------------------
-- 2. "Transactions" Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "Transactions" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "transaction_id" TEXT UNIQUE NOT NULL,
    "user_id" TEXT NOT NULL,
    "event_type" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "category" TEXT,
    "direction" TEXT NOT NULL,
    "amount" NUMERIC(14, 2) NOT NULL,
    "currency" VARCHAR(10) DEFAULT 'USD',
    "event_date" DATE NOT NULL,
    "settlement_date" DATE,
    "status" TEXT DEFAULT 'SETTLED',
    "flexibility" TEXT DEFAULT 'variable',
    "ml_confidence" FLOAT8,
    "ml_status" TEXT,
    "ml_confidence_level" TEXT,
    "created_at" TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure all columns exist
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "transaction_id" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "user_id" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "event_type" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "description" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "category" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "direction" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "amount" NUMERIC(14, 2);
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "currency" VARCHAR(10) DEFAULT 'USD';
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "event_date" DATE;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "settlement_date" DATE;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "status" TEXT DEFAULT 'SETTLED';
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "flexibility" TEXT DEFAULT 'variable';
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "ml_confidence" FLOAT8;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "ml_status" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "ml_confidence_level" TEXT;
ALTER TABLE "Transactions" ADD COLUMN IF NOT EXISTS "created_at" TIMESTAMPTZ DEFAULT NOW();

CREATE UNIQUE INDEX IF NOT EXISTS "ix_transactions_transaction_id" ON "Transactions" ("transaction_id");
CREATE INDEX IF NOT EXISTS "ix_transactions_user_id" ON "Transactions" ("user_id");
CREATE INDEX IF NOT EXISTS "ix_transactions_event_date" ON "Transactions" ("event_date");

-- -----------------------------------------------------------------------------
-- 3. "Financial_Summaries" Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "Financial_Summaries" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "summary_id" TEXT UNIQUE NOT NULL,
    "user_id" TEXT NOT NULL,
    "reporting_period" TEXT NOT NULL,
    "income" NUMERIC(14, 2) DEFAULT 0.0,
    "expenses" NUMERIC(14, 2) DEFAULT 0.0,
    "savings" NUMERIC(14, 2) DEFAULT 0.0,
    "savings_rate" FLOAT8 DEFAULT 0.0,
    "cash_flow" NUMERIC(14, 2) DEFAULT 0.0,
    "essential_expenses" NUMERIC(14, 2) DEFAULT 0.0,
    "discretionary_expenses" NUMERIC(14, 2) DEFAULT 0.0,
    "recurring_obligations" NUMERIC(14, 2) DEFAULT 0.0,
    "emi_burden" FLOAT8 DEFAULT 0.0,
    "data_quality_confidence" FLOAT8 DEFAULT 1.0,
    "summary_data" JSONB DEFAULT '{}'::jsonb,
    "created_at" TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure all columns exist
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "summary_id" TEXT;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "user_id" TEXT;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "reporting_period" TEXT;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "income" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "expenses" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "savings" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "savings_rate" FLOAT8 DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "cash_flow" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "essential_expenses" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "discretionary_expenses" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "recurring_obligations" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "emi_burden" FLOAT8 DEFAULT 0.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "data_quality_confidence" FLOAT8 DEFAULT 1.0;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "summary_data" JSONB DEFAULT '{}'::jsonb;
ALTER TABLE "Financial_Summaries" ADD COLUMN IF NOT EXISTS "created_at" TIMESTAMPTZ DEFAULT NOW();

CREATE INDEX IF NOT EXISTS "ix_financial_summaries_user_id" ON "Financial_Summaries" ("user_id");
CREATE INDEX IF NOT EXISTS "ix_financial_summaries_period" ON "Financial_Summaries" ("user_id", "reporting_period");

-- -----------------------------------------------------------------------------
-- 4. "Forecasts" Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "Forecasts" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "forecast_id" TEXT UNIQUE NOT NULL,
    "user_id" TEXT NOT NULL,
    "forecast_period" TEXT NOT NULL,
    "projected_income" NUMERIC(14, 2) DEFAULT 0.0,
    "projected_expenses" NUMERIC(14, 2) DEFAULT 0.0,
    "known_obligations" NUMERIC(14, 2) DEFAULT 0.0,
    "projected_cash_flow" NUMERIC(14, 2) DEFAULT 0.0,
    "uncertainty" FLOAT8 DEFAULT 0.0,
    "confidence" FLOAT8 DEFAULT 1.0,
    "evaluation_mae" FLOAT8,
    "evaluation_rmse" FLOAT8,
    "forecast_data" JSONB DEFAULT '{}'::jsonb,
    "created_at" TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure all columns exist
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "forecast_id" TEXT;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "user_id" TEXT;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "forecast_period" TEXT;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "projected_income" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "projected_expenses" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "known_obligations" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "projected_cash_flow" NUMERIC(14, 2) DEFAULT 0.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "uncertainty" FLOAT8 DEFAULT 0.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "confidence" FLOAT8 DEFAULT 1.0;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "evaluation_mae" FLOAT8;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "evaluation_rmse" FLOAT8;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "forecast_data" JSONB DEFAULT '{}'::jsonb;
ALTER TABLE "Forecasts" ADD COLUMN IF NOT EXISTS "created_at" TIMESTAMPTZ DEFAULT NOW();

CREATE INDEX IF NOT EXISTS "ix_forecasts_user_id" ON "Forecasts" ("user_id");
CREATE INDEX IF NOT EXISTS "ix_forecasts_period" ON "Forecasts" ("user_id", "forecast_period");

-- -----------------------------------------------------------------------------
-- 5. "Monthly_Reports" Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "Monthly_Reports" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "report_id" TEXT UNIQUE NOT NULL,
    "user_id" TEXT NOT NULL,
    "reporting_period" TEXT NOT NULL,
    "previous_period" TEXT,
    "report_data" JSONB DEFAULT '{}'::jsonb,
    "storage_reference" TEXT,
    "created_at" TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure all columns exist
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "report_id" TEXT;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "user_id" TEXT;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "reporting_period" TEXT;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "previous_period" TEXT;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "report_data" JSONB DEFAULT '{}'::jsonb;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "storage_reference" TEXT;
ALTER TABLE "Monthly_Reports" ADD COLUMN IF NOT EXISTS "created_at" TIMESTAMPTZ DEFAULT NOW();

CREATE INDEX IF NOT EXISTS "ix_monthly_reports_user_id" ON "Monthly_Reports" ("user_id");
CREATE INDEX IF NOT EXISTS "ix_monthly_reports_period" ON "Monthly_Reports" ("user_id", "reporting_period");
