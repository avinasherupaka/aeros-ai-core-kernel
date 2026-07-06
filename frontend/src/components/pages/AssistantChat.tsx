import type { FC } from 'react';

import type { AssistantQueryRequest, AssistantResponse, PersonaType } from '../../types/control-plane';
import { AssistantPanel } from '../assistant/AssistantPanel';

export interface AssistantChatProps {
  persona: PersonaType;
  response: AssistantResponse | null;
  onSubmit: (request: AssistantQueryRequest) => void;
}

export const AssistantChat: FC<AssistantChatProps> = ({ persona, response, onSubmit }) => (
  <section className="stack">
    <h2>Assistant Chat</h2>
    <AssistantPanel persona={persona} response={response ?? undefined} onSubmit={onSubmit} />
  </section>
);
