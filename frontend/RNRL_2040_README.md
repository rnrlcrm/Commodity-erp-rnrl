# RNRL Global Commodity Platform – 2040 AI-Assisted Back Office

A futuristic, holographic volumetric operating system for enterprise commodity workflows. Built with React, TypeScript, Tailwind CSS 4.0, and Framer Motion.

## 🌟 Vision

This is not a flat dashboard—it's a **volumetric operating system** where every surface is holographic, translucent, and context-aware. AI is embedded inside every interaction to predict, suggest, explain, and automate across all modules.

## 🎨 Design Philosophy

- **Holographic Surfaces**: Translucent glass-morphism with depth layers, glow effects, and volumetric transforms
- **AI-First**: Every module has embedded AI insights, predictions, and automated suggestions
- **Real-time**: All data streams with sub-second updates via WebSocket
- **2040 Aesthetics**: No pure black backgrounds, neon glows, liquid buttons, and volumetric tables
- **Brand Palette**: Saturn (primary blue), Sun (golden accents), Mars (alert red), Pearl (neutral glass), Space (deep layers)

## 🏗️ Architecture

### Core Systems

1. **Holographic Design System** (`tailwind.config.2040.js`)
   - Custom color palette with glow variants
   - Volumetric shadow system
   - Glass-morphism utilities
   - 3D transform helpers

2. **AI Orchestration** (`hooks/useAIOrchestrator.ts`)
   - Background Web Worker for AI processing
   - Real-time predictions and suggestions
   - Automation triggers
   - Explainability interface

3. **Scene Management** (`store/sceneStore.ts`)
   - Zustand + IndexedDB persistence
   - Workspace scene memory
   - Camera angle and panel state
   - Motion preferences

4. **Realtime Engine** (`hooks/useRealtime.ts`)
   - Socket.io WebSocket connections
   - Channel subscriptions
   - Message streaming

### Module Architecture

Each back office module follows this pattern:

```
SceneComponent.tsx
├── HoloPanel (header)
├── Stats Overview (HoloCards)
├── VolumetricTable (data grid)
├── AI Predictions/Insights
└── AIInsightBar (floating suggestions)
```

## 📦 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── 2040/
│   │       ├── HoloPanel.tsx           # Base holographic surface
│   │       ├── VolumetricTable.tsx     # 3D floating table
│   │       ├── AIInsightBar.tsx        # AI suggestion stream
│   │       ├── CommandHalo.tsx         # Radial command palette
│   │       └── index.ts                # Component exports
│   ├── pages/
│   │   └── 2040/
│   │       ├── TradeDeskScene.tsx
│   │       ├── PartnerManagementScene.tsx
│   │       ├── DocumentIntelligenceScene.tsx
│   │       ├── SettingsScene.tsx
│   │       ├── UserManagementScene.tsx
│   │       ├── QualityScene.tsx
│   │       ├── LogisticsScene.tsx
│   │       ├── DeliveryScene.tsx
│   │       ├── AccountsScene.tsx
│   │       ├── DisputesScene.tsx
│   │       └── AuditScene.tsx
│   ├── layouts/
│   │   └── Layout2040.tsx              # Main holographic layout
│   ├── hooks/
│   │   ├── useAIOrchestrator.ts        # AI system integration
│   │   └── useRealtime.ts              # WebSocket streaming
│   ├── store/
│   │   └── sceneStore.ts               # Scene persistence
│   ├── workers/
│   │   └── aiOrchestrator.worker.ts    # Background AI processing
│   ├── types/
│   │   └── 2040.types.ts               # TypeScript definitions
│   └── routes/
│       └── 2040.routes.tsx             # Route configuration
├── tailwind.config.2040.js             # Holographic design tokens
└── RNRL_2040_COMPONENTS.md             # Component documentation
```

## 🚀 Getting Started

### Installation

```bash
cd frontend
npm install
# or
pnpm install
```

New dependencies added:
- `framer-motion` - Advanced animations and gestures
- `idb` - IndexedDB wrapper for scene persistence
- `@radix-ui/react-command` - Command palette primitives
- `@radix-ui/react-dialog` - Modal dialogs
- `three` - 3D rendering (optional for advanced effects)
- `@react-three/fiber` - React Three.js integration
- `@react-three/drei` - Three.js helpers

### Development

```bash
npm run dev
```

Navigate to: `http://localhost:3000/2040/trade-desk`

### Build

```bash
npm run build
```

## 🎯 Back Office Modules

### 1. Settings
- System configuration
- Integration management
- Security policies

### 2. Internal User Management
- User roles and permissions
- Activity monitoring
- Access control

### 3. Business Partner Management
- KYC verification workflow
- Credit limit management
- Risk scoring
- Partner lifecycle tracking

### 4. Trade Desk (Back Office Ops)
- Trade execution monitoring
- Reconciliation automation
- Position tracking
- Real-time market data

### 5. Quality Management
- AI-powered inspections
- Compliance reports
- Quality metrics dashboard
- Issue flagging and resolution

### 6. Logistics
- Shipment tracking
- Route optimization
- Carrier management
- Delivery predictions

### 7. Delivery Management
- Schedule coordination
- Delivery confirmations
- Exception handling
- Performance analytics

### 8. Accounts & Settlement
- Transaction processing
- Automated reconciliation
- Payment tracking
- Financial reporting

### 9. Dispute Management
- Case tracking
- Mediation workflows
- Resolution automation
- Evidence management

