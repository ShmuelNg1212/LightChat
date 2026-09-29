import threading

from django.contrib.auth import get_user_model
from django.db import OperationalError, connection
from django.test import TransactionTestCase

from billing import services


class ConcurrentHoldTests(TransactionTestCase):
    """Many simultaneous holds (double clicks, several tabs) must never overspend."""

    def test_parallel_holds_never_exceed_available(self):
        user = get_user_model().objects.create_user("ana", password="x")
        services.grant(user, 1_000_000)
        results = []
        barrier = threading.Barrier(10)

        def attempt():
            barrier.wait()
            outcome = None
            try:
                services.hold(user, 300_000)
                outcome = "held"
            except services.InsufficientCredit:
                outcome = "refused"
            except OperationalError as exc:
                outcome = f"error: {exc}"
            finally:
                connection.close()
            results.append(outcome)

        threads = [threading.Thread(target=attempt) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(sorted(results), ["held"] * 3 + ["refused"] * 7, results)
        wallet = services.get_wallet(user)
        self.assertEqual(wallet.held, 900_000)
        self.assertEqual(wallet.entries.filter(kind="hold").count(), 3)
