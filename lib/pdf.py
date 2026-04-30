import os
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter

W, H = A4  # 595.28 x 841.89

BLACK = colors.black
WHITE = colors.white
LGREY = colors.Color(0.88, 0.88, 0.88)
MGREY = colors.Color(0.65, 0.65, 0.65)
DGREY = colors.Color(0.93, 0.93, 0.93)
RED = colors.Color(0.82, 0.1, 0.1)


def fmt_date(d) -> str:
    if not d:
        return ""
    if isinstance(d, str):
        try:
            d = datetime.fromisoformat(d)
        except Exception:
            return d
    return d.strftime("%d/%m/%Y")


def find_logo() -> str | None:
    candidates = [
        "./logo.png",
        os.path.join(os.path.dirname(__file__), "..", "logo.png"),
        "/app/logo.png",
        "../logo.png",
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


def wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    words = (text or "").split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


# ── Low-level drawing helpers ─────────────────────────────────────────────────

def hline(c, x1, x2, y, lw=0.6, color=BLACK):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x1, y, x2, y)


def vline(c, x, y1, y2, lw=0.5, color=BLACK):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x, y1, x, y2)


def filled_rect(c, x, y, w, h, fill=LGREY, stroke=None, lw=0.5):
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
        c.rect(x, y, w, h, fill=1, stroke=1)
    else:
        c.setLineWidth(0)
        c.rect(x, y, w, h, fill=1, stroke=0)


