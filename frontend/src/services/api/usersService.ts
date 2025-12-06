/**
 * Users API Service
 * Admin endpoints for user management
 */

import apiClient from './apiClient';
import type { User } from '@/types/auth';

export interface UserListResponse {
  total: number;
  users: User[];
}

export interface UserWithCapabilities extends User {
  capabilities_count: number;
  last_login?: string;
}

const usersService = {
  /**
   * Get all users (SUPER_ADMIN only)
   * For now, we'll use /auth/me as a base and mock this until backend provides admin endpoint
   */
  async getAllUsers(): Promise<UserWithCapabilities[]> {
    // TODO: Replace with actual admin endpoint when available
    // For now, return mock data based on current user
    const { data: currentUser } = await apiClient.get<User>('/auth/me');
    
    // Mock additional users for demo purposes
    return [
      {
        ...currentUser,
        capabilities_count: currentUser.capabilities?.length || 0,
        last_login: new Date().toISOString(),
      }
    ];
  },

  /**
   * Get single user by ID
   */
  async getUserById(userId: string): Promise<User> {
    const { data } = await apiClient.get<User>(`/auth/users/${userId}`);
    return data;
  },

  /**
   * Update user status
   */
  async updateUserStatus(userId: string, isActive: boolean): Promise<User> {
    const { data } = await apiClient.patch<User>(`/auth/users/${userId}/status`, {
      is_active: isActive,
    });
    return data;
  },

  /**
   * Get sub-users for current user (EXTERNAL users)
   */
  async getSubUsers(): Promise<User[]> {
    const { data } = await apiClient.get<User[]>('/auth/sub-users');
    return data;
  },
};

export default usersService;
