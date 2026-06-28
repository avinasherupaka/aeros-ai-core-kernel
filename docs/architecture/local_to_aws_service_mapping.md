# Local to AWS Service Mapping

- `ingestion/edge_gateway.py` → AWS IoT Greengrass V2 component pattern
- `ot/mqtt_publisher.py` + `ot/mqtt_subscriber.py` → AWS IoT Core publish/subscribe
- `storage/local_sitewise.py` → AWS IoT SiteWise model abstraction
- `storage/object_store.py` → S3 evidence/object paths
- `storage/graph_adapter.py` → Neptune-backed graph adapter target
