# Textos de GC Lucas — borradores para revisión

Los 10 archivos de Word (5 textos × ES/EN) pasados a `data/texts/*.json`. Solo se corrigieron el título del punto 1 y los typos evidentes (ver abajo).
Los 5 publicados el 2026-10-27 (`"published": true`); los pendientes de abajo siguen abiertos y se pueden corregir desde el CMS.

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

## Typos corregidos (2026-10-27)
**EN:** aplied, Maecel Duschamp (→ Marcel Duchamp), critized, the the, ehibition, expresions, seperately, unreconciliable (→ irreconcilable), pictoric (→ pictorial), movility, mayority, prescence, mistery (×2), conjuction, evereyday, iceyness, fist plane, bellybotton.
**ES:** maquinara, através, igual mente, aerea, atmosfera, mas → más (×4, todos comparativos), "La contradicciones".

## Sin corregir (dudosos)
- **Itatti / Ittati** (Carballo ES/EN): no está claro cuál es el nombre real de la galería Arcos.
- **inadverted** (epígrafe de Cerón EN): va con el punto 7, conviene revisar la frase completa.
- **Gonzales** (Gortázar): no aparece en el JSON (el autor va como "Fernando González Gortázar").
- **diptics** (Gortázar EN, debería ser *diptychs*): no estaba en la lista original; se dejó igual.

## Qué quitó el generador
Título, firma del autor y fecha del final de cada Word; van en `titleEn/Es`, `author`, `dateEn/Es`. Una línea rota por salto de línea en Noyola EN ("...and to the / unfathomable taste...") se unió en un solo párrafo. Las cursivas del original se conservaron como `*...*` (markdown).
