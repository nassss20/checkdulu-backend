# 1. Start with an official PHP 8.4 Linux image
FROM php:8.4-cli

# 2. Force Linux to install Python 3, pip, and required system tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    unzip \
    libzip-dev \
    && docker-php-ext-install zip

# 3. Set the working directory inside the server
WORKDIR /app

# 4. Copy all your CheckDulu files into the server
COPY . .

# 5. Install Composer (PHP package manager)
COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

# 6. Install Laravel's PHP dependencies
RUN composer install --no-dev --optimize-autoloader

# 7. Install your specific Machine Learning Python libraries globally
RUN pip3 install pandas scikit-learn joblib --break-system-packages

# 8. Fix folder permissions so Laravel doesn't crash
RUN chmod -R 775 storage bootstrap/cache

# 9. Start the Laravel server on the port Railway assigns
CMD php artisan serve --host=0.0.0.0 --port=$PORT