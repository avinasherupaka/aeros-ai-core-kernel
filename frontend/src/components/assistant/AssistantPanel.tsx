import type { FC } from 'react';

import type { AssistantQueryRequest, AssistantResponse, PersonaType } from '../../types/control-plane';

export interface AssistantPanelProps {
  persona?: PersonaType;
  request?: AssistantQueryRequest;
  response?: AssistantResponse;
  onSubmit?: (request: AssistantQueryRequest) => void;
}

/**
 * Shell component for the Manufacturing Control Plane assistant experience.
 * Intended to host persona-aware prompts, grounded responses, and evidence citations.
 */
export const AssistantPanel: FC<AssistantPanelProps> = (_props) => null;
