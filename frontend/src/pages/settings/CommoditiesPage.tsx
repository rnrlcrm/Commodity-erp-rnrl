/**
 * Commodities Settings Page
 * Manage commodities, varieties, parameters, and trading terms
 */

import { useState, useEffect } from 'react';
import {
  CubeIcon,
  SparklesIcon,
  Cog6ToothIcon,
  DocumentDuplicateIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { MultiLayerTabs } from '@/components/2040/MultiLayerTabs';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import { useToast } from '@/contexts/ToastContext';
import {
  CommodityModal,
  TradeTypeModal,
  BargainTypeModal,
  TermModal,
  PaymentTermModal,
} from '@/components/settings/CommodityModals';
import commodityService from '@/services/api/commodityService';
import SettingsSceneLayout from './components/SettingsSceneLayout';
import type {
  Commodity,
  TradeType,
  BargainType,
  PassingTerm,
  WeightmentTerm,
  DeliveryTerm,
  PaymentTerm,
} from '@/types/settings';

export default function CommoditiesPage() {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<'commodities' | 'trade-types' | 'bargain-types' | 'terms'>('commodities');
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [tradeTypes, setTradeTypes] = useState<TradeType[]>([]);
  const [bargainTypes, setBargainTypes] = useState<BargainType[]>([]);
  const [passingTerms, setPassingTerms] = useState<PassingTerm[]>([]);
  const [weightmentTerms, setWeightmentTerms] = useState<WeightmentTerm[]>([]);
  const [deliveryTerms, setDeliveryTerms] = useState<DeliveryTerm[]>([]);
  const [paymentTerms, setPaymentTerms] = useState<PaymentTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [commodityModal, setCommodityModal] = useState<{ open: boolean; data?: Commodity }>({ open: false });
  const [tradeTypeModal, setTradeTypeModal] = useState<{ open: boolean; data?: TradeType }>({ open: false });
  const [bargainTypeModal, setBargainTypeModal] = useState<{ open: boolean; data?: BargainType }>({ open: false });
  const [passingTermModal, setPassingTermModal] = useState<{ open: boolean; data?: PassingTerm }>({ open: false });
  const [weightmentTermModal, setWeightmentTermModal] = useState<{ open: boolean; data?: WeightmentTerm }>({ open: false });
  const [deliveryTermModal, setDeliveryTermModal] = useState<{ open: boolean; data?: DeliveryTerm }>({ open: false });
  const [paymentTermModal, setPaymentTermModal] = useState<{ open: boolean; data?: PaymentTerm }>({ open: false });

  useEffect(() => {
    loadCommodityData();
  }, []);

  const loadCommodityData = async () => {
    try {
      setLoading(true);
      const [
        comms,
        trade,
        bargain,
        passing,
        weightment,
        delivery,
        payment,
      ] = await Promise.all([
        commodityService.listCommodities(),
        commodityService.listTradeTypes(),
        commodityService.listBargainTypes(),
        commodityService.listPassingTerms(),
        commodityService.listWeightmentTerms(),
        commodityService.listDeliveryTerms(),
        commodityService.listPaymentTerms(),
      ]);

      setCommodities(comms);
      setTradeTypes(trade);
      setBargainTypes(bargain);
      setPassingTerms(passing);
      setWeightmentTerms(weightment);
      setDeliveryTerms(delivery);
      setPaymentTerms(payment);
    } catch (err: any) {
      setError(err.message || 'Failed to load commodity data');
    } finally {
      setLoading(false);
    }
  };

  // Delete handlers
  const handleDeleteCommodity = async (id: string) => {
    if (!confirm('Are you sure you want to delete this commodity?')) return;
    try {
      await commodityService.deleteCommodity(id);
      toast.success('Commodity deleted successfully');
      loadCommodityData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete commodity');
    }
  };

  const tabs = [
    { id: 'commodities' as const, label: 'Commodities', icon: CubeIcon },
    { id: 'trade-types' as const, label: 'Trade Types', icon: Cog6ToothIcon },
    { id: 'bargain-types' as const, label: 'Bargain Types', icon: SparklesIcon },
    { id: 'terms' as const, label: 'Trading Terms', icon: DocumentDuplicateIcon },
  ];

  if (loading) {
    return (
      <SettingsSceneLayout
        title="Commodity Settings"
        subtitle="Manage commodities, trading types, and trading terms"
      >
        <HoloPanel theme="space" className="p-12 text-center text-pearl-200">
          Loading commodity data...
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  if (error) {
    return (
      <SettingsSceneLayout
        title="Commodity Settings"
        subtitle="Manage commodities, trading types, and trading terms"
      >
        <HoloPanel theme="mars" className="p-6 text-pearl-100">
          {error}
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  return (
    <SettingsSceneLayout
      title="Commodity Settings"
      subtitle="Manage commodities, trading types, and trading terms"
    >
      <HoloPanel theme="space" glow className="overflow-hidden p-0">
        <div className="border-b border-white/10 px-4 py-5 md:px-6">
          <MultiLayerTabs
            tabs={tabs.map((tab) => {
              const Icon = tab.icon;
              return {
                key: tab.id,
                label: (
                  <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.12em] text-pearl-100">
                    <Icon className="h-4 w-4 text-sun-300" />
                    <span>{tab.label}</span>
                  </div>
                ),
              };
            })}
            activeKey={activeTab}
            onChange={(key) => setActiveTab(key as typeof activeTab)}
          />
        </div>

        <div className="space-y-8 px-4 py-6 md:px-6">
          {activeTab === 'commodities' && (
            <CommoditiesList
              commodities={commodities}
              onAdd={() => setCommodityModal({ open: true })}
              onEdit={(commodity) => setCommodityModal({ open: true, data: commodity })}
              onDelete={handleDeleteCommodity}
            />
          )}

          {activeTab === 'trade-types' && (
            <TradeTypesList
              tradeTypes={tradeTypes}
              onAdd={() => setTradeTypeModal({ open: true })}
              onEdit={(type) => setTradeTypeModal({ open: true, data: type })}
            />
          )}

          {activeTab === 'bargain-types' && (
            <BargainTypesList
              bargainTypes={bargainTypes}
              onAdd={() => setBargainTypeModal({ open: true })}
              onEdit={(type) => setBargainTypeModal({ open: true, data: type })}
            />
          )}

          {activeTab === 'terms' && (
            <TradingTerms
              passingTerms={passingTerms}
              weightmentTerms={weightmentTerms}
              deliveryTerms={deliveryTerms}
              paymentTerms={paymentTerms}
              onAddPassing={() => setPassingTermModal({ open: true })}
              onEditPassing={(term) => setPassingTermModal({ open: true, data: term })}
              onAddWeightment={() => setWeightmentTermModal({ open: true })}
              onEditWeightment={(term) => setWeightmentTermModal({ open: true, data: term })}
              onAddDelivery={() => setDeliveryTermModal({ open: true })}
              onEditDelivery={(term) => setDeliveryTermModal({ open: true, data: term })}
              onAddPayment={() => setPaymentTermModal({ open: true })}
              onEditPayment={(term) => setPaymentTermModal({ open: true, data: term })}
            />
          )}
        </div>
      </HoloPanel>

      <CommodityModal
        isOpen={commodityModal.open}
        onClose={() => setCommodityModal({ open: false })}
        commodity={commodityModal.data}
        onSuccess={loadCommodityData}
      />
      <TradeTypeModal
        isOpen={tradeTypeModal.open}
        onClose={() => setTradeTypeModal({ open: false })}
        tradeType={tradeTypeModal.data}
        onSuccess={loadCommodityData}
      />
      <BargainTypeModal
        isOpen={bargainTypeModal.open}
        onClose={() => setBargainTypeModal({ open: false })}
        bargainType={bargainTypeModal.data}
        onSuccess={loadCommodityData}
      />
      <TermModal
        isOpen={passingTermModal.open}
        onClose={() => setPassingTermModal({ open: false })}
        term={passingTermModal.data}
        termType="passing"
        onSuccess={loadCommodityData}
      />
      <TermModal
        isOpen={weightmentTermModal.open}
        onClose={() => setWeightmentTermModal({ open: false })}
        term={weightmentTermModal.data}
        termType="weightment"
        onSuccess={loadCommodityData}
      />
      <TermModal
        isOpen={deliveryTermModal.open}
        onClose={() => setDeliveryTermModal({ open: false })}
        term={deliveryTermModal.data}
        termType="delivery"
        onSuccess={loadCommodityData}
      />
      <PaymentTermModal
        isOpen={paymentTermModal.open}
        onClose={() => setPaymentTermModal({ open: false })}
        paymentTerm={paymentTermModal.data}
        onSuccess={loadCommodityData}
      />
    </SettingsSceneLayout>
  );
}

// Component for Commodities List
function CommoditiesList({
  commodities,
  onAdd,
  onEdit,
  onDelete,
}: {
  commodities: Commodity[];
  onAdd: () => void;
  onEdit: (commodity: Commodity) => void;
  onDelete: (id: string) => void;
}) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCommodities = commodities.filter((commodity) =>
    commodity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    commodity.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const emptyStateMessage = searchTerm
    ? 'No commodities found matching your search'
    : 'No commodities configured yet';

  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-4 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Commodities Catalog</h2>
          <p className="text-sm text-pearl-300/80">
            Curate the tradable commodities and maintain their trading attributes
          </p>
        </div>
        <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row md:items-center">
          <div className="relative md:w-72">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-saturn-200/70" />
            <input
              type="text"
              placeholder="Search commodities"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-space-900/60 py-2.5 pl-10 pr-4 text-pearl-100 placeholder-pearl-500 shadow-[0_0_20px_rgba(59,130,246,0.12)] transition-colors focus:border-saturn-400/60 focus:outline-none"
            />
          </div>
          <Button type="button" onClick={onAdd} className="flex items-center gap-2">
            <PlusIcon className="h-4 w-4" />
            <span>Add Commodity</span>
          </Button>
        </div>
      </HoloPanel>

      {filteredCommodities.length === 0 ? (
        <HoloPanel theme="space" className="py-16 text-center text-pearl-200">
          {emptyStateMessage}
        </HoloPanel>
      ) : (
        <div className="grid gap-4">
          {filteredCommodities.map((commodity) => (
            <HoloPanel
              key={commodity.id}
              theme="space"
              elevated
              className="flex flex-col gap-4 border border-white/5 lg:flex-row lg:items-start lg:justify-between"
            >
              <div className="flex-1 space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-heading text-pearl-50">{commodity.name}</h3>
                  <VolumetricBadge status="active">{commodity.category}</VolumetricBadge>
                  {!commodity.is_active && <VolumetricBadge status="failed">Inactive</VolumetricBadge>}
                </div>

                <div className="grid gap-4 text-sm text-pearl-200 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-pearl-400/70">HSN</p>
                    <p className="text-base text-pearl-100">{commodity.hsn_code || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-pearl-400/70">GST</p>
                    <p className="text-base text-pearl-100">
                      {commodity.gst_rate ? `${commodity.gst_rate}%` : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-pearl-400/70">Base Unit</p>
                    <p className="text-base text-pearl-100">{commodity.base_unit}</p>
                  </div>
                  <div>
                    <p className="text-xs font-mono uppercase tracking-[0.2em] text-pearl-400/70">Trade Unit</p>
                    <p className="text-base text-pearl-100">{commodity.trade_unit || 'N/A'}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end lg:self-start">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(commodity)}
                  className="px-3 py-2"
                  aria-label="Edit commodity"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onDelete(commodity.id)}
                  className="px-3 py-2"
                  aria-label="Delete commodity"
                >
                  <TrashIcon className="h-4 w-4 text-white" />
                </Button>
              </div>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}

// Component for Trade Types List
function TradeTypesList({
  tradeTypes,
  onAdd,
  onEdit,
}: {
  tradeTypes: TradeType[];
  onAdd: () => void;
  onEdit: (type: TradeType) => void;
}) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Trade Archetypes</h2>
          <p className="text-sm text-pearl-300/80">
            Configure the primary trading behaviours supported by the platform
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Trade Type</span>
        </Button>
      </HoloPanel>

      {tradeTypes.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No trade types configured yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {tradeTypes.map((type) => (
            <HoloPanel
              key={type.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-heading text-pearl-50">{type.name}</h3>
                    <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/60">
                      {type.id}
                    </p>
                  </div>
                  <VolumetricBadge status={type.is_active ? 'active' : 'failed'}>
                    {type.is_active ? 'Active' : 'Inactive'}
                  </VolumetricBadge>
                </div>

                {type.description && (
                  <p className="text-sm text-pearl-300/80">{type.description}</p>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-pearl-400">
                <span>
                  Created{' '}
                  <span className="font-semibold text-pearl-100">
                    {new Date(type.created_at).toLocaleDateString()}
                  </span>
                </span>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(type)}
                  className="px-3 py-1.5"
                  aria-label="Edit trade type"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
              </div>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}

// Component for Bargain Types List
function BargainTypesList({
  bargainTypes,
  onAdd,
  onEdit,
}: {
  bargainTypes: BargainType[];
  onAdd: () => void;
  onEdit: (type: BargainType) => void;
}) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Negotiation Playbooks</h2>
          <p className="text-sm text-pearl-300/80">
            Define the bargaining paradigms available to trade desks and brokers
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Bargain Type</span>
        </Button>
      </HoloPanel>

      {bargainTypes.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No bargain types configured yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {bargainTypes.map((type) => (
            <HoloPanel
              key={type.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-lg font-heading text-pearl-50">{type.name}</h3>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => onEdit(type)}
                    className="px-3 py-1.5"
                    aria-label="Edit bargain type"
                  >
                    <PencilIcon className="h-4 w-4 text-pearl-100" />
                  </Button>
                </div>
                {type.description && (
                  <p className="text-sm text-pearl-300/80">{type.description}</p>
                )}
              </div>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}

// Component for Trading Terms
function TradingTerms({
  passingTerms,
  weightmentTerms,
  deliveryTerms,
  paymentTerms,
  onAddPassing,
  onEditPassing,
  onAddWeightment,
  onEditWeightment,
  onAddDelivery,
  onEditDelivery,
  onAddPayment,
  onEditPayment,
}: {
  passingTerms: PassingTerm[];
  weightmentTerms: WeightmentTerm[];
  deliveryTerms: DeliveryTerm[];
  paymentTerms: PaymentTerm[];
  onAddPassing: () => void;
  onEditPassing: (term: PassingTerm) => void;
  onAddWeightment: () => void;
  onEditWeightment: (term: WeightmentTerm) => void;
  onAddDelivery: () => void;
  onEditDelivery: (term: DeliveryTerm) => void;
  onAddPayment: () => void;
  onEditPayment: (term: PaymentTerm) => void;
}) {
  const [activeTermTab, setActiveTermTab] =
    useState<'passing' | 'weightment' | 'delivery' | 'payment'>('passing');

  const termTabs = [
    {
      id: 'passing' as const,
      label: 'Passing Terms',
      description: 'Define the acceptance thresholds and quality tolerances for incoming lots.',
    },
    {
      id: 'weightment' as const,
      label: 'Weightment Terms',
      description: 'Govern the weighbridge, tare, and measurement protocols across facilities.',
    },
    {
      id: 'delivery' as const,
      label: 'Delivery Terms',
      description: 'Detail logistics, dispatch, and receiving obligations for each trade.',
    },
    {
      id: 'payment' as const,
      label: 'Payment Terms',
      description: 'Set credit periods, instalment structures, and settlement commitments.',
    },
  ];

  const activeMeta = termTabs.find((tab) => tab.id === activeTermTab) ?? termTabs[0];

  return (
    <div className="space-y-6">
      <HoloPanel theme="space" className="space-y-4 border border-white/5">
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Trading Terms Matrix</h2>
          <p className="text-sm text-pearl-300/80">{activeMeta.description}</p>
        </div>
        <MultiLayerTabs
          tabs={termTabs.map((tab) => ({ key: tab.id, label: tab.label }))}
          activeKey={activeTermTab}
          onChange={(key) => setActiveTermTab(key as typeof activeTermTab)}
        />
      </HoloPanel>

      {activeTermTab === 'passing' && (
        <TermsList terms={passingTerms} type="Passing" onAdd={onAddPassing} onEdit={onEditPassing} />
      )}
      {activeTermTab === 'weightment' && (
        <TermsList
          terms={weightmentTerms}
          type="Weightment"
          onAdd={onAddWeightment}
          onEdit={onEditWeightment}
        />
      )}
      {activeTermTab === 'delivery' && (
        <TermsList terms={deliveryTerms} type="Delivery" onAdd={onAddDelivery} onEdit={onEditDelivery} />
      )}
      {activeTermTab === 'payment' && (
        <PaymentTermsList terms={paymentTerms} onAdd={onAddPayment} onEdit={onEditPayment} />
      )}
    </div>
  );
}

function TermsList({
  terms,
  type,
  onAdd,
  onEdit,
}: {
  terms: any[];
  type: string;
  onAdd: () => void;
  onEdit: (term: any) => void;
}) {
  const emptyCopy = `No ${type.toLowerCase()} terms configured yet`;

  return (
    <div className="space-y-4">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h3 className="text-lg font-heading text-pearl-50">{type} Terms</h3>
          <p className="text-sm text-pearl-300/80">
            Curate {type.toLowerCase()} policies that align with organisational guardrails
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add {type} Term</span>
        </Button>
      </HoloPanel>

      {terms.length === 0 ? (
        <HoloPanel theme="space" className="py-12 text-center text-pearl-200">
          {emptyCopy}
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {terms.map((term) => (
            <HoloPanel
              key={term.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-3 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-base font-heading text-pearl-50">{term.name}</h4>
                    {term.reference_code && (
                      <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/60">
                        {term.reference_code}
                      </p>
                    )}
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => onEdit(term)}
                    className="px-3 py-1.5"
                    aria-label={`Edit ${type.toLowerCase()} term`}
                  >
                    <PencilIcon className="h-4 w-4 text-pearl-100" />
                  </Button>
                </div>
                {term.description && (
                  <p className="text-sm text-pearl-300/80">{term.description}</p>
                )}
              </div>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}

function PaymentTermsList({
  terms,
  onAdd,
  onEdit,
}: {
  terms: PaymentTerm[];
  onAdd: () => void;
  onEdit: (term: PaymentTerm) => void;
}) {
  const emptyCopy = 'No payment terms configured yet';

  return (
    <div className="space-y-4">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h3 className="text-lg font-heading text-pearl-50">Payment Terms</h3>
          <p className="text-sm text-pearl-300/80">
            Define credit exposure, cadence, and downstream settlement requirements
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Payment Term</span>
        </Button>
      </HoloPanel>

      {terms.length === 0 ? (
        <HoloPanel theme="space" className="py-12 text-center text-pearl-200">
          {emptyCopy}
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {terms.map((term) => (
            <HoloPanel
              key={term.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-3 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-base font-heading text-pearl-50">{term.name}</h4>
                    {term.description && (
                      <p className="text-sm text-pearl-300/80">{term.description}</p>
                    )}
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => onEdit(term)}
                    className="px-3 py-1.5"
                    aria-label="Edit payment term"
                  >
                    <PencilIcon className="h-4 w-4 text-pearl-100" />
                  </Button>
                </div>
                {term.days !== null && term.days !== undefined && (
                  <VolumetricBadge status="pending">{term.days} days</VolumetricBadge>
                )}
              </div>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}
