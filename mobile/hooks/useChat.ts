/**
 * hooks/useChat.ts
 * Real-time chat state for a single gig workspace.
 * Fetches history via REST then subscribes to the WebSocket for live messages.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { chatApi, Message } from '../lib/api';
import { useAuth } from './useAuth';
import { velaiWS } from '../lib/ws';

export function useChat(gigId: string) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);

  // Load message history
  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    try {
      const { data } = await chatApi.list(gigId);
      if (mounted.current) setMessages(data);
    } catch {
      if (mounted.current) setError('Could not load messages.');
    } finally {
      if (mounted.current) setIsLoading(false);
    }
  }, [gigId]);

  // Connect WebSocket + subscribe
  useEffect(() => {
    mounted.current = true;
    loadHistory();
    velaiWS.connect(gigId);

    const remove = velaiWS.addHandler((raw) => {
      try {
        const msg: Message = JSON.parse(raw);
        if (mounted.current) {
          setMessages((prev) =>
            prev.some((m) => m.id === msg.id) ? prev : [...prev, msg]
          );
        }
      } catch {
        // ignore malformed frames
      }
    });

    return () => {
      mounted.current = false;
      remove();
      velaiWS.disconnect();
    };
  }, [gigId, loadHistory]);

  const sendMessage = useCallback(
    async (body: string, attachmentUrl?: string) => {
      if (!body.trim()) return;
      setIsSending(true);
      try {
        const { data } = await chatApi.send(gigId, body, attachmentUrl);
        // Optimistically add (WS echo will be deduplicated)
        setMessages((prev) =>
          prev.some((m) => m.id === data.id) ? prev : [...prev, data]
        );
      } catch {
        setError('Message not sent. Try again.');
      } finally {
        setIsSending(false);
      }
    },
    [gigId]
  );

  return { messages, isLoading, isSending, error, sendMessage, currentUserId: user?.id };
}
