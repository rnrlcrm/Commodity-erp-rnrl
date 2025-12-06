/**
 * User Capabilities Management
 * Pure capability-based user permission management (no roles)
 * Purpose: Assign/revoke capabilities to individual users
 */

import { useState, useEffect } from 'react';
import { 
  UserCircleIcon,
  KeyIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import usersService, { type UserWithCapabilities } from '@/services/api/usersService';
import capabilitiesService from '@/services/api/capabilitiesService';
import type { 
  Capability, 
  UserCapabilitiesResponse,
  UserCapability 
} from '@/types/capability';

interface CapabilityAssignmentModal {
  isOpen: boolean;
  user: UserWithCapabilities | null;
  currentCapabilities: UserCapabilitiesResponse | null;
}

export function UserCapabilitiesPage() {
  const [users, setUsers] = useState<UserWithCapabilities[]>([]);
  const [allCapabilities, setAllCapabilities] = useState<Capability[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [userCapabilities, setUserCapabilities] = useState<UserCapabilitiesResponse | null>(null);
  const [assignModal, setAssignModal] = useState<CapabilityAssignmentModal>({
    isOpen: false,
    user: null,
    currentCapabilities: null,
  });
  const [capabilitySearch, setCapabilitySearch] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      loadUserCapabilities(selectedUserId);
    }
  }, [selectedUserId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersData, capabilitiesData] = await Promise.all([
        usersService.getAllUsers(),
        capabilitiesService.getAllCapabilities(),
      ]);
      setUsers(usersData);
      setAllCapabilities(capabilitiesData);
    } catch (error) {
      console.error('Failed to load data:', error);
      setErrorMessage('Failed to load users and capabilities');
    } finally {
      setLoading(false);
    }
  };

  const loadUserCapabilities = async (userId: string) => {
    try {
      const capabilities = await capabilitiesService.getUserCapabilities(userId);
      setUserCapabilities(capabilities);
    } catch (error) {
      console.error('Failed to load user capabilities:', error);
      setErrorMessage('Failed to load user capabilities');
    }
  };

  const handleGrantCapability = async (userId: string, capabilityCode: string) => {
    try {
      setSubmitting(true);
      await capabilitiesService.grantCapabilityToUser(userId, {
        capability_code: capabilityCode,
      });
      setSuccessMessage(`Capability ${capabilityCode} granted successfully`);
      await loadUserCapabilities(userId);
      closeAssignModal();
    } catch (error: any) {
      console.error('Failed to grant capability:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to grant capability');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevokeCapability = async (userId: string, capabilityCode: string) => {
    try {
      setSubmitting(true);
      await capabilitiesService.revokeCapabilityFromUser(userId, capabilityCode);
      setSuccessMessage(`Capability ${capabilityCode} revoked successfully`);
      await loadUserCapabilities(userId);
    } catch (error: any) {
      console.error('Failed to revoke capability:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to revoke capability');
    } finally {
      setSubmitting(false);
    }
  };

  const openAssignModal = (user: UserWithCapabilities) => {
    loadUserCapabilities(user.id).then(() => {
      setAssignModal({
        isOpen: true,
        user,
        currentCapabilities: userCapabilities,
      });
    });
  };

  const closeAssignModal = () => {
    setAssignModal({
      isOpen: false,
      user: null,
      currentCapabilities: null,
    });
    setCapabilitySearch('');
  };

  const filteredUsers = users.filter((user) =>
    user.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const availableCapabilities = allCapabilities.filter((cap) => {
    const isAssigned = userCapabilities?.capabilities.includes(cap.code);
    const matchesSearch = cap.name.toLowerCase().includes(capabilitySearch.toLowerCase()) ||
      cap.code.toLowerCase().includes(capabilitySearch.toLowerCase()) ||
      cap.description?.toLowerCase().includes(capabilitySearch.toLowerCase());
    return !isAssigned && matchesSearch;
  });

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      auth: 'emerald',
      organization: 'saturn',
      partner: 'sun',
      commodity: 'mars',
      location: 'purple',
      availability: 'blue',
      requirement: 'indigo',
      matching: 'teal',
      settings: 'gray',
      admin: 'red',
      system: 'slate',
    };
    return colors[category] || 'gray';
  };

  const getUserTypeColor = (userType: string) => {
    switch (userType) {
      case 'SUPER_ADMIN':
        return 'red';
      case 'INTERNAL':
        return 'saturn';
      case 'EXTERNAL':
        return 'sun';
      default:
        return 'gray';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-saturn-500 mx-auto mb-4"></div>
          <p className="text-saturn-600 font-medium">Loading users and capabilities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-space-900">User Capabilities Management</h1>
          <p className="text-saturn-600 mt-1">Assign and manage individual user permissions</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-2xl font-heading font-bold text-space-900">{users.length}</div>
            <div className="text-xs text-saturn-500">Total Users</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-heading font-bold text-space-900">{allCapabilities.length}</div>
            <div className="text-xs text-saturn-500">Available Capabilities</div>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4 flex items-center gap-3">
          <CheckCircleIcon className="w-6 h-6 text-emerald-600 flex-shrink-0" />
          <p className="text-emerald-800 font-medium">{successMessage}</p>
          <button onClick={() => setSuccessMessage(null)} className="ml-auto">
            <XMarkIcon className="w-5 h-5 text-emerald-600" />
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-center gap-3">
          <ExclamationTriangleIcon className="w-6 h-6 text-red-600 flex-shrink-0" />
          <p className="text-red-800 font-medium">{errorMessage}</p>
          <button onClick={() => setErrorMessage(null)} className="ml-auto">
            <XMarkIcon className="w-5 h-5 text-red-600" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* User List */}
        <div className="col-span-5">
          <div className="bg-white/80 backdrop-blur-sm border-2 border-space-200/30 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-heading font-bold text-space-900">Users</h2>
              <div className="relative flex-1 max-w-xs ml-4">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-saturn-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-2 border-2 border-space-200 rounded-xl focus:outline-none focus:border-saturn-400 transition-colors text-sm"
                />
              </div>
            </div>

            <div className="space-y-2 max-h-[calc(100vh-20rem)] overflow-y-auto">
              {filteredUsers.map((user) => (
                <div
                  key={user.id}
                  onClick={() => setSelectedUserId(user.id)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-120 ${
                    selectedUserId === user.id
                      ? 'border-saturn-400 bg-saturn-50 shadow-md'
                      : 'border-space-200/50 hover:border-saturn-300 hover:shadow-sm'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br from-${getUserTypeColor(user.user_type)}-400 to-${getUserTypeColor(user.user_type)}-600 flex items-center justify-center text-white font-heading font-bold flex-shrink-0`}>
                      {user.full_name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-heading font-bold text-space-900 truncate">{user.full_name || 'Unknown User'}</h3>
                      <p className="text-xs text-saturn-600 truncate">{user.email}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`px-2 py-0.5 rounded-md text-xs font-bold bg-${getUserTypeColor(user.user_type)}-100 text-${getUserTypeColor(user.user_type)}-700`}>
                          {user.user_type}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-saturn-100 text-saturn-700">
                          {user.capabilities_count || 0} caps
                        </span>
                        {!user.is_active && (
                          <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-red-100 text-red-700">
                            INACTIVE
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {filteredUsers.length === 0 && (
                <div className="text-center py-12">
                  <UserCircleIcon className="w-16 h-16 text-saturn-300 mx-auto mb-4" />
                  <p className="text-saturn-600 font-medium">No users found</p>
                  <p className="text-sm text-saturn-500 mt-1">Try adjusting your search</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* User Capabilities Details */}
        <div className="col-span-7">
          {!selectedUserId ? (
            <div className="bg-white/80 backdrop-blur-sm border-2 border-space-200/30 rounded-2xl p-12 text-center h-full flex items-center justify-center">
              <div>
                <UserCircleIcon className="w-20 h-20 text-saturn-300 mx-auto mb-4" />
                <p className="text-saturn-600 font-medium text-lg">Select a user to manage capabilities</p>
                <p className="text-sm text-saturn-500 mt-2">Click on a user from the list to view and assign capabilities</p>
              </div>
            </div>
          ) : (
            <div className="bg-white/80 backdrop-blur-sm border-2 border-space-200/30 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br from-${getUserTypeColor(users.find(u => u.id === selectedUserId)?.user_type || 'EXTERNAL')}-400 to-${getUserTypeColor(users.find(u => u.id === selectedUserId)?.user_type || 'EXTERNAL')}-600 flex items-center justify-center text-white font-heading font-bold text-lg flex-shrink-0`}>
                    {users.find(u => u.id === selectedUserId)?.full_name?.charAt(0) || 'U'}
                  </div>
                  <div>
                    <h2 className="text-lg font-heading font-bold text-space-900">
                      {users.find(u => u.id === selectedUserId)?.full_name || 'Unknown User'}
                    </h2>
                    <p className="text-sm text-saturn-600">{users.find(u => u.id === selectedUserId)?.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => openAssignModal(users.find(u => u.id === selectedUserId)!)}
                  disabled={submitting}
                  className="px-4 py-2 bg-gradient-to-r from-saturn-500 to-sun-500 text-white font-heading font-bold rounded-xl shadow-md hover:shadow-lg transition-all duration-120 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PlusIcon className="w-5 h-5" />
                  Assign Capability
                </button>
              </div>

              {/* Capabilities Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-saturn-50 border-2 border-saturn-200 rounded-xl p-4">
                  <div className="text-2xl font-heading font-bold text-space-900">{userCapabilities?.capabilities.length || 0}</div>
                  <div className="text-xs text-saturn-600 mt-1">Total Capabilities</div>
                </div>
                <div className="bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4">
                  <div className="text-2xl font-heading font-bold text-space-900">{userCapabilities?.direct_capabilities.length || 0}</div>
                  <div className="text-xs text-emerald-600 mt-1">Direct Grants</div>
                </div>
                <div className="bg-sun-50 border-2 border-sun-200 rounded-xl p-4">
                  <div className="text-2xl font-heading font-bold text-space-900">
                    {userCapabilities?.direct_capabilities.filter(c => c.expires_at && !isExpired(c.expires_at)).length || 0}
                  </div>
                  <div className="text-xs text-sun-600 mt-1">Temporary</div>
                </div>
              </div>

              {/* Direct Capabilities List */}
              <div>
                <h3 className="text-sm font-heading font-bold text-space-900 mb-3">Direct Capability Grants</h3>
                <div className="space-y-2 max-h-[calc(100vh-28rem)] overflow-y-auto">
                  {userCapabilities?.direct_capabilities.map((userCap: UserCapability) => {
                    const capability = userCap.capability;
                    const expired = isExpired(userCap.expires_at || undefined);
                    
                    return (
                      <div
                        key={userCap.id}
                        className={`p-3 rounded-xl border-2 ${expired ? 'border-red-200 bg-red-50' : 'border-space-200/50 bg-white'}`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1">
                            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br from-${getCategoryColor(capability?.category || 'system')}-400 to-${getCategoryColor(capability?.category || 'system')}-600 flex items-center justify-center flex-shrink-0`}>
                              <KeyIcon className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-heading font-bold text-space-900 text-sm">{capability?.name || 'Unknown'}</h4>
                              <p className="text-xs font-mono text-saturn-500">{capability?.code}</p>
                              {capability?.description && (
                                <p className="text-xs text-saturn-600 mt-1 line-clamp-1">{capability.description}</p>
                              )}
                              <div className="flex items-center gap-2 mt-2 flex-wrap">
                                {capability?.category && (
                                  <span className={`px-2 py-0.5 rounded-md text-xs font-bold bg-${getCategoryColor(capability.category)}-100 text-${getCategoryColor(capability.category)}-700`}>
                                    {capability.category}
                                  </span>
                                )}
                                {userCap.expires_at && (
                                  <span className={`px-2 py-0.5 rounded-md text-xs font-bold flex items-center gap-1 ${expired ? 'bg-red-100 text-red-700' : 'bg-sun-100 text-sun-700'}`}>
                                    <ClockIcon className="w-3 h-3" />
                                    {expired ? 'EXPIRED' : `Expires ${formatDate(userCap.expires_at)}`}
                                  </span>
                                )}
                                {userCap.reason && (
                                  <span className="px-2 py-0.5 rounded-md text-xs bg-space-100 text-space-700 italic">
                                    {userCap.reason}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRevokeCapability(selectedUserId, capability?.code || '')}
                            disabled={submitting}
                            className="p-2 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Revoke capability"
                          >
                            <XMarkIcon className="w-5 h-5 text-red-600" />
                          </button>
                        </div>
                      </div>
                    );
                  })}

                  {(!userCapabilities?.direct_capabilities || userCapabilities.direct_capabilities.length === 0) && (
                    <div className="text-center py-8">
                      <KeyIcon className="w-12 h-12 text-saturn-300 mx-auto mb-3" />
                      <p className="text-saturn-600 font-medium">No direct capabilities assigned</p>
                      <p className="text-sm text-saturn-500 mt-1">Click "Assign Capability" to grant permissions</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Capability Assignment Modal */}
      {assignModal.isOpen && assignModal.user && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b-2 border-space-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-heading font-bold text-space-900">Assign Capability</h2>
                  <p className="text-sm text-saturn-600 mt-1">
                    Assigning to: <span className="font-bold">{assignModal.user.full_name}</span>
                  </p>
                </div>
                <button
                  onClick={closeAssignModal}
                  disabled={submitting}
                  className="p-2 rounded-lg hover:bg-space-100 transition-colors disabled:opacity-50"
                >
                  <XMarkIcon className="w-6 h-6 text-space-600" />
                </button>
              </div>
            </div>

            {/* Search */}
            <div className="p-6 border-b-2 border-space-200">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-saturn-400" />
                <input
                  type="text"
                  placeholder="Search available capabilities..."
                  value={capabilitySearch}
                  onChange={(e) => setCapabilitySearch(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border-2 border-space-200 rounded-xl focus:outline-none focus:border-saturn-400 transition-colors"
                />
              </div>
            </div>

            {/* Capabilities Grid */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {availableCapabilities.map((capability) => (
                  <div
                    key={capability.id}
                    onClick={() => handleGrantCapability(assignModal.user!.id, capability.code)}
                    className="p-4 border-2 border-space-200/50 rounded-xl hover:border-saturn-400 hover:shadow-md transition-all duration-120 cursor-pointer group"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br from-${getCategoryColor(capability.category)}-400 to-${getCategoryColor(capability.category)}-600 flex items-center justify-center shadow-sm flex-shrink-0 group-hover:scale-110 transition-transform`}>
                        <KeyIcon className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-heading font-bold text-space-900 group-hover:text-saturn-700 transition-colors text-sm">
                          {capability.name}
                        </h3>
                        <p className="text-xs font-mono text-saturn-500 mt-0.5">{capability.code}</p>
                        {capability.description && (
                          <p className="text-xs text-saturn-600 mt-2 line-clamp-2">
                            {capability.description}
                          </p>
                        )}
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`px-2 py-0.5 rounded-md text-xs font-bold bg-${getCategoryColor(capability.category)}-100 text-${getCategoryColor(capability.category)}-700`}>
                            {capability.category}
                          </span>
                          {capability.is_system && (
                            <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-red-100 text-red-700">
                              SYSTEM
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {availableCapabilities.length === 0 && (
                <div className="text-center py-12">
                  <KeyIcon className="w-16 h-16 text-saturn-300 mx-auto mb-4" />
                  <p className="text-saturn-600 font-medium">
                    {capabilitySearch ? 'No matching capabilities found' : 'All capabilities already assigned'}
                  </p>
                  <p className="text-sm text-saturn-500 mt-1">
                    {capabilitySearch ? 'Try adjusting your search' : 'This user has all available capabilities'}
                  </p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t-2 border-space-200 bg-space-50">
              <div className="flex items-center justify-between">
                <p className="text-sm text-saturn-600">
                  Click on a capability to assign it instantly
                </p>
                <button
                  onClick={closeAssignModal}
                  disabled={submitting}
                  className="px-6 py-2 border-2 border-space-300 rounded-xl font-heading font-bold text-space-700 hover:bg-space-100 transition-colors disabled:opacity-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserCapabilitiesPage;
