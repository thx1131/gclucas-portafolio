# Textos de GC Lucas — borradores para revisión

Los 10 archivos de Word (5 textos × ES/EN) pasados a `data/texts/*.json` **sin corregir nada** (salvo el título del punto 1).
Todos con `"published": false` hasta que Lucas apruebe cada uno.

## Pendientes de decisión (Lucas)
1. **Monsiváis EN no tiene título** (el Word solo trae el nombre del autor). Se puso la propuesta "The Two Landscapes of G.C. Lucas" en `titleEn` (2026-10-27): **falta que Lucas la apruebe**.
2. **Cerón ES**: el título del Word es "G C Lucas: la transfiguración de lo palpado". El EN es "The Transfiguration of the Tangible". ¿Se queda el prefijo "G C Lucas:" en el español?
3. **Gortázar ES**: el título trae punto final ("Las dualidades felices.").
4. **Carballo**: ES "GC Lucas" / EN "GC Lucas´ Saga" (apóstrofo como acento).
5. **Noyola**: ES "G (eometría) C (uerpo) LUCAS" / EN "G(eometry) C(orps) Lucas".
6. **Fechas**: Noyola ES "Mayo 2001" vs EN "2001"; Cerón ES "2001" vs EN "May 2001" (en el JSON: `dateEs`/`dateEn` guardan cada una tal cual).
7. **Epígrafe de Cerón EN**: la traducción dice "we find that things are not what they are", y el español dice que las cosas *son* lo que son. Revisar.
8. **Permisos**: confirmar que se pueden republicar estos textos de terceros en el sitio.
9. **Imagen** de cada texto (`image`, `imageCaptionEn/Es`): vacías por ahora.

## Typos detectados (no corregidos)
**EN:** aplied, Maecel Duschamp, critized, the the, ehibition, Itatti/Ittati (Arcos), Gonzales (Gortázar), expresions, seperately, unreconciliable, pictoric, inadverted, movility, mayority, prescence, mistery, conjuction, evereyday, iceyness, fist plane, bellybotton, mistery.
**ES:** maquinara, através, igual mente, aerea, atmosfera, mas (sin tilde), CARLOS MONIVÁIS (firma de Monsiváis, omitida del JSON; el autor va en `author`), "La contradicciones".

## Qué quitó el generador
Título, firma del autor y fecha del final de cada Word; van en `titleEn/Es`, `author`, `dateEn/Es`. Una línea rota por salto de línea en Noyola EN ("...and to the / unfathomable taste...") se unió en un solo párrafo. Las cursivas del original se conservaron como `*...*` (markdown).
