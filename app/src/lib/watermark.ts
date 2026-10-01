/**
 * Every PDF download is stamped with who bought it and which order it came from
 * (AUDIT_BUSINESS F08; FUNNEL.md canonical policy "watermarked with the buyer's
 * email"). Footer on every page plus the document metadata. Ink colour: no gray.
 */
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

export interface WatermarkInfo {
  name: string;
  email: string;
  orderRef: string;
  date?: Date;
}

/** Helvetica (WinAnsi) can't draw every character; fold accents, replace the rest. */
export function pdfSafe(s: string): string {
  return s
    .normalize("NFKD")
    .replace(/\p{M}+/gu, "")
    .replace(/[^\x20-\x7E]/g, "?")
    .slice(0, 120);
}

export function watermarkLine(w: WatermarkInfo): string {
  const d = (w.date ?? new Date()).toISOString().slice(0, 10);
  return pdfSafe(`Licensed to ${w.name} <${w.email}> | Order ${w.orderRef} | ${d} | Personal use only. Please don't share or resell.`);
}

export async function watermarkPdf(bytes: Uint8Array, w: WatermarkInfo): Promise<Uint8Array> {
  const doc = await PDFDocument.load(bytes, { updateMetadata: false });
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const line = watermarkLine(w);
  const ink = rgb(0.086, 0.071, 0.055); // #16120E
  for (const page of doc.getPages()) {
    const { width } = page.getSize();
    let size = 8;
    while (size > 5 && font.widthOfTextAtSize(line, size) > width - 36) size -= 0.5;
    const tw = font.widthOfTextAtSize(line, size);
    page.drawRectangle({ x: (width - tw) / 2 - 4, y: 6, width: tw + 8, height: size + 6, color: rgb(1, 1, 1) });
    page.drawText(line, { x: (width - tw) / 2, y: 9, size, font, color: ink });
  }
  doc.setSubject(pdfSafe(`Licensed to ${w.email}, order ${w.orderRef}`));
  doc.setKeywords([pdfSafe(w.email), pdfSafe(w.orderRef)]);
  doc.setProducer("Strong Years");
  return doc.save();
}
