from pydantic import BaseModel


class Measurement(BaseModel):
    name: str
    unit: str


class Transform(BaseModel):
    name: str
    expression: str


class Metric(BaseModel):
    name: str
    expression: str


class AssetModel(BaseModel):
    model_id: str
    name: str
    measurements: list[Measurement] = []
    transforms: list[Transform] = []
    metrics: list[Metric] = []


class Asset(BaseModel):
    asset_id: str
    model_id: str
    tenant_id: str
    site_id: str
    area_id: str


class LocalSiteWiseRegistry:
    def __init__(self):
        self.asset_models: dict[str, AssetModel] = {}
        self.assets: dict[str, Asset] = {}

    def register_model(self, model: AssetModel) -> None:
        self.asset_models[model.model_id] = model

    def register_asset(self, asset: Asset) -> None:
        self.assets[asset.asset_id] = asset
