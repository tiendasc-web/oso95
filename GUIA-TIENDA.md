# 🐝 Pasito Feliz – Tienda Shopify de productos para bebé

Todo lo necesario para lanzar la tienda está en este repositorio:

| Carpeta | Qué contiene |
|---|---|
| `theme/` | Tema Shopify 2.0 de marca (rosa + lila), en español, optimizado para móvil, con WhatsApp flotante, pago contra entrega, preguntas frecuentes y datos SEO. Pasa `shopify theme check` sin errores. |
| `productos/catalogo.json` | Catálogo maestro: 12 productos, 5 colecciones, 4 páginas y 1 cupón. |
| `productos/productos_shopify.csv` | El mismo catálogo listo para **Productos → Importar** en Shopify. |
| `productos/imagenes/` | Foto del producto estrella (protector de cabeza Abejita, SKU de proveedor `SU00111427`). |
| `contenido/paginas/` | Textos de Nosotros, Envíos, Cambios y Contacto. |
| `scripts/tienda.py` | Crea o actualiza productos, colecciones, páginas, menús y el cupón con la API de Shopify. |
| `.github/workflows/deploy-tienda.yml` | Sube el tema automáticamente cada vez que cambia `theme/`. |
| `automatizacion/AUTOMATIZACION.md` | Pedidos, proveedor, correos y WhatsApp en piloto automático. |

## Producto estrella

**Protector de Cabeza para Bebé Abejita – Mochila Anticaídas**
- SKU / código de proveedor: `SU00111427`
- Precio sugerido: **₡12.900** (tienda en colones, Costa Rica). Ajústalo según tu costo del proveedor y el envío.
- Etiquetas: `seguridad`, `primeros-pasos`, `mas-vendidos`. Aparece solo en esas colecciones.

Los otros 11 productos son **complementos que se venden junto al protector** (otras figuras del protector, rodilleras, casco, arnés, seguros de hogar, sueño y alimentación). Se crean como **borrador** con SKU `PENDIENTE-...`. Para activar cada uno:
1. Búscalo en el catálogo de tu proveedor.
2. Cambia el SKU por el código real del proveedor, ajusta el precio y sube las fotos.
3. Cambia el estado a **Activo**.

## Puesta en marcha (unos 20 minutos)

### Opción A – Manual, sin código
1. **Tema:** comprime la carpeta `theme/` en un `.zip` con los archivos en la raíz del zip (`layout/`, `sections/`…). Luego ve a *Tienda online → Temas → Agregar tema → Subir archivo zip* y pulsa **Publicar**.
2. **Productos:** ve a *Productos → Importar* y sube `productos/productos_shopify.csv`.
3. **Colecciones:** crea 5 colecciones automáticas con la condición *“Etiqueta del producto es igual a …”*:
   `mas-vendidos`, `seguridad`, `primeros-pasos`, `hora-de-dormir`, `alimentacion`. Usa los nombres y URLs de `catalogo.json` (por ejemplo, la URL `seguridad-bebe` lleva la etiqueta `seguridad`).
4. **Páginas:** copia los textos de `contenido/paginas/` en *Tienda online → Páginas*.
5. **Menús:** en *Tienda online → Navegación*, edita “Menú principal” y “Footer” (los enlaces están en `scripts/tienda.py`, en `MENUS`).
6. **Cupón:** crea el descuento `BIENVENIDA10` (10 %, una vez por cliente).

### Opción B – Automática
1. En Shopify: *Configuración → Apps → Desarrollar apps → Crear app*. Dale estos permisos de Admin API:
   `write_products`, `write_content`, `write_online_store_navigation`, `write_discounts`, `write_publications`.
   Instálala y copia el token `shpat_...`.
2. Ejecuta:
   ```bash
   export SHOPIFY_STORE=tu-tienda.myshopify.com
   export SHOPIFY_ADMIN_TOKEN=shpat_xxx
   python3 scripts/tienda.py setup
   ```
   Así se crean productos, colecciones automáticas, páginas, menús y el cupón. Puedes ejecutarlo varias veces: lo que ya existe no se duplica.
3. **Tema automático con GitHub Actions:** instala la app **Theme Access** en Shopify para obtener un token. Después, en GitHub ve a *Settings → Secrets and variables → Actions* y agrega:
   - Variable `SHOPIFY_STORE` = `tu-tienda.myshopify.com`
   - Secreto `SHOPIFY_CLI_THEME_TOKEN` = token de Theme Access
   - Secreto `SHOPIFY_ADMIN_TOKEN` = token `shpat_...` (para sincronizar el catálogo desde *Actions → Run workflow*)
   - (Opcional) Variable `SHOPIFY_THEME_ID` = ID del tema publicado, para que cada cambio en `theme/` se suba directo a la tienda en vivo.

### Ajustes finales en el editor de temas
- **Configuración del tema → Contacto y ventas:** tu número de WhatsApp, con indicativo (`506…`).
- **Redes sociales:** tus enlaces de Instagram, Facebook y TikTok.
- **Encabezado:** sube tu logo (si no lo haces, se muestra “🐝 nombre de la tienda”).
- **Testimonios:** reemplaza los textos de ejemplo por reseñas **reales** de tus clientes.
- **Portada:** después de importar, puedes elegir la imagen desde *Archivos* en lugar de la URL.

> La imagen del producto se carga desde este repositorio público (rama `claude/tienda-bebes-shopify`). Si fusionas a `main` y borras la rama, cambia `image_base` en `catalogo.json` a `.../refs/heads/main/...`. Shopify copia la imagen al importar, así que solo importa en ese momento.
