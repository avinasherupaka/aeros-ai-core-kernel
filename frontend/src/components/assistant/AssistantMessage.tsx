import type { FC } from 'react';

export interface AssistantMessageProps {
  title: string;
  body: string;
}

export const AssistantMessage: FC<AssistantMessageProps> = ({ title, body }) => (
  <article className="card">
    <h4>{title}</h4>
    <pre className="markdown-box">{body}</pre>
  </article>
);
