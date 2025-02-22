"""Utility functions for PDF Highlighter."""
import os
import pygame
import fitz


def play_sound(sound_file, sound_enabled):
    """Play a sound file if sound is enabled and the file exists."""
    if sound_enabled and os.path.exists(sound_file):
        pygame.mixer.Sound(sound_file).play()


def rgb_to_hex(rgb):
    """Convert RGB tuple (0-1 values) to hex string."""
    return "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))


def rect_area(rect):
    """Calculate the area of a rectangle (fitz.Rect)."""
    return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)


def intersection_area(rect1, rect2):
    """Calculate the intersection area between two rectangles."""
    inter = rect1.intersect(rect2)
    if inter is None:
        return 0
    return rect_area(inter)


def occurrence_is_highlighted(page, occ_rect, threshold=0.5):
    """
    Check if an occurrence is highlighted.
    
    Args:
        page: The PDF page object
        occ_rect: The rectangle of the occurrence
        threshold: Minimum overlap ratio to consider highlighted
        
    Returns:
        The highlight color if found, None otherwise
    """
    try:
        for annot in page.annots():
            if annot.type[0] == "Highlight":
                inter = occ_rect.intersect(annot.rect)
                if inter:
                    ratio = intersection_area(occ_rect, annot.rect) / rect_area(occ_rect)
                    if ratio >= threshold:
                        if annot.colors and "stroke" in annot.colors:
                            return annot.colors["stroke"]
    except Exception:
        pass
    return None