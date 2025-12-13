// RNRL 2040 Holographic Back Office - Component Documentation

## Component Library

### Core Components

#### HoloPanel
Volumetric glass-morphism panel with depth and glow effects.

**Props:**
- `theme`: 'saturn' | 'sun' | 'mars' | 'pearl' | 'space'
- `intensity`: 'subtle' | 'normal' | 'strong'
- `glow`: boolean - Enable edge glow
- `elevated`: boolean - Enable 3D hover effects

**Usage:**
```tsx
<HoloPanel theme="saturn" intensity="strong" glow elevated>
  <h1>Content</h1>
</HoloPanel>
```

#### VolumetricTable
Floating table rows with curvature and volumetric transforms.

**Features:**
- Animated row entrance/exit
- Hover effects with 3D translation
- Real-time data streaming support
- Customizable column rendering

**Usage:**
```tsx
<VolumetricTable
  data={items}
  columns={[
    { key: 'id', label: 'ID', width: '100px' },
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status', render: (v) => <Badge>{v}</Badge> }
  ]}
  keyExtractor={(row) => row.id}
  onRowClick={(row) => console.log(row)}
  theme="saturn"
/>
```

#### AIInsightBar
Streaming AI suggestions with acceptance/rejection UX.

**Features:**
- Real-time AI prediction display
- Expandable suggestion cards
- Confidence scoring
- Accept/reject actions
- Explainability snippets

**Usage:**
```tsx
<AIInsightBar
  module="trade-desk"
  context={{ trades, selectedTrade }}
/>
```

#### CommandHalo
Omnipresent radial command palette.

**Activation:**
- Keyboard: `⌘+Shift+Space` or `Ctrl+Shift+Space`
- Programmatic: `useCommandHalo()` hook

**Features:**
- Fuzzy search across all commands
- Keyboard navigation
- Module quick access
- AI action triggers
- Scene management

**Usage:**
```tsx
const commandHalo = useCommandHalo();

<CommandHalo
  isOpen={commandHalo.isOpen}
  onClose={commandHalo.close}
/>
```

### Design Tokens

#### Tailwind Classes

**Holographic Glass:**
- `.hologlass` - Base holographic glass surface
- `.hologlass-strong` - Higher opacity glass
- `.hologlass-saturn` - Saturn-themed glow
- `.hologlass-sun` - Sun-themed glow
- `.hologlass-pearl` - Neutral pearl glass

**Text Glow:**
- `.text-glow-saturn` - Saturn blue glow
- `.text-glow-sun` - Golden sun glow

**Volumetric Effects:**
- `.transform-3d` - Enable 3D transforms
- `.volumetric-float` - Subtle Z-axis translation
- `.volumetric-hover` - Interactive 3D hover

**Shadows:**
- `.shadow-holo` - Holographic shadow with glow
- `.shadow-holo-strong` - Stronger glow
- `.shadow-depth-1/2/3` - Layered depth shadows

#### Color Palette

**Saturn (Primary):**
- `saturn-500` - #3366FF
- `saturn-glow` - rgba(51, 102, 255, 0.4)

**Sun (CTA):**
- `sun-500` - #FFB800
- `sun-glow` - rgba(255, 184, 0, 0.5)

**Mars (Alerts):**
- `mars-500` - #FF3B4A
- `mars-glow` - rgba(255, 59, 74, 0.5)

**Pearl (Neutral):**
- `pearl-500` - #B8B8B8
- `pearl-glass` - rgba(255, 255, 255, 0.08)

**Space (Depth):**
- `space-500` - #242B45
- `space-void` - rgba(10, 15, 28, 0.95)

### Hooks

#### useAIOrchestrator
```tsx
const {
  aiState,
  isProcessing,
  acceptSuggestion,
  rejectSuggestion,
  triggerAutomation,
  requestInsight,
} = useAIOrchestrator({
  module: 'trade-desk',
  context: { trades },
  enablePredictions: true,
  enableSuggestions: true,
});
```

#### useRealtime
```tsx
const { isConnected, subscribe, send } = useRealtime({
  channels: ['trade.ticks', 'trade.executions'],
  onMessage: (channel, data) => {
    console.log(channel, data);
  },
});
```

#### useSceneStore
```tsx
const { 
  currentScene,
  savedScenes,
  motionPreferences,
  saveScene,
  loadScene 
} = useSceneStore();
```

### Performance Guidelines

**Reduced Motion:**
```tsx
const { motionPreferences } = useSceneStore();
if (motionPreferences.reducedMotion) {
  // Disable animations
}
```

**Low-End Device Degradation:**
- Disable volumetric transforms: `motionPreferences.disableVolumetric`
- Simplify glow effects: `motionPreferences.simplifyGlow`
- Reduce animation complexity

**Web Worker Usage:**
- AI processing runs in background worker
- Prevents main thread blocking
- Handles predictions, suggestions, insights

### Accessibility

**Keyboard Navigation:**
- All interactive elements are keyboard accessible
- Command Halo: `⌘+Shift+Space`
- Focus indicators with holographic glow

**Motion Preferences:**
- Respects `prefers-reduced-motion`
- Toggle via UI settings
- Disables volumetric effects and complex animations

**Screen Readers:**
- ARIA labels on all interactive components
- Semantic HTML structure
- Descriptive status messages
