import type { FC } from 'react';

export interface NavigationItem {
  id: string;
  label: string;
}

export interface NavigationSidebarProps {
  title: string;
  items: NavigationItem[];
  activeItem: string;
  onSelect: (id: string) => void;
}

export const NavigationSidebar: FC<NavigationSidebarProps> = ({ title, items, activeItem, onSelect }) => (
  <aside className="side-nav" aria-label={title}>
    <p className="tabs-label">{title}</p>
    <div className="tab-row">
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          className={item.id === activeItem ? 'tab active' : 'tab'}
          onClick={() => onSelect(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  </aside>
);
