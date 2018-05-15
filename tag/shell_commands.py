# Shell session 1
# python manage.py shell

from tags.models import Tag 

qs = Tag.objects.all()
print(qs)
red = Tag.objects.last()
red.title
red.slug

red.products 

# Returns: a manytomany relationship manager. so it is 
# much like a manager, so, we can do this --

red.products.all()

# this is an actual queryset of PRODUCTS
# Much like, Products.objects.all, but in this case, it's
# ALL of the products that are related to the "red" tag

red.products.all().first() 
# Returns the first instance, if any

exit()


# Shell session 2
# python manage.py shell

from products.models import Product

qs=Product.objects.all()
print(qs)
tshirt=qs.first()
tshirt.title
tshirt.description

tshirt.tag
# Raises an error bcoz the Product model 
# doesnt have a field "tag"


tshirt.tags
# Raises an error bcoz the Product model 
# doesnt have a field "tags"

tshirt.tag_set
# this will work bcoz Tag has Product as manytomany field

tshirt.tag_set.all()