# models.py
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing_extensions import Annotated

def limpiar_numeros(value: Any) -> float:
    """Limpia y convierte valores financieros a float de manera robusta"""
    if value is None: return 0.0
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        clean_str = value.replace('$', '').replace('€', '').replace(',', '').strip()
        if not clean_str or clean_str.lower() in ('n/a', 'nan', 'none'): return 0.0
        multiplier = 1.0
        if clean_str.upper().endswith('T'): multiplier, clean_str = 1e12, clean_str[:-1]
        elif clean_str.upper().endswith('B'): multiplier, clean_str = 1e9, clean_str[:-1]
        elif clean_str.upper().endswith('M'): multiplier, clean_str = 1e6, clean_str[:-1]
        try: return float(clean_str) * multiplier
        except ValueError: return 0.0
    return 0.0

RobustFloat = Annotated[float, BeforeValidator(limpiar_numeros)]

class DatosFinancieros(BaseModel):
    model_config = ConfigDict(extra='ignore')
    revenue: RobustFloat = Field(description="Ventas totales")
    net_income: RobustFloat = Field(description="Beneficio neto")
    total_assets: RobustFloat = Field(description="Activos totales")
    total_liabilities: RobustFloat = Field(description="Pasivos totales")
    free_cash_flow: RobustFloat = Field(description="Flujo de caja libre")
    operating_cash_flow: Optional[RobustFloat] = Field(default=None)
    capital_expenditure: Optional[RobustFloat] = Field(default=None)

class TelemetriaMercado(BaseModel):
    model_config = ConfigDict(extra='ignore')
    enterprise_value: RobustFloat
    forward_pe: Optional[float] = None
    profit_margins: Optional[float] = None
    current_price: RobustFloat
    market_cap: Optional[RobustFloat] = None
    dividend_yield: Optional[float] = None

class Noticia(BaseModel):
    titulo: str
    fuente: str
    url: str
    fecha: Optional[str] = None

class ReporteFinal(BaseModel):
    ticker: str
    fecha: str
    fundamentales: Optional[DatosFinancieros] = None
    mercado: Optional[TelemetriaMercado] = None
    noticias: List[Noticia] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
