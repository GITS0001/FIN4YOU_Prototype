// ─────────────────────────────────────────────────────────────
//  FIN4YOU — Supabase Client  (React/Vite build)
//  Only the publishable (anon) key is used here.
//  NEVER put sb_secret_ keys in frontend code.
// ─────────────────────────────────────────────────────────────
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://dabvqdwncvfcuzsvqqga.supabase.co';
const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_82r7pElqAcg1Q-cVNgqR9w_Nw95uzmQ';

export const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
