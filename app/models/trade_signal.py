from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"

class TradeSignal(BaseModel):
    action: Action
    entry: Optional[float] = None
    sl: Optional[float] = None
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    risk_reward: Optional[float] = None
    confidence: float = 0.0
    reasoning: str = ""

class ChartAnalysis(BaseModel):
    current_price: float
    pattern: Optional[str] = None
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    indicators: dict = {}
    trade: TradeSignal

class AnalysisResponse(BaseModel):
    status: str
    analysis: ChartAnalysis
    processing_time_ms: float
