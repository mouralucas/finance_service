from datetime import datetime, timezone

default_model_dict = {
    'created_at': datetime.now(timezone.utc),
    'active': True
}