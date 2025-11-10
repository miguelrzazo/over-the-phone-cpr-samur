# Guía de Migración de Ramas - RCP Transtelefónica

**Fecha:** 10 de Noviembre de 2025  
**Objetivo:** Hacer que la rama `copilot/delete-old-branches` se convierta en la rama `main` y eliminar las ramas antiguas

---

## 📋 Situación Actual

### Ramas Existentes en el Repositorio

| Rama | Commit SHA | Estado | Acción Requerida |
|------|-----------|--------|------------------|
| `copilot/delete-old-branches` | `2a870b0` | ✅ **MÁS RECIENTE** | Convertir en `main` |
| `main` | `058ff83` | ⚠️ Desactualizada | Actualizar con contenido nuevo |
| `copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189` | `8d356ba` | ❌ Antigua | Eliminar |
| `add-claude-github-actions-1762778821956` | `3bbba3e` | ❌ Antigua | Eliminar |

---

## 🎯 Objetivo

La rama `copilot/delete-old-branches` contiene el trabajo más reciente y completo del proyecto. Necesitamos:

1. ✅ Hacer que el contenido de `copilot/delete-old-branches` se convierta en la nueva rama `main`
2. ✅ Eliminar las ramas antiguas que ya no se necesitan
3. ✅ Mantener el historial limpio

---

## 🚀 Opción 1: Actualización mediante Pull Request (RECOMENDADO)

Esta es la forma más segura y permite revisión antes de los cambios.

### Pasos:

1. **Ir a GitHub y crear un Pull Request:**
   ```
   Base: main
   Compare: copilot/delete-old-branches
   ```

2. **Revisar los cambios** en la interfaz de GitHub

3. **Aprobar y hacer merge del PR** usando "Squash and merge" o "Merge commit"

4. **Eliminar las ramas antiguas** desde la interfaz de GitHub:
   - Ve a Settings → Branches → Branch protection rules
   - O usa la interfaz de ramas para eliminar cada una manualmente

---

## 🚀 Opción 2: Actualización Local mediante Git (Avanzado)

Para usuarios con experiencia en Git que prefieren trabajar localmente.

### Prerequisitos:
- Tener Git instalado localmente
- Tener acceso al repositorio clonado
- Tener permisos de escritura en el repositorio remoto

### Pasos Detallados:

```bash
# 1. Clonar el repositorio (si no lo tienes ya)
git clone https://github.com/miguelrzazo/over-the-phone-cpr-samur.git
cd over-the-phone-cpr-samur

# 2. Asegurarse de tener todas las ramas actualizadas
git fetch --all

# 3. Crear una copia de seguridad de la rama main actual (por precaución)
git checkout main
git branch main-backup-$(date +%Y%m%d)

# 4. Actualizar main con el contenido de copilot/delete-old-branches
git checkout copilot/delete-old-branches
git checkout -b new-main

# 5. Forzar que main tenga el mismo contenido que copilot/delete-old-branches
git checkout main
git reset --hard copilot/delete-old-branches

# 6. Subir los cambios a GitHub (requiere force push)
# ⚠️ ADVERTENCIA: Esto reescribirá la historia de main
git push origin main --force

# 7. Eliminar las ramas antiguas del remoto
git push origin --delete copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189
git push origin --delete add-claude-github-actions-1762778821956

# 8. Opcionalmente, eliminar también copilot/delete-old-branches ya que su contenido está en main
git push origin --delete copilot/delete-old-branches

# 9. Limpiar ramas locales
git branch -D copilot/delete-old-branches
git branch -D copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189
git branch -D add-claude-github-actions-1762778821956

# 10. Limpiar referencias remotas obsoletas
git fetch --prune
```

---

## 🚀 Opción 3: Actualización mediante GitHub CLI (gh)

Si tienes GitHub CLI instalado:

```bash
# 1. Verificar estado actual
gh repo view miguelrzazo/over-the-phone-cpr-samur

# 2. Crear PR para merge
gh pr create --base main --head copilot/delete-old-branches \
  --title "Actualizar main con último trabajo" \
  --body "Actualiza main con el contenido más reciente de copilot/delete-old-branches"

# 3. Hacer merge del PR
gh pr merge --squash --delete-branch

# 4. Eliminar ramas antiguas
gh api repos/miguelrzazo/over-the-phone-cpr-samur/git/refs/heads/copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189 -X DELETE
gh api repos/miguelrzazo/over-the-phone-cpr-samur/git/refs/heads/add-claude-github-actions-1762778821956 -X DELETE
```

---

## ⚠️ Consideraciones Importantes

### Antes de Proceder

1. **Backup:** Asegúrate de tener una copia de seguridad del repositorio completo
2. **Colaboradores:** Si hay otros colaboradores, notifícales de los cambios
3. **CI/CD:** Verifica que no haya pipelines en ejecución que dependan de las ramas a eliminar
4. **Branch Protection:** Si `main` tiene protección de rama en GitHub, temporalmente desactívala

### Después de los Cambios

1. **Verificar:** Comprueba que `main` tiene el contenido correcto
2. **Probar:** Ejecuta los tests y verifica que todo funciona
3. **Actualizar Equipos:** Notifica a los colaboradores para que actualicen sus repositorios locales:
   ```bash
   git fetch --all --prune
   git checkout main
   git reset --hard origin/main
   ```

---

## 🔍 Verificación Post-Migración

Después de completar la migración, verifica:

```bash
# 1. Verificar que main está actualizado
git checkout main
git log --oneline -5
# Debería mostrar: 2a870b0 Initial plan

# 2. Verificar qué ramas quedan
git branch -a
# Solo debería quedar main (y posiblemente main-backup)

# 3. Verificar el contenido
ls -la
# Debería mostrar todos los directorios: data/, documentation/, final_noteboooks/, latex/, etc.

# 4. Verificar que el proyecto funciona
cd final_noteboooks/
jupyter notebook  # O el comando que uses para trabajar
```

---

## 📞 Soporte

Si encuentras problemas durante la migración:

1. **No fuerces cambios** si no estás seguro
2. **Crea un issue** en GitHub describiendo el problema
3. **Contacta al equipo** de desarrollo del proyecto

---

## 🔐 Seguridad

- ✅ Los datos sensibles permanecen protegidos por `.gitignore`
- ✅ No se comparten datos de pacientes
- ✅ Solo se migran archivos de código y documentación

---

## 📝 Resumen de Comandos Rápidos

Para usuarios expertos que solo quieren los comandos esenciales:

```bash
git fetch --all
git checkout main
git reset --hard copilot/delete-old-branches
git push origin main --force
git push origin --delete copilot/fix-5409a270-e64e-4f78-a418-19815b3ed189
git push origin --delete add-claude-github-actions-1762778821956
git push origin --delete copilot/delete-old-branches
git fetch --prune
```

⚠️ **ADVERTENCIA:** Estos comandos reescriben historia. Úsalos solo si entiendes las implicaciones.

---

**Última actualización:** 10 de Noviembre de 2025  
**Versión:** 1.0
