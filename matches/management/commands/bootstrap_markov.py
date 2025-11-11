from __future__ import annotations

from typing import Iterable, Optional

from django.core.management.base import BaseCommand
from django.db import transaction

from matches.models import Match


class Command(BaseCommand):
    help = "Initialize Markov runtime fields (seed/token/state) on existing matches."

    def add_arguments(self, parser):
        status_choices = [choice for choice, _ in Match._meta.get_field("status").choices]
        parser.add_argument(
            "--status",
            choices=status_choices,
            help="Filter matches by status before applying changes.",
        )
        parser.add_argument(
            "--match-ids",
            nargs="+",
            type=int,
            help="If provided, restrict updates to the given match IDs.",
        )
        parser.add_argument(
            "--reset-status",
            choices=["keep", "scheduled", "in_progress"],
            default="keep",
            help="Optionally move matches back to a specific status after resetting state.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="By default matches that already have markov_seed are skipped. "
                 "Pass this flag to overwrite existing state.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without persisting anything.",
        )

    def handle(self, *args, **options):
        status_filter: Optional[str] = options.get("status")
        ids_filter: Optional[Iterable[int]] = options.get("match_ids")
        reset_status: str = options.get("reset_status")
        overwrite: bool = options.get("overwrite", False)
        dry_run: bool = options.get("dry_run", False)

        qs = Match.objects.all()
        if status_filter:
            qs = qs.filter(status=status_filter)
        if ids_filter:
            qs = qs.filter(id__in=ids_filter)

        total = qs.count()
        updated = 0

        if total == 0:
            self.stdout.write(self.style.WARNING("No matches matched the filters."))
            return

        self.stdout.write(f"Preparing {total} matches (overwrite={overwrite}, dry_run={dry_run})")

        with transaction.atomic():
            for match in qs.select_for_update():
                if not overwrite and match.markov_seed:
                    continue

                fields_to_update = {
                    "markov_seed": match.id,
                    "markov_token": None,
                    "markov_last_summary": None,
                    "markov_coefficients": None,
                    "waiting_for_next_minute": False,
                }

                if reset_status != "keep":
                    fields_to_update["status"] = reset_status
                    if reset_status == "scheduled":
                        fields_to_update["current_minute"] = 1
                        fields_to_update["processed"] = False

                updated += 1

                if dry_run:
                    self.stdout.write(
                        f"[dry-run] Match {match.id}: would update {list(fields_to_update.keys())}"
                    )
                    continue

                for field, value in fields_to_update.items():
                    setattr(match, field, value)
                match.save(update_fields=list(fields_to_update.keys()))

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run complete. {updated} matches would be updated."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated {updated} matches."))
