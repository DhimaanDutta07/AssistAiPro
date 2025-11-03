from datetime import datetime
import pytz

def now_iso():
    return datetime.now(pytz.utc).isoformat()