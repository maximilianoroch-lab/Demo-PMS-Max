# Migración de DEMO PMS Max a cartera empresarial

## Estado actual
- Fuente independiente: Base DEMO PMS Max.
- Modo actual: `demo_legacy_scaled`, con multiplicación histórica x4. No implica anonimización ni es una cartera empresarial independiente.
- No cambia fuentes, posiciones ni historial actual.

## Pasos para migrar
1. Crear o importar una base nueva con datos autorizados de la nueva entidad. No reutilizar pestañas con operaciones personales, incluso ocultas.
2. Verificar posiciones, custodia, unidades, monedas, caja y conciliación.
3. Configurar `portfolio_config.py`: `sheet_id`, `display_name`, `app_name`, `id`, `data_mode="independent"`, `legacy_value_multiplier=1.0`.
4. Configurar `history_mode="none"` si falta historial verificable. Así se omiten los feeds históricos y la vista Evolución lo explica; mantener operativas las posiciones actuales.
5. Sustituir las equivalencias ficticias de `cuentas_demo` por cuentas autorizadas de la empresa o retirar esa tabla.
6. Validar Resumen, Custodia, Posiciones, Asesor y Comparador. Confirmar ausencia de referencias a la base personal.
7. Revisar permisos de acceso, claves, y el despliegue independiente.

## Controles
- No calcular retornos históricos o costos de adquisición con una simple foto de posiciones.
- Compartir públicamente una Demo requiere datos sintéticos propios o datos empresariales autorizados.
- La copia actual conserva datos derivados de Bersoch: no declararla anonimizada por el solo cambio de cuentas.
