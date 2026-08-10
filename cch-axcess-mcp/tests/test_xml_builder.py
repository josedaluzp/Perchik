import base64
from xml.etree import ElementTree as ET

from cch_axcess_mcp.xml_builder import (
    build_and_encode,
    build_configuration_xml,
    build_payload_xml_bytes,
)

RETURN_HEADER = {
    "ClientID": "SALVIN7",
    "TaxYear": "2025",
    "ReturnType": "P",
    "ReturnGroupName": "Default",
    "Country": "US",
    "OfficeName": "Dallas",
    "BusinessUnitName": "Development",
    "ConfigurationSet": "Default",
    "ReturnVersion": "1",
    "EINorSSN": "12-3456789",
    "ControlNumber": "20260810000001",
}
TAXPAYER_DETAILS = {"NameLine1": "SALVIN7", "NameLine2": "LLC"}
VIEWS = [
    {
        "hierarchy": "Federal\\Partner Information",
        "entity_id": 1,
        "sections": [
            {"name": "General", "fields": [{"location": "IPDSPTR.1", "value": "50.0000"}]}
        ],
    }
]


def test_build_payload_xml_bytes_is_valid_and_has_expected_structure():
    xml_bytes = build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)

    root = ET.fromstring(xml_bytes)
    assert root.tag == "Payload"
    assert root.attrib["DataType"] == "Tax"
    assert root.attrib["DataFormat"] == "Standard"

    return_header = root.find("TaxReturn/ReturnHeader")
    assert return_header.attrib["ClientID"] == "SALVIN7"
    assert return_header.attrib["ReturnType"] == "P"

    taxpayer = root.find("TaxReturn/TaxPayerDetails")
    assert taxpayer.attrib["NameLine1"] == "SALVIN7"

    identifier = root.find("TaxReturn/View/Identifier")
    assert identifier.attrib["Hierarchy"] == "Federal\\Partner Information"

    entity = root.find("TaxReturn/View/Controls/Entity")
    assert entity.attrib["ID"] == "1"

    field = root.find("TaxReturn/View/WorkSheetSection/FieldData")
    assert field.attrib["Location"] == "IPDSPTR.1"
    assert field.attrib["LocationType"] == "FieldID"
    assert field.attrib["Value"] == "50.0000"


def test_build_payload_xml_bytes_omits_controls_when_no_entity_id():
    views = [{"hierarchy": "Federal\\General\\Basic Data", "sections": []}]
    xml_bytes = build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, views)

    root = ET.fromstring(xml_bytes)
    assert root.find("TaxReturn/View/Controls") is None


def test_build_and_encode_roundtrips_through_base64():
    encoded = build_and_encode(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)
    decoded_bytes = base64.b64decode(encoded)

    assert decoded_bytes == build_payload_xml_bytes(RETURN_HEADER, TAXPAYER_DETAILS, VIEWS)


def test_build_configuration_xml_default_options():
    xml_str = build_configuration_xml()
    root = ET.fromstring(xml_str)

    assert root.tag == "TaxDataImportOptions"
    assert root.find("ImportMode").text == "MatchAndUpdate"
    assert root.find("CaseSensitiveMatching").text == "false"
    assert root.find("InvalidContentErrorHandling").text == "RejectReturnOnAnyError"
    assert root.find("CalcReturnAfterImport").text == "false"


def test_build_configuration_xml_custom_options():
    xml_str = build_configuration_xml(import_mode="Overwrite", calc_return_after_import=True)
    root = ET.fromstring(xml_str)

    assert root.find("ImportMode").text == "Overwrite"
    assert root.find("CalcReturnAfterImport").text == "true"
