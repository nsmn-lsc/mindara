from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date

from apps.authentication.models import User
from apps.eventos.models import Evento


class ReportesViewsTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		# Crear usuario admin para tener acceso completo
		cls.user = User.objects.create_user(
			username="adminuser",
			email="admin@example.com",
			password="testpass123",
			first_name="Admin",
			last_name="User",
		)
		cls.user.user_level = "ADMIN"
		cls.user.save()

		# Crear eventos de ejemplo futuros (para pasar validaciones de modelo)
		hoy = timezone.now().date()
		manana = hoy + timedelta(days=1)
		fin_de_semana = hoy + timedelta(days=(6 - hoy.weekday()))  # aprox dentro de la semana

		Evento.objects.create(
			nombre_evento="Evento Agenda 1",
			fecha_evento=manana,
			hora_evento="10:00",
			usuario=cls.user,
			etapa="confirmado",
			prioridad="media",
		)

		Evento.objects.create(
			nombre_evento="Evento Semana",
			fecha_evento=fin_de_semana if fin_de_semana >= hoy else hoy + timedelta(days=2),
			hora_evento="11:00",
			usuario=cls.user,
			etapa="planificacion",
			prioridad="alta",
		)

		Evento.objects.create(
			nombre_evento="Evento Mes con Carpeta",
			fecha_evento=(hoy.replace(day=28) if hoy.day < 28 else hoy + timedelta(days=3)),
			hora_evento="12:00",
			usuario=cls.user,
			etapa="revision",
			prioridad="baja",
			carpeta_ejecutiva=True,
			carpeta_ejecutiva_liga="https://example.com/presentacion.pptx",
		)

	def setUp(self):
		# Ingresar como el usuario admin
		self.client.force_login(self.user)

	def test_index_view_ok(self):
		url = reverse("reportes:index")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "Reportes")

	def test_historial_view_ok(self):
		url = reverse("reportes:historial")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "Historial")

	def test_generar_agenda_xlsx(self):
		url = reverse("reportes:agenda") + "?formato=xlsx"
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(
			resp["Content-Type"],
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)
		# Nombre de archivo en cabecera
		self.assertIn("attachment; filename=", resp.get("Content-Disposition", ""))

	def test_generar_semana_pdf(self):
		url = reverse("reportes:semana") + "?formato=pdf"
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp["Content-Type"], "application/pdf")

	def test_generar_carpeta_xlsx(self):
		url = reverse("reportes:carpeta_ejecutiva") + "?formato=xlsx"
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(
			resp["Content-Type"],
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)

