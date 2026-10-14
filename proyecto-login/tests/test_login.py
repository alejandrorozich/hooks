"""Pruebas de las reglas del login. Están protegidas por un hook: nadie puede editarlas."""
import unittest

import auth
import db

EMAIL = "ana@upb.edu"
PASSWORD = "clave-segura-1"


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.conexion = db.conectar(":memory:")
        self.addCleanup(self.conexion.close)
        auth.registrar_usuario(self.conexion, "Ana", EMAIL, PASSWORD)

    def test_cada_usuario_tiene_sal_distinta(self):
        auth.registrar_usuario(self.conexion, "Luis", "luis@upb.edu", PASSWORD)
        hashes = [f["password_hash"] for f in self.conexion.execute("SELECT password_hash FROM usuarios")]
        self.assertNotIn(PASSWORD, hashes)
        self.assertNotEqual(hashes[0], hashes[1], "misma contraseña no debe producir el mismo hash")

    def test_password_incorrecta_no_inicia_sesion(self):
        self.assertIsNone(auth.iniciar_sesion(self.conexion, EMAIL, "otra-clave-123"))
        self.assertIsNotNone(auth.iniciar_sesion(self.conexion, EMAIL, PASSWORD))

    def test_email_duplicado_sin_importar_mayusculas(self):
        with self.assertRaises(auth.ErrorAuth):
            auth.registrar_usuario(self.conexion, "Ana 2", "  ANA@upb.edu ", "otra-clave-123")

    def test_password_menor_a_8_caracteres(self):
        with self.assertRaises(auth.ErrorAuth):
            auth.registrar_usuario(self.conexion, "Luis", "luis@upb.edu", "1234567")

    def test_cerrar_sesion_invalida_el_token(self):
        sesion = auth.iniciar_sesion(self.conexion, EMAIL, PASSWORD)
        self.assertEqual(auth.usuario_por_token(self.conexion, sesion["token"])["email"], EMAIL)
        auth.cerrar_sesion(self.conexion, sesion["token"])
        self.assertIsNone(auth.usuario_por_token(self.conexion, sesion["token"]))


if __name__ == "__main__":
    unittest.main()
