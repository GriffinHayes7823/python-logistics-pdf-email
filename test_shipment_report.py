from shipment_report import ShipmentEvent, ShipmentRequest, should_email


def test_exception_requires_a_report_even_without_delivery():
    request = ShipmentRequest(
        shipment_id="SHP-7",
        recipient="ops@example.com",
        events=(ShipmentEvent("delayed", "2026-09-05T09:00:00Z", "Busan"),),
        exception="temperature threshold exceeded",
    )
    assert should_email(request) is True


def test_in_transit_shipment_does_not_email():
    request = ShipmentRequest(
        shipment_id="SHP-8",
        recipient="ops@example.com",
        events=(ShipmentEvent("in_transit", "2026-09-05T09:00:00Z", "Busan"),),
    )
    assert should_email(request) is False
