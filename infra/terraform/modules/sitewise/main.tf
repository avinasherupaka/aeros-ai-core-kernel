locals {
  model_template = {
    site = {
      name = "${var.site_name}-site"
      hierarchy = ["osd_manufacturing_area", "compression_room", "ahu", "tablet_press"]
    }
    measurements = [
      "relative_humidity",
      "temperature",
      "differential_pressure",
      "ahu_status",
      "tablet_press_state"
    ]
    notes = "Transforms/metrics are scaffolded in artifacts/sitewise/osd_sitewise_models.example.json"
  }
}

# Optional seed model scaffold (kept disabled by default).
resource "aws_iotsitewise_asset_model" "site" {
  count = var.enable_sitewise_resources ? 1 : 0
  name  = "${var.site_name}-site-model"

  asset_model_property {
    name     = "relative_humidity"
    data_type = "DOUBLE"
    type {
      measurement {}
    }
    unit = "%"
  }

  asset_model_property {
    name      = "temperature"
    data_type = "DOUBLE"
    type {
      measurement {}
    }
    unit = "C"
  }
}
