from django.test import TestCase, Client
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from apps.authentication.models import User
from .models import Evento


class EventoFechaValidacionTests(TestCase):
	def setUp(self):
		# Custom user model uses email as USERNAME_FIELD
		self.user = User.objects.create_user(
			username='tester',
			email='tester@example.com',
			password='pass1234'
		)
		self.client = Client()
		self.client.login(email='tester@example.com', password='pass1234')

	def test_no_crear_evento_fecha_pasada(self):
		ayer = (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
		resp = self.client.post('/eventos/api/eventos/', data={
			'nombre_evento': 'Evento Pasado',
			'fecha_evento': ayer,
			'hora_evento': '10:00',
			'duracion': '1'
		}, content_type='application/json', follow=False)
		self.assertEqual(resp.status_code, 400)
		self.assertIn('La fecha del evento no puede ser en el pasado', resp.json().get('message', ''))

	def test_crear_evento_fecha_hoy(self):
		hoy = timezone.now().date().strftime('%Y-%m-%d')
		resp = self.client.post('/eventos/api/eventos/', data={
			'nombre_evento': 'Evento Hoy',
			'fecha_evento': hoy,
			'hora_evento': '10:00',
			'duracion': '1'
		}, content_type='application/json', follow=False)
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(resp.json().get('success'))
		self.assertTrue(Evento.objects.filter(nombre_evento='Evento Hoy').exists())

	def test_no_actualizar_evento_a_fecha_pasada(self):
		hoy = timezone.now().date()
		evento = Evento.objects.create(
			nombre_evento='Editable',
			objetivo='Obj',
			fecha_evento=hoy,
			hora_evento='09:00',
			duracion='1',
			sede='Lugar',
			prioridad='media',
			etapa='planificacion',
			aforo=10,
			usuario=self.user
		)
		ayer = (hoy - timedelta(days=1)).strftime('%Y-%m-%d')
		resp = self.client.put(f'/eventos/api/eventos/{evento.id}/', data={
			'nombre_evento': 'Editable',
			'fecha_evento': ayer,
			'hora_evento': '10:00',
			'duracion': '1'
		}, content_type='application/json', follow=False)
		self.assertEqual(resp.status_code, 400)
		self.assertIn('La fecha del evento no puede ser en el pasado', resp.json().get('message', ''))

	def test_actualizar_evento_fecha_futura(self):
		hoy = timezone.now().date()
		evento = Evento.objects.create(
			nombre_evento='Editable Futuro',
			objetivo='Obj',
			fecha_evento=hoy,
			hora_evento='09:00',
			duracion='1',
			sede='Lugar',
			prioridad='media',
			etapa='planificacion',
			aforo=10,
			usuario=self.user
		)
		manana = (hoy + timedelta(days=1)).strftime('%Y-%m-%d')
		resp = self.client.put(f'/eventos/api/eventos/{evento.id}/', data={
			'nombre_evento': 'Editable Futuro',
			'fecha_evento': manana,
			'hora_evento': '11:00',
			'duracion': '1'
		}, content_type='application/json', follow=False)
		self.assertEqual(resp.status_code, 200)
		evento.refresh_from_db()
		self.assertEqual(evento.fecha_evento.strftime('%Y-%m-%d'), manana)
