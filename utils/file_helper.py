import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def save_stall_image(file_content: bytes, filename: str) -> str:
    """
    Save stall image to stallImages folder and return the relative path
    
    Args:
        file_content: Binary content of the image file
        filename: Original filename
        
    Returns:
        Relative URL path to the image
    """
    try:
        # Create stallImages directory if it doesn't exist
        base_dir = Path(__file__).parent.parent
        images_dir = base_dir / "stallImages"
        
        # Create directory with parents if needed
        images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Images directory: {images_dir}")
        logger.info(f"Directory exists: {images_dir.exists()}")
        
        # Generate unique filename to avoid conflicts
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = images_dir / unique_name
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Verify file was saved
        if file_path.exists():
            logger.info(f"File saved successfully: {file_path}")
        else:
            logger.error(f"File was not saved: {file_path}")
        
        # Return relative URL path
        return f"/stallImages/{unique_name}"
    
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}", exc_info=True)
        raise

def delete_stall_image(image_url: str) -> bool:
    """
    Delete stall image from stallImages folder
    
    Args:
        image_url: Relative URL path to the image (e.g., "/stallImages/uuid.jpg")
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        if not image_url:
            return False
        
        # Extract filename from URL
        # Expected format: /stallImages/filename
        if not image_url.startswith("/stallImages/"):
            logger.warning(f"Invalid image URL format: {image_url}")
            return False
        
        filename = image_url.replace("/stallImages/", "")
        
        # Build full file path
        base_dir = Path(__file__).parent.parent
        file_path = base_dir / "stallImages" / filename
        
        # Delete file if it exists
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Image deleted successfully: {file_path}")
            return True
        else:
            logger.warning(f"Image file not found: {file_path}")
            return False
    
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}", exc_info=True)
        return False
