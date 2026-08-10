from cch_axcess_mcp.client import _escape_odata


def test_escape_odata_doubles_single_quotes():
    assert _escape_odata("O'Brien") == "O''Brien"


def test_escape_odata_leaves_plain_strings_unchanged():
    assert _escape_odata("SALVIN7") == "SALVIN7"
