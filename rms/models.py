from django.db import models

# Create your models here.

class Category (models.Model) :
    id = models.AutoField(primary_key=True)
    Category_name = models.CharField(max_length=100,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.Category_name
    
class Food (models.Model):
    id = models.AutoField(primary_key=True)
    Food_name = models.CharField(max_length=100)
    price = models.DecimalField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return self.Food_name
        
class order(models.Model):
    username = models.CharField(max_length=150,blank=False,null=False)
    phone = models.CharField(max_length=10,blank=False,null=False)
    food = models.ForeignKey("Food", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.username
