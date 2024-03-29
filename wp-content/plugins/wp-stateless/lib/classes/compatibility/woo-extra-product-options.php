<?php

/**
 * Plugin Name: WooCommerce Extra Product Options
 * Plugin URI: https://codecanyon.net/item/woocommerce-extra-product-options/7908619
 * Related issue: https://github.com/wpCloud/wp-stateless/issues/266
 *
 * Compatibility Description: Ensures compatibility with WooCommerce Extra Product Options.
 *
 */

namespace wpCloud\StatelessMedia {

  if (!class_exists('wpCloud\StatelessMedia\CompatibilityWooExtraProductOptions')) {

    class CompatibilityWooExtraProductOptions extends Compatibility {
      protected $id = 'woo-extra-product-options';
      protected $title = 'WooCommerce Extra Product Options';
      protected $constant = 'WP_STATELESS_COMPATIBILITY_WOO_EXTRA_PRODUCT_OPTION';
      protected $description = 'Ensures compatibility with WooCommerce Extra Product Options.';
      protected $plugin_file = 'woocommerce-tm-extra-product-options/tm-woo-extra-product-options.php';
      protected $enabled = false;
      protected $is_internal = true;

      /**
       * @param $sm
       */
      public function module_init($sm) {
        add_filter('woocommerce_add_cart_item_data', array($this, 'add_cart_item_data'), 1);
      }

      /**
       * Adding filter late to insure that it only runs when a product is added.
       * @param $cart_item_meta
       * @return mixed
       */
      public function add_cart_item_data($cart_item_meta) {
        add_filter('wp_handle_upload', array($this, 'wp_handle_upload'));
        return $cart_item_meta;
      }

      /**
       * upload image to GCS and return GCS link.
       * @param $upload
       * @return mixed
       */
      public function wp_handle_upload($upload) {
        $file = $upload['file'];
        $url = $upload['url'];
        $type = $upload['type'];

        $client = ud_get_stateless_media()->get_client();

        $file_path = apply_filters('wp_stateless_file_name', $file, 0);
        $file_info = @getimagesize($file);

        if ($file_info) {
          $_metadata = array(
            'width'  => $file_info[0],
            'height' => $file_info[1],
            'object-id' => 'unknown', // we really don't know it
            'source-id' => md5($file . ud_get_stateless_media()->get('sm.bucket')),
            'file-hash' => md5($file)
          );
        }

        $media = $client->add_media(apply_filters('sm:item:on_fly:before_add', array(
          'use_root' => false,
          'name' => $file_path,
          'absolutePath' => wp_normalize_path($file),
          'cacheControl' => apply_filters('sm:item:cacheControl', 'public, max-age=36000, must-revalidate', $_metadata),
          'contentDisposition' => null,
          'mimeType' => $type,
          'metadata' => $_metadata
        )));

        $upload['url'] = ud_get_stateless_media()->get_gs_host() . '/' . $file_path;
        return $upload;
      }
    }
  }
}
