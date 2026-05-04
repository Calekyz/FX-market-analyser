from typing import Dict, Any

class StrategyEngine:
    def generate_signal(self, analysis: Dict[str, Any], risk_percent: float) -> Dict[str, Any]:
        """Generate entry, SL, TP based on analysis"""
        
        current = analysis.get("current_price")
        supports = analysis.get("support_levels", [])
        resistances = analysis.get("resistance_levels", [])
        trend = analysis.get("trend", "sideways")
        indicators = analysis.get("indicators", {})
        rsi = indicators.get("rsi", 50)
        
        if not current:
            return {
                "action": "WAIT",
                "reasoning": "Could not determine current price from chart",
                "confidence": 0.0
            }
        
        # Get nearest support and resistance
        support = None
        resistance = None
        
        if supports:
            support = min(supports, key=lambda x: abs(x - current))
        else:
            support = round(current * 0.99, 5)
        
        if resistances:
            resistance = min(resistances, key=lambda x: abs(x - current))
        else:
            resistance = round(current * 1.01, 5)
        
        # Calculate risk amounts
        buy_risk = abs(current - support) if support else 0.001
        sell_risk = abs(resistance - current) if resistance else 0.001
        buy_reward = abs(resistance - current) if resistance else 0.002
        sell_reward = abs(current - support) if support else 0.002
        
        # Decision logic
        buy_score = 0
        sell_score = 0
        
        # Trend
        if trend == "bullish":
            buy_score += 2
        elif trend == "bearish":
            sell_score += 2
        
        # RSI
        if rsi and rsi < 35:
            buy_score += 1
        elif rsi and rsi > 65:
            sell_score += 1
        
        # Distance to support/resistance
        if support and (current - support) < (resistance - current) * 1.2:
            buy_score += 1
        if resistance and (resistance - current) < (current - support) * 1.2:
            sell_score += 1
        
        # Make decision
        if buy_score > sell_score and buy_score >= 2:
            risk = buy_risk
            reward = buy_reward
            rr = round(reward / risk, 2) if risk > 0 else 0
            
            return {
                "action": "BUY",
                "entry": round(current, 5),
                "sl": round(current - risk * 0.7, 5),
                "tp1": round(resistance, 5) if resistance else round(current + reward, 5),
                "tp2": round((resistance + reward * 0.5) if resistance else current + reward * 1.5, 5),
                "risk_reward": rr,
                "confidence": round(min(0.9, buy_score / 4), 2),
                "reasoning": f"Bullish setup. Price near support at {support}. Trend is {trend}."
            }
        
        elif sell_score > buy_score and sell_score >= 2:
            risk = sell_risk
            reward = sell_reward
            rr = round(reward / risk, 2) if risk > 0 else 0
            
            return {
                "action": "SELL",
                "entry": round(current, 5),
                "sl": round(current + risk * 0.7, 5),
                "tp1": round(support, 5) if support else round(current - reward, 5),
                "tp2": round((support - reward * 0.5) if support else current - reward * 1.5, 5),
                "risk_reward": rr,
                "confidence": round(min(0.9, sell_score / 4), 2),
                "reasoning": f"Bearish setup. Price near resistance at {resistance}. Trend is {trend}."
            }
        
        else:
            return {
                "action": "WAIT",
                "reasoning": f"No clear signal. Trend: {trend}, RSI: {rsi}. Wait for better setup.",
                "confidence": 0.3
            }
