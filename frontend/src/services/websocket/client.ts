/**
 * WebSocket Client - Real-time Connection to Backend
 * 
 * Connects to backend sharded WebSocket for real-time updates.
 * Features:
 * - Auto-reconnect
 * - Event subscriptions
 * - Heartbeat monitoring
 * 
 * 2035-ready: Real-time everything, not polling
 */

import { io, Socket } from 'socket.io-client';

type EventHandler = (...args: any[]) => void;

class WebSocketClient {
  private socket: Socket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private eventHandlers: Map<string, Set<EventHandler>> = new Map();

  constructor(url: string = import.meta.env.VITE_WEBSOCKET_URL || 'http://localhost:8000') {
    this.url = url;
  }

  /**
   * Connect to WebSocket server
   */
  connect(userId: string, token: string): void {
    if (this.socket?.connected) {
      console.log('✅ WebSocket already connected');
      return;
    }

    console.log('🔌 Connecting to WebSocket...', this.url);

    this.socket = io(this.url, {
      auth: {
        token,
        user_id: userId,
      },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    // Connection events
    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('❌ Max reconnection attempts reached');
      }
    });

    // Heartbeat
    this.socket.on('heartbeat', () => {
      this.socket?.emit('heartbeat_ack');
    });

    // Re-attach event handlers after reconnect
    this.socket.on('connect', () => {
      this.eventHandlers.forEach((handlers, event) => {
        handlers.forEach(handler => {
          this.socket?.on(event, handler);
        });
      });
    });
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('🔌 WebSocket disconnected');
    }
  }

  /**
   * Subscribe to event
   */
  on(event: string, handler: EventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
    this.socket?.on(event, handler);
  }

  /**
   * Unsubscribe from event
   */
  off(event: string, handler: EventHandler): void {
    this.eventHandlers.get(event)?.delete(handler);
    this.socket?.off(event, handler);
  }

  /**
   * Emit event to server
   */
  emit(event: string, data: any): void {
    this.socket?.emit(event, data);
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Subscribe to entity-specific events
   * Example: subscribeToEntity('trade', '123') → listens to 'trade:123' events
   */
  subscribeToEntity(entityType: string, entityId: string, handler: EventHandler): void {
    const event = `${entityType}:${entityId}`;
    this.on(event, handler);
  }

  /**
   * Unsubscribe from entity events
   */
  unsubscribeFromEntity(entityType: string, entityId: string, handler: EventHandler): void {
    const event = `${entityType}:${entityId}`;
    this.off(event, handler);
  }
}

// Singleton instance
export const websocketClient = new WebSocketClient();

export default websocketClient;