### 10. Audit Timeline Stream
- Real-time event log
- Compliance monitoring
- Activity timeline
- Audit trail export

### 11. Document Intelligence System
- AI-powered OCR
- Document classification
- Data extraction
- Confidence scoring

## 🤖 AI Integration

### AI Orchestrator

Each module connects to the AI orchestrator:

```tsx
const { aiState, isProcessing, acceptSuggestion, rejectSuggestion } = 
  useAIOrchestrator({
    module: 'trade-desk',
    context: { trades, selectedTrade },
    enablePredictions: true,
    enableSuggestions: true,
  });
```

### AI Features

- **Predictions**: Risk alerts, opportunity detection, trend analysis
- **Suggestions**: Action recommendations with confidence scores
- **Automations**: Background task execution
- **Insights**: Contextual analysis and explanations

### Web Worker

AI processing runs in background worker (`aiOrchestrator.worker.ts`) to prevent UI blocking.

## 🔄 Real-time Subscriptions

Each module subscribes to relevant channels:

```tsx
useRealtimeChannel('trade.ticks', (data) => {
  // Handle real-time trade updates
});

useRealtimeChannel('trade.executions', (data) => {
  // Handle execution confirmations
});
```

Channel naming pattern: `<module>.<topic>`

## ⌨️ Keyboard Shortcuts

- `⌘+Shift+Space` (Mac) / `Ctrl+Shift+Space` (Windows): Open Command Halo
- `⌘+K`: Quick search
- `⌘+Shift+A`: AI Assist
- `⌘+S`: Save scene
- `⌘+Shift+I`: Toggle AI insights
- `Escape`: Close modals/panels

## 🎨 Design Tokens

### Color Palette

```css
/* Saturn - Primary */
--saturn-500: #3366FF;
--saturn-glow: rgba(51, 102, 255, 0.4);

/* Sun - CTA */
--sun-500: #FFB800;
--sun-glow: rgba(255, 184, 0, 0.5);

/* Mars - Alerts */
--mars-500: #FF3B4A;
--mars-glow: rgba(255, 59, 74, 0.5);

/* Pearl - Neutral */
--pearl-500: #B8B8B8;
--pearl-glass: rgba(255, 255, 255, 0.08);

/* Space - Depth */
--space-500: #242B45;
--space-void: rgba(10, 15, 28, 0.95);
```

### Holographic Classes

```html
<!-- Base glass surface -->
<div class="hologlass rounded-holo shadow-holo">

<!-- Saturn-themed panel -->
<div class="hologlass-saturn rounded-holo-lg shadow-holo-strong">

<!-- Volumetric table row -->
<div class="volumetric-row transform-3d">

<!-- Glowing text -->
<h1 class="text-glow-saturn">
```

## ♿ Accessibility

### Motion Preferences

System respects user motion preferences:

```tsx
const { motionPreferences, setMotionPreferences } = useSceneStore();

// Toggle reduced motion
setMotionPreferences({ reducedMotion: true });

// Disable volumetric effects
setMotionPreferences({ disableVolumetric: true });

// Simplify glow effects
setMotionPreferences({ simplifyGlow: true });
```

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Focus indicators with holographic glow
- Command Halo for quick navigation
- Tab order follows visual hierarchy

### Screen Readers

- Semantic HTML structure
- ARIA labels on interactive components
- Status messages for real-time updates
- Descriptive button and link text

## 📊 Performance Optimization

### Code Splitting

Modules are lazy-loaded:

```tsx
const SettingsScene = React.lazy(() => 
  import('../pages/2040/SettingsScene')
);
```

### Web Workers

CPU-intensive AI processing runs in background:

```tsx
// aiOrchestrator.worker.ts
self.onmessage = (e) => {
  // Process AI tasks without blocking UI
};
```

### Device Degradation

Low-end devices automatically:
- Disable volumetric transforms
- Reduce animation complexity
- Simplify glow effects
- Lower backdrop blur intensity

## 🧪 Testing

```bash
# Run tests
npm test

# E2E tests
npm run test:e2e
```

## 📝 Development Guidelines

### Creating New Modules

1. Create scene component in `pages/2040/ModuleScene.tsx`
2. Add route in `routes/2040.routes.tsx`
3. Register in `BACKOFFICE_MODULES` array
4. Implement AI orchestrator integration
5. Add realtime channel subscriptions

### Component Best Practices

- Use `HoloPanel` for all surfaces
- Wrap data grids in `VolumetricTable`
- Include `AIInsightBar` for suggestions
- Implement keyboard shortcuts
- Add loading states
- Handle errors gracefully

## 🔧 Configuration

### Environment Variables

```env
VITE_WS_URL=ws://localhost:8000
VITE_API_URL=http://localhost:8000
VITE_AI_ENDPOINT=http://localhost:8000/ai
```

### Tailwind Config

Use the 2040 config for holographic styles:

```js
// tailwind.config.js
import config2040 from './tailwind.config.2040.js';
export default config2040;
```

## 📚 Documentation

- [Component Documentation](./RNRL_2040_COMPONENTS.md)
- [API Reference](../docs/api/)
- [Architecture Guide](../docs/architecture/)

## 🤝 Contributing

1. Follow volumetric design system
2. Include AI integration in new modules
3. Add keyboard shortcuts for common actions
4. Test with reduced motion enabled
5. Document new components

## 📄 License

Proprietary - RNRL Global Commodity Platform

---

**Built with ♥ by RNRL Engineering Team**

*"The future of commodity trading is holographic."*
