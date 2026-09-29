from django.core.management.base import BaseCommand

from chat.services import flag_stale


class Command(BaseCommand):
    help = "Flag replies stuck in progress (e.g. after a server restart) for reconciliation."

    def add_arguments(self, parser):
        parser.add_argument("--minutes", type=int, default=10)

    def handle(self, *args, **opts):
        count = flag_stale(opts["minutes"])
        self.stdout.write(f"Flagged {count} stale reply(ies) for reconciliation.")
