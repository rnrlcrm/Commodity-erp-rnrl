import React from 'react';

export type CompanyLogoSize = 'xs' | 'sm' | 'md' | 'lg';

interface CompanyLogoProps {
  size?: CompanyLogoSize;
  className?: string;
}

const SIZE_CLASSES: Record<CompanyLogoSize, string> = {
  xs: 'h-8',
  sm: 'h-10',
  md: 'h-14',
  lg: 'h-20',
};

export function CompanyLogo({ size = 'md', className = '' }: Readonly<CompanyLogoProps>) {
  const sizeClass = SIZE_CLASSES[size];

  return (
    <img
      src="/rnrl-logo.svg"
      alt="RNRL Supply | Service | Solutions logo"
      className={`${sizeClass} w-auto select-none ${className}`}
      draggable={false}
    />
  );
}

export default CompanyLogo;
