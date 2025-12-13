# RNRL 2040 Documentation Index

Welcome to the RNRL 2040 Holographic Back Office documentation! This index will help you find the information you need.

## 🚀 Getting Started

**Start here if you're new:**
- [START_HERE.txt](./START_HERE.txt) - Quick overview and getting started guide
- [start-2040.sh](./start-2040.sh) - Quick start script (run this!)

## 📚 Main Documentation

### Complete Guide
[RNRL_2040_README.md](./RNRL_2040_README.md)
- System architecture
- Installation instructions
- Feature overview
- Configuration guide
- Development guidelines

### Component Reference
[RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md)
- Component API documentation
- Props and usage examples
- Design tokens
- Hooks reference
- Accessibility guidelines

### Implementation Details
[IMPLEMENTATION_SUMMARY_2040.md](./IMPLEMENTATION_SUMMARY_2040.md)
- Complete file list
- Implementation metrics
- Feature checklist
- Technical decisions
- Next steps

### Visual Guide
[VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md)
- Component hierarchy diagrams
- Data flow visualization
- Color palette reference
- Animation timings
- Performance budgets

## 🎯 Quick Reference

### File Structure
```
frontend/
├── src/
│   ├── components/2040/     → Core holographic components
│   ├── pages/2040/          → 11 module scenes
│   ├── layouts/             → Layout2040 main layout
│   ├── hooks/               → AI & realtime hooks
│   ├── store/               → Scene persistence
│   ├── workers/             → AI Web Worker
│   ├── types/               → TypeScript definitions
│   └── routes/              → Route configuration
├── tailwind.config.2040.js  → Holographic design system
└── Documentation files      → You are here!
```

### Core Components
- **HoloPanel** - `src/components/2040/HoloPanel.tsx`
- **VolumetricTable** - `src/components/2040/VolumetricTable.tsx`
- **AIInsightBar** - `src/components/2040/AIInsightBar.tsx`
- **CommandHalo** - `src/components/2040/CommandHalo.tsx`

### Module Scenes (All in `src/pages/2040/`)
1. SettingsScene.tsx
2. UserManagementScene.tsx
3. PartnerManagementScene.tsx
4. TradeDeskScene.tsx
5. QualityScene.tsx
6. LogisticsScene.tsx
7. DeliveryScene.tsx
8. AccountsScene.tsx
9. DisputesScene.tsx
10. AuditScene.tsx
11. DocumentIntelligenceScene.tsx

### Hooks
- **useAIOrchestrator** - `src/hooks/useAIOrchestrator.ts`
- **useRealtime** - `src/hooks/useRealtime.ts`
- **useSceneStore** - `src/store/sceneStore.ts`
- **useCommandHalo** - `src/components/2040/CommandHalo.tsx`

## 🎨 Design System

### Color Palette
```
Saturn:  #3366FF  (Primary blue with glow)
Sun:     #FFB800  (Golden CTA)
Mars:    #FF3B4A  (Alert red)
Pearl:   #B8B8B8  (Neutral glass)
Space:   #242B45  (Deep layers)
```

### Key Classes
```css
.hologlass           /* Base holographic surface */
.hologlass-saturn    /* Saturn-themed glow */
.volumetric-row      /* 3D floating row */
.text-glow-saturn    /* Text with glow */
.shadow-holo         /* Holographic shadow */
```

### Keyboard Shortcuts
```
⌘+Shift+Space  - Open Command Halo
⌘+K            - Quick Search
⌘+Shift+A      - AI Assist
⌘+S            - Save Scene
Escape         - Close Modals
```

## 📖 Topic-Specific Guides

### For Developers
1. Read [RNRL_2040_README.md](./RNRL_2040_README.md) - Architecture section
2. Review [RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md) - Component APIs
3. Check [VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md) - Data flow diagrams

### For Designers
1. Check [VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md) - Color palette & visual hierarchy
2. Review [tailwind.config.2040.js](./tailwind.config.2040.js) - Design tokens
3. See component examples in module scenes

### For Product Managers
1. Read [START_HERE.txt](./START_HERE.txt) - Feature overview
2. Review [IMPLEMENTATION_SUMMARY_2040.md](./IMPLEMENTATION_SUMMARY_2040.md) - What's built
3. Check module routes in [RNRL_2040_README.md](./RNRL_2040_README.md)

## 🔍 Finding Specific Information

### "How do I create a new component?"
→ [RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md) - Component patterns section

### "What's the color for alerts?"
→ [VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md) - Color palette section
→ Mars: #FF3B4A

### "How does AI orchestration work?"
→ [RNRL_2040_README.md](./RNRL_2040_README.md) - AI Integration section
→ [VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md) - Data flow diagram

### "What keyboard shortcuts are available?"
→ [RNRL_2040_README.md](./RNRL_2040_README.md) - Keyboard Shortcuts section
→ [START_HERE.txt](./START_HERE.txt) - Quick reference

### "How do I add a new module?"
→ [RNRL_2040_README.md](./RNRL_2040_README.md) - Creating New Modules section

### "What files were created?"
→ [IMPLEMENTATION_SUMMARY_2040.md](./IMPLEMENTATION_SUMMARY_2040.md) - Complete file list

### "How do I customize animations?"
→ [VISUAL_GUIDE_2040.md](./VISUAL_GUIDE_2040.md) - Animation timings section
→ [RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md) - Motion preferences

### "How do I enable reduced motion?"
→ [RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md) - Accessibility section
→ Toggle in UI top bar or use `useSceneStore().setMotionPreferences()`

## 🐛 Troubleshooting

### Dependencies not installing?
```bash
rm -rf node_modules package-lock.json
npm install
```

### Animations not working?
- Check if reduced motion is enabled
- Verify framer-motion is installed
- See [RNRL_2040_COMPONENTS.md](./RNRL_2040_COMPONENTS.md) - Performance section

### WebSocket not connecting?
- Check VITE_WS_URL in .env
- Verify backend is running
- See [RNRL_2040_README.md](./RNRL_2040_README.md) - Configuration section

### Command Halo not opening?
- Try ⌘+Shift+Space (Mac) or Ctrl+Shift+Space (Windows)
- Check console for errors
- Verify @radix-ui/react-command is installed

## 📞 Support

For questions or issues:
1. Check this index first
2. Review relevant documentation section
3. Check implementation files in `src/`
4. Contact RNRL Engineering Team

## 🎯 Quick Links

- [Complete README](./RNRL_2040_README.md)
- [Component Docs](./RNRL_2040_COMPONENTS.md)
- [Visual Guide](./VISUAL_GUIDE_2040.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY_2040.md)
- [Quick Start Script](./start-2040.sh)

---

**Built with ♥ by RNRL Engineering Team**
*Branch: Backoffice-layout-2040-re-acrticutre*
*Date: December 12, 2025*
