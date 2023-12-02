ARG PHP_VERSION=8.3

FROM php:${PHP_VERSION}-apache as wp_cli_builder

ENV WORDPRESS_CLI_VERSION 2.9.0

RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && php wp-cli.phar --info \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp \
    && wp --allow-root --version


## Setup Base Container - lifted from https://github.com/docker-library/wordpress/blob/master/latest/php8.2/apache/Dockerfile
FROM wordpress:6.4.1-php8.3-apache as wpbase

## Copy CLI Installations
COPY --chown=www-data:www-data --from=wp_cli_builder /usr/local/bin/wp /usr/local/bin/wp

#WORKDIR /usr/src/wordpress
#RUN set -eux; \
#	find /etc/apache2 -name '*.conf' -type f -exec sed -ri -e "s!/var/www/html!$PWD!g" -e "s!Directory /var/www/!Directory $PWD!g" '{}' +; \
#	cp -s wp-config-docker.php wp-config.php


# Setup Customizations
FROM wpbase

COPY --chown=www-data:www-data ./wp-content/themes /usr/src/wordpress/wp-content/themes
COPY --chown=www-data:www-data ./wp-content/plugins /usr/src/wordpress/wp-content/plugins
COPY --chown=www-data:www-data ./wp-content/bcf-fonts  /usr/src/wordpress/wp-content/bcf-fonts
#COPY --chown=www-data:www-data wp-config-docker.php /usr/src/wordpress/
#COPY --chown=www-data:www-data docker-entrypoint.sh /usr/local/bin/
#RUN chmod +x /usr/local/bin/docker-entrypoint.sh
#RUN chown -R www-data:www-data /var/www

#USER www-data
#ENTRYPOINT ["docker-entrypoint.sh"]
#CMD ["apache2-foreground"]