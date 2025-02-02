from django.urls import path
from . import views

urlpatterns = [
    # Dynamic route for disease pages
    path('ugonjwa/upungufu_wa_nguvu_za_kiume/', views.upungufu_wa_nguvu_za_kiume, name='upungufu_wa_nguvu_za_kiume'),
    path('ugonjwa/kisukari/', views.kisukari, name='kisukari'),
    path('ugonjwa/presha/', views.presha, name='presha'),
    path('ugonjwa/michirizi/', views.michirizi, name='michirizi'),
    path('ugonjwa/pid/', views.pid, name='pid'),
    path('ugonjwa/uti_sugu/', views.uti_sugu, name='uti_sugu'),
    path('ugonjwa/tezi_dume/', views.tezi_dume, name='tezi_dume'),
    path('ugonjwa/magonjwa_ya_ngozi/', views.magonjwa_ya_ngozi, name='magonjwa_ya_ngozi'),
    path('ugonjwa/bawasiri/', views.bawasiri, name='bawasiri'),
    path('ugonjwa/vidonda_vya_tumbo/', views.vidonda_vya_tumbo, name='vidonda_vya_tumbo'),
    path('ugonjwa/gas_tumboni/', views.gas_tumboni, name='gas_tumboni'),
    path('ugonjwa/stroke/', views.stroke, name='stroke'),
    path('ugonjwa/pumu/', views.pumu, name='pumu'),
    path('ugonjwa/ngiri/', views.ngiri, name='ngiri'),
    path('ugonjwa/mimba_kuharibika/', views.mimba_kuharibika, name='mimba_kuharibika'),
    path('ugonjwa/kutokushika_ujauzito/', views.kutokushika_ujauzito, name='kutokushika_ujauzito'),
    path('ugonjwa/kupunguza_uzito/', views.kupunguza_uzito, name='kupunguza_uzito'),

    # Other routes
    path('kuhusu-sisi/', views.kuhusu, name='kuhusu'),
    path('ajira/', views.ajira, name='ajira'),
    path('wasiliana-nasi/', views.mawasiliano, name='mawasiliano'),
    path('tiba-ya-magonjwa/', views.tiba, name='tiba'),
    
    # Home page
    path('', views.home, name='home'),  # Example for the home page

    path('weka_oda/', views.weka_oda, name='weka_oda'),
]
