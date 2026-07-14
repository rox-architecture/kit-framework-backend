from cee.models.edc.entity import JsonLdEntity


class Edr(JsonLdEntity):
    """EDC EDR model."""

    transfer_process_id: str
    agreement_id: str
    contract_negotiation_id: str
    asset_id: str
    provider_id: str
    created_at: int
