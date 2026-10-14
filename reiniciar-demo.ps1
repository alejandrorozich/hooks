# Deja la demo de hooks como al inicio: código correcto, pruebas originales y bitácora vacía.
$raiz = $PSScriptRoot
Copy-Item "$raiz\.reset\notas.py" "$raiz\proyecto-demo\notas.py" -Force
Copy-Item "$raiz\.reset\test_notas.py" "$raiz\proyecto-demo\tests\test_notas.py" -Force
Copy-Item "$raiz\.reset\login\auth.py" "$raiz\proyecto-login\auth.py" -Force
Copy-Item "$raiz\.reset\login\test_login.py" "$raiz\proyecto-login\tests\test_login.py" -Force
Remove-Item "$raiz\proyecto-login\login.db" -Force -ErrorAction SilentlyContinue
Remove-Item "$raiz\.claude\auditoria.log", "$raiz\.codex\auditoria.log", "$raiz\.opencode\auditoria.log" -Force -ErrorAction SilentlyContinue
Get-ChildItem "$raiz\proyecto-demo", "$raiz\proyecto-login", "$raiz\hooks" -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Write-Host "Demo de hooks reiniciada."
