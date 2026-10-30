"""Stable decimal dimensions shared by all geometry emitters."""
def decimal(value):
    """PGF dimensions do not accept Python scientific notation."""
    result=f"{float(value):.8f}".rstrip("0").rstrip(".")
    return "0" if result in ("", "-0") else result

