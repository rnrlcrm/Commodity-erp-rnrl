interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  sheen?: boolean;
}

export function Button({
  variant = 'primary',
  sheen = true,
  className = '',
  children,
  ...props
}: Readonly<ButtonProps>) {
  const base = 'relative px-4 py-2 rounded-lg transition-all overflow-hidden';
  const variants: Record<string, string> = {
    primary: 'bg-saturn-500/80 text-white hover:bg-saturn-500 shadow-holo',
    secondary: 'bg-pearl-50/10 text-pearl-100 hover:bg-pearl-50/20 border border-white/10',
    danger: 'bg-mars-500/80 text-white hover:bg-mars-500 shadow-holo',
  };

  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {/* Liquid Button Sheen */}
      {sheen && <span className="btn-sheen" />}
      <span className="relative z-10">{children}</span>
    </button>
  );
}

export default Button;