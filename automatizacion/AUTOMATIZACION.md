# ⚙️ Automatización de Pasito Feliz

La idea es que tú solo revises el panel. Pedidos, proveedor, correos y seguimiento funcionan solos.

## 1. Pedido → proveedor (dropshipping)
El código `SU00111427` es de tu proveedor. Conecta su app o integración con Shopify para que cada pedido se le envíe automáticamente:

| Si tu proveedor es… | Haz esto |
|---|---|
| **Dropi** (LatAm) | En Dropi: *Integraciones → Shopify*, conecta la tienda y vincula cada producto por SKU (el SKU de la Abejita ya es `SU00111427`). Los pedidos, incluidos los de pago contra entrega, pasan solos a Dropi, y la guía vuelve a Shopify. |
| **AliExpress / CJ / otro** | Usa la app oficial (DSers, CJdropshipping, etc.). Mapea el producto por SKU y activa *Auto-order* y *Sincronización de seguimiento*. |

✅ Mantén el SKU de Shopify **igual** al código del proveedor. Así el mapeo es automático.

## 2. Pago contra entrega con confirmación por WhatsApp
- *Configuración → Pagos → Métodos de pago manuales → Pago contra entrega (COD)*.
- Para reducir pedidos falsos, instala una app de formulario COD con confirmación por WhatsApp (por ejemplo, Releasit COD Form o EasySell). Así el cliente compra en 1 paso y recibe un mensaje automático para confirmar.

## 3. Shopify Flow (gratis)
Instala **Shopify Flow** y crea estos flujos:

| Disparador | Condición | Acción |
|---|---|---|
| Pedido creado | Método de pago = contra entrega | Etiquetar pedido `COD-por-confirmar` |
| Pedido creado | Riesgo de fraude = alto | Etiquetar `revisar` y enviarte un correo interno |
| Pedido creado | El total de pedidos del cliente es ≥ 2 | Etiquetar al cliente `recurrente` |
| Producto: inventario cambia | Cantidad < 5 | Enviarte un correo: “Reponer {{product.title}}” |
| Pedido completado (fulfilled) | — | Esperar 10 días y enviar solicitud de reseña (con la app de reseñas) |

## 4. Correos automáticos (Shopify Email / Marketing → Automatizaciones)
Activa las plantillas que ya trae Shopify:
1. **Carrito abandonado:** 1 hora después. Incluye el cupón `BIENVENIDA10`.
2. **Checkout abandonado:** 10 horas después.
3. **Bienvenida a suscriptores:** se dispara con el formulario “Club Pasito Feliz” del pie de página, que etiqueta al cliente con `newsletter`. Entrega el cupón `BIENVENIDA10`.
4. **Recompra / venta cruzada:** 30 días después de la compra del protector, ofrece rodilleras y casco.

## 5. Reseñas reales
Instala **Judge.me** (plan gratis). Envía automáticamente la solicitud de reseña tras la entrega. Cuando tengas reseñas reales, cópialas en la sección *Testimonios* de la portada.

## 6. Tema y catálogo
- Cada cambio en `theme/` que llegue a `main` se sube solo a Shopify (`.github/workflows/deploy-tienda.yml`).
- Para agregar productos nuevos, edita `productos/catalogo.json` y ejecuta *Actions → Desplegar tienda Shopify → Run workflow* con “setup_catalogo” activado. También puedes ejecutar `python3 scripts/tienda.py setup` en local.
  ⚠️ Ese paso **reemplaza** con lo que dice `catalogo.json` los productos que ya existen con el mismo handle. Haz los cambios de catálogo en el JSON, no en el panel de Shopify.

## 7. Checklist legal (Costa Rica)
- *Configuración → Políticas:* genera Reembolso, Privacidad y Términos. Revisa que coincidan con `contenido/paginas/cambios.html`, que incluye el derecho de retracto de 8 días hábiles (Ley 7472).
- No uses precios “antes/ahora” inventados: el MEIC puede sancionar la publicidad engañosa. Por eso el catálogo no trae “precio de comparación”.
- En productos de seguridad infantil, evita prometer “evita el 100 % de las lesiones”. El texto del producto ya aclara que no reemplaza la supervisión de un adulto.
