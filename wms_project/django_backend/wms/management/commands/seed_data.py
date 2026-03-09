"""
Management command to seed demo data:
  python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wms.models import UserProfile, SKU


DEMO_USERS = [
    {'username': 'admin',      'password': 'admin123',   'role': 'inbound_admin',  'full_name': 'Ahmad Fauzi'},
    {'username': 'outadmin',   'password': 'out123',     'role': 'outbound_admin', 'full_name': 'Fira Handayani'},
    {'username': 'security',   'password': 'sec123',     'role': 'security',       'full_name': 'Budi Santoso'},
    {'username': 'checker1',   'password': 'check123',   'role': 'checker',        'full_name': 'Citra Dewi'},
    {'username': 'picker1',    'password': 'pick123',    'role': 'picker',         'full_name': 'Doni Prasetyo'},
    {'username': 'supervisor', 'password': 'super123',   'role': 'supervisor',     'full_name': 'Eko Wibowo'},
]

DEMO_SKUS = [
    {'sku_number': 'SKU-001', 'product_name': 'Aqua Botol 600ml',       'cse_per_pallet': 48},
    {'sku_number': 'SKU-002', 'product_name': 'Indomie Goreng Karton',   'cse_per_pallet': 60},
    {'sku_number': 'SKU-003', 'product_name': 'Pocari Sweat 350ml',      'cse_per_pallet': 36},
    {'sku_number': 'SKU-004', 'product_name': 'Good Day Cappuccino',     'cse_per_pallet': 72},
    {'sku_number': 'SKU-005', 'product_name': 'Teh Botol Sosro 450ml',   'cse_per_pallet': 54},
    {'sku_number': 'SKU-006', 'product_name': 'Mie Sedaap Original',     'cse_per_pallet': 60},
    {'sku_number': 'SKU-007', 'product_name': 'Sprite 1.5L',             'cse_per_pallet': 24},
    {'sku_number': 'SKU-008', 'product_name': 'Chitato Reguler 68g',     'cse_per_pallet': 80},
    {'sku_number': 'SKU-009', 'product_name': 'Ovaltine Tin 400g',       'cse_per_pallet': 30},
    {'sku_number': 'SKU-010', 'product_name': 'Pepsodent Tube 190g',     'cse_per_pallet': 96},
]


class Command(BaseCommand):
    help = 'Seed demo users and SKU masterlist data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo users...')
        for u in DEMO_USERS:
            user, created = User.objects.get_or_create(username=u['username'])
            user.set_password(u['password'])
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': u['role'], 'full_name': u['full_name']}
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f"  {status}: {u['username']} ({u['role']})")

        self.stdout.write('\nSeeding SKU masterlist...')
        for s in DEMO_SKUS:
            _, created = SKU.objects.update_or_create(
                sku_number=s['sku_number'],
                defaults={'product_name': s['product_name'], 'cse_per_pallet': s['cse_per_pallet']}
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f"  {status}: {s['sku_number']} — {s['product_name']}")

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
