from django.db import models

class Oda(models.Model):
    jina_dawa = models.CharField(max_length=255)
    jina_mnunuzi = models.CharField(max_length=255)
    namba_simu = models.CharField(max_length=15)
    maelezo_ziada = models.TextField(blank=True, null=True)
    tarehe_ya_oda = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Oda ya {self.jina_dawa} - {self.jina_mnunuzi}'

class Dawa(models.Model):
    jina = models.CharField(max_length=200, verbose_name="Jina la Dawa")  # Medicine name
    maelezo = models.TextField(verbose_name="Maelezo ya Dawa", blank=True)  # Description
    bei = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bei ya Dawa")  # Price
    picha = models.ImageField(upload_to='dawa_picha/', blank=True, null=True, verbose_name="Picha ya Dawa")  # Optional image

    class Meta:
        verbose_name = "Dawa"
        verbose_name_plural = "Dawa"
        ordering = ['jina']  # Sort alphabetically by name

    def __str__(self):
        return self.jina

class MaoniMteja(models.Model):
    jina_mteja = models.CharField(max_length=100)
    eneo = models.CharField(max_length=100)
    ujumbe = models.TextField()
    tarehe_iliyoandikwa = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jina_mteja} - {self.eneo}"