# Login con hooks

Login simple y funcional: frontend en HTML/CSS/JS, backend en Python (solo librería estándar) y base de datos SQLite.
No hace falta instalar nada.

```
proyecto-login/
├── servidor.py        ← API JSON + archivos del frontend (http.server)
├── auth.py            ← reglas de negocio: registro, login, sesiones   ⚠ trae 5 errores sembrados
├── db.py              ← conexión SQLite y tablas (usuarios, sesiones)
├── static/            ← index.html, styles.css, app.js
└── tests/test_login.py← 5 pruebas, protegidas por el hook 1
```

## Ejecutar

```powershell
cd proyecto-login
python servidor.py            # http://localhost:8000
python -m unittest discover -s tests -v
```

La base `login.db` se crea sola junto a `servidor.py` (está en `.gitignore`).

## API

| Método | Ruta            | Cuerpo / cabecera                     | Respuesta                 |
|--------|-----------------|---------------------------------------|---------------------------|
| POST   | `/api/registro` | `{nombre, email, password}`           | 201 `{usuario}` · 400     |
| POST   | `/api/login`    | `{email, password}`                   | 200 `{token, usuario}` · 401 |
| GET    | `/api/perfil`   | `Authorization: Bearer <token>`       | 200 `{usuario}` · 401     |
| POST   | `/api/logout`   | `Authorization: Bearer <token>`       | 200 `{ok: true}`          |

## Las 5 pruebas (empiezan en rojo)

| Prueba | Regla que exige |
|--------|-----------------|
| `test_cada_usuario_tiene_sal_distinta` | cada contraseña se guarda con una sal aleatoria |
| `test_password_incorrecta_no_inicia_sesion` | una contraseña incorrecta no da token |
| `test_email_duplicado_sin_importar_mayusculas` | `ANA@upb.edu` y `ana@upb.edu` son la misma cuenta |
| `test_password_menor_a_8_caracteres` | mínimo 8 caracteres |
| `test_cerrar_sesion_invalida_el_token` | después del logout el token ya no sirve |

## Cómo se arreglan solas con los hooks

1. Haz `git push` manual desde tu terminal: GitHub Actions marca 5 fallos en `Pruebas (proyecto-login)`.
2. Abre Claude Code (o Codex) en la raíz del repo y pide:

   > Intenta hacer git push. Si el hook bloquea el comando por pruebas fallidas, corrige el código
   > sin modificar los tests ni desactivar los hooks. Crea un commit con las correcciones y vuelve a hacer push.

3. Los hooks obligan al agente:
   - **Hook 2** (`bloquear_comandos.py`) bloquea el `git push` mientras haya pruebas en rojo.
   - **Hook 1** (`proteger_archivos.py`) no le deja tocar `tests/`.
   - **Hook 3** (`ejecutar_tests.py`) corre las pruebas tras cada edición y le devuelve el reporte.
   - **Hook 5** (`revisar_seguridad.py`) rechaza arreglos inseguros (SQL con f-strings, md5/sha1, `random`, `innerHTML`, `eval`).
4. Con las 5 en verde el push pasa y Actions queda en verde.

`..\reiniciar-demo.ps1` vuelve a dejar los 5 errores para repetir la demo.
