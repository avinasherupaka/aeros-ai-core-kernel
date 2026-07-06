import type { FC } from 'react';
import * as Icons from 'lucide-react';
import clsx from 'clsx';

export interface NavigationItem {
  id: string;
  label: string;
  icon?: keyof typeof Icons;
}

export interface NavigationSidebarProps {
  title: string;
  items: NavigationItem[];
  activeItem: string;
  onSelect: (id: string) => void;
}

export const NavigationSidebar: FC<NavigationSidebarProps> = ({ title, items, activeItem, onSelect }) => (
  <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-full overflow-y-auto" aria-label={title}>
    <div className="p-4 border-b border-slate-800">
      <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</h2>
    </div>
    <nav className="flex-1 px-2 py-4 space-y-1">
      {items.map((item) => {
        const Icon = item.icon ? (Icons[item.icon as keyof typeof Icons] as FC<any>) : null;
        return (
          <button
            key={item.id}
            type="button"
            className={clsx(
              'w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              item.id === activeItem
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
            )}
            onClick={() => onSelect(item.id)}
          >
            {Icon && <Icon className="mr-3 flex-shrink-0 h-5 w-5" aria-hidden="true" />}
            {item.label}
          </button>
        );
      })}
    </nav>
  </aside>
);
