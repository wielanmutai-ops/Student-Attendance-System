from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an admin user for the system'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')
    
    def handle(self, *args, **options):
        email = options.get('email') or 'admin@university.edu'
        password = options.get('password') or 'admin123'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin with email {email} already exists'))
            return
        
        admin = User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            user_type='admin',
            is_approved=True
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'Admin user created successfully!\n'
            f'Email: {email}\n'
            f'Password: {password}'
        ))