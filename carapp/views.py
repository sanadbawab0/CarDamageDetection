from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import os
from keras import backend as k


from .models import *
from .forms import *
from .model import *
# Create your views here.


def index(request):
    return render(request, 'index.html')



def list(request):
    image_path = ''
    image_path1 = ''
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            newdoc = PicUpload(imagefile=request.FILES['imagefile'])
            newdoc.save()

            return HttpResponseRedirect(reverse('list'))

    else:
        form = ImageForm()

    documents = PicUpload.objects.all()

    for doc in documents:
        image_path = doc.imagefile.name
        image_path1 = '/'+image_path

    request.session['image_path'] = image_path


    return render(request, 'list.html',
                  {'documents': documents, 'image_path1': image_path1, 'form': form}
                  )

def engine(request):
    myCar = request.session['image_path']
    img_path = myCar
    request.session.pop('image_path',None)
    request.session.modified = True
    with graph.as_default():
        img_224 = prepare_img_224(img_path)
        img_flat = prepare_flat(img_224)
        g1 = car_categories_check(img_224)
        g2 = car_damage_check(img_flat)

        while True:
            try:
                g1_pic = 'N/A'
                g2_pic = 'N/A'
                g3 = 'N/A'
                g4 = 'N/A'
                ns = 'N/A'

                if g1 is False:
                    g1_pic = "Are you sure its a car? Make sure you upload a clear picture of your car"
                    break
                else:
                    g1_pic = "Its a Car"

                if g2 is False:
                    g2_pic = "Are you sure your car is damaged? Make sure you upload a clear picture of your car"
                    break
                else:
                    g2_pic = "Car Damaged"

                    g3 = location_assesment(img_flat)
                    g4 = severity_assesment(img_flat)
                    ns = 'a) Create a report \nb) Proceed to cost estimator'
                    break

            except:
                break

        src = 'pic_upload/'
        for image_file_name in os.listdir(src):
            #if image_file_name.endswith(".jpg"):
                os.remove(src + image_file_name)

        #k.clear_session()

        return render(
            request,
            'result.html', context={'g1_pic': g1_pic, 'g2_pic': g2_pic, 'loc': g3, 'sev': g4, 'ns': ns}
        )
