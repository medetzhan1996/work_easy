import json

from .models import Funnel


def get_formatted_funnels():
    funnels = Funnel.objects.all().prefetch_related('card_set')

    formatted_data = [
        {
            "id": str(funnel.pk),
            "title": funnel.title,
            "class": "",
            "item": [
                {
                    "id": str(card.pk),
                    "title": card.comment or "No comment",
                    "class": ["card-funnelget_formatted_funnels"]
                }
                for card in funnel.card_set.all()
            ],
        }
        for funnel in funnels
    ]

    return formatted_data
