import fitz
from pdf_utils import rect_area, intersection_area, union_rectangles

def get_occurrence_annotation_color(page, occ_rects, threshold=0.1):
    best_ratio = 0.0
    best_color = None
    try:
        if not isinstance(occ_rects, (list, tuple)):
            occ_rects = [occ_rects]
        annots = list(page.annots() or [])
        if not annots:
            return None
        for occ in occ_rects:
            for annot in annots:
                if annot.type[0] != "Highlight":
                    continue
                if not annot.colors:
                    continue
                inter = occ.intersect(annot.rect)
                if inter:
                    ratio = intersection_area(occ, annot.rect) / rect_area(occ)
                    if ratio > best_ratio:
                        best_ratio = ratio
                        color = annot.colors.get("stroke", None)
                        if color is None:
                            color = annot.colors.get("fill", None)
                        best_color = color
        if best_ratio >= threshold:
            return best_color
    except Exception as e:
        print("Error in get_occurrence_annotation_color:", e)
    return None

def toggle_highlight_on_page(page, keyword, highlight_color, threshold=0.1):
    occurrences = page.search_for(keyword)
    if not occurrences:
        return None

    union = union_rectangles(occurrences)
    existing_color = get_occurrence_annotation_color(page, occurrences, threshold)
    
    if existing_color is not None:
        try:
            for annot in list(page.annots() or []):
                if annot.type[0] == "Highlight":
                    ratio = intersection_area(union, annot.rect) / rect_area(union)
                    if ratio >= threshold:
                        annot.delete()
        except Exception as e:
            print("Error removing annotations:", e)
        return "removed"
    else:
        if highlight_color is None:
            return "no_color"
        try:
            for occ in occurrences:
                annot = page.add_highlight_annot(occ)
                annot.set_colors(stroke=highlight_color)
                annot.update()
        except Exception as e:
            print("Error adding annotations:", e)
        return "added"

