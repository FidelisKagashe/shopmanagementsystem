from django.contrib import admin
from .models import Oda, Dawa, MaoniMteja

@admin.register(Oda)
class OdaAdmin(admin.ModelAdmin):
    list_display = ('jina_dawa', 'jina_mnunuzi', 'namba_simu', 'tarehe_ya_oda')
    search_fields = ('jina_dawa', 'jina_mnunuzi', 'namba_simu')
    list_filter = ('tarehe_ya_oda',)
    ordering = ('-tarehe_ya_oda',)

@admin.register(Dawa)
class DawaAdmin(admin.ModelAdmin):
    list_display = ('jina', 'bei')
    search_fields = ('jina',)
    list_filter = ('bei',)

@admin.register(MaoniMteja)
class MaoniMtejaAdmin(admin.ModelAdmin):
    list_display = ('jina_mteja', 'eneo', 'tarehe_iliyoandikwa')
    search_fields = ('jina_mteja', 'eneo')
    list_filter = ('tarehe_iliyoandikwa',)