from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):

    help = "Create restaurant staff groups and users"

    def handle(self, *args, **kwargs):

        # Create groups
        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        reception_group, _ = Group.objects.get_or_create(
            name="Reception"
        )

        waiter_group, _ = Group.objects.get_or_create(
            name="Waiter"
        )

        chef_group, _ = Group.objects.get_or_create(
            name="Chef"
        )

        # -----------------------------------------
        # Manager
        # -----------------------------------------

        manager, created = User.objects.get_or_create(
            username="manager1"
        )

        if created:
            manager.set_password("Manager@123")
            manager.save()

        manager.groups.add(manager_group)

        # -----------------------------------------
        # Reception
        # -----------------------------------------

        reception, created = User.objects.get_or_create(
            username="reception1"
        )

        if created:
            reception.set_password("Reception@123")
            reception.save()

        reception.groups.add(reception_group)

        # -----------------------------------------
        # Waiter
        # -----------------------------------------

        waiter, created = User.objects.get_or_create(
            username="waiter1"
        )

        if created:
            waiter.set_password("Waiter@123")
            waiter.save()

        waiter.groups.add(waiter_group)

        # -----------------------------------------
        # Chef
        # -----------------------------------------

        chef, created = User.objects.get_or_create(
            username="chef1"
        )

        if created:
            chef.set_password("Chef@123")
            chef.save()

        chef.groups.add(chef_group)

        self.stdout.write(
            self.style.SUCCESS(
                "Staff users created successfully!"
            )
        )

        self.stdout.write(
            "manager1 / Manager@123"
        )

        self.stdout.write(
            "reception1 / Reception@123"
        )

        self.stdout.write(
            "waiter1 / Waiter@123"
        )

        self.stdout.write(
            "chef1 / Chef@123"
        )
