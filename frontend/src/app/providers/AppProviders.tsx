import { QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useMemo } from 'react';
import { queryClient } from './queryClient';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: Readonly<AppProvidersProps>) {
  const client = useMemo(() => queryClient, []);

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
