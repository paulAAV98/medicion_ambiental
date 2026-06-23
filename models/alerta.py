from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NivelAlerta(Enum):
    ADVERTENCIA = "⚠️  ADVERTENCIA"
    PELIGRO     = "🔶 PELIGRO"
    CRITICO     = "🔴 CRÍTICO"


@dataclass
class AlertaAmbiental:
    estacion: str
    zona: str
    variable: str
    valor: float
    umbral: float
    unidad: str
    ciclo: int
    nivel: NivelAlerta = field(init=False)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        exceso = (self.valor - self.umbral) / self.umbral
        if exceso > 0.50:
            self.nivel = NivelAlerta.CRITICO
        elif exceso > 0.25:
            self.nivel = NivelAlerta.PELIGRO
        else:
            self.nivel = NivelAlerta.ADVERTENCIA

    def __str__(self) -> str:
        return (
            f"{self.nivel.value} | {self.zona} - {self.estacion} | "
            f"{self.variable}: {self.valor:.2f} {self.unidad} "
            f"(umbral: {self.umbral:.2f}) | Ciclo {self.ciclo}"
        )

    @property
    def porcentaje_exceso(self) -> float:
        return (self.valor - self.umbral) / self.umbral