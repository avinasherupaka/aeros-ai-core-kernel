import type { FC } from 'react';

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
  <section>
    <p className="tabs-label">{label}</p>
    <div className="tab-row" role="tablist" aria-label={label}>
      {options.map((item) => (
        <button
          key={item.id}
          type="button"
          role="tab"
          aria-selected={item.id === selected}
          className={item.id === selected ? 'tab active' : 'tab'}
          onClick={() => onSelect(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  </section>
);
