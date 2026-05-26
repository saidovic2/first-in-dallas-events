-- ============================================================
-- Run this in the Supabase SQL editor (Dashboard → SQL Editor)
-- ============================================================
-- Creates a trigger so that an organizer row is automatically
-- created whenever a new user signs up (email or OAuth).
-- This runs as SECURITY DEFINER (database owner) and bypasses
-- RLS, which is why the client-side insert was failing.
-- ============================================================

-- 1. Function called by the trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.organizers (id, email, full_name, organization_name)
  VALUES (
    new.id,
    new.email,
    COALESCE(new.raw_user_meta_data->>'full_name', ''),
    COALESCE(new.raw_user_meta_data->>'organization_name', '')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN new;
END;
$$;

-- 2. Trigger on auth.users (fires on every new signup, including Google OAuth)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 3. RLS policies for organizers table
--    (trigger handles INSERT; clients only need SELECT + UPDATE on their own row)
ALTER TABLE public.organizers ENABLE ROW LEVEL SECURITY;

-- Drop old/conflicting policies if they exist
DROP POLICY IF EXISTS "Users can view own organizer profile"       ON public.organizers;
DROP POLICY IF EXISTS "Users can update own organizer profile"     ON public.organizers;
DROP POLICY IF EXISTS "Users can insert own organizer profile"     ON public.organizers;
DROP POLICY IF EXISTS "Service role full access to organizers"     ON public.organizers;

CREATE POLICY "Users can view own organizer profile"
  ON public.organizers FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own organizer profile"
  ON public.organizers FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Service role used by the FastAPI backend (reads organizer data)
CREATE POLICY "Service role full access to organizers"
  ON public.organizers FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
