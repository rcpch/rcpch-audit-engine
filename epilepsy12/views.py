from multiprocessing import context
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView

from epilepsy12.forms import CaseForm


from .models import Case


class CaseListView(ListView):
    model = Case
    context_object_name = 'epilepsy12_cases'

    def get_context_data(self, **kwargs):
        context['cases_list'] = Case.objects.all()
        return context


class CaseDetailView(DetailView):

    queryset = Case.objects.all()

    def get_object(self):
        # change fields in the record and save them
        return super().get_object()


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    return render(request, template_name, {})


def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})


def hospital(request):
    case_list = Case.objects.order_by('surname')[:10]
    context = {'case_list': case_list}
    template_name = 'epilepsy12/hospital.html'
    return render(request, template_name, context)


def create(request):
    form = CaseForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('hospital')
    context = {
        "form": form
    }
    return render(request=request, template_name='epilepsy12/createcase.html', context=context)


def update(request, id):
    case = get_object_or_404(Case, id=id)
    form = CaseForm(instance=case)

    if request.method == "POST":
        form = CaseForm(request.POST, instance=case)
        if form.is_valid:
            form.save()
            return redirect('hospital')

    context = {
        "form": form
    }

    return render(request=request, template_name='epilepsy12/createcase.html', context=context)


# def case(request, id):
#     case = Case.objects.get(id=id)
#     context = {
#         'selected_case': case,
#         'date_of_birth': case.date_of_birth.strftime('%Y-%m-%d')
#     }
#     template_name = 'epilepsy12/case.html'

#     if (request.method == "GET"):
#         case = Case.objects.get(id=id)
#         context = {
#             'selected_case': case,
#             'date_of_birth': case.date_of_birth.strftime('%Y-%m-%d')
#         }
#         template_name = 'epilepsy12/case.html'
#         return render(request, template_name=template_name, context=context)

#     elif(request.method == "POST"):
#         if 'update' in request.POST:
#             # need to update database here
#             return render(request, template_name=template_name, context=context)
#         elif 'delete' in request.POST:
#             # need to delete record here
#             return render(request, template_name=template_name, context=context)
#         else:
#             return
#     else:
#         # must be PUT or some other type
#         return


def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})


def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})
