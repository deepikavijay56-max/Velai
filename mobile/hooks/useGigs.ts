/**
 * hooks/useGigs.ts
 * Data-fetching hooks for the gig feed, a single gig, and posting.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { gigsApi, Gig, GigFilters, CreateGigPayload } from '../lib/api';

// ── Gig feed (paginated) ─────────────────────────────────────────────────────
export function useGigFeed(filters: GigFilters = {}) {
  const [gigs, setGigs] = useState<Gig[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const allGigsRef = useRef<Gig[]>([]);
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  const load = useCallback(async (refresh = false) => {
    if (refresh) setIsRefreshing(true);
    else setIsLoading(true);
    setError(null);
    try {
      const { data } = await gigsApi.list(filtersRef.current);
      allGigsRef.current = data;
      setGigs(data.slice(0, 20));
      setTotal(data.length);
    } catch {
      setError('Could not load gigs. Pull down to retry.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Reload when filters change
  useEffect(() => {
    load();
  }, [
    filters.category,
    filters.status,
    filters.budget_min,
    filters.budget_max,
    filters.search,
    load,
  ]);

  const refresh = useCallback(() => load(true), [load]);
  const loadMore = useCallback(() => {
    if (!isLoading && gigs.length < total) {
      setGigs(allGigsRef.current.slice(0, gigs.length + 20));
    }
  }, [isLoading, gigs.length, total]);

  return { gigs, total, isLoading, isRefreshing, error, refresh, loadMore };
}

// ── Single gig ───────────────────────────────────────────────────────────────
export function useGig(id: string) {
  const [gig, setGig] = useState<Gig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await gigsApi.get(id);
      setGig(data);
    } catch {
      setError('Could not load this gig.');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => { fetch(); }, [fetch]);

  return { gig, isLoading, error, refetch: fetch };
}

// ── Post a gig ───────────────────────────────────────────────────────────────
export function usePostGig() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const post = useCallback(async (payload: CreateGigPayload): Promise<Gig | null> => {
    setIsSubmitting(true);
    setError(null);
    try {
      const { data } = await gigsApi.create(payload);
      return data;
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Could not post gig. Check your details.';
      setError(typeof msg === 'string' ? msg : 'Could not post gig.');
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  return { post, isSubmitting, error };
}
