(function () {
  // Rotating announcement bar
  document.querySelectorAll('[data-rotator]').forEach(function (track) {
    var items = track.querySelectorAll('.announcement__item');
    if (items.length < 2) return;
    var i = 0;
    setInterval(function () {
      items[i].classList.remove('is-active');
      i = (i + 1) % items.length;
      items[i].classList.add('is-active');
    }, 4000);
  });

  // Mobile menu
  var toggle = document.querySelector('[data-menu-toggle]');
  var menu = document.querySelector('[data-menu]');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  function formatMoney(cents) {
    try {
      var currency = (window.Shopify && Shopify.currency && Shopify.currency.active) || 'COP';
      return new Intl.NumberFormat(document.documentElement.lang || 'es', {
        style: 'currency', currency: currency, maximumFractionDigits: 0
      }).format(cents / 100);
    } catch (e) { return (cents / 100).toFixed(0); }
  }

  document.querySelectorAll('[data-product]').forEach(function (root) {
    var form = root.querySelector('[data-product-form]');
    if (!form) return;
    var idInput = form.querySelector('[data-variant-id]');
    var button = form.querySelector('[data-add-button]');
    var message = form.querySelector('[data-form-message]');
    var variantsEl = form.querySelector('[data-variants]');
    var variants = variantsEl ? JSON.parse(variantsEl.textContent) : [];
    var mainImg = root.querySelector('[data-main-image]');

    // Thumbnails
    root.querySelectorAll('[data-thumb]').forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        if (mainImg) { mainImg.removeAttribute('srcset'); mainImg.src = thumb.getAttribute('data-thumb'); }
      });
    });

    // Variant selection
    form.addEventListener('change', function (e) {
      if (!e.target.matches('[data-option-index]')) return;
      var selected = [];
      form.querySelectorAll('fieldset.option').forEach(function (fs, idx) {
        var checked = fs.querySelector('input:checked');
        selected[idx] = checked ? checked.value : null;
        var label = form.querySelector('[data-option-label="' + idx + '"]');
        if (label && checked) label.textContent = checked.value;
      });
      var variant = variants.find(function (v) {
        return v.options.every(function (o, i) { return o === selected[i]; });
      });
      if (!variant) return;
      idInput.value = variant.id;
      button.disabled = !variant.available;
      button.textContent = variant.available ? 'Agregar al carrito' : 'Agotado';
      var priceEl = root.querySelector('.price__current');
      if (priceEl) priceEl.textContent = formatMoney(variant.price);
      if (variant.featured_image && mainImg) { mainImg.removeAttribute('srcset'); mainImg.src = variant.featured_image.src; }
      var url = new URL(window.location.href);
      if (url.pathname.indexOf('/products/') !== -1) {
        url.searchParams.set('variant', variant.id);
        window.history.replaceState({}, '', url.toString());
      }
    });

    // AJAX add to cart
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      button.disabled = true;
      fetch((window.Shopify && Shopify.routes ? Shopify.routes.root : '/') + 'cart/add.js', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(form)
      })
        .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
        .then(function () { return fetch((window.Shopify && Shopify.routes ? Shopify.routes.root : '/') + 'cart.js'); })
        .then(function (r) { return r.json(); })
        .then(function (cart) {
          document.querySelectorAll('[data-cart-count]').forEach(function (el) {
            el.textContent = cart.item_count; el.hidden = cart.item_count === 0;
          });
          if (message) message.innerHTML = '¡Agregado al carrito! <a href="/cart">Ver carrito →</a>';
        })
        .catch(function () { if (message) message.textContent = 'No pudimos agregar el producto. Intenta de nuevo.'; })
        .finally(function () { button.disabled = false; });
    });
  });
})();
