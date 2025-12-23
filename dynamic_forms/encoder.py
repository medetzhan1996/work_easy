import json
import decimal
from datetime import date, datetime


class DateTimeDecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, decimal.Decimal):
            return float(o)
        return super(DateTimeDecimalEncoder, self).default(o)
