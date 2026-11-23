"""Turn the existing Markdown strategy brief into a styled PDF, in memory."""
from io import BytesIO
import html
import re
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether


def build_pdf(markdown: str) -> bytes:
    if len(markdown) > 1_000_000:
        raise ValueError('Report exceeds the PDF export size limit.')
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=(612,792),leftMargin=52,rightMargin=52,
       topMargin=62,bottomMargin=54,title='FORGE | Technology Strategy Brief',author='FORGE')
    s=getSampleStyleSheet()
    s.add(ParagraphStyle(name='ForgeTitle',parent=s['Title'],fontName='Helvetica-Bold',
       fontSize=19,leading=24,textColor=colors.HexColor('#163e53'),spaceAfter=15,alignment=TA_LEFT))
    s.add(ParagraphStyle(name='ForgeH2',parent=s['Heading2'],fontName='Helvetica-Bold',
       fontSize=13,leading=18,textColor=colors.HexColor('#116e75'),spaceBefore=17,spaceAfter=7))
    s.add(ParagraphStyle(name='ForgeBody',parent=s['BodyText'],fontSize=9.5,leading=15,
       textColor=colors.HexColor('#223947'),spaceAfter=8))
    s.add(ParagraphStyle(name='ForgeSmall',parent=s['ForgeBody'],fontSize=8.5,leading=13,leftIndent=12))
    def inline(t):
        # Escape first, then allow only basic inline formatting. No arbitrary HTML input.
        t=html.escape(t)
        t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t)
        t=re.sub(r'`([^`]+)`',r'<font face="Courier">\1</font>',t)
        return t
    story=[]
    for raw in markdown.splitlines():
        line=raw.strip()
        if not line:
            story.append(Spacer(1,5));continue
        if line.startswith('# '): style=s['ForgeTitle'];line=line[2:]
        elif line.startswith(('## ','### ','#### ')):
            style=s['ForgeH2'];line=line.lstrip('#').strip()
        elif line.startswith(('- ','* ')):
            style=s['ForgeSmall'];line='• '+line[2:]
        else: style=s['ForgeBody']
        # Markdown links display as label plus URL, retaining reference location.
        line=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'\1 (\2)',line)
        story.append(Paragraph(inline(line),style))
    def decorations(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#b5d9dc'))
        canvas.line(52,746,560,746)
        canvas.setFont('Helvetica-Bold',9)
        canvas.setFillColor(colors.HexColor('#116e75'))
        canvas.drawString(52,759,'FORGE  /  TECHNOLOGY STRATEGY')
        canvas.setFont('Helvetica',8)
        canvas.drawRightString(560,34,f'Page {doc.page}')
        canvas.restoreState()
    doc.build(story,onFirstPage=decorations,onLaterPages=decorations)
    return buffer.getvalue()
