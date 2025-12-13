/**
 * HoloPanel - Volumetric glass-morphism panel with depth and glow effects
 * From RNRL 2040 Design System Specification
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface HoloPanelProps {
  children: ReactNode;
  theme?: 'saturn' | 'sun' | 'mars' | 'pearl' | 'space';
  intensity?: 'subtle' | 'normal' | 'strong';
  glow?: boolean;
  elevated?: boolean;
  className?: string;
}

export function HoloPanel({
  children,
  theme = 'saturn',
  glow = false,
  elevated = false,
  className = ''
}: Readonly<HoloPanelProps>) {
  const getThemeStyles = () => {
    const baseStyle = {
      background: 'rgba(255, 255, 255, 0.08)',
      backdropFilter: 'blur(20px)',
      border: '1px solid',
    };

    switch (theme) {
      case 'saturn':
        return {
          ...baseStyle,
          borderColor: 'rgba(51, 102, 255, 0.2)',
          boxShadow: glow ? '0 0 30px rgba(51, 102, 255, 0.4)' : 'none'
        };
      case 'sun':
        return {
          ...baseStyle,
          borderColor: 'rgba(255, 184, 0, 0.2)',
          boxShadow: glow ? '0 0 30px rgba(255, 184, 0, 0.5)' : 'none'
        };
      case 'mars':
        return {
          ...baseStyle,
          borderColor: 'rgba(255, 59, 74, 0.2)',
          boxShadow: glow ? '0 0 30px rgba(255, 59, 74, 0.5)' : 'none'
        };
      case 'pearl':
        return {
          ...baseStyle,
          borderColor: 'rgba(184, 184, 184, 0.2)',
          boxShadow: 'none'
        };
      case 'space':
        return {
          ...baseStyle,
          background: 'rgba(10, 15, 28, 0.95)',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          boxShadow: 'none'
        };
    }
  };

  const Component = elevated ? motion.div : 'div';

  const elevatedProps = elevated ? {
    whileHover: { y: -4, scale: 1.01 },
    transition: { duration: 0.2 }
  } : {};

  return (
    <Component
      className={`rounded-xl p-6 ${className}`}
      style={getThemeStyles()}
      {...elevatedProps}
    >
      {children}
    </Component>
  );
}

// Provide HoloCard export via this module for compatibility with existing imports
export { HoloCard } from './HoloCard';
