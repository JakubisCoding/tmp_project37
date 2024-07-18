from django.shortcuts import render, reverse
from django.views.generic import *
from .models import *
from django.views import *
from .forms import *
from django.urls import reverse_lazy

class TeachersListView(ListView):
    model = Teacher
    template_name = 'app/teachers_list.html'
    context_object_name = 'teachers'

class TeacherCreateView(View):
    
    def get(self, request):
        form=  TeacherForm()
        return render(request, 'app/teacher_add.html', {'form':form} )
    
    def post(self, request):
        form=  TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            empty_form = TeacherForm()
            return render(request, 'app/teacher_add.html', {'form':empty_form})
        return render(request, 'app/teacher_add.html', {'form':form})
    
class TeacherCreateView(CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'app/teacher_add.html'
    success_url = reverse_lazy('teachers_list')



    