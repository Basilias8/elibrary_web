from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError, transaction
from .forms import ParseForm
from .models import ScientificPaper, Source, Author, PaperAuthor
from .parser import ELibraryParser

def index(request):
    form = ParseForm()
    recent_papers = ScientificPaper.objects.all().order_by('-parsed_at')[:10]
    return render(request, 'parser_app/index.html', {
        'form': form,
        'recent_papers': recent_papers,
    })

def parse_article(request):
    if request.method == 'POST':
        form = ParseForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Проверка на дубликат
            if ScientificPaper.objects.filter(url=url).exists():
                messages.error(request, '⚠️ Статья уже существует!')
                return redirect('index')
            
            try:
                parser = ELibraryParser()
                data = parser.parse_article(url)
                
                if not data['title']:
                    messages.error(request, '❌ Не удалось извлечь данные')
                    return redirect('index')
                
                with transaction.atomic():
                    source, _ = Source.objects.get_or_create(
                        url='https://www.elibrary.ru',
                        defaults={'name': 'eLibrary.ru'}
                    )
                    
                    paper, created = ScientificPaper.objects.get_or_create(
                        url=url,
                        defaults={
                            'title': data['title'],
                            'publication_year': data['year'],
                            'place_of_publication': data.get('place'),
                            'work_type': data.get('work_type'),
                            'pages_count': data.get('pages'),
                            'source': source,
                        }
                    )
                    
                    if not created:
                        messages.warning(request, '⚠️ Статья уже существует')
                        return redirect('index')
                    
                    for author_name in data['authors']:
                        if author_name and len(author_name) > 3:
                            author, _ = Author.objects.get_or_create(fullname=author_name)
                            PaperAuthor.objects.get_or_create(paper=paper, author=author)
                
                messages.success(request, f'✅ Статья сохранена: {data["title"][:50]}...')
                return redirect('result', paper_id=paper.paper_id)
                
            except IntegrityError:
                messages.error(request, '❌ Статья уже существует в БД')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'❌ Ошибка: {str(e)}')
                return redirect('index')
    
    return redirect('index')

def result(request, paper_id):
    try:
        paper = ScientificPaper.objects.get(paper_id=paper_id)
        authors = PaperAuthor.objects.filter(paper=paper).select_related('author')
        return render(request, 'parser_app/result.html', {
            'paper': paper,
            'authors': authors,
        })
    except ScientificPaper.DoesNotExist:
        messages.error(request, 'Статья не найдена')
        return redirect('index')