#!/usr/bin/env python
"""
Script to create multiple healthcare providers (doctors) at once
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeghealth_backend.settings')
django.setup()

from appointments.models import HealthcareProvider

# Sample doctors data
doctors_data = [
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@hospital.com",
        "phone_number": "+233501234568",
        "specialization": "Pediatrics",
        "license_number": "MD789012",
        "hospital_clinic": "Children's Hospital",
        "address": "456 Health Avenue, Kumasi, Ghana",
        "bio": "Experienced pediatrician specializing in child healthcare and development.",
        "years_of_experience": 12,
        "consultation_fee": 180.00
    },
    {
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@clinic.com",
        "phone_number": "+233501234569",
        "specialization": "Dermatology",
        "license_number": "MD345678",
        "hospital_clinic": "Skin Care Clinic",
        "address": "789 Derma Street, Tamale, Ghana",
        "bio": "Board-certified dermatologist with expertise in skin conditions and cosmetic procedures.",
        "years_of_experience": 8,
        "consultation_fee": 200.00
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@orthopedic.com",
        "phone_number": "+233501234570",
        "specialization": "Orthopedics",
        "license_number": "MD567890",
        "hospital_clinic": "Bone & Joint Center",
        "address": "321 Orthopedic Lane, Cape Coast, Ghana",
        "bio": "Orthopedic surgeon specializing in bone, joint, and muscle disorders.",
        "years_of_experience": 18,
        "consultation_fee": 300.00
    },
    {
        "first_name": "David",
        "last_name": "Wilson",
        "email": "david.wilson@neuro.com",
        "phone_number": "+233501234571",
        "specialization": "Neurology",
        "license_number": "MD234567",
        "hospital_clinic": "Brain Health Institute",
        "address": "654 Neural Drive, Ho, Ghana",
        "bio": "Neurologist with extensive experience in brain and nervous system disorders.",
        "years_of_experience": 20,
        "consultation_fee": 350.00
    },
    {
        "first_name": "Lisa",
        "last_name": "Anderson",
        "email": "lisa.anderson@gyn.com",
        "phone_number": "+233501234572",
        "specialization": "Gynecology",
        "license_number": "MD876543",
        "hospital_clinic": "Women's Health Center",
        "address": "987 Women's Way, Sunyani, Ghana",
        "bio": "Gynecologist and obstetrician providing comprehensive women's healthcare.",
        "years_of_experience": 14,
        "consultation_fee": 220.00
    }
]

def create_doctors():
    """Create multiple doctors"""
    created_count = 0
    
    for doctor_data in doctors_data:
        try:
            # Check if doctor already exists
            if HealthcareProvider.objects.filter(email=doctor_data['email']).exists():
                print(f"❌ Doctor with email {doctor_data['email']} already exists. Skipping...")
                continue
                
            if HealthcareProvider.objects.filter(license_number=doctor_data['license_number']).exists():
                print(f"❌ Doctor with license {doctor_data['license_number']} already exists. Skipping...")
                continue
            
            # Create doctor
            doctor = HealthcareProvider.objects.create(**doctor_data)
            print(f"✅ Created doctor: Dr. {doctor.full_name} - {doctor.specialization}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating doctor {doctor_data['first_name']} {doctor_data['last_name']}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} doctors!")
    print(f"📊 Total doctors in system: {HealthcareProvider.objects.count()}")

if __name__ == "__main__":
    create_doctors()
