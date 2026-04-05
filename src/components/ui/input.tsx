import * as React from 'react';
import { cn } from '@/lib/utils';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        'flex h-9 w-full rounded-lg border border-[var(--input)] bg-black/30 px-3 py-1 text-sm text-[var(--parchment)]',
        'transition-colors placeholder:text-[var(--muted-foreground)]',
        'focus-visible:outline-none focus-visible:border-[var(--gold)] focus-visible:ring-1 focus-visible:ring-[var(--ring)]',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      ref={ref}
      {...props}
    />
  ),
);
Input.displayName = 'Input';
