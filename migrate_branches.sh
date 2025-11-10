#!/bin/bash

###############################################################################
# Script de Migración de Ramas - RCP Transtelefónica
# Propósito: Automatizar la actualización de main y limpieza de ramas antiguas
# Autor: Generado automáticamente
# Fecha: 10 de Noviembre de 2025
###############################################################################

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para confirmar acciones
confirm() {
    read -p "$(echo -e ${YELLOW}$1${NC}) (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Operación cancelada"
        exit 1
    fi
}

###############################################################################
# PASO 0: Verificaciones Iniciales
###############################################################################

print_info "=== Script de Migración de Ramas ==="
echo

# Verificar que estamos en un repositorio git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "No estás en un repositorio Git"
    exit 1
fi

# Verificar que estamos en el repositorio correcto
REPO_URL=$(git remote get-url origin)
if [[ ! "$REPO_URL" == *"over-the-phone-cpr-samur"* ]]; then
    print_warning "Este script está diseñado para el repositorio over-the-phone-cpr-samur"
    confirm "¿Continuar de todas formas?"
fi

print_success "Repositorio verificado"
echo

###############################################################################
# PASO 1: Mostrar Estado Actual
###############################################################################

print_info "Estado actual de ramas:"
echo
git branch -a
echo

###############################################################################
# PASO 2: Backup de Seguridad
###############################################################################

print_info "Creando backup de la rama main actual..."

# Obtener fecha actual para nombre de backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BRANCH="main-backup-${BACKUP_DATE}"

# Crear backup
git fetch origin main:refs/remotes/origin/main || print_warning "No se pudo actualizar referencia remota de main"
git branch ${BACKUP_BRANCH} origin/main 2>/dev/null || git branch ${BACKUP_BRANCH} main

print_success "Backup creado: ${BACKUP_BRANCH}"
echo

###############################################################################
# PASO 3: Confirmación del Usuario
###############################################################################

print_warning "⚠️  ADVERTENCIA ⚠️"
echo
echo "Este script va a:"
echo "  1. Reescribir la rama 'main' con el contenido de 'copilot/delete-old-branches'"
echo "  2. Eliminar las siguientes ramas remotas:"
echo "     - copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189"
echo "     - add-claude-github-actions-1762778821956"
echo "     - copilot/delete-old-branches"
echo "  3. Esto requiere FORCE PUSH a main"
echo
echo "Se ha creado un backup en: ${BACKUP_BRANCH}"
echo

confirm "¿Estás seguro de que quieres continuar?"

###############################################################################
# PASO 4: Actualizar Todas las Referencias
###############################################################################

print_info "Actualizando referencias remotas..."
git fetch --all --prune
print_success "Referencias actualizadas"
echo

###############################################################################
# PASO 5: Actualizar Main
###############################################################################

print_info "Actualizando rama main..."

# Checkout a la rama objetivo
git checkout copilot/delete-old-branches

# Verificar que estamos en el commit correcto
CURRENT_COMMIT=$(git rev-parse HEAD)
print_info "Commit actual: ${CURRENT_COMMIT}"

# Forzar main a apuntar al mismo commit
git checkout main 2>/dev/null || git checkout -b main
git reset --hard copilot/delete-old-branches

print_success "Rama main actualizada localmente"
echo

###############################################################################
# PASO 6: Push a Remoto
###############################################################################

print_warning "Preparando para hacer push a origin/main (requiere force)"
confirm "¿Proceder con el push a main?"

print_info "Haciendo push a origin/main..."
git push origin main --force

print_success "Rama main actualizada en GitHub"
echo

###############################################################################
# PASO 7: Eliminar Ramas Antiguas
###############################################################################

print_info "Eliminando ramas antiguas del remoto..."

# Array de ramas a eliminar
BRANCHES_TO_DELETE=(
    "copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189"
    "add-claude-github-actions-1762778821956"
)

for branch in "${BRANCHES_TO_DELETE[@]}"; do
    print_info "Eliminando rama: ${branch}"
    if git push origin --delete "${branch}" 2>/dev/null; then
        print_success "Eliminada: ${branch}"
    else
        print_warning "No se pudo eliminar ${branch} (puede que ya no exista)"
    fi
done

echo

# Preguntar si eliminar también copilot/delete-old-branches
print_info "La rama copilot/delete-old-branches ahora tiene el mismo contenido que main"
confirm "¿Quieres eliminar también copilot/delete-old-branches del remoto?"

print_info "Eliminando copilot/delete-old-branches..."
if git push origin --delete copilot/delete-old-branches 2>/dev/null; then
    print_success "Eliminada: copilot/delete-old-branches"
else
    print_warning "No se pudo eliminar copilot/delete-old-branches"
fi

echo

###############################################################################
# PASO 8: Limpieza Local
###############################################################################

print_info "Limpiando ramas locales..."

# Checkout a main antes de eliminar otras ramas
git checkout main

# Eliminar ramas locales
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    git branch -D "${branch}" 2>/dev/null || true
done

git branch -D copilot/delete-old-branches 2>/dev/null || true

print_success "Ramas locales limpiadas"
echo

###############################################################################
# PASO 9: Limpiar Referencias Remotas Obsoletas
###############################################################################

print_info "Limpiando referencias remotas obsoletas..."
git fetch --prune
print_success "Referencias limpiadas"
echo

###############################################################################
# PASO 10: Verificación Final
###############################################################################

print_info "=== Verificación Final ==="
echo

print_info "Ramas locales restantes:"
git branch -l
echo

print_info "Ramas remotas restantes:"
git branch -r
echo

print_info "Últimos commits en main:"
git log --oneline -5 main
echo

###############################################################################
# Resumen Final
###############################################################################

print_success "=== Migración Completada Exitosamente ==="
echo
echo "Resumen:"
echo "  ✅ La rama main ha sido actualizada con el contenido más reciente"
echo "  ✅ Las ramas antiguas han sido eliminadas"
echo "  ✅ Se mantiene un backup en: ${BACKUP_BRANCH}"
echo
echo "Próximos pasos para colaboradores:"
echo "  1. git fetch --all --prune"
echo "  2. git checkout main"
echo "  3. git reset --hard origin/main"
echo
print_info "Si necesitas revertir los cambios, usa el backup: ${BACKUP_BRANCH}"
echo

###############################################################################
# Fin del Script
###############################################################################
