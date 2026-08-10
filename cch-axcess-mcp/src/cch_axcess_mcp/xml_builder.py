import base64
from xml.etree.ElementTree import Element, SubElement, tostring


def build_payload_xml_bytes(return_header: dict, taxpayer_details: dict, views: list) -> bytes:
    """
    return_header: atributos de <ReturnHeader> (ClientID, TaxYear, ReturnType,
      ReturnVersion, EINorSSN, ControlNumber, OfficeName, BusinessUnitName, ...).
    taxpayer_details: atributos de <TaxPayerDetails> (NameLine1, NameLine2).
    views: lista de {hierarchy, entity_id (opcional), sections: [{name, fields:
      [{location, location_type, value}]}]}.

    Devuelve el XML Payload completo codificado en UTF-16 (formato Tax Transfer).
    """
    payload = Element(
        "Payload",
        {
            "DataType": "Tax",
            "DataFormat": "Standard",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
    )
    tax_return = SubElement(payload, "TaxReturn")
    SubElement(tax_return, "ReturnHeader", {k: str(v) for k, v in return_header.items()})
    SubElement(tax_return, "TaxPayerDetails", {k: str(v) for k, v in taxpayer_details.items()})

    for view in views:
        view_el = SubElement(tax_return, "View", {"xsi:type": "Worksheet"})
        SubElement(view_el, "Identifier", {"Hierarchy": view["hierarchy"]})
        if view.get("entity_id") is not None:
            controls = SubElement(view_el, "Controls")
            SubElement(controls, "Entity", {"ID": str(view["entity_id"])})
        for section in view.get("sections", []):
            section_el = SubElement(view_el, "WorkSheetSection", {"Name": section["name"]})
            for field in section.get("fields", []):
                SubElement(
                    section_el,
                    "FieldData",
                    {
                        "Location": field["location"],
                        "LocationType": field.get("location_type", "FieldID"),
                        "Value": str(field["value"]),
                    },
                )

    return tostring(payload, encoding="utf-16")


def build_configuration_xml(
    import_mode: str = "MatchAndUpdate",
    case_sensitive_matching: bool = False,
    invalid_content_error_handling: str = "RejectReturnOnAnyError",
    calc_return_after_import: bool = False,
) -> str:
    root = Element("TaxDataImportOptions")
    SubElement(root, "ImportMode").text = import_mode
    SubElement(root, "CaseSensitiveMatching").text = str(case_sensitive_matching).lower()
    SubElement(root, "InvalidContentErrorHandling").text = invalid_content_error_handling
    SubElement(root, "CalcReturnAfterImport").text = str(calc_return_after_import).lower()
    return tostring(root, encoding="unicode")


def build_and_encode(return_header: dict, taxpayer_details: dict, views: list) -> str:
    """Arma el Payload XML y lo devuelve en base64, listo para FileDataList."""
    xml_bytes = build_payload_xml_bytes(return_header, taxpayer_details, views)
    return base64.b64encode(xml_bytes).decode("ascii")
