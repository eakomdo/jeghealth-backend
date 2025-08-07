from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Create default roles for the application'

    def handle(self, *args, **options):
        # Create user role
        user_role, created = Role.objects.get_or_create(
            name='user',
            defaults={
                'description': 'Default user role for patients',
                'permissions': {
                    'can_view_own_data': True,
                    'can_edit_own_profile': True,
                    'can_add_health_metrics': True,
                    'can_view_own_health_metrics': True,
                    'can_book_appointments': True,
                    'can_view_own_appointments': True,
                }
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "user" role')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"user" role already exists')
            )

        # Create provider role
        provider_role, created = Role.objects.get_or_create(
            name='provider',
            defaults={
                'description': 'Healthcare provider role for doctors and medical professionals',
                'permissions': {
                    'can_view_own_data': True,
                    'can_edit_own_profile': True,
                    'can_view_appointments': True,
                    'can_manage_appointments': True,
                    'can_view_patient_data': True,
                    'can_add_medical_records': True,
                    'can_prescribe_medications': True,
                    'can_update_appointment_status': True,
                    'can_view_patient_health_metrics': True,
                }
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "provider" role')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"provider" role already exists')
            )

        # Create admin role
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={
                'description': 'Administrator role with full system access',
                'permissions': {
                    'can_view_own_data': True,
                    'can_edit_own_profile': True,
                    'can_view_all_data': True,
                    'can_manage_users': True,
                    'can_manage_providers': True,
                    'can_manage_appointments': True,
                    'can_view_analytics': True,
                    'can_manage_system_settings': True,
                }
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "admin" role')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"admin" role already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('Role setup completed successfully!')
        )