def draw_logo(c, logo_path, x, y, max_w, max_h):
    if not logo_path:
        _logo_text(c, x, y + max_h - 20)
        return
    try:
        from reportlab.lib.utils import ImageReader
        img = ImageReader(logo_path)
        iw, ih = img.getSize()
        ratio = min(max_w / iw, max_h / ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(logo_path, x, y + (max_h - dh) / 2, width=dw, height=dh, mask="auto")
    except Exception:
        _logo_text(c, x, y + max_h - 20)


def _logo_text(c, x, y):
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(RED)
    c.drawString(x, y, "Ramery")
    c.setFont("Helvetica", 7)
    c.setFillColor(MGREY)
    c.drawString(x, y - 13, "travaux publics")


# ── FICHE D'AGREMENT ──────────────────────────────────────────────────────────

def draw_fiche(c, data: dict, logo_path: str | None):
    ml, mt = 20, 20
    cw = W - 2 * ml
    ct, cb = H - mt, mt

    h1, h2, h3, h4, h5 = 95, 66, 130, 78, 112
    h6 = ct - cb - h1 - h2 - h3 - h4 - h5

    y1 = ct - h1
    y2 = y1 - h2
    y3 = y2 - h3
    y4 = y3 - h4
    y5 = y4 - h5

    # Outer border
    filled_rect(c, ml, cb, cw, ct - cb, fill=WHITE, stroke=BLACK, lw=0.8)

    # ── Header ────────────────────────────────────────────────────────────────
    fw = 92
    fx = ml + cw - fw
    hline(c, ml, ml + cw, y1, 0.8)
    vline(c, fx, y1, ct, 0.8)

    draw_logo(c, logo_path, ml + 8, y1, 115, h1 - 18)

    title = "FICHE d'AGREMENT"
    tsz = 14
    tw = stringWidth(title, "Helvetica-Bold", tsz)
    c.setFont("Helvetica-Bold", tsz)
    c.setFillColor(BLACK)
    c.drawString(ml + (fx - ml) / 2 - tw / 2, y1 + h1 / 2 - 6, title)

    c.setFont("Helvetica", 8)
    c.setFillColor(MGREY)
    c.drawString(fx + 6, ct - 18, "Fiche n°")

    num = str(data["number"])
    nsz = 24 if data["number"] >= 10 else 28
    nw = stringWidth(num, "Helvetica-Bold", nsz)
    c.setFont("Helvetica-Bold", nsz)
    c.setFillColor(BLACK)
    c.drawString(fx + fw / 2 - nw / 2, y1 + 20, num)

    # ── Chantier ──────────────────────────────────────────────────────────────
    lw = 78
    hline(c, ml, ml + cw, y2, 0.8)
    filled_rect(c, ml, y2, lw, h2)
    vline(c, ml + lw, y2, y1, 0.5, MGREY)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y2 + h2 / 2 - 5, "Chantier :")

    lines = wrap(data["project_name"].upper(), "Helvetica-Bold", 10, cw - lw - 20)
    lh = 14
    sy = y2 + h2 / 2 + len(lines) * lh / 2 - lh / 2
    for i, line in enumerate(lines):
        tw2 = stringWidth(line, "Helvetica-Bold", 10)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(ml + lw + (cw - lw) / 2 - tw2 / 2, sy - i * lh, line)

    # ── Objet ─────────────────────────────────────────────────────────────────
    hline(c, ml, ml + cw, y3, 0.8)
    filled_rect(c, ml, y3, lw, h3)
    vline(c, ml + lw, y3, y2, 0.5, MGREY)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y2 - 15, "Objet :")

    cx2, vx = ml + lw + 12, ml + lw + 172
    objet_rows = [
        ("Demande d'agrément pour\nla fourniture de :", data.get("designation", "")),
        ("Provenance :", data.get("supplier_name", "")),
        ("Utilisation :", data.get("category", "")),
        ("Date :", fmt_date(data.get("submitted_at"))),
    ]
    ry = y2 - 22
    for lbl, val in objet_rows:
        lbl_lines = lbl.split("\n")
        for li, ll in enumerate(lbl_lines):
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.Color(0.4, 0.4, 0.4))
            c.drawString(cx2, ry - li * 11, ll)
        if val:
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(BLACK)
            c.drawString(vx, ry, str(val)[:50])
        ry -= 36 if len(lbl_lines) > 1 else 28

    # ── Pièces jointes / Références ───────────────────────────────────────────
    hline(c, ml, ml + cw, y4, 0.8)
    shh = 17
    half = cw / 2
    filled_rect(c, ml, y3 - shh, cw, shh)
    hline(c, ml, ml + cw, y3 - shh, 0.5)
    vline(c, ml + half, y4, y3, 0.5)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y3 - 12, "Pièces jointes :")
    c.drawString(ml + half + 6, y3 - 12, "Références :")
    c.setFont("Helvetica", 8)
    c.drawString(ml + 5, y3 - shh - 18, "Fiche techniques :")

    # ── Contrôle interne / externe ────────────────────────────────────────────
    hline(c, ml, ml + cw, y5, 0.8)
    filled_rect(c, ml, y4 - shh, cw, shh)
    hline(c, ml, ml + cw, y4 - shh, 0.5)
    vline(c, ml + half, y5, y4, 0.5)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y4 - 12, "Contrôle interne")
    c.drawString(ml + half + 6, y4 - 12, "Contrôle externe")

    ctrl = [
        ("Nom :", data.get("submitted_by", "")),
        ("Fonction :", "Conducteur de travaux"),
        ("Date :", fmt_date(data.get("submitted_at"))),
        ("Signature :", ""),
    ]
    cy = y4 - shh - 18
    for lbl, val in ctrl:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(BLACK)
        c.drawString(ml + 5, cy, lbl)
        if val:
            c.setFont("Helvetica", 9)
            c.drawString(ml + 52, cy, val)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ml + half + 6, cy, lbl)
        cy -= 22

    # ── Agrément / Commentaires ───────────────────────────────────────────────
    agw = 108
    filled_rect(c, ml, y5 - shh, cw, shh)
    hline(c, ml, ml + cw, y5 - shh, 0.5)
    vline(c, ml + agw, cb, y5, 0.5)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y5 - 12, "AGREMENT")
    c.drawString(ml + agw + 8, y5 - 12, "Commentaires :")

    ay = y5 - shh - 22
    for label in ["ACCEPTE", "ACCEPTE AVEC\nRESERVES", "REFUSE"]:
        lls = label.split("\n")
        for li, ll in enumerate(lls):
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(BLACK)
            c.drawString(ml + 5, ay - li * 12, ll)
        bx = ml + 5 + stringWidth(lls[0], "Helvetica-Bold", 8) + 4
        filled_rect(c, bx, ay - 8, 9, 9, fill=WHITE, stroke=BLACK, lw=0.7)
        ay -= 38 if len(lls) > 1 else 26

    # Visa separator
    vsy = cb + 115
    hline(c, ml, ml + agw, vsy, 0.5)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, vsy - 14, "Visa du représentant")
    c.drawString(ml + 5, vsy - 26, "du client")
    vy2 = vsy - 44
    for f in ["Nom :", "Fonction :", "Date :", "Signature :"]:
        c.setFont("Helvetica", 8)
        c.drawString(ml + 5, vy2, f)
        vy2 -= 18


# ── LISTE DES FICHES ──────────────────────────────────────────────────────────

