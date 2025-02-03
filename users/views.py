from django.shortcuts import render
from django.shortcuts import render, redirect

from django.core.mail import send_mail
from django.http import JsonResponse
from .models import Oda, Dawa, MaoniMteja  # Import your order model
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    dawa_list = Dawa.objects.all()
    maoni_list = list(MaoniMteja.objects.all().order_by('-tarehe_iliyoandikwa').values('jina_mteja', 'eneo', 'ujumbe'))  
    return render(request, 'diseases/home.html', {'dawa_list': dawa_list, 'maoni_json': maoni_list})

def kisukari(request):
    return render(request, 'diseases/kisukari.html')

def presha(request):
    return render(request, 'diseases/presha.html')

def michirizi(request):
    return render(request, 'diseases/michirizi.html')

def upungufu_wa_nguvu_za_kiume(request):
    return render(request, 'diseases/upungufu_wa_nguvu_za_kiume.html')

def pid(request):
    return render(request, 'diseases/pid.html')

def uti_sugu(request):
    return render(request, 'diseases/uti_sugu.html')

def tezi_dume(request):
    return render(request, 'diseases/tezi_dume.html')

def magonjwa_ya_ngozi(request):
    return render(request, 'diseases/magonjwa_ya_ngozi.html')

def bawasiri(request):
    return render(request, 'diseases/bawasiri.html')

def vidonda_vya_tumbo(request):
    return render(request, 'diseases/vidonda_vya_tumbo.html')

def gas_tumboni(request):
    return render(request, 'diseases/gas_tumboni.html')

def stroke(request):
    return render(request, 'diseases/stroke.html')

def pumu(request):
    return render(request, 'diseases/pumu.html')

def ngiri(request):
    return render(request, 'diseases/ngiri.html')

def mimba_kuharibika(request):
    return render(request, 'diseases/mimba_kuharibika.html')

def kutokushika_ujauzito(request):
    return render(request, 'diseases/kutokushika_ujauzito.html')

def kupunguza_uzito(request):
    return render(request, 'diseases/kupunguza_uzito.html')

def magonjwa(request):
    return render(request, 'diseases/magonjwa.html')

def tiba(request):
    dawa_list = Dawa.objects.all()
    return render(request, 'diseases/tiba.html', {'dawa_list': dawa_list})

def kuhusu(request):
    return render(request, 'diseases/kuhusu.html')

def mawasiliano(request):
    return render(request, 'diseases/mawasiliano.html')

def ajira(request):
    return render(request, 'diseases/ajira.html')


#__________#

def weka_oda(request):
    if request.method == 'POST':
        jina_dawa = request.POST.get('jina_dawa')
        jina_mnunuzi = request.POST.get('jina_mnunuzi')
        namba_simu = request.POST.get('namba_simu')
        maelezo_ziada = request.POST.get('maelezo_ziada')

        # Save the order to the database
        if jina_dawa and jina_mnunuzi and namba_simu:
            oda = Oda(
                jina_dawa=jina_dawa,
                jina_mnunuzi=jina_mnunuzi,
                namba_simu=namba_simu,
                maelezo_ziada=maelezo_ziada
            )
            oda.save()

            # Notify all superusers by email
            superusers = User.objects.filter(is_superuser=True)
            subject = "New Order Received"
            message = f"New order details:\n\nMedicine: {jina_dawa}\nCustomer: {jina_mnunuzi}\nPhone: {namba_simu}\nAdditional Info: {maelezo_ziada}"

            # Send email to each superuser
            for superuser in superusers:
                send_mail(
                    subject,
                    message,
                    'fmklink@gmail.com',  # Sender's email address (change this if needed)
                    [superuser.email],  # Recipient's email
                    fail_silently=False,
                )

            # Return success message as JSON for AJAX
            return JsonResponse({'success': True})

        else:
            # Return error message as JSON if required fields are missing
            return JsonResponse({'success': False, 'error': 'Tafadhali jaza taarifa zote zinazohitajika.'})

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
