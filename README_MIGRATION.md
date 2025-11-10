# 🔄 Migración de Ramas - Instrucciones Rápidas

Este directorio contiene herramientas para actualizar la rama `main` con el contenido más reciente.

## 📌 Situación

La rama `copilot/delete-old-branches` contiene el trabajo más actualizado del proyecto. Necesitamos hacer que este contenido se convierta en la nueva rama `main` y eliminar ramas obsoletas.

## 🚀 Opción Rápida: Script Automatizado (RECOMENDADO)

**Para usuarios de Mac/Linux:**

```bash
# 1. Dar permisos de ejecución (solo primera vez)
chmod +x migrate_branches.sh

# 2. Ejecutar el script
./migrate_branches.sh
```

**Para usuarios de Windows:**

```bash
# Usar Git Bash
bash migrate_branches.sh
```

El script te guiará paso a paso y pedirá confirmación antes de cada acción importante.

## 📖 Opción Detallada: Guía Manual

Si prefieres hacer el proceso manualmente o necesitas más información:

👉 **Lee la guía completa:** [`BRANCH_MIGRATION_GUIDE.md`](BRANCH_MIGRATION_GUIDE.md)

La guía incluye:
- Explicación detallada de cada paso
- Tres opciones diferentes de migración
- Comandos para Git, GitHub CLI, y Pull Requests
- Verificaciones de seguridad
- Troubleshooting

## ⚠️ Importante

**Antes de ejecutar:**
- ✅ Asegúrate de tener permisos de escritura en el repositorio
- ✅ Notifica a otros colaboradores (si los hay)
- ✅ El script crea backups automáticamente, pero es buena idea tener una copia local

**Después de la migración:**
- Los colaboradores deben actualizar sus copias locales:
  ```bash
  git fetch --all --prune
  git checkout main
  git reset --hard origin/main
  ```

## 📁 Archivos en este Directorio

- `migrate_branches.sh` - Script automatizado de migración (Mac/Linux/Git Bash)
- `BRANCH_MIGRATION_GUIDE.md` - Guía detallada con todas las opciones
- `README_MIGRATION.md` - Este archivo

## 🆘 Ayuda

Si tienes problemas:
1. Lee primero `BRANCH_MIGRATION_GUIDE.md`
2. Verifica que tienes Git instalado: `git --version`
3. Verifica que tienes permisos en el repositorio
4. Crea un issue en GitHub si el problema persiste

## ✅ Verificación Post-Migración

Después de ejecutar la migración, verifica que todo está correcto:

```bash
# Ver ramas actuales
git branch -a

# Ver últimos commits en main
git log --oneline -5 main

# Verificar contenido
ls -la
```

Deberías ver:
- Solo la rama `main` (y posiblemente un backup)
- El commit más reciente: `2a870b0 Initial plan`
- Todos los directorios del proyecto: `data/`, `documentation/`, `final_noteboooks/`, `latex/`, etc.

---

**¿Listo para comenzar?** → Ejecuta `./migrate_branches.sh` o lee `BRANCH_MIGRATION_GUIDE.md`