def draw_liste(c, project_name: str, items: list[dict], logo_path: str | None):
    ml, mt = 20, 20
    cw = W - 2 * ml
    ct, cb = H - mt, mt

    hdr_h, chan_h, list_hdr_h, col_hdr_h = 82, 58, 18, 20
    row_h = 30

    cnw, cdw, cpw, ccw = 52, 188, 150, 120
    cpag_w = cw - cnw - cdw - cpw - ccw
    cdx = ml + cnw
    cpx = cdx + cdw
    ccx = cpx + cpw
    cpgx = ccx + ccw

    # Outer border
    filled_rect(c, ml, cb, cw, ct - cb, fill=WHITE, stroke=BLACK, lw=0.8)

    # Header
    y_hdr = ct - hdr_h
    hline(c, ml, ml + cw, y_hdr, 0.8)
    draw_logo(c, logo_path, ml + 10, y_hdr, 95, hdr_h - 15)

    title = "LISTE DES FICHES A  AGREMENTER"
    tsz = 15
    tw = stringWidth(title, "Helvetica-Bold", tsz)
    c.setFont("Helvetica-Bold", tsz)
    c.setFillColor(BLACK)
    c.drawString(ml + cw / 2 - tw / 2 + 30, y_hdr + hdr_h / 2 - 7, title)

    # Chantier
    y_chan = y_hdr - chan_h
    hline(c, ml, ml + cw, y_chan, 0.8)
    lw2 = 78
    filled_rect(c, ml, y_chan, lw2, chan_h)
    vline(c, ml + lw2, y_chan, y_hdr, 0.5, MGREY)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + 5, y_chan + chan_h / 2 - 5, "Chantier :")

    plines = wrap(project_name.upper(), "Helvetica-Bold", 10, cw - lw2 - 20)
    lh2 = 15
    sy2 = y_chan + chan_h / 2 + len(plines) * lh2 / 2 - lh2 / 2
    for i, line in enumerate(plines):
        tw2 = stringWidth(line, "Helvetica-Bold", 10)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(BLACK)
        c.drawString(ml + lw2 + (cw - lw2) / 2 - tw2 / 2, sy2 - i * lh2, line)

    # "Liste des fiches" row
    y_lhdr = y_chan - list_hdr_h
    filled_rect(c, ml, y_lhdr, cw, list_hdr_h)
    hline(c, ml, ml + cw, y_lhdr, 0.5)
    t = "Liste des fiches"
    tw3 = stringWidth(t, "Helvetica-Bold", 9)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(ml + cw / 2 - tw3 / 2, y_lhdr + 5, t)

    # Column headers
    y_chdr = y_lhdr - col_hdr_h
    filled_rect(c, ml, y_chdr, cw, col_hdr_h, fill=DGREY)
    hline(c, ml, ml + cw, y_chdr, 0.5)
    for x in [cdx, cpx, ccx, cpgx]:
        vline(c, x, y_chdr, y_lhdr, 0.5)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(BLACK)
    c.drawString(ml + 3, y_chdr + 6, "Numéro :")
    c.drawString(cdx + 3, y_chdr + 6, "Désignation :")
    c.drawString(cpx + 3, y_chdr + 6, "Provenance :")
    c.drawString(ccx + 3, y_chdr + 6, "Catégorie :")
    c.drawString(cpgx + 3, y_chdr + 6, "Page :")

    # Rows
    ty = y_chdr
    for a in items:
        ty -= row_h
        if ty < cb + 5:
            break
        gc = colors.Color(0.75, 0.75, 0.75)
        hline(c, ml, ml + cw, ty, 0.4, gc)
        for x in [cdx, cpx, ccx, cpgx]:
            vline(c, x, ty, ty + row_h, 0.4, gc)

        c.setFont("Helvetica", 8)
        c.setFillColor(BLACK)
        ns = str(a["number"])
        nw2 = stringWidth(ns, "Helvetica", 8)
        c.drawString(ml + cnw / 2 - nw2 / 2, ty + row_h / 2 - 4, ns)

        for text, x_pos, col_w in [
            (a["designation"], cdx, cdw),
            (a["supplier_name"], cpx, cpw),
            (a.get("category", ""), ccx, ccw),
        ]:
            tlines = wrap(text, "Helvetica", 8, col_w - 6)
            base_y = ty + row_h / 2 + (4 if len(tlines) > 1 else -4)
            for i, line in enumerate(tlines[:2]):
                c.drawString(x_pos + 3, base_y - i * 10, line)


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_doe(project: dict, agrements: list[dict], uploads_dir: str) -> bytes:
    logo_path = find_logo()

    # Items per list page
    hdr_h, chan_h, list_hdr_h, col_hdr_h, row_h = 82, 58, 18, 20, 30
    mt, ct, cb = 20, H - 20, 20
    fixed = hdr_h + chan_h + list_hdr_h + col_hdr_h
    avail = ct - cb - fixed
    ipp = max(1, int(avail / row_h))

    writer = PdfWriter()

    # List pages
    n_list = max(1, -(-len(agrements) // ipp))
    for pi in range(n_list):
        items = agrements[pi * ipp:(pi + 1) * ipp]
        buf = BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        draw_liste(c, project["name"], items, logo_path)
        c.save()
        buf.seek(0)
        writer.add_page(PdfReader(buf).pages[0])

    # Individual fiche pages + attached datasheets
    for a in agrements:
        a_data = {**a, "project_name": project["name"]}
        buf = BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        draw_fiche(c, a_data, logo_path)
        c.save()
        buf.seek(0)
        writer.add_page(PdfReader(buf).pages[0])

        if a.get("datasheet_path"):
            ds = os.path.join(uploads_dir, a["datasheet_path"])
            if os.path.exists(ds):
                try:
                    for page in PdfReader(ds).pages:
                        writer.add_page(page)
                except Exception:
                    pass

    out = BytesIO()
    writer.write(out)
    return out.getvalue()
