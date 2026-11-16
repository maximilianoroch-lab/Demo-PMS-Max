# DEMO V5 — históricas independientes (pendiente de fuente real)

El inventario `DEMO_INVENTARIO_V5` es **ficticio**. Sus precios USD indicativos no equivalen a cierres bursátiles de mercado. El archivo heredado `historial_precios` de la Google Sheet DEMO se originó en una copia de Bersoch y no debe usarse.

Este borrador agrega `demo_price_history_gate.py` como puerta de entrada estricta para futuros precios unitarios históricos de DEMO. No incorpora precios nuevos ni habilita rankings en producción.

### Formato requerido para un CSV histórico independiente

```csv
Fecha,Ticker,Precio,Moneda,Fuente,Referencia,Fecha_fuente,Origen_cartera
```

`Origen_cartera` = `DEMO_V5_MERCADO_INDEPENDIENTE`. `Referencia` debe permitir auditar el dato fechado (identificador de proveedor o enlace verificable). Las fechas tienen formato AAAA-MM-DD y corresponden al mismo cierre publicado por la fuente. No se permiten precios inventados, escalados o heredados de Bersoch.

### Condiciones de activación

1. Obtener datos históricos **por ticker, fecha, moneda y fuente** del universo DEMO; respetar fecha y plaza real.
2. Registrar la referencia externa de cada precio. No pasar un número simulado como cotización observada.
3. Conciliar cobertura y procedencia, revisando casos especiales: CEDEAR, bonos en precio por 100 VN, ETF, cripto y contratos.
4. Validar con `validate_price_history`, inspeccionar los resultados y después conectar a la interfaz.
5. Hasta entonces, mostrar aviso “Sin cotizaciones históricas independientes verificadas”, nunca rendimientos presuntos.

La comparativa provista requiere dos fechas comunes para cada ticker y la misma moneda. No atribuir a la cartera ficticia rentabilidad bursátil observada; el ranking refiere únicamente a **precio unitario de mercado** cuando se documente su fuente.

No se cambian bases, inventarios, valuaciones ni despliegues.
