#!/bin/bash
set -e

echo "========================================"
echo "Flowlite Database Initialization Script"
echo "========================================"

# Esperar un poco más para asegurar que MySQL esté completamente listo
echo "Waiting for MySQL to be fully ready..."
sleep 5

# Ejecutar inicialización de base de datos
echo ""
echo "Step 1: Running database initialization..."
python /app/scripts/init_database.py

# Verificar si la inicialización fue exitosa
if [ $? -eq 0 ]; then
    echo "✓ Database initialization completed successfully"
else
    echo "✗ Database initialization failed"
    exit 1
fi

# Ejecutar seed de base de datos
echo ""
echo "Step 2: Running database seeding..."
python /app/scripts/seed_database.py

# Verificar si el seed fue exitoso
if [ $? -eq 0 ]; then
    echo "✓ Database seeding completed successfully"
else
    echo "✗ Database seeding failed"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Database initialization complete!"
echo "========================================"
