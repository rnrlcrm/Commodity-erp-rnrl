# 2040 Architecture - Quick Reference Guide

## 🚀 How to Navigate the System

### Access URLs

```
Dashboard:           /backoffice
Clearing:           /backoffice/clearing
Risk Monitoring:    /backoffice/risk
Audit Trail:        /backoffice/audit
User Management:    /backoffice/users
Accounts:           /backoffice/accounts
```

### Top Navigation Systems

| Button | Destination | Key Features |
|--------|-------------|--------------|
| Trading | /backoffice/trade-desk | Trading operations |
| Clearing | /backoffice/clearing | Settlement management |
| Risk | /backoffice/risk | Live risk heat map |
| Accounts | /backoffice/accounts | Financial ledger |
| Audit | /backoffice/audit | Compliance trail |

### Quantum Hub Toggle

**Location:** Top navigation bar (sparkles icon)
**Features:**
- Real-time quantum field visualization
- Anomaly detection with neural-pulse alerts
- AI predictions with confidence scores
- System status monitoring

---

## 🎨 Using 2040 Components

### Button2040

```tsx
import { Button2040 } from '@/components/2040/InteractionComponents';

<Button2040 variant="primary" size="lg" onClick={handleClick}>
  Click Me
</Button2040>

// Variants: primary, secondary, danger, success
// Sizes: sm (40px), md (50px), lg (60px), xl (70px)
```

### MagneticTabs

```tsx
import { MagneticTabs } from '@/components/2040/InteractionComponents';

<MagneticTabs
  tabs={[
    { id: 'tab1', label: 'Overview', count: 5 },
    { id: 'tab2', label: 'Details' }
  ]}
  activeTab={activeTab}
  onChange={setActiveTab}
/>
```

### AdaptiveGraph

```tsx
import { AdaptiveGraph } from '@/components/2040/InteractionComponents';

<AdaptiveGraph
  data={[10, 25, 40, 35, 60, 45, 70]}
  title="Market Trend"
/>
```

### SmartDataGrid

```tsx
import { SmartDataGrid } from '@/components/2040/InteractionComponents';

<SmartDataGrid
  data={[
    { id: '1', client: 'ABC Corp', amount: '₹2.8L', status: 'Active', details: '...' }
  ]}
/>
```

---

## 🎯 Animation Classes

### Apply Motion Effects

```html
<!-- Neural pulse for alerts -->
<div className="animate-neural-pulse">Critical Alert</div>

<!-- Pulse ring for status indicators -->
<div className="animate-pulse-ring">Live</div>

<!-- Wave ripple for AI loading -->
<div className="animate-wave-ripple">Processing</div>

<!-- Soft bloom on hover -->
<button className="hover-soft-bloom">Hover Me</button>

<!-- Fade in on mount -->
<div className="animate-fadeIn">Content</div>
```

### 120ms Transitions

```html
<!-- All transitions use 120ms standard -->
<div className="transition-all duration-120">Smooth</div>
```

---

## 🎨 Typography Classes

```html
<!-- Headings (Inter) -->
<h1 className="font-heading font-bold">Title</h1>

<!-- Body text (IBM Plex Sans) - default -->
<p className="font-body">Regular text</p>

<!-- Numbers & Data (JetBrains Mono) -->
<span className="font-mono">₹12,345.67</span>
```

---

## 🏗️ Module Styling Guidelines

### Clearing & Settlement
**Theme:** Calm minimal (white + navy)
```tsx
// Clean white cards
<div className="bg-white border-2 border-saturn-100 rounded-xl p-6">
  ...
</div>

// Monospace for numbers
<span className="font-mono font-bold">₹28.47L</span>
```

### Risk Monitoring
**Theme:** Quantum heat-mapping + AI glow
```tsx
// Dark gradient background
<div className="bg-gradient-to-b from-space-900 to-space-800">
  ...
</div>

// Neural pulse for critical
<div className="animate-neural-pulse">
  <div className="w-3 h-3 bg-mars-500 rounded-full" />
</div>
```

