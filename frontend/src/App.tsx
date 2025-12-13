import { AppProviders } from './app/providers/AppProviders';
import { HoloShell } from './scenes/HoloShell';

export function App() {
  return (
    <AppProviders>
      <HoloShell />
    </AppProviders>
  );
}
