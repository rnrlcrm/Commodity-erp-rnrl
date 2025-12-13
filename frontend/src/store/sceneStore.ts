import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { openDB, DBSchema, IDBPDatabase } from 'idb';
import type { SceneMemory, MotionPreferences } from '../types/2040.types';

// IndexedDB Schema
interface SceneDB extends DBSchema {
  scenes: {
    key: string;
    value: SceneMemory;
    indexes: { 'by-timestamp': number };
  };
}

// Scene Store
interface SceneStore {
  currentScene: SceneMemory | null;
  savedScenes: SceneMemory[];
  motionPreferences: MotionPreferences;
  db: IDBPDatabase<SceneDB> | null;
  
  // Actions
  initDB: () => Promise<void>;
  saveScene: (scene: SceneMemory) => Promise<void>;
  loadScene: (id: string) => Promise<void>;
  deleteScene: (id: string) => Promise<void>;
  listScenes: () => Promise<SceneMemory[]>;
  setMotionPreferences: (prefs: Partial<MotionPreferences>) => void;
  updateCurrentScene: (updates: Partial<SceneMemory>) => void;
}

export const useSceneStore = create<SceneStore>()(
  persist(
    (set, get) => ({
      currentScene: null,
      savedScenes: [],
      motionPreferences: {
        reducedMotion: false,
        disableVolumetric: false,
        simplifyGlow: false,
      },
      db: null,

      // Initialize IndexedDB
      initDB: async () => {
        const db = await openDB<SceneDB>('rnrl-2040-scenes', 1, {
          upgrade(db) {
            const sceneStore = db.createObjectStore('scenes', { keyPath: 'id' });
            sceneStore.createIndex('by-timestamp', 'timestamp');
          },
        });
        set({ db });
      },

      // Save scene to IndexedDB
      saveScene: async (scene: SceneMemory) => {
        const { db } = get();
        if (!db) {
          await get().initDB();
          return get().saveScene(scene);
        }
        
        await db.put('scenes', scene);
        const scenes = await db.getAllFromIndex('scenes', 'by-timestamp');
        set({ savedScenes: scenes.reverse() });
      },

      // Load scene from IndexedDB
      loadScene: async (id: string) => {
        const { db } = get();
        if (!db) {
          await get().initDB();
          return get().loadScene(id);
        }
        
        const scene = await db.get('scenes', id);
        if (scene) {
          set({ currentScene: scene });
        }
      },

      // Delete scene
      deleteScene: async (id: string) => {
        const { db } = get();
        if (!db) return;
        
        await db.delete('scenes', id);
        const scenes = await db.getAllFromIndex('scenes', 'by-timestamp');
        set({ savedScenes: scenes.reverse() });
      },

      // List all saved scenes
      listScenes: async () => {
        const { db } = get();
        if (!db) {
          await get().initDB();
          return get().listScenes();
        }
        
        const scenes = await db.getAllFromIndex('scenes', 'by-timestamp');
        set({ savedScenes: scenes.reverse() });
        return scenes.reverse();
      },

      // Update motion preferences
      setMotionPreferences: (prefs) => {
        set((state) => ({
          motionPreferences: { ...state.motionPreferences, ...prefs },
        }));
      },

      // Update current scene
      updateCurrentScene: (updates) => {
        set((state) => ({
          currentScene: state.currentScene
            ? { ...state.currentScene, ...updates }
            : null,
        }));
      },
    }),
    {
      name: 'scene-storage',
      partialize: (state) => ({
        motionPreferences: state.motionPreferences,
      }),
    }
  )
);

// Initialize DB on app start
if (typeof window !== 'undefined') {
  useSceneStore.getState().initDB();
}
