import { useEffect, useRef, useCallback, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface RealtimeConfig {
  channels: string[];
  onMessage?: (channel: string, data: any) => void;
  onError?: (error: Error) => void;
}

interface RealtimeMessage {
  channel: string;
  topic: string;
  data: any;
  timestamp: number;
}

export function useRealtime(config: RealtimeConfig) {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [latestMessages, setLatestMessages] = useState<Map<string, RealtimeMessage>>(new Map());

  // Initialize socket connection
  useEffect(() => {
    const socket = io(import.meta.env.VITE_WS_URL || 'ws://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      
      // Subscribe to channels
      config.channels.forEach((channel) => {
        socket.emit('subscribe', channel);
      });
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('error', (error) => {
      config.onError?.(new Error(error));
    });

    // Handle incoming messages
    socket.onAny((eventName: string, data: any) => {
      const message: RealtimeMessage = {
        channel: eventName,
        topic: data.topic || '',
        data: data.data || data,
        timestamp: Date.now(),
      };

      setLatestMessages((prev) => new Map(prev).set(eventName, message));
      config.onMessage?.(eventName, data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Subscribe to additional channel
  const subscribe = useCallback((channel: string) => {
    if (socketRef.current) {
      socketRef.current.emit('subscribe', channel);
    }
  }, []);

  // Unsubscribe from channel
  const unsubscribe = useCallback((channel: string) => {
    if (socketRef.current) {
      socketRef.current.emit('unsubscribe', channel);
    }
  }, []);

  // Send message to channel
  const send = useCallback((channel: string, data: any) => {
    if (socketRef.current) {
      socketRef.current.emit(channel, data);
    }
  }, []);

  // Get latest message for channel
  const getLatest = useCallback((channel: string) => {
    return latestMessages.get(channel);
  }, [latestMessages]);

  return {
    isConnected,
    subscribe,
    unsubscribe,
    send,
    getLatest,
    latestMessages: Array.from(latestMessages.values()),
  };
}

// Hook for specific channel subscription
export function useRealtimeChannel(channel: string, handler: (data: any) => void) {
  const { subscribe, unsubscribe, isConnected } = useRealtime({
    channels: [channel],
    onMessage: (ch, data) => {
      if (ch === channel) {
        handler(data);
      }
    },
  });

  useEffect(() => {
    if (isConnected) {
      subscribe(channel);
    }

    return () => {
      unsubscribe(channel);
    };
  }, [channel, isConnected]);

  return { isConnected };
}