### Compliance/Audit
**Theme:** Paper-like ledger
```tsx
// Amber sepia tones
<div className="bg-gradient-to-b from-amber-50 to-white border-2 border-amber-200/50">
  ...
</div>

// Georgia serif for authenticity
<p style={{ fontFamily: 'Georgia, serif' }}>Audit entry</p>
```

### User Management
**Theme:** Card grid + holograms
```tsx
// Holographic avatar
<div className="relative">
  <div className="absolute -inset-2 bg-gradient-to-br from-sun-400 via-saturn-500 to-mars-500 rounded-full opacity-20 blur-lg" />
  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-sun-400 via-saturn-500 to-mars-500">
    <span>RK</span>
  </div>
</div>
```

### Accounts & Finance
**Theme:** Ledger-centric neutral
```tsx
// Professional number formatting
<span className="font-mono font-bold text-space-900">
  {formatAmount(amount)}
</span>

// Debit/Credit color coding
<span className="text-mars-700">Debit</span>
<span className="text-emerald-700">Credit</span>
```

---

## 🎨 Color Palette Reference

```tsx
// Primary system colors
saturn-500   // Deep blue (primary)
sun-500      // Orange/gold (accent)
mars-500     // Red (danger/alerts)
emerald-500  // Green (success)
space-900    // Dark background

// Neutral tones
pearl-50     // Light background
pearl-100    // Subtle borders
space-900    // Dark text
saturn-600   // Medium text
```

---

## 🔧 Common Patterns

### Card with Hover Effect
```tsx
<div className="bg-white border-2 border-saturn-100 rounded-xl p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-120 hover-soft-bloom">
  Content
</div>
```

### Status Badge
```tsx
<span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
  ACTIVE
</span>
```

### Gradient Header
```tsx
<div className="bg-gradient-to-r from-space-900 via-space-800 to-space-900 border-b border-saturn-700/30 p-6">
  <h1 className="text-white font-heading font-bold">Title</h1>
</div>
```

### Data Table Row
```tsx
<tr className="hover:bg-saturn-50/20 transition-colors duration-120">
  <td className="px-6 py-4 font-mono text-sm">Data</td>
</tr>
```

---

## 🚨 Important Notes

### Performance
- Canvas animations run at 60fps using `requestAnimationFrame`
- All transitions use GPU-accelerated properties
- 120ms timing provides instant feedback without lag

### Accessibility
- High contrast ratios in all modules
- Monospace fonts for number clarity
- Clear visual hierarchy
- Hover states for all interactive elements

### Responsiveness
- Grid layouts adapt to screen size
- Sidebar collapses on smaller screens
- Touch-friendly hit zones (min 40px)

---

## 📱 Responsive Breakpoints

```css
sm:  640px  /* Small tablets */
md:  768px  /* Tablets */
lg:  1024px /* Laptops */
xl:  1280px /* Desktops */
```

---

## 🎯 Best Practices

1. **Always use font-mono for numbers:** Financial data, IDs, timestamps
2. **Apply hover-soft-bloom to interactive cards:** Subtle feedback
3. **Use neural-pulse for critical alerts:** High attention indicators
4. **Maintain 120ms transitions:** Consistent feel across app
5. **Follow module-specific color schemes:** Avoid mixing themes

---

## 🔗 File Locations

```
Components:     /src/components/2040/
Layouts:        /src/layouts/
Pages:          /src/pages/backoffice/
Styles:         /src/index.css
Config:         /tailwind.config.js
Routes:         /src/App.tsx
```

---

## 💡 Tips & Tricks

### Quick Navigation
- Use top nav for system-level switching
- Sidebar for module navigation
- Quantum Hub toggle for AI insights

### Customization
- Modify animation timing in `index.css`
- Adjust colors in `tailwind.config.js`
- Extend components in `InteractionComponents.tsx`

### Debugging
- Check browser console for React warnings
- Verify import paths use `@/` alias
- Ensure all transitions use `duration-120`

---

**Last Updated:** December 5, 2024
**Version:** 2.0.40
**Status:** Production Ready ✅
