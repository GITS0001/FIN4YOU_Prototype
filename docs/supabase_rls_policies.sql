-- =============================================================================
-- FIN4YOU SUPABASE ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- Enforces per-user isolation so authenticated users can only access
-- and modify their own records across all financial entities.
-- Service-role / backend privileged calls bypass RLS when necessary.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Enable Row Level Security on all 5 tables
-- -----------------------------------------------------------------------------
ALTER TABLE "Profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Transactions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Financial_Summaries" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Forecasts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Monthly_Reports" ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------------------------
-- 2. Policies for "Profiles"
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own profile" ON "Profiles";
CREATE POLICY "Users can view their own profile"
    ON "Profiles"
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can insert their own profile" ON "Profiles";
CREATE POLICY "Users can insert their own profile"
    ON "Profiles"
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can update their own profile" ON "Profiles";
CREATE POLICY "Users can update their own profile"
    ON "Profiles"
    FOR UPDATE
    TO authenticated
    USING (auth.uid()::text = "user_id")
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can delete their own profile" ON "Profiles";
CREATE POLICY "Users can delete their own profile"
    ON "Profiles"
    FOR DELETE
    TO authenticated
    USING (auth.uid()::text = "user_id");

-- -----------------------------------------------------------------------------
-- 3. Policies for "Transactions"
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own transactions" ON "Transactions";
CREATE POLICY "Users can view their own transactions"
    ON "Transactions"
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can insert their own transactions" ON "Transactions";
CREATE POLICY "Users can insert their own transactions"
    ON "Transactions"
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can update their own transactions" ON "Transactions";
CREATE POLICY "Users can update their own transactions"
    ON "Transactions"
    FOR UPDATE
    TO authenticated
    USING (auth.uid()::text = "user_id")
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can delete their own transactions" ON "Transactions";
CREATE POLICY "Users can delete their own transactions"
    ON "Transactions"
    FOR DELETE
    TO authenticated
    USING (auth.uid()::text = "user_id");

-- -----------------------------------------------------------------------------
-- 4. Policies for "Financial_Summaries"
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own financial summaries" ON "Financial_Summaries";
CREATE POLICY "Users can view their own financial summaries"
    ON "Financial_Summaries"
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can insert their own financial summaries" ON "Financial_Summaries";
CREATE POLICY "Users can insert their own financial summaries"
    ON "Financial_Summaries"
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can update their own financial summaries" ON "Financial_Summaries";
CREATE POLICY "Users can update their own financial summaries"
    ON "Financial_Summaries"
    FOR UPDATE
    TO authenticated
    USING (auth.uid()::text = "user_id")
    WITH CHECK (auth.uid()::text = "user_id");

-- -----------------------------------------------------------------------------
-- 5. Policies for "Forecasts"
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own forecasts" ON "Forecasts";
CREATE POLICY "Users can view their own forecasts"
    ON "Forecasts"
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can insert their own forecasts" ON "Forecasts";
CREATE POLICY "Users can insert their own forecasts"
    ON "Forecasts"
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can update their own forecasts" ON "Forecasts";
CREATE POLICY "Users can update their own forecasts"
    ON "Forecasts"
    FOR UPDATE
    TO authenticated
    USING (auth.uid()::text = "user_id")
    WITH CHECK (auth.uid()::text = "user_id");

-- -----------------------------------------------------------------------------
-- 6. Policies for "Monthly_Reports"
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own monthly reports" ON "Monthly_Reports";
CREATE POLICY "Users can view their own monthly reports"
    ON "Monthly_Reports"
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can insert their own monthly reports" ON "Monthly_Reports";
CREATE POLICY "Users can insert their own monthly reports"
    ON "Monthly_Reports"
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid()::text = "user_id");

DROP POLICY IF EXISTS "Users can update their own monthly reports" ON "Monthly_Reports";
CREATE POLICY "Users can update their own monthly reports"
    ON "Monthly_Reports"
    FOR UPDATE
    TO authenticated
    USING (auth.uid()::text = "user_id")
    WITH CHECK (auth.uid()::text = "user_id");
