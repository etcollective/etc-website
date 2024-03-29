ARG PHP_VERSION=8.3
ARG WP_VERSION=6.4.3

FROM php:${PHP_VERSION}-apache as wp_cli_builder

RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && php wp-cli.phar --info \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp \
    && wp --allow-root --version


## Setup Base Container - lifted from https://github.com/docker-library/wordpress/blob/master/latest/php8.2/apache/Dockerfile
FROM wordpress:${WP_VERSION}-php${PHP_VERSION}-apache as wpbase

## Copy CLI Installations
COPY --chown=www-data:www-data --from=wp_cli_builder /usr/local/bin/wp /usr/local/bin/wp

## Remove Default Themes and Plugins
RUN rm -rf /usr/src/wordpress/wp-content/themes/* \
    rm -rf /usr/src/wordpress/wp-content/plugins/*

# Setup Customizations
FROM wpbase

COPY --chown=www-data:www-data ./wp-content/themes /usr/src/wordpress/wp-content/themes
COPY --chown=www-data:www-data ./wp-content/plugins /usr/src/wordpress/wp-content/plugins
COPY --chown=www-data:www-data ./wp-content/bcf-fonts  /usr/src/wordpress/wp-content/bcf-fonts