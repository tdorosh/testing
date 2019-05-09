from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Title, IncomingLetter, OutgoingLetter, Counterparty
# Create your views here.

#Function for generate unique elements, not view (usefull for generate select option)
def get_unique_list_elements(elements):
	unique_elements = []
	for el in elements:
		if el not in unique_elements:
			unique_elements.append(el)
	return unique_elements

def title_list(request):
	titles = Title.objects.all()
	clients = set([client['client_id__name'] for client in titles.values("client_id__name")])
	years = titles.dates('entry_datetime', 'year')
	months = titles.dates('entry_datetime', 'month')
	#Add search logic
	if request.GET.get('search_button') is not None:
		search_request = request.GET.get('search', '').strip()
		titles = titles.filter(title__contains=search_request)
		
	if request.GET.get('filtration_button') is not None:
		data = {}
		if request.GET.get('year'):
			data['entry_datetime__year'] = request.GET.get('year')
			
		if request.GET.get('month'):
			data['entry_datetime__month'] = request.GET.get('month')
		
		if request.GET.get('type'):
			data['type'] = request.GET.get('type')
			
		if request.GET.get('client'):
			data['client__name'] = request.GET.get('client')	
			
		if request.GET.get('agreement') == 'on':
			data['ministry_agreement'] = True
		else:
			data['ministry_agreement'] = False
			
		if request.GET.get('done') == 'on':
			data['is_done'] = True
		else:
			data['is_done'] = False
		
		titles = titles.filter(**data)
		
	
	return render(request, 'title/titles_list.html', {'titles': titles, 'years': years, 'months': months, 'clients': clients})
	
def title_add(request):
	titles = Title.objects.all()
	clients = get_unique_list_elements(titles.values("client_id", "client__name"))
	inletters = IncomingLetter.objects.all()
	outletters = OutgoingLetter.objects.all()
	
	if request.method == 'POST':
		
		if request.POST.get('cancel_button') is not None:
			return HttpResponseRedirect('{}?status_message=Додавання титулу відмінено'.format(reverse('title:home')))
			
		if request.POST.get('submit_button') is not None:
			errors = {}
			data = {'type': request.POST.get('type'), 'notes': request.POST.get('notes')}
			
			title = request.POST.get('title', '').strip()
			if title:
				data['title'] = title
			else:
				errors['title'] = 'Введіть назву титулу'
				
			client = Counterparty.objects.get(pk=request.POST.get('client'))
			data['client'] = client
			
			if request.POST.get('agreement') == 'on':
				data['ministry_agreement'] = True
			else:
				data['ministry_agreement'] = False
			
			if request.POST.get('done') == 'on':
				data['is_done'] = True
			else:
				data['is_done'] = False
				
			date = request.POST.get('date', '')
			if date:
				data['entry_datetime'] = date
			else:
				errors['date'] = 'Введіть дату'
				
			incoming_letters = request.POST.getlist('incoming_letter')
			outgoing_letters = request.POST.getlist('outgoing_letter')
			
			
			if errors:
				return render(request, 'title/title_add.html', {'titles': titles, 'clients': clients, 'inletters': inletters, 'outletters': outletters, 'errors': errors})
			
			else:
				title = Title.objects.create(**data)
				if incoming_letters:
					title.incoming_letter.set(incoming_letters)
				if outgoing_letters:
					title.outgoing_letter.set(outgoing_letters)
				title.save()
				return HttpResponseRedirect('{}?status_message=Титул успішно додано'.format(reverse('title:home')))
			
	return render(request, 'title/title_add.html', {'titles': titles, 'clients': clients, 'inletters': inletters, 'outletters': outletters})
	
def title_edit(request, pk):
	title = Title.objects.get(pk=pk)
	return render(request, 'title/title_edit.html', {'title': title})
	
def title_delete(request, pk):
	title = Title.objects.get(pk=pk)
	return render(request, 'title/title_delete.html', {'title': title})