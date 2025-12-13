/**
 * Locations Settings Page
 * Manage warehouses, branches, and other locations with Google Places integration
 */

import { useState, useEffect } from 'react';
import {
  MapPinIcon,
  BuildingStorefrontIcon,
  BuildingOfficeIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import { useToast } from '@/contexts/ToastContext';
import { LocationModal } from '@/components/settings/LocationModal';
import locationService from '@/services/api/locationService';
import type { Location } from '@/types/settings';
import SettingsSceneLayout from './components/SettingsSceneLayout';

export default function LocationsPage() {
  const toast = useToast();
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationModal, setLocationModal] = useState<{ open: boolean; data?: Location }>({ open: false });

  useEffect(() => {
    loadLocations();
  }, [filterType, filterActive]);

  const loadLocations = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (filterType !== 'all') filters.location_type = filterType;
      if (filterActive !== null) filters.is_active = filterActive;

      const data = await locationService.listLocations(filters);
      setLocations(data.locations);
    } catch (err: any) {
      setError(err.message || 'Failed to load locations');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLocation = async (id: string) => {
    if (!confirm('Are you sure you want to delete this location?')) return;
    try {
      await locationService.deleteLocation(id);
      toast.success('Location deleted successfully');
      loadLocations();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete location');
    }
  };

  const filteredLocations = locations.filter(loc => {
    const address = `${loc.address_line1 || ''} ${loc.address_line2 || ''}`.trim();
    return (
      loc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (loc.city && loc.city.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  });

  const locationTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'warehouse', label: 'Warehouse' },
    { value: 'branch', label: 'Branch' },
    { value: 'factory', label: 'Factory' },
    { value: 'office', label: 'Office' },
  ];

  const getLocationIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'warehouse':
        return BuildingStorefrontIcon;
      case 'branch':
      case 'office':
        return BuildingOfficeIcon;
      default:
        return MapPinIcon;
    }
  };

  const openNewLocation = () => setLocationModal({ open: true });

  if (loading) {
    return (
      <SettingsSceneLayout title="Location Settings" subtitle="Manage warehouses, branches, and other execution sites">
        <HoloPanel theme="space" className="p-12 text-center text-pearl-200">
          Loading locations...
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  if (error) {
    return (
      <SettingsSceneLayout title="Location Settings" subtitle="Manage warehouses, branches, and other execution sites">
        <HoloPanel theme="mars" className="p-6 text-pearl-100">
          {error}
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  return (
    <SettingsSceneLayout
      title="Location Settings"
      subtitle="Manage warehouses, branches, and other locations"
      actions={
        <Button type="button" onClick={openNewLocation} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>New Location</span>
        </Button>
      }
    >
      <div className="space-y-6">
        <HoloPanel theme="space" className="space-y-6 border border-white/5">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="space-y-3">
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">Location Type</p>
              <div className="flex flex-wrap gap-2">
                {locationTypes.map((type) => {
                  const isActive = filterType === type.value;
                  return (
                    <Button
                      key={type.value}
                      type="button"
                      sheen={false}
                      variant={isActive ? 'primary' : 'secondary'}
                      onClick={() => setFilterType(type.value)}
                      className={`rounded-xl px-3 py-1.5 text-sm ${
                        isActive ? 'shadow-holo' : 'bg-white/5 text-pearl-300 hover:bg-white/10'
                      }`}
                    >
                      {type.label}
                    </Button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">Activation State</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: null as boolean | null, label: 'All' },
                  { value: true, label: 'Active' },
                  { value: false, label: 'Inactive' },
                ].map((option) => {
                  const isActive = filterActive === option.value;
                  return (
                    <Button
                      key={String(option.value ?? 'all')}
                      type="button"
                      sheen={false}
                      variant={isActive ? 'primary' : 'secondary'}
                      onClick={() => setFilterActive(option.value)}
                      className={`rounded-xl px-3 py-1.5 text-sm ${
                        isActive ? 'shadow-holo' : 'bg-white/5 text-pearl-300 hover:bg-white/10'
                      }`}
                    >
                      {option.label}
                    </Button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">Search</p>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <div className="relative flex-1">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-saturn-200/70" />
                  <input
                    type="text"
                    placeholder="Search locations"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-space-900/60 py-2.5 pl-10 pr-4 text-pearl-100 placeholder-pearl-500 transition focus:border-saturn-400/60 focus:outline-none"
                  />
                </div>
                <Button type="button" onClick={openNewLocation} className="flex items-center gap-2 sm:w-auto">
                  <PlusIcon className="h-4 w-4" />
                  <span>Add Location</span>
                </Button>
              </div>
            </div>
          </div>
        </HoloPanel>

        {filteredLocations.length === 0 ? (
          <HoloPanel theme="space" className="py-20 text-center text-pearl-200">
            {searchTerm ? 'No locations found matching your search' : 'No locations configured yet'}
          </HoloPanel>
        ) : (
          <div className="grid gap-4">
            {filteredLocations.map((location) => {
              const Icon = getLocationIcon(location.location_type);
              return (
                <HoloPanel
                  key={location.id}
                  theme="space"
                  elevated
                  className="flex flex-col gap-4 border border-white/5 lg:flex-row lg:items-start lg:justify-between"
                >
                  <div className="flex-1 space-y-5">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div className="flex flex-1 items-start gap-4">
                        <div className="rounded-2xl bg-gradient-to-br from-saturn-500/30 to-sun-500/20 p-3">
                          <Icon className="h-6 w-6 text-sun-300" />
                        </div>
                        <div className="space-y-3">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="text-lg font-heading text-pearl-50">{location.name}</h3>
                            {location.location_type && (
                              <VolumetricBadge status="active">{location.location_type}</VolumetricBadge>
                            )}
                            <VolumetricBadge status={location.is_active ? 'active' : 'failed'}>
                              {location.is_active ? 'Active' : 'Inactive'}
                            </VolumetricBadge>
                          </div>
                          <div className="flex items-start gap-2 text-sm text-pearl-300/90">
                            <MapPinIcon className="h-4 w-4 flex-shrink-0 text-saturn-200/70" />
                            <span>
                              {location.address_line1}
                              {location.address_line2 && `, ${location.address_line2}`}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-4 text-sm text-pearl-200 sm:grid-cols-2 lg:grid-cols-4">
                      {location.city && (
                        <div>
                          <p className="text-xs font-mono uppercase tracking-[0.25em] text-saturn-200/70">City</p>
                          <p className="text-base text-pearl-50">{location.city}</p>
                        </div>
                      )}
                      {location.state && (
                        <div>
                          <p className="text-xs font-mono uppercase tracking-[0.25em] text-saturn-200/70">State</p>
                          <p className="text-base text-pearl-50">{location.state}</p>
                        </div>
                      )}
                      {location.postal_code && (
                        <div>
                          <p className="text-xs font-mono uppercase tracking-[0.25em] text-saturn-200/70">Postal Code</p>
                          <p className="text-base text-pearl-50">{location.postal_code}</p>
                        </div>
                      )}
                      {location.country && (
                        <div>
                          <p className="text-xs font-mono uppercase tracking-[0.25em] text-saturn-200/70">Country</p>
                          <p className="text-base text-pearl-50">{location.country}</p>
                        </div>
                      )}
                    </div>

                    {location.google_place_id && (
                      <div className="flex flex-wrap items-center gap-2 text-xs text-saturn-200/70">
                        <GlobeAltIcon className="h-4 w-4" />
                        <span>Verified with Google Places</span>
                        {location.latitude && location.longitude && (
                          <span className="text-pearl-200">
                            • {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 self-end lg:self-start">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => setLocationModal({ open: true, data: location })}
                      className="px-3 py-2"
                      aria-label="Edit location"
                    >
                      <PencilIcon className="h-4 w-4 text-pearl-100" />
                    </Button>
                    <Button
                      type="button"
                      variant="danger"
                      onClick={() => handleDeleteLocation(location.id)}
                      className="px-3 py-2"
                      aria-label="Delete location"
                    >
                      <TrashIcon className="h-4 w-4 text-white" />
                    </Button>
                  </div>
                </HoloPanel>
              );
            })}
          </div>
        )}
      </div>

      <LocationModal
        isOpen={locationModal.open}
        onClose={() => setLocationModal({ open: false })}
        location={locationModal.data}
        onSuccess={loadLocations}
      />
    </SettingsSceneLayout>
  );
}
