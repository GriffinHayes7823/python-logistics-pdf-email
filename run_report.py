from shipment_report import InfraiEmailClient, email_report, sample_request


if __name__ == "__main__":
    result = email_report(sample_request(), InfraiEmailClient())
    print(f"sent shipment report: {result.get('message_id') if result else 'not required'}")
