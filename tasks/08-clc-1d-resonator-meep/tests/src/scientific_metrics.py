"""CLC metrics with explicit equivalent spellings of the fixed channel order."""

from scientific_core import derive_metrics as derive_core_metrics, specs
from clc_reference_inputs import configure_reference_inputs, reference_quantities


METRIC_SPECS = specs("clc")
configure_reference_inputs(METRIC_SPECS["clc_reference_compare"])
METRIC_SPECS["clc_channels"]["required_context"] = {
    "channel_order": "Global ['plus','minus'] or equivalent ['+','-']; never per-row labels. Both denote output/input e+ then e- in the fixed public basis."
}


def derive_metrics(quantities, context):
    context = dict(context)
    if context.get("operation") in ("clc_channels", "clc_reference_compare"):
        order = context.get("channel_order")
        if not isinstance(order, (list, tuple)) or tuple(order) not in (("plus", "minus"), ("+", "-")):
            raise ValueError("Declare context.channel_order=['plus','minus'] or ['+','-']; a single fixed global e+/e- mapping is required")
        context["channel_order"] = ["plus", "minus"]
    if context.get("operation") == "clc_reference_compare":
        quantities = reference_quantities(quantities, context)
    return derive_core_metrics(quantities, context)
