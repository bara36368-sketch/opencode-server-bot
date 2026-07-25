"""
Finance & Crypto Tracker — v1.0
OpenCode Bot Feature

Telegram bot features for finance and cryptocurrency:
- Real-time crypto price tracking
- Portfolio management
- Price alerts
- Market overview
- Fiat currency conversion
- News aggregation
- Watchlists
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINANCE_DATA_FILE = os.path.join(BASE_DIR, "finance_data.json")


class AssetType(Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FIAT = "fiat"
    COMMODITY = "commodity"


@dataclass
class PriceAlert:
    alert_id: str
    asset: str
    asset_type: str
    condition: str  # "above", "below", "change_pct"
    target_value: float
    current_value: float = 0.0
    message: str = ""
    enabled: bool = True
    created_at: float = 0.0
    last_triggered: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PortfolioItem:
    asset: str
    asset_type: str
    quantity: float
    avg_buy_price: float
    current_price: float = 0.0
    last_updated: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def total_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return (self.current_price - self.avg_buy_price) * self.quantity

    @property
    def profit_loss_pct(self) -> float:
        if self.avg_buy_price == 0:
            return 0.0
        return ((self.current_price - self.avg_buy_price) / self.avg_buy_price) * 100


@dataclass
class WatchlistItem:
    asset: str
    asset_type: str
    added_at: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Transaction:
    tx_id: str
    asset: str
    tx_type: str  # "buy", "sell"
    quantity: float
    price: float
    total: float
    timestamp: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UserFinanceProfile:
    user_id: str
    portfolio: List[PortfolioItem] = field(default_factory=list)
    alerts: List[PriceAlert] = field(default_factory=list)
    watchlist: List[WatchlistItem] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    default_currency: str = "USD"
    created_at: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "portfolio": [p.to_dict() for p in self.portfolio],
            "alerts": [a.to_dict() for a in self.alerts],
            "watchlist": [w.to_dict() for w in self.watchlist],
            "transactions": [t.to_dict() for t in self.transactions[-50:]],
            "default_currency": self.default_currency,
            "created_at": self.created_at
        }

    @property
    def total_portfolio_value(self) -> float:
        return sum(item.total_value for item in self.portfolio)

    @property
    def total_profit_loss(self) -> float:
        return sum(item.profit_loss for item in self.portfolio)


POPULAR_CRYPTOS = {
    "BTC": {"name": "Bitcoin", "symbol": "BTC"},
    "ETH": {"name": "Ethereum", "symbol": "ETH"},
    "BNB": {"name": "BNB", "symbol": "BNB"},
    "SOL": {"name": "Solana", "symbol": "SOL"},
    "XRP": {"name": "XRP", "symbol": "XRP"},
    "ADA": {"name": "Cardano", "symbol": "ADA"},
    "DOGE": {"name": "Dogecoin", "symbol": "DOGE"},
    "DOT": {"name": "Polkadot", "symbol": "DOT"},
    "AVAX": {"name": "Avalanche", "symbol": "AVAX"},
    "LINK": {"name": "Chainlink", "symbol": "LINK"},
    "MATIC": {"name": "Polygon", "symbol": "MATIC"},
    "UNI": {"name": "Uniswap", "symbol": "UNI"},
    "ATOM": {"name": "Cosmos", "symbol": "ATOM"},
    "FIL": {"name": "Filecoin", "symbol": "FIL"},
    "LTC": {"name": "Litecoin", "symbol": "LTC"},
}

FIAT_CURRENCIES = {
    "USD": "🇺🇸 US Dollar",
    "EUR": "🇪🇺 Euro",
    "GBP": "🇬🇧 British Pound",
    "JPY": "🇯🇵 Japanese Yen",
    "AUD": "🇦🇺 Australian Dollar",
    "CAD": "🇨🇦 Canadian Dollar",
    "CHF": "🇨🇭 Swiss Franc",
    "CNY": "🇨🇳 Chinese Yuan",
    "INR": "🇮🇳 Indian Rupee",
    "BRL": "🇧🇷 Brazilian Real",
    "KRW": "🇰🇷 Korean Won",
    "RUB": "🇷🇺 Russian Ruble",
    "TRY": "🇹🇷 Turkish Lira",
    "NGN": "🇳🇬 Nigerian Naira",
    "IDR": "🇮🇩 Indonesian Rupiah",
}

MOCK_PRICES = {
    "BTC": 67500.0, "ETH": 3450.0, "BNB": 590.0, "SOL": 175.0,
    "XRP": 0.62, "ADA": 0.48, "DOGE": 0.14, "DOT": 7.20,
    "AVAX": 38.50, "LINK": 18.30, "MATIC": 0.72, "UNI": 11.50,
    "ATOM": 9.80, "FIL": 6.20, "LTC": 85.0,
}


class FinanceManager:
    def __init__(self):
        self.profiles: Dict[str, UserFinanceProfile] = {}
        self._load_data()

    def _load_data(self):
        try:
            if os.path.exists(FINANCE_DATA_FILE):
                with open(FINANCE_DATA_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for uid, udata in data.items():
                        try:
                            profile = UserFinanceProfile(
                                user_id=uid,
                                default_currency=udata.get("default_currency", "USD"),
                                created_at=udata.get("created_at", 0)
                            )
                            for pdata in udata.get("portfolio", []):
                                profile.portfolio.append(PortfolioItem(**{
                                    k: v for k, v in pdata.items()
                                    if k in PortfolioItem.__dataclass_fields__
                                }))
                            for adata in udata.get("alerts", []):
                                profile.alerts.append(PriceAlert(**{
                                    k: v for k, v in adata.items()
                                    if k in PriceAlert.__dataclass_fields__
                                }))
                            for wdata in udata.get("watchlist", []):
                                profile.watchlist.append(WatchlistItem(**{
                                    k: v for k, v in wdata.items()
                                    if k in WatchlistItem.__dataclass_fields__
                                }))
                            for tdata in udata.get("transactions", []):
                                profile.transactions.append(Transaction(**{
                                    k: v for k, v in tdata.items()
                                    if k in Transaction.__dataclass_fields__
                                }))
                            self.profiles[uid] = profile
                        except Exception as e:
                            logger.warning(f"Failed to restore finance profile {uid}: {e}")
        except Exception as e:
            logger.error(f"Failed to load finance data: {e}")

    def _save_data(self):
        try:
            with open(FINANCE_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({uid: p.to_dict() for uid, p in self.profiles.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save finance data: {e}")

    def get_profile(self, user_id: str) -> UserFinanceProfile:
        if user_id not in self.profiles:
            self.profiles[user_id] = UserFinanceProfile(
                user_id=user_id, created_at=time.time()
            )
        return self.profiles[user_id]

    def get_price(self, symbol: str) -> Optional[float]:
        return MOCK_PRICES.get(symbol.upper())

    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        return {s: MOCK_PRICES.get(s.upper(), 0) for s in symbols}

    def get_market_overview(self) -> Dict:
        top10 = list(MOCK_PRICES.items())[:10]
        total_market = sum(MOCK_PRICES.values())
        return {
            "total_market_cap": total_market,
            "top_cryptos": [
                {"symbol": s, "price": p, "name": POPULAR_CRYPTOS.get(s, {}).get("name", s)}
                for s, p in top10
            ]
        }

    def add_to_portfolio(self, user_id: str, symbol: str, quantity: float,
                         buy_price: float, asset_type: str = "crypto") -> bool:
        profile = self.get_profile(user_id)
        symbol = symbol.upper()
        existing = next((p for p in profile.portfolio if p.asset == symbol), None)
        if existing:
            total_cost = (existing.quantity * existing.avg_buy_price) + (quantity * buy_price)
            existing.quantity += quantity
            existing.avg_buy_price = total_cost / existing.quantity
            existing.current_price = self.get_price(symbol) or buy_price
            existing.last_updated = time.time()
        else:
            current = self.get_price(symbol) or buy_price
            profile.portfolio.append(PortfolioItem(
                asset=symbol, asset_type=asset_type,
                quantity=quantity, avg_buy_price=buy_price,
                current_price=current, last_updated=time.time()
            ))
        tx = Transaction(
            tx_id=f"tx_{int(time.time()*1000) % 100000}",
            asset=symbol, tx_type="buy", quantity=quantity,
            price=buy_price, total=quantity * buy_price,
            timestamp=time.time()
        )
        profile.transactions.append(tx)
        self._save_data()
        return True

    def sell_from_portfolio(self, user_id: str, symbol: str,
                            quantity: float, sell_price: float) -> Tuple[bool, str]:
        profile = self.get_profile(user_id)
        symbol = symbol.upper()
        existing = next((p for p in profile.portfolio if p.asset == symbol), None)
        if not existing:
            return False, f"No {symbol} in portfolio."
        if existing.quantity < quantity:
            return False, f"Insufficient {symbol}. Have {existing.quantity}, need {quantity}"
        existing.quantity -= quantity
        if existing.quantity < 0.0001:
            profile.portfolio = [p for p in profile.portfolio if p.asset != symbol]
        tx = Transaction(
            tx_id=f"tx_{int(time.time()*1000) % 100000}",
            asset=symbol, tx_type="sell", quantity=quantity,
            price=sell_price, total=quantity * sell_price,
            timestamp=time.time()
        )
        profile.transactions.append(tx)
        self._save_data()
        return True, f"Sold {quantity} {symbol} at ${sell_price:,.2f}"

    def get_portfolio_summary(self, user_id: str) -> str:
        profile = self.get_profile(user_id)
        if not profile.portfolio:
            return "📭 Your portfolio is empty. Use /fin buy <symbol> <qty> <price> to add."
        lines = ["💼 **Portfolio Summary:**\n"]
        total_value = 0
        total_cost = 0
        for item in profile.portfolio:
            value = item.total_value
            pnl = item.profit_loss
            pnl_pct = item.profit_loss_pct
            total_value += value
            total_cost += item.avg_buy_price * item.quantity
            icon = "📈" if pnl >= 0 else "📉"
            lines.append(
                f"**{item.asset}** — {item.quantity:.4f} units\n"
                f"  Value: ${value:,.2f} | P/L: {icon} ${pnl:,.2f} ({pnl_pct:+.1f}%)"
            )
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        lines.append(f"\n💰 **Total Value:** ${total_value:,.2f}")
        lines.append(f"📊 **Total P/L:** ${total_pnl:,.2f} ({total_pnl_pct:+.1f}%)")
        return "\n".join(lines)

    def add_alert(self, user_id: str, symbol: str, condition: str,
                  target: float, message: str = "") -> bool:
        profile = self.get_profile(user_id)
        symbol = symbol.upper()
        alert = PriceAlert(
            alert_id=f"alert_{int(time.time()*1000) % 100000}",
            asset=symbol, asset_type="crypto",
            condition=condition, target_value=target,
            message=message or f"{symbol} {condition} {target}",
            created_at=time.time()
        )
        profile.alerts.append(alert)
        self._save_data()
        return True

    def remove_alert(self, user_id: str, alert_id: str) -> bool:
        profile = self.get_profile(user_id)
        before = len(profile.alerts)
        profile.alerts = [a for a in profile.alerts if a.alert_id != alert_id]
        if len(profile.alerts) < before:
            self._save_data()
            return True
        return False

    def check_alerts(self, user_id: str) -> List[str]:
        profile = self.get_profile(user_id)
        triggered = []
        for alert in profile.alerts:
            if not alert.enabled:
                continue
            price = self.get_price(alert.asset)
            if price is None:
                continue
            alert.current_value = price
            fired = False
            if alert.condition == "above" and price >= alert.target_value:
                fired = True
            elif alert.condition == "below" and price <= alert.target_value:
                fired = True
            if fired:
                alert.last_triggered = time.time()
                triggered.append(
                    f"🔔 **{alert.asset}** is now ${price:,.2f} "
                    f"({alert.condition} ${alert.target_value:,.2f})!\n"
                    f"{alert.message}"
                )
        if triggered:
            self._save_data()
        return triggered

    def add_to_watchlist(self, user_id: str, symbol: str,
                         notes: str = "") -> bool:
        profile = self.get_profile(user_id)
        symbol = symbol.upper()
        existing = next((w for w in profile.watchlist if w.asset == symbol), None)
        if existing:
            return False
        profile.watchlist.append(WatchlistItem(
            asset=symbol, asset_type="crypto",
            added_at=time.time(), notes=notes
        ))
        self._save_data()
        return True

    def remove_from_watchlist(self, user_id: str, symbol: str) -> bool:
        profile = self.get_profile(user_id)
        symbol = symbol.upper()
        before = len(profile.watchlist)
        profile.watchlist = [w for w in profile.watchlist if w.asset != symbol]
        if len(profile.watchlist) < before:
            self._save_data()
            return True
        return False

    def get_watchlist_display(self, user_id: str) -> str:
        profile = self.get_profile(user_id)
        if not profile.watchlist:
            return "📭 Watchlist empty. Use /fin watch <symbol> to add."
        lines = ["👀 **Watchlist:**\n"]
        for item in profile.watchlist:
            price = self.get_price(item.asset)
            price_str = f"${price:,.2f}" if price else "N/A"
            name = POPULAR_CRYPTOS.get(item.asset, {}).get("name", item.asset)
            lines.append(f"**{item.asset}** ({name}) — {price_str}")
        return "\n".join(lines)

    def get_transactions(self, user_id: str, limit: int = 10) -> str:
        profile = self.get_profile(user_id)
        txs = profile.transactions[-limit:]
        if not txs:
            return "📭 No transactions yet."
        lines = ["📜 **Recent Transactions:**\n"]
        for tx in reversed(txs):
            ts = datetime.fromtimestamp(tx.timestamp).strftime("%Y-%m-%d %H:%M")
            icon = "🟢" if tx.tx_type == "buy" else "🔴"
            lines.append(
                f"{icon} `{ts}` — {tx.tx_type.upper()} {tx.quantity:.4f} "
                f"{tx.asset} @ ${tx.price:,.2f} = ${tx.total:,.2f}"
            )
        return "\n".join(lines)

    def convert_currency(self, amount: float, from_curr: str,
                         to_curr: str) -> Optional[float]:
        rates = {
            "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5,
            "AUD": 1.53, "CAD": 1.36, "CHF": 0.88, "CNY": 7.24,
            "INR": 83.1, "BRL": 4.97, "KRW": 1320.0, "RUB": 92.5,
            "TRY": 27.5, "NGN": 1550.0, "IDR": 15800.0,
        }
        from_rate = rates.get(from_curr.upper(), 1.0)
        to_rate = rates.get(to_curr.upper(), 1.0)
        return round((amount / from_rate) * to_rate, 2)

    def get_crypto_info(self, symbol: str) -> Optional[Dict]:
        symbol = symbol.upper()
        info = POPULAR_CRYPTOS.get(symbol)
        price = self.get_price(symbol)
        if not info and not price:
            return None
        return {
            "symbol": symbol,
            "name": info.get("name", symbol) if info else symbol,
            "price": price,
            "market_cap_rank": list(MOCK_PRICES.keys()).index(symbol) + 1 if symbol in MOCK_PRICES else None,
        }


_finance_manager = None

def get_finance_manager() -> FinanceManager:
    global _finance_manager
    if _finance_manager is None:
        _finance_manager = FinanceManager()
    return _finance_manager


def build_finance_commands() -> str:
    return """
