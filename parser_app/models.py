from django.db import models

class Source(models.Model):
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True, max_length=500)
    name = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'sources'
    
    def __str__(self):
        return self.name

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=150, unique=True)
    
    class Meta:
        db_table = 'authors'
    
    def __str__(self):
        return self.fullname

class ScientificPaper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    publication_year = models.IntegerField(null=True, blank=True)
    place_of_publication = models.CharField(max_length=200, blank=True)
    work_type = models.CharField(max_length=100, blank=True)
    pages_count = models.IntegerField(null=True, blank=True)
    url = models.URLField(max_length=500, unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    parsed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scientific_papers'
        indexes = [models.Index(fields=['url'])]
    
    def __str__(self):
        return self.title[:50]

class PaperAuthor(models.Model):
    paper = models.ForeignKey(ScientificPaper, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'paper_authors'
        unique_together = ['paper', 'author']
    
    def __str__(self):
        return f"{self.paper.title[:30]} - {self.author.fullname}"