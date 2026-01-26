import math
import os
import argparse
from PyPDF2 import PdfReader, PdfWriter

def duplicate_pdf(
    input_path: str,
    output_path: str,
    target_pages: int,
    strip_metadata: bool = True
):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No se encuentra el archivo: {input_path}")

    reader = PdfReader(input_path)
    src_pages = len(reader.pages)
    if src_pages == 0:
        raise ValueError("El PDF de entrada no tiene páginas.")

    if target_pages <= 0:
        raise ValueError("El número de páginas objetivo debe ser mayor que 0.")

    # Asegurar que el objetivo sea múltiplo del tamaño del documento
    if target_pages % src_pages != 0:
        raise ValueError(
            f"El número de páginas objetivo ({target_pages}) debe ser múltiplo del número de páginas del PDF de entrada ({src_pages})."
        )

    # Calcular cuántas veces hay que repetir el documento para igualar exactamente
    repeats = target_pages // src_pages

    writer = PdfWriter()

    # (Opcional) Quitar metadatos para anonimizar
    if strip_metadata:
        writer.add_metadata({})

    # Copiado iterativo para no disparar RAM
    for r in range(repeats):
        for i in range(src_pages):
            writer.add_page(reader.pages[i])

    # Guardar a disco
    with open(output_path, "wb") as f:
        writer.write(f)

    total_pages = src_pages * repeats
    return total_pages, repeats, src_pages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Duplica un PDF repitiendo sus páginas hasta alcanzar un número exacto de páginas.")
    parser.add_argument("file", help="Nombre del archivo PDF a ampliar (se busca en el directorio actual)")
    parser.add_argument("pages", type=int, help="Número total de páginas objetivo (debe ser múltiplo del número de páginas del PDF)")
    parser.add_argument("--keep-metadata", action="store_true", help="Conservar metadatos del PDF (por defecto se eliminan)")

    args = parser.parse_args()

    # Resolver rutas desde el directorio actual
    cwd = os.getcwd()
    input_path = os.path.join(cwd, args.file)

    # Generar nombre de salida en el mismo directorio
    name, ext = os.path.splitext(os.path.basename(args.file))
    output_filename = f"{name}_{args.pages}p{ext or '.pdf'}"
    output_path = os.path.join(cwd, output_filename)

    total, reps, src = duplicate_pdf(
        input_path=input_path,
        output_path=output_path,
        target_pages=args.pages,
        strip_metadata=not args.keep_metadata,
    )
    print(f"PDF original: {src} páginas")
    print(f"Repeticiones realizadas: {reps}")
    print(f"PDF final: {total} páginas -> {output_path}")