💰 Finance & Crypto Commands:

📊 MARKET:
/fin price <symbol> — Get crypto price
/fin market — Market overview top 10
/fin convert <amount> <from> <to> — Currency converter
/fin info <symbol> — Crypto info

💼 PORTFOLIO:
/fin buy <symbol> <quantity> <price> — Add to portfolio
/fin sell <symbol> <quantity> <price> — Sell from portfolio
/fin portfolio — View portfolio
/fin transactions — Transaction history

🔔 ALERTS:
/fin alert <symbol> <above/below> <price> [msg] — Set price alert
/fin alerts — List alerts
/fin delalert <alert_id> — Remove alert

👀 WATCHLIST:
/fin watch <symbol> [notes] — Add to watchlist
/fin unwatch <symbol> — Remove from watchlist
/fin watchlist — View watchlist

Supported cryptos: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, AVAX, LINK, MATIC, UNI, ATOM, FIL, LTC
Fiat: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, BRL, KRW, RUB, TRY, NGN, IDR
"""


def handle_finance_command(update, context) -> str:
    if not context.args:
        return build_finance_commands()

    subcmd = context.args[0].lower()
    user_id = str(update.effective_user.id)
    mgr = get_finance_manager()

    if subcmd == "price":
        if len(context.args) < 2:
            return "Usage: /fin price <symbol>"
        symbol = context.args[1].upper()
        price = mgr.get_price(symbol)
        if price is None:
            return f"❌ Unknown symbol: {symbol}\nSupported: {', '.join(POPULAR_CRYPTOS.keys())}"
        name = POPULAR_CRYPTOS.get(symbol, {}).get("name", symbol)
        rank = list(MOCK_PRICES.keys()).index(symbol) + 1 if symbol in MOCK_PRICES else "?"
        return (f"💰 **{name}** ({symbol})\n\n"
                f"Price: **${price:,.2f}**\n"
                f"Market Rank: #{rank}")

    elif subcmd == "market":
        overview = mgr.get_market_overview()
        lines = ["📊 **Market Overview:**\n"]
        for item in overview["top_cryptos"]:
            price = item["price"]
            lines.append(f"**{item['symbol']}** ({item['name']}) — ${price:,.2f}")
        return "\n".join(lines)

    elif subcmd == "convert":
        if len(context.args) < 4:
            return "Usage: /fin convert <amount> <from> <to>"
        try:
            amount = float(context.args[1])
        except ValueError:
            return "Amount must be a number."
        from_curr = context.args[2].upper()
        to_curr = context.args[3].upper()
        result = mgr.convert_currency(amount, from_curr, to_curr)
        if result is None:
            return f"❌ Unknown currency: {from_curr} or {to_curr}"
        return f"💱 {amount:,.2f} {from_curr} = **{result:,.2f} {to_curr}**"

    elif subcmd == "info":
        if len(context.args) < 2:
            return "Usage: /fin info <symbol>"
        info = mgr.get_crypto_info(context.args[1])
        if not info:
            return f"❌ Unknown: {context.args[1]}"
        return (f"ℹ️ **{info['name']}** ({info['symbol']})\n\n"
                f"Price: ${info['price']:,.2f}\n"
                f"Rank: #{info['market_rank']}")

    elif subcmd == "buy":
        if len(context.args) < 4:
            return "Usage: /fin buy <symbol> <quantity> <price>"
        symbol = context.args[1].upper()
        try:
            qty = float(context.args[2])
            price = float(context.args[3])
        except ValueError:
            return "Quantity and price must be numbers."
        mgr.add_to_portfolio(user_id, symbol, qty, price)
        total = qty * price
        return f"✅ Bought {qty} {symbol} at ${price:,.2f} = ${total:,.2f}"

    elif subcmd == "sell":
        if len(context.args) < 4:
            return "Usage: /fin sell <symbol> <quantity> <price>"
        symbol = context.args[1].upper()
        try:
            qty = float(context.args[2])
            price = float(context.args[3])
        except ValueError:
            return "Quantity and price must be numbers."
        ok, msg = mgr.sell_from_portfolio(user_id, symbol, qty, price)
        return f"✅ {msg}" if ok else f"❌ {msg}"

    elif subcmd == "portfolio":
        return mgr.get_portfolio_summary(user_id)

    elif subcmd == "transactions":
        limit = 10
        if len(context.args) > 1:
            try:
                limit = int(context.args[1])
            except ValueError:
                pass
        return mgr.get_transactions(user_id, limit)

    elif subcmd == "alert":
        if len(context.args) < 4:
            return "Usage: /fin alert <symbol> <above/below> <price> [message]"
        symbol = context.args[1].upper()
        condition = context.args[2].lower()
        if condition not in ("above", "below"):
            return "Condition must be 'above' or 'below'."
        try:
            target = float(context.args[3])
        except ValueError:
            return "Target price must be a number."
        msg = " ".join(context.args[4:]) if len(context.args) > 4 else ""
        mgr.add_alert(user_id, symbol, condition, target, msg)
        return f"✅ Alert set: {symbol} {condition} ${target:,.2f}"

    elif subcmd == "alerts":
        profile = mgr.get_profile(user_id)
        if not profile.alerts:
            return "📭 No alerts set."
        lines = ["🔔 **Price Alerts:**\n"]
        for a in profile.alerts:
            status = "🟢" if a.enabled else "⚪"
            price_str = f"${a.current_value:,.2f}" if a.current_value else "N/A"
            lines.append(
                f"{status} `{a.alert_id[-6:]}` — {a.asset} {a.condition} "
                f"${a.target_value:,.2f} (current: {price_str})"
            )
        return "\n".join(lines)

    elif subcmd == "delalert":
        if len(context.args) < 2:
            return "Usage: /fin delalert <alert_id>"
        alert_id = context.args[1]
        profile = mgr.get_profile(user_id)
        for a in profile.alerts:
            if a.alert_id.endswith(alert_id):
                mgr.remove_alert(user_id, a.alert_id)
                return f"✅ Alert removed: {a.asset} {a.condition} {a.target_value}"
        return "❌ Alert not found."

    elif subcmd == "watch":
        if len(context.args) < 2:
            return "Usage: /fin watch <symbol> [notes]"
        symbol = context.args[1].upper()
        notes = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        ok = mgr.add_to_watchlist(user_id, symbol, notes)
        return f"✅ Added {symbol} to watchlist." if ok else f"⚠️ {symbol} already in watchlist."

    elif subcmd == "unwatch":
        if len(context.args) < 2:
            return "Usage: /fin unwatch <symbol>"
        symbol = context.args[1].upper()
        ok = mgr.remove_from_watchlist(user_id, symbol)
        return f"✅ Removed {symbol} from watchlist." if ok else f"❌ {symbol} not in watchlist."

    elif subcmd == "watchlist":
        return mgr.get_watchlist_display(user_id)

    return build_finance_commands()
