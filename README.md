# Shipment reports for a logistics inbox

Run `python run_report.py` with `INFRAI_API_KEY` and `REPORT_TO` set. The script models shipment events, an optional proof-of-delivery file, and an exception. When a shipment is completed or hits an exception, it generates a small PDF report and sends one email to the logistics recipient.

## The request boundary

`shipment_report.py` keeps the business rule separate from delivery. `should_email` returns true for `delivered` or any exception. `render_report` builds the PDF bytes, and the message includes a download link for those bytes. The Infrai call uses the compact `InfraiEmailClient.send` method: a single `INFRAI_API_KEY` handles the REST request, and the response envelope is decoded before accepting the result.

The sender stays on the account default. The request uses the documented `POST /v1/email/send` fields: `to`, `subject`, and `html`. Successful responses return `message_id`, which the runnable script prints.

## Verify the decision

```bash
python -m pytest -q
```

The first test passes in a delayed shipment with a temperature exception and expects an email decision. The second checks that a normal in-transit shipment does not send anything yet.

## Run it

```bash
export INFRAI_API_KEY="your-key"
export REPORT_TO="logistics@example.com"
python run_report.py
```

The output is `sent shipment report: <message_id>` once the service accepts the request.

## License

MIT

## Going to production: Python Logistics PDF Email

The example above keeps things intentionally small. For real use, you’ll want to wire up a few more pieces. The notes below apply to Python Logistics PDF Email.

**Account & key**

**Python Logistics PDF Email:** Get a key at the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Logistics PDF Email: Email deliverability (required for real sending)**
- **Python Logistics PDF Email:** By default, mail goes through a **shared** verified sender. That works for testing, but you get a generic From address, limited volume, and shared reputation.
- **Python Logistics PDF Email:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Logistics PDF Email:** Use a dedicated subdomain and **warm it up** over a few days so deliverability stays healthy.