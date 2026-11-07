"use client";

import type { SupabaseClient } from "@supabase/supabase-js";

import { isSupabaseEnabled, supabaseAnonKey, supabaseUrl } from "./config";

let browserClient: SupabaseClient | null = null;

/**
 * Lazily load the Supabase browser client.
 * In demo mode this resolves to null and never downloads @supabase/ssr.
 */
export async function getSupabaseBrowser(): Promise<SupabaseClient | null> {
  if (!isSupabaseEnabled) return null;
  if (!browserClient) {
    const { createBrowserClient } = await import("@supabase/ssr");
    browserClient = createBrowserClient(supabaseUrl, supabaseAnonKey);
  }
  return browserClient;
}
