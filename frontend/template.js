// template — frontend of the Add-on Template (Add-on Contract 2).
// One script per Bundle. Everything it registers lives under the id:
// view keys and slot keys start with "template.", routes with "/template/",
// locale keys with "template.", CSS classes with "template-".
//
// The core loads this file before it mounts its router and expects exactly
// one synchronous call to LocalBib.registerPlugin while it runs. Texts come
// from the locale files next to it (frontend/locales/*.json) through $t.
(function () {
  'use strict';
  var LB = window.LocalBib;
  if (!LB || typeof LB.registerPlugin !== 'function') return;

  LB.registerPlugin({
    id: 'template',
    views: {
      // The nav item of the Manifest ("route": "/template") points here.
      'template.main': {
        template:
          '<section class="template-view">' +
          '<h1 class="template-title">{{ $t("template.view.title") }}</h1>' +
          '<p class="template-intro">{{ $t("template.view.intro") }}</p>' +
          '</section>'
      }
    },
    // The one Slot this template occupies: the Item-detail aside. It calls
    // the Add-on's one endpoint and shows how many times this Item was
    // looked up — replace with whatever your own Add-on contributes there.
    slots: {
      'item-detail-aside': {
        key: 'template.aside',
        component: {
          props: ['itemId', 'citeKey'],
          data: function () {
            return { views: null };
          },
          watch: {
            citeKey: { immediate: true, handler: 'load' }
          },
          methods: {
            load: function () {
              var self = this;
              if (!this.citeKey) return;
              LB.api('/api/plugins/template/lookup/' + encodeURIComponent(this.citeKey))
                .then(function (data) { self.views = data.views; })
                .catch(function () { self.views = null; });
            }
          },
          template:
            '<aside class="template-aside" :data-item-id="itemId">' +
            '{{ $t("template.aside.label") }} ' +
            '<strong v-if="views !== null">{{ views }}</strong>' +
            '</aside>'
        }
      }
    }
  });
})();
