from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Medicion:
    estacion: str
    zona: str
    variable: str
    valor: float
    unidad: str
    ciclo: int
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return (
            f"[Ciclo {self.ciclo:02d}] {self.estacion} ({self.zona}) | "
            f"{self.variable}: {self.valor:.2f} {self.unidad} | "
            f"{self.timestamp.strftime('%H:%M:%S')}"
        )

    def to_dict(self) -> dict:
        return {
            "estacion": self.estacion,
            "zona": self.zona,
            "variable": self.variable,
            "valor": self.valor,
            "unidad": self.unidad,
            "ciclo": self.ciclo,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Medicion":
        return cls(
            estacion=data["estacion"],
            zona=data["zona"],
            variable=data["variable"],
            valor=data["valor"],
            unidad=data["unidad"],
            ciclo=data["ciclo"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )