from pydantic import BaseModel, ConfigDict
from typing import Any


class BoardNode(BaseModel):
    """
    Representa um node do quadro investigativo (retângulo, círculo, losango,
    post-it, evidência com imagem, ou label solto).

    Não travamos o schema de `data` porque cada `type` de node
    (textBox / imageBox / note) tem um formato diferente:

      textBox  -> { label: str, color: str (hex), shape?: str, variant?: str }
      imageBox -> { imageUrl: str, caption: str }
      note     -> { text: str }

    O frontend é a fonte da verdade sobre o formato de cada `data`; aqui só
    validamos o "envelope" comum a todo node do React Flow. `extra = "allow"`
    deixa passar campos que o React Flow anexa sozinho (selected, dragging,
    measured, zIndex etc) sem quebrar a validação.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    type: str  # 'textBox' | 'imageBox' | 'note'
    position: dict[str, float]
    data: dict[str, Any]


class BoardEdge(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    source: str
    target: str
    type: str | None = None
    label: str | None = None
    style: dict[str, Any] | None = None


class SaveBoardRequest(BaseModel):
    nodes: list[BoardNode]
    edges: list[BoardEdge]
