import fitz  # PyMuPDF
from typing import List, Optional, Tuple

def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    """
    Konverterer en farge, representert som en tuple med verdier (r, g, b) mellom 0 og 1, 
    til en hex-streng.
    
    Eksempel:
      (1, 0, 0) -> "#ff0000"
    
    :param rgb: Tuple med tre float-verdier for rød, grønn og blå.
    :return: En streng som representerer fargen i hex-format.
    """
    return "#%02x%02x%02x" % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def union_rectangles(rects: List[fitz.Rect]) -> Optional[fitz.Rect]:
    """
    Returnerer unionen (det samlede rektangelet) av en liste med fitz.Rect-objekter.
    
    :param rects: En liste med fitz.Rect-objekter.
    :return: Et fitz.Rect som dekker alle rektanglene, eller None hvis listen er tom.
    """
    if not rects:
        return None
    x0 = min(r.x0 for r in rects)
    y0 = min(r.y0 for r in rects)
    x1 = max(r.x1 for r in rects)
    y1 = max(r.y1 for r in rects)
    return fitz.Rect(x0, y0, x1, y1)

def inflate_rect(rect: fitz.Rect, amount: float) -> fitz.Rect:
    """
    Utvider et fitz.Rect-objekt med 'amount' poeng i alle retninger.
    
    :param rect: Et fitz.Rect-objekt.
    :param amount: Antall poeng som skal legges til (positiv verdi utvider rektangelet).
    :return: Et nytt fitz.Rect-objekt som er utvidet.
    """
    return fitz.Rect(rect.x0 - amount, rect.y0 - amount, rect.x1 + amount, rect.y1 + amount)

def rect_area(rect: fitz.Rect) -> float:
    """
    Beregner arealet til et fitz.Rect-objekt.
    
    :param rect: Et fitz.Rect-objekt.
    :return: Arealet som en float.
    """
    return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)

def intersection_area(rect1: fitz.Rect, rect2: fitz.Rect) -> float:
    """
    Beregner overlappingsarealet mellom to fitz.Rect-objekter.
    
    :param rect1: Første rektangel.
    :param rect2: Andre rektangel.
    :return: Arealet av overlappende område. Returnerer 0 dersom de ikke overlapper.
    """
    inter = rect1.intersect(rect2)
    if inter is None:
        return 0
    return rect_area(inter)
