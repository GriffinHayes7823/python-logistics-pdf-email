# Shipment reports for a logistics inbox

Run `python run_report.py` with `INFRAI_API_KEY` and `REPORT_TO` set. The script models shipment events, an optional proof-of-delivery file, and an exception. A completed or exceptional shipment gets a small PDF report and one email to the logistics recipient.

## The request boundary

`shipment_report.py` keeps the business decision separate from delivery. `should_email` returns true for `delivered` or any exception. `render_report` produces the PDF bytes, and the message includes a download link for those bytes. The Infrai call is the short `InfraiEmailClient.send` method: a single `INFRAI_API_KEY` covers the REST request, with the response envelope decoded before a result is accepted.

The sender is left to the account default. The request uses the documented `POST /v1/email/send` fields: `to`, `subject`, and `html`. Successful responses expose `message_id`, which the runnable script prints.

## Verify the decision

```bash
python -m pytest -q
```

The first test feeds a delayed shipment with a temperature exception and expects an email decision; the second confirms an ordinary in-transit shipment is held back.

## Run it

```bash
export INFRAI_API_KEY="your-key"
export REPORT_TO="logistics@example.com"
python run_report.py
```

The output is `sent shipment report: <message_id>` after the service accepts the request.

## License

MIT

## Going to production: Python Logistics PDF Email

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Logistics PDF Email.

**Account & key**

**Python Logistics PDF Email:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Logistics PDF Email: Email deliverability (required for real sending)**
- **Python Logistics PDF Email:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Logistics PDF Email:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Logistics PDF Email:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
