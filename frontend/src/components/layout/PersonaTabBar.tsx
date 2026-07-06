import type { FC } from 'react';
import clsx from 'clsx';

export interface PersonaOption {
  id: string;
  label: string;
}

export interface PersonaTabBarProps {
  label: string;
  options: PersonaOption[];
  selected: string;
  onSelect: (id: string) => void;
}

export const PersonaTabBar: FC<PersonaTabBarProps> = ({ label, options, selected, onSelect }) => (
  <div className="flex items-center space-x-4">
    <span className="text-sm font-medium text-slate-400">{label}:</span>
    <nav className="flex space-x-2" aria-label={label}>
      {options.map((item) => (
        <button
          key={item.id}
          type="button"
          aria-selected={item.id === selected}
          className={clsx(
            'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            item.id === selected
              ? 'bg-blue-600 text-white'
              : 'text-slate-300 hover:bg-slate-800 hover:text-white'
          )}
          onClick={() => onSelect(item.id)}
        >
          {item.label}
        </button>
      ))}
    </nav>
  </div>
);
