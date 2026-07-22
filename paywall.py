import json, os, time, re, hashlib, hmac
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANS_FILE = os.path.join(BASE_DIR, "paywall_plans.json")
SUBS_FILE = os.path.join(BASE_DIR, "paywall_subs.json")
INVOICES_FILE = os.path.join(BASE_DIR, "paywall_invoices.json")

def _load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default if default is not None else {}

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

STARS_PER_USD = 100
IDR_PER_MONTH = 28000

class Paywall:
    def __init__(self):
        self.plans = _load_json(PLANS_FILE, {})
        self.subs = _load_json(SUBS_FILE, {})
        self.invoices = _load_json(INVOICES_FILE, [])

    def _save_plans(self):
        _save_json(PLANS_FILE, self.plans)

    def _save_subs(self):
        _save_json(SUBS_FILE, self.subs)

    def _save_invoices(self):
        _save_json(INVOICES_FILE, self.invoices)

    def create_plan(self, creator_id, name, description, stars_price, duration_days, channel_id=None, max_members=0):
        pid = hashlib.md5(f"{creator_id}:{name}:{time.time()}".encode()).hexdigest()[:12]
        self.plans[pid] = {
            "id": pid, "creator": str(creator_id), "name": name,
            "description": description, "stars_price": stars_price,
            "duration_days": duration_days, "channel_id": channel_id,
            "max_members": max_members, "active": True,
            "created": time.time(), "subscriber_count": 0
        }
        self._save_plans()
        return pid

    def update_plan(self, plan_id, **kwargs):
        if plan_id not in self.plans:
            return False
        for k, v in kwargs.items():
            if k in ("name", "description", "stars_price", "duration_days", "channel_id", "max_members", "active"):
                self.plans[plan_id][k] = v
        self._save_plans()
        return True

    def get_plan(self, plan_id):
        return self.plans.get(plan_id)

    def list_plans(self, creator_id=None):
        if creator_id:
            return [p for p in self.plans.values() if p.get("creator") == str(creator_id) and p.get("active")]
        return [p for p in self.plans.values() if p.get("active")]

    def subscribe(self, plan_id, user_id, stars_invoice_id=None):
        plan = self.plans.get(plan_id)
        if not plan or not plan.get("active"):
            return None, "Plan not found or inactive"
        if plan.get("max_members") and plan.get("subscriber_count", 0) >= plan["max_members"]:
            return None, "Plan is sold out"
        uid = str(user_id)
        now = time.time()
        existing = self.subs.get(uid, {}).get(plan_id)
        if existing and existing.get("expires", 0) > now:
            existing["expires"] += plan["duration_days"] * 86400
            existing["renewed"] = now
        else:
            self.subs.setdefault(uid, {})[plan_id] = {
                "user_id": uid, "plan_id": plan_id,
                "started": now, "expires": now + plan["duration_days"] * 86400,
                "renewed": now, "active": True
            }
            plan["subscriber_count"] = plan.get("subscriber_count", 0) + 1
        if stars_invoice_id:
            self.invoices.append({
                "id": stars_invoice_id, "plan_id": plan_id, "user_id": uid,
                "stars": plan["stars_price"], "time": now, "status": "paid"
            })
            if len(self.invoices) > 1000:
                self.invoices = self.invoices[-500:]
            self._save_invoices()
        self._save_subs()
        self._save_plans()
        return self.subs[uid][plan_id], None

    def cancel(self, plan_id, user_id):
        uid = str(user_id)
        if uid in self.subs and plan_id in self.subs[uid]:
            self.subs[uid][plan_id]["active"] = False
            self._save_subs()
            return True
        return False

    def get_subscription(self, plan_id, user_id):
        uid = str(user_id)
        return self.subs.get(uid, {}).get(plan_id)

    def user_subs(self, user_id):
        uid = str(user_id)
        return list(self.subs.get(uid, {}).values())

    def check_expired(self):
        now = time.time()
        expired = []
        for uid, plans in list(self.subs.items()):
            for pid, sub in list(plans.items()):
                if sub.get("active") and sub.get("expires", 0) < now:
                    sub["active"] = False
                    expired.append((uid, pid))
        if expired:
            self._save_subs()
        return expired

    def create_stars_invoice(self, plan_id, user_id):
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        invoice_id = hashlib.md5(f"star_{plan_id}_{user_id}_{time.time()}".encode()).hexdigest()[:16]
        self.invoices.append({
            "id": invoice_id, "plan_id": plan_id, "user_id": str(user_id),
            "stars": plan["stars_price"], "time": time.time(), "status": "pending"
        })
        if len(self.invoices) > 1000:
            self.invoices = self.invoices[-500:]
        self._save_invoices()
        return invoice_id

    def confirm_payment(self, invoice_id):
        for inv in self.invoices:
            if inv.get("id") == invoice_id:
                inv["status"] = "paid"
                self._save_invoices()
                return True
        return False

    def format_plan(self, plan):
        price_idr = IDR_PER_MONTH
        duration_days = plan["duration_days"]
        total = price_idr * (duration_days // 30) if duration_days >= 30 else price_idr
        duration_str = f"{duration_days}d" if duration_days < 30 else f"{duration_days // 30}bln"
        cap = f" (max {plan['max_members']} member)" if plan.get("max_members") else ""
        return (f"🛒 {plan['name']}\n"
                f"  {plan['description'][:100]}\n"
                f"  Rp{total:,} / {duration_str}{cap}\n"
                f"  ID: {plan['id']}")

    def payment_instructions(self):
        return (
            "💳 Pembayaran:\n"
            "  Harga: Rp28.000/bulan\n"
            "  Transfer ke Dana: 081295316346 a/n [Owner]\n"
            "  Kirim bukti transfer ke bot setelah bayar.\n\n"
            "⚠️ Tidak punya Dana Premium / limit?\n"
            "  ✅ Gunakan hotelmurah.com\n"
            "  Daftar di hotelmurah.com untuk transaksi mudah."
        )

    def calculate_price(self, duration_days):
        months = max(1, duration_days // 30)
        return IDR_PER_MONTH * months

_paywall = None
def get_paywall():
    global _paywall
    if _paywall is None:
        _paywall = Paywall()
    return _paywall
