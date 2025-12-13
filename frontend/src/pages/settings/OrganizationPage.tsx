/**
 * Organization Settings Page
 * Manage company details, GST, bank accounts, financial years, and document series
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/2040/Button';
import { HoloPanel } from '@/components/2040/HoloPanel';
import { MultiLayerTabs } from '@/components/2040/MultiLayerTabs';
import { VolumetricBadge } from '@/components/2040/VolumetricTable';
import { 
  BuildingOfficeIcon, 
  BanknotesIcon, 
  CalendarIcon, 
  DocumentTextIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import organizationService from '@/services/api/organizationService';
import { useToast } from '@/contexts/ToastContext';
import { 
  GSTModal, 
  BankAccountModal, 
  FinancialYearModal, 
  DocumentSeriesModal 
} from '@/components/settings/OrganizationModals';
import type { 
  Organization, 
  OrganizationGST, 
  OrganizationBankAccount,
  OrganizationFinancialYear,
  OrganizationDocumentSeries,
} from '@/types/settings';
import SettingsSceneLayout from './components/SettingsSceneLayout';

export default function OrganizationPage() {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<'company' | 'gst' | 'banks' | 'fy' | 'docs'>('company');
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [gstList, setGstList] = useState<OrganizationGST[]>([]);
  const [bankAccounts, setBankAccounts] = useState<OrganizationBankAccount[]>([]);
  const [financialYears, setFinancialYears] = useState<OrganizationFinancialYear[]>([]);
  const [documentSeries, setDocumentSeries] = useState<OrganizationDocumentSeries[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [gstModal, setGstModal] = useState<{ open: boolean; data?: OrganizationGST }>({ open: false });
  const [bankModal, setBankModal] = useState<{ open: boolean; data?: OrganizationBankAccount }>({ open: false });
  const [fyModal, setFyModal] = useState<{ open: boolean; data?: OrganizationFinancialYear }>({ open: false });
  const [docModal, setDocModal] = useState<{ open: boolean; data?: OrganizationDocumentSeries }>({ open: false });

  useEffect(() => {
    loadOrganizationData();
  }, []);

  const loadOrganizationData = async () => {
    try {
      setLoading(true);
      const orgs = await organizationService.listOrganizations();
      if (orgs.length > 0) {
        const org = orgs[0];
        setOrganization(org);
        
        // Load related data
        const [gst, banks, fy, docs] = await Promise.all([
          organizationService.listGST(org.id),
          organizationService.listBankAccounts(org.id),
          organizationService.listFinancialYears(org.id),
          organizationService.listDocumentSeries(org.id),
        ]);
        
        setGstList(gst);
        setBankAccounts(banks);
        setFinancialYears(fy);
        setDocumentSeries(docs);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load organization data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGST = async (id: string) => {
    if (!confirm('Are you sure you want to delete this GST detail?')) return;
    try {
      await organizationService.deleteGST(id);
      toast.success('GST deleted successfully');
      loadOrganizationData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete GST');
    }
  };

  const handleDeleteBank = async (id: string) => {
    if (!confirm('Are you sure you want to delete this bank account?')) return;
    try {
      await organizationService.deleteBankAccount(id);
      toast.success('Bank account deleted successfully');
      loadOrganizationData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete bank account');
    }
  };

  const handleDeleteFY = async (id: string) => {
    if (!confirm('Are you sure you want to delete this financial year?')) return;
    try {
      await organizationService.deleteFinancialYear(id);
      toast.success('Financial year deleted successfully');
      loadOrganizationData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete financial year');
    }
  };

  const handleDeleteDocSeries = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document series?')) return;
    try {
      await organizationService.deleteDocumentSeries(id);
      toast.success('Document series deleted successfully');
      loadOrganizationData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete document series');
    }
  };

  const tabs = [
    { id: 'company' as const, label: 'Company Details', icon: BuildingOfficeIcon },
    { id: 'gst' as const, label: 'GST', icon: DocumentTextIcon },
    { id: 'banks' as const, label: 'Bank Accounts', icon: BanknotesIcon },
    { id: 'fy' as const, label: 'Financial Years', icon: CalendarIcon },
    { id: 'docs' as const, label: 'Document Series', icon: DocumentTextIcon },
  ];

  if (loading) {
    return (
      <SettingsSceneLayout
        title="Organization Settings"
        subtitle="Manage your company information and configurations"
      >
        <HoloPanel theme="space" className="p-12 text-center text-pearl-200">
          Loading organization data...
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  if (error) {
    return (
      <SettingsSceneLayout
        title="Organization Settings"
        subtitle="Manage your company information and configurations"
      >
        <HoloPanel theme="mars" className="p-6 text-pearl-100">
          {error}
        </HoloPanel>
      </SettingsSceneLayout>
    );
  }

  return (
    <SettingsSceneLayout
      title="Organization Settings"
      subtitle="Manage your company information and configurations"
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
          {activeTab === 'company' && organization && <CompanyDetails organization={organization} />}

          {activeTab === 'gst' && (
            <GSTManagement
              gstList={gstList}
              onAdd={() => setGstModal({ open: true })}
              onEdit={(gst) => setGstModal({ open: true, data: gst })}
              onDelete={handleDeleteGST}
            />
          )}

          {activeTab === 'banks' && (
            <BankAccountsManagement
              accounts={bankAccounts}
              onAdd={() => setBankModal({ open: true })}
              onEdit={(account) => setBankModal({ open: true, data: account })}
              onDelete={handleDeleteBank}
            />
          )}

          {activeTab === 'fy' && (
            <FinancialYearsManagement
              years={financialYears}
              onAdd={() => setFyModal({ open: true })}
              onEdit={(year) => setFyModal({ open: true, data: year })}
              onDelete={handleDeleteFY}
            />
          )}

          {activeTab === 'docs' && (
            <DocumentSeriesManagement
              series={documentSeries}
              onAdd={() => setDocModal({ open: true })}
              onEdit={(doc) => setDocModal({ open: true, data: doc })}
              onDelete={handleDeleteDocSeries}
            />
          )}
        </div>
      </HoloPanel>

      {organization && (
        <>
          <GSTModal
            isOpen={gstModal.open}
            onClose={() => setGstModal({ open: false })}
            organizationId={organization.id}
            gst={gstModal.data}
            onSuccess={loadOrganizationData}
          />
          <BankAccountModal
            isOpen={bankModal.open}
            onClose={() => setBankModal({ open: false })}
            organizationId={organization.id}
            account={bankModal.data}
            onSuccess={loadOrganizationData}
          />
          <FinancialYearModal
            isOpen={fyModal.open}
            onClose={() => setFyModal({ open: false })}
            organizationId={organization.id}
            year={fyModal.data}
            onSuccess={loadOrganizationData}
          />
          <DocumentSeriesModal
            isOpen={docModal.open}
            onClose={() => setDocModal({ open: false })}
            organizationId={organization.id}
            series={docModal.data}
            onSuccess={loadOrganizationData}
          />
        </>
      )}
    </SettingsSceneLayout>
  );
}

// Component for Company Details tab
function CompanyDetails({ organization }: Readonly<{ organization: Organization }>) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Company Information</h2>
          <p className="text-sm text-pearl-300/80">
            Centralise statutory identity, contact coordinates, and compliance capabilities
          </p>
        </div>
        <Button type="button" className="flex items-center gap-2">
          <PencilIcon className="h-4 w-4" />
          <span>Edit Details</span>
        </Button>
      </HoloPanel>

      <HoloPanel theme="space" className="space-y-6 border border-white/5">
        <div className="grid gap-6 md:grid-cols-2">
          {[{
            label: 'Company Name',
            value: organization.name,
          },
          {
            label: 'Legal Name',
            value: organization.legal_name,
          },
          {
            label: 'PAN',
            value: organization.PAN,
          },
          {
            label: 'CIN',
            value: organization.CIN,
          },
          {
            label: 'Contact Email',
            value: organization.contact_email,
          },
          {
            label: 'Contact Phone',
            value: organization.contact_phone,
          }].map((field) => (
            <div key={field.label}>
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">{field.label}</p>
              <p className="mt-2 text-lg text-pearl-50">{field.value || 'N/A'}</p>
            </div>
          ))}

          <div className="md:col-span-2">
            <p className="text-xs font-mono uppercase tracking-[0.3em] text-saturn-200/70">Registered Address</p>
            <p className="mt-2 text-lg text-pearl-50">
              {organization.address_line1 || 'N/A'}
              {organization.address_line2 && `, ${organization.address_line2}`}
              {organization.city && `, ${organization.city}`}
              {organization.state && `, ${organization.state}`}
              {organization.pincode && ` - ${organization.pincode}`}
            </p>
          </div>
        </div>

        <div className="grid gap-4 border-t border-white/10 pt-6 sm:grid-cols-2 lg:grid-cols-4">
          {[{
            label: 'E-Invoice Required',
            active: organization.einvoice_required,
          },
          {
            label: 'FX Enabled',
            active: organization.fx_enabled,
          },
          {
            label: 'Auto Invoice',
            active: organization.auto_invoice,
          },
          {
            label: 'Auto Contract Number',
            active: organization.auto_contract_number,
          }].map((toggle) => (
            <div key={toggle.label} className="flex items-center gap-3">
              <VolumetricBadge status={toggle.active ? 'active' : 'failed'}>
                {toggle.active ? 'Enabled' : 'Disabled'}
              </VolumetricBadge>
              <span className="text-sm text-pearl-300/90">{toggle.label}</span>
            </div>
          ))}
        </div>
      </HoloPanel>
    </div>
  );
}

// Component for GST Management tab
function GSTManagement({ gstList, onAdd, onEdit, onDelete }: Readonly<{
  gstList: OrganizationGST[];
  onAdd: () => void;
  onEdit: (gst: OrganizationGST) => void;
  onDelete: (id: string) => void;
}>) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">GST Details</h2>
          <p className="text-sm text-pearl-300/80">Track registered GSTINs, billing addresses, and filing status</p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add GST</span>
        </Button>
      </HoloPanel>

      {gstList.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No GST details added yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {gstList.map((gst) => (
            <HoloPanel
              key={gst.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-heading text-pearl-50">{gst.gstin}</h3>
                  {gst.is_primary && <VolumetricBadge status="pending">Primary</VolumetricBadge>}
                  <VolumetricBadge status={gst.is_active ? 'active' : 'failed'}>
                    {gst.is_active ? 'Active' : 'Inactive'}
                  </VolumetricBadge>
                </div>
                <p className="text-sm text-pearl-300/80">{gst.legal_name}</p>
                <p className="text-sm text-pearl-200">{gst.address} • {gst.state}</p>
              </div>
              <div className="flex items-center justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(gst)}
                  className="px-3 py-2"
                  aria-label="Edit GST"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onDelete(gst.id)}
                  className="px-3 py-2"
                  aria-label="Delete GST"
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

// Component for Bank Accounts Management tab
function BankAccountsManagement({ accounts, onAdd, onEdit, onDelete }: Readonly<{
  accounts: OrganizationBankAccount[];
  onAdd: () => void;
  onEdit: (account: OrganizationBankAccount) => void;
  onDelete: (id: string) => void;
}>) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Bank Accounts</h2>
          <p className="text-sm text-pearl-300/80">
            Maintain verified banking rails for payouts, invoicing, and settlements
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Account</span>
        </Button>
      </HoloPanel>

      {accounts.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No bank accounts added yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {accounts.map((account) => (
            <HoloPanel
              key={account.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-heading text-pearl-50">{account.bank_name}</h3>
                  {account.is_primary && (
                    <VolumetricBadge status="pending">Primary</VolumetricBadge>
                  )}
                </div>
                <div className="text-sm text-pearl-300/80">
                  <p>{account.account_holder_name}</p>
                  <p className="font-mono text-pearl-200">{account.account_number}</p>
                </div>
                <div className="text-xs uppercase tracking-[0.25em] text-saturn-200/70">
                  IFSC {account.ifsc_code} • {account.branch_name}
                </div>
              </div>
              <div className="flex items-center justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(account)}
                  className="px-3 py-2"
                  aria-label="Edit bank account"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onDelete(account.id)}
                  className="px-3 py-2"
                  aria-label="Delete bank account"
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

// Component for Financial Years Management tab
function FinancialYearsManagement({ years, onAdd, onEdit, onDelete }: Readonly<{
  years: OrganizationFinancialYear[];
  onAdd: () => void;
  onEdit: (year: OrganizationFinancialYear) => void;
  onDelete: (id: string) => void;
}>) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Financial Years</h2>
          <p className="text-sm text-pearl-300/80">
            Configure fiscal periods for reporting, statutory filings, and close processes
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Financial Year</span>
        </Button>
      </HoloPanel>

      {years.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No financial years configured yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {years.map((fy) => (
            <HoloPanel
              key={fy.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-heading text-pearl-50">{fy.year_name}</h3>
                  {fy.is_current && (
                    <VolumetricBadge status="completed">Current</VolumetricBadge>
                  )}
                </div>
                <p className="text-sm text-pearl-300/80">
                  {new Date(fy.start_date).toLocaleDateString()} – {new Date(fy.end_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(fy)}
                  className="px-3 py-2"
                  aria-label="Edit financial year"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onDelete(fy.id)}
                  className="px-3 py-2"
                  aria-label="Delete financial year"
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

// Component for Document Series Management tab
function DocumentSeriesManagement({ series, onAdd, onEdit, onDelete }: Readonly<{
  series: OrganizationDocumentSeries[];
  onAdd: () => void;
  onEdit: (doc: OrganizationDocumentSeries) => void;
  onDelete: (id: string) => void;
}>) {
  return (
    <div className="space-y-6">
      <HoloPanel
        theme="space"
        className="flex flex-col gap-3 border border-white/5 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h2 className="text-xl font-heading text-pearl-50">Document Series</h2>
          <p className="text-sm text-pearl-300/80">
            Control numbering sequences for invoices, delivery challans, and trade contracts
          </p>
        </div>
        <Button type="button" onClick={onAdd} className="flex items-center gap-2">
          <PlusIcon className="h-4 w-4" />
          <span>Add Series</span>
        </Button>
      </HoloPanel>

      {series.length === 0 ? (
        <HoloPanel theme="space" className="py-14 text-center text-pearl-200">
          No document series configured yet
        </HoloPanel>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {series.map((doc) => (
            <HoloPanel
              key={doc.id}
              theme="space"
              elevated
              className="flex h-full flex-col gap-4 border border-white/5"
            >
              <div className="flex flex-1 flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-heading text-pearl-50">{doc.document_type}</h3>
                </div>
                <p className="text-sm text-pearl-300/80">
                  Format {doc.prefix}
                  {String(doc.current_number).padStart(doc.padding_length, '0')}
                  {doc.suffix || ''}
                </p>
                <div className="text-xs uppercase tracking-[0.25em] text-saturn-200/70">
                  Current {doc.current_number} • Padding {doc.padding_length} digits
                </div>
              </div>
              <div className="flex items-center justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => onEdit(doc)}
                  className="px-3 py-2"
                  aria-label="Edit document series"
                >
                  <PencilIcon className="h-4 w-4 text-pearl-100" />
                </Button>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onDelete(doc.id)}
                  className="px-3 py-2"
                  aria-label="Delete document series"
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
