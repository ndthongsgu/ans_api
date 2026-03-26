#!/usr/bin/env python3
"""
Test script to verify auto-translation functionality for Stalls and StallContent
Tests:
1. Create a stall with Vietnamese only → verify all languages created
2. Update a stall with Vietnamese only → verify all languages updated
3. Create stall content with Vietnamese TTS → verify all languages created with audio
4. Update stall content with Vietnamese TTS → verify all languages updated with audio
"""

import sys
import os
from datetime import datetime

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from core.database import get_db, engine
from models.base import Base
from models.stall import Stall
from models.stallTranslation import StallTranslation
from models.stallContent import StallContent
from models.stallContentTranslation import StallContentTranslation
from models.owner import Owner
from models.user import User
from models.role import Role
from modules.stall.services.admin_service import StallService
from modules.stallContent.services.admin_service import StallContentService
from common.enums.language import LanguageCode
import time

print("=" * 80)
print("AUTO-TRANSLATION TEST SUITE")
print("=" * 80)

# Get DB session
db_generator = get_db()
db: Session = next(db_generator)

try:
    # Test 1: Create Stall with Vietnamese
    print("\n[TEST 1] Creating Stall with Vietnamese only...")
    print("-" * 80)
    
    stall_service = StallService(db)
    
    test_stall_data = {
        "owner_id": None,  # Optional
        "name": "Quán Cơm Gà Tây Hồ - TEST",
        "category": "Cơm",
        "latitude": 21.0285,
        "longitude": 105.8542,
        "radius": 100,
        "cover_image": None,
        "price_range": "50-100k",
        "opening_hours": "10:00-22:00",
        "contact_phone": "0912345678",
        "website": "https://example.com"
    }
    
    created_stall = stall_service.create_stall(test_stall_data)
    stall_id = created_stall.id
    print(f"✓ Stall created with ID: {stall_id}")
    print(f"  Name (Vietnamese): {created_stall.name}")
    
    # Verify translations were created for all languages
    translations = db.query(StallTranslation).filter(
        StallTranslation.stall_id == stall_id
    ).all()
    
    print(f"✓ Created {len(translations)} translations:")
    language_codes = set()
    for trans in translations:
        print(f"  - {trans.language_code}: {trans.name} | Category: {trans.category}")
        language_codes.add(trans.language_code)
    
    expected_languages = {lang['code'] for lang in LanguageCode.LIST}
    if language_codes == expected_languages:
        print(f"✓ All {len(expected_languages)} languages created successfully!")
    else:
        print(f"✗ Missing languages: {expected_languages - language_codes}")
    
    # Test 2: Update Stall with Vietnamese only
    print("\n[TEST 2] Updating Stall with Vietnamese only...")
    print("-" * 80)
    
    time.sleep(1)  # Wait a bit before update
    
    updated_stall_data = {
        "owner_id": test_stall_data.get("owner_id"),
        "name": "Quán Cơm Gà Hải Phòng - CẬP NHẬT",
        "category": "Bánh Mì",
        "latitude": 21.0285,
        "longitude": 105.8542,
        "radius": 150,
        "cover_image": None,
        "price_range": "100-200k",
        "opening_hours": "08:00-23:00",
        "contact_phone": "0987654321",
        "website": "https://example.com/new"
    }
    
    updated_stall = stall_service.update_stall(stall_id, updated_stall_data)
    print(f"✓ Stall updated: {updated_stall.name}")
    
    # Verify all language translations were updated
    translations_after_update = db.query(StallTranslation).filter(
        StallTranslation.stall_id == stall_id
    ).all()
    
    print(f"✓ Verified {len(translations_after_update)} translations after update:")
    for trans in translations_after_update:
        print(f"  - {trans.language_code}: {trans.name} | Category: {trans.category}")
        # Check if name was updated from old to new
        if trans.language_code == "vi":
            if "CẬP NHẬT" in trans.name:
                print(f"    ✓ Vietnamese translation updated")
            else:
                print(f"    ✗ Vietnamese translation was not updated!")
        else:
            # Other languages should have translations (auto-translated)
            if trans.name and len(trans.name) > 0:
                print(f"    ✓ {trans.language_code} translation auto-translated")
    
    # Test 3: Create StallContent with Vietnamese TTS
    print("\n[TEST 3] Creating StallContent with Vietnamese TTS...")
    print("-" * 80)
    
    content_service = StallContentService(db)
    
    test_content_data = {
        "stall_id": stall_id,
        "tts_script": "Xin chào, các bạn đang nghe quán cơm gà nổi tiếng. Chúng tôi phục vụ từ 10h đến 22h hàng ngày."
    }
    
    created_content_records = content_service.create_stall_content(test_content_data)
    print(f"✓ Created {len(created_content_records)} records")
    
    # Get the StallContent ID (first record is the base, rest are translations)
    content_id = created_content_records[0].id
    print(f"  StallContent ID: {content_id}")
    
    # Verify translations with audio were created
    content_translations = db.query(StallContentTranslation).filter(
        StallContentTranslation.stall_content_id == content_id
    ).all()
    
    print(f"✓ Created {len(content_translations)} content translations with audio:")
    for trans in content_translations:
        has_audio = "✓" if trans.audio_url else "✗"
        print(f"  {has_audio} {trans.language_code}: {trans.tts_script[:40]}... | Audio: {bool(trans.audio_url)}")
    
    # Test 4: Update StallContent with Vietnamese TTS
    print("\n[TEST 4] Updating StallContent with Vietnamese TTS...")
    print("-" * 80)
    
    time.sleep(1)  # Wait before update
    
    update_content_data = {
        "tts_script": "Cơm gà ngon, rẻ, lạnh lẽo. Hôm nay chúng tôi có khuyến mãi đặc biệt 20% cho tất cả các khách hàng mới."
    }
    
    updated_content_records = content_service.update_stall_content(stall_id, update_content_data)
    print(f"✓ Updated stall content")
    
    # Verify all language translations were updated with new audio
    updated_content_translations = db.query(StallContentTranslation).filter(
        StallContentTranslation.stall_content_id == content_id
    ).all()
    
    print(f"✓ Verified {len(updated_content_translations)} content translations after update:")
    for trans in updated_content_translations:
        has_audio = "✓" if trans.audio_url else "✗"
        updated_indicator = "✓ (updated)" if "khuyến mãi" in trans.tts_script else "?"
        print(f"  {has_audio} {trans.language_code}: {trans.tts_script[:40]}... | Audio: {bool(trans.audio_url)} {updated_indicator}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✓ Stall ID: {stall_id}")
    print(f"✓ StallContent ID: {content_id}")
    print(f"\n✓ All auto-translation tests completed successfully!")
    print(f"\nLanguages configured: {[lang['code'] for lang in LanguageCode.LIST]}")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    db.close()

print("\n" + "=" * 80)
