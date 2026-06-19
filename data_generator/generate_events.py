# data_generator/generate_events.py
"""Synthetic e-commerce event generator. Reads real Olist IDs, writes JSONL events,
and in --mode bad injects deliberate data-quality problems. --sink kinesis sends to AWS."""
import argparse, json, random, uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
import boto3

RAW = Path("data/raw/historical")
PAYMENT_TYPES = ["credit_card", "boleto", "voucher", "debit_card"]
CHANNELS = ["mobile_app", "web", "marketplace"]

def now_iso(jitter=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=jitter)).isoformat()

def load_reference_ids(sample=3000):
    prod = pd.read_csv(RAW/"olist_products_dataset.csv", usecols=["product_id"])["product_id"].dropna()
    sell = pd.read_csv(RAW/"olist_sellers_dataset.csv", usecols=["seller_id"])["seller_id"].dropna()
    cust = pd.read_csv(RAW/"olist_customers_dataset.csv", usecols=["customer_id"])["customer_id"].dropna()
    return (prod.sample(min(sample, len(prod))).tolist(), sell.tolist(),
            cust.sample(min(sample, len(cust))).tolist())

def make_order_created(order_id, cust, prod, sell):
    return {"event_id": f"evt_{uuid.uuid4().hex[:12]}", "event_type": "order_created",
            "event_timestamp": now_iso(), "order_id": order_id, "customer_id": cust,
            "product_id": prod, "seller_id": sell, "quantity": random.randint(1, 4),
            "unit_price": round(random.uniform(10, 300), 2), "channel": random.choice(CHANNELS)}

def make_payment_processed(order_id, amount):
    return {"event_id": f"evt_{uuid.uuid4().hex[:12]}", "event_type": "payment_processed",
            "event_timestamp": now_iso(2), "order_id": order_id,
            "payment_type": random.choice(PAYMENT_TYPES), "payment_status": "approved",
            "payment_value": amount}

def make_inventory_updated(prod, qty):
    return {"event_id": f"evt_{uuid.uuid4().hex[:12]}", "event_type": "inventory_updated",
            "event_timestamp": now_iso(3), "product_id": prod, "warehouse_id": f"wh_{random.randint(1,5):02d}",
            "change_type": "sale", "quantity_change": -qty, "available_quantity": random.randint(0, 200)}

def maybe_corrupt(event, bad_rate):
    if random.random() > bad_rate:
        return [event]
    et = event["event_type"]
    if et == "order_created":
        if random.random() < 0.5: event["customer_id"] = None
        else: return [event, dict(event)]
    elif et == "payment_processed":
        c = random.random()
        if c < 0.4: event["payment_value"] = -abs(event["payment_value"])
        elif c < 0.7: event["payment_type"] = "not_defined"
        else: return [event, dict(event)]
    elif et == "inventory_updated":
        event["available_quantity"] = -random.randint(1, 20)
    return [event]

def send_to_kinesis(records, stream_name, region="us-east-1"):
    client = boto3.client("kinesis", region_name=region)
    sent = 0
    for i in range(0, len(records), 500):
        batch = records[i:i+500]
        client.put_records(
            StreamName=stream_name,
            Records=[{"Data": (json.dumps(r) + "\n").encode("utf-8"),
                      "PartitionKey": str(r.get("order_id") or r.get("product_id") or "k")}
                     for r in batch])
        sent += len(batch)
    return sent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", type=int, default=1000)
    ap.add_argument("--mode", choices=["normal", "bad"], default="normal")
    ap.add_argument("--sink", choices=["local", "kinesis"], default="local")
    ap.add_argument("--stream", default="ecom-lakehouse-events")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--out", default="data/raw/streaming/events.jsonl")
    args = ap.parse_args()

    bad_rate = 0.15 if args.mode == "bad" else 0.0
    products, sellers, customers = load_reference_ids()

    records = []
    for _ in range(args.events):
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        cust, prod, sell = random.choice(customers), random.choice(products), random.choice(sellers)
        oc = make_order_created(order_id, cust, prod, sell)
        amount = round(oc["quantity"] * oc["unit_price"], 2)
        for e in [oc, make_payment_processed(order_id, amount), make_inventory_updated(prod, oc["quantity"])]:
            records.extend(maybe_corrupt(e, bad_rate))

    if args.sink == "kinesis":
        sent = send_to_kinesis(records, args.stream, args.region)
        print(f"Sent {sent} events to Kinesis '{args.stream}' ({args.mode} mode)")
    else:
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        print(f"Wrote {len(records)} events ({args.mode} mode) -> {out}")

if __name__ == "__main__":
    main()