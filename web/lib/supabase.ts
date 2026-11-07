import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

/**
 * Demo mode runs without Supabase.
 * Add NEXT_PUBLIC_SUPABASE_URL / ANON_KEY to enable the production adapter.
 */
export const supabase = url && anonKey ? createClient(url, anonKey) : null;

export const isSupabaseEnabled = Boolean(url && anonKey);
