from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import *
from .forms import CustomerCreationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
    def get(self, request):
        totalitem=0
        top_wears=Product.objects.filter(category="TW")
        bottom_wears=Product.objects.filter(category="BW")
        mobiles=Product.objects.filter(category="M")
        if request.user.is_authenticated:
          totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears':top_wears, 'bottomwears':bottom_wears, 
                      'mobiles':mobiles, 'totalitem': totalitem})


class ProductDetails(View):
    def get(self, request, id):
        totalitem=0
        productview=Product.objects.get(id=id)
        item_already_in_cart = False
        if request.user.is_authenticated:
          item_already_in_cart = Cart.objects.filter(Q(product=productview.id) & Q(user=request.user)).exists()
          totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/productdetail.html', {'productview': productview, 
                      'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem })

@login_required
def add_to_cart(request):
  user=request.user
  prod_id=request.GET.get("prod_id")
  product=Product.objects.get(id=prod_id)
  Cart(user=user, product=product).save()
  return redirect("/cart")

@login_required
def show_cart(request):
  totalitem=0
  if request.user.is_authenticated:
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    totalitem = len(Cart.objects.filter(user=request.user))
    cart_product=[p for p in Cart.objects.all() if p.user == user]
    if cart_product:
      for p in cart_product:
        tempamount = (p.quantity * p.product.discounted_price)
        amount += tempamount
        total_amount=amount + shipping_amount
      return render(request, 'app/addtocart.html',{'carts':cart, 'totalamount':total_amount, 'amount':amount, 'totalitem': totalitem})
    else:
      return render(request, 'app/emptycart.html')


def plus_cart(request):
  if request.method == "GET":
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity+=1
    c.save()
    amount = 0.0
    shipping_amount = 70.0
    cart_product=[p for p in Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount += tempamount
    data = {
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount,
    }
    return JsonResponse(data)

def minus_cart(request):
  if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    if c.quantity !=1:
      c.quantity -=1
      c.save()
    amount = 0.0
    shipping_amount = 70.0
    cart_product=[p for p in Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount += tempamount
    data = {
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount,
    }
    return JsonResponse(data)


def remove_cart(request):
  if request.method == "GET":
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.delete()
    amount = 0.0
    shipping_amount = 70.0
    cart_product=[p for p in Cart.objects.all() if p.user == request.user]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount += tempamount
    data = {
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount,
    }
    return JsonResponse(data)

def buy_now(request):
  user=request.user
  prod_id=request.GET.get("prod_id")
  product=Product.objects.get(id=prod_id)
  Cart(user=user, product=product).save()
  return redirect("/checkout")

@login_required
def address(request):
 totalitem=0
 if request.user.is_authenticated:
   totalitem = len(Cart.objects.filter(user=request.user))
 address=Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html', {'address':address, 'active':'btn-primary', 'totalitem': totalitem})

@login_required
def orders(request):
 totalitem=0
 if request.user.is_authenticated:
   totalitem = len(Cart.objects.filter(user=request.user))
 ord=OrderPlaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html', {'order_placed':ord, 'totalitem': totalitem})

def change_password(request):
 totalitem=0
 if request.user.is_authenticated:
   totalitem = len(Cart.objects.filter(user=request.user))
 return render(request, 'app/changepassword.html',{'totalitem': totalitem})

def mobile(request, data=None):
 totalitem=0
 if request.user.is_authenticated:
   totalitem = len(Cart.objects.filter(user=request.user))
 if data==None:
   mobiles=Product.objects.filter(category='M')
 elif data=='Oppo' or data=='Samsung' or data=='Iphone' or data == 'Redmi':
   mobiles=Product.objects.filter(category='M').filter(brand=data) 
 elif data=='below':
   mobiles=Product.objects.filter(category='M').filter(discounted_price__lte=15000)
 elif data=='above':
   mobiles=Product.objects.filter(category='M').filter(discounted_price__gt=15000)
 return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem': totalitem})

def topwear(request, data=None):
  totalitem=0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  if data == None:
    products=Product.objects.filter(category='TW')
  elif data == 'Puma' or data == 'Spykar' or data == 'Nike' or data == 'Casual':
    products=Product.objects.filter(category='TW').filter(brand=data)
  return render(request, 'app/topwear.html', {'products':products, 'totalitem': totalitem})

def bottomwear(request, data=None):
  totalitem=0
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  if data == None:
    products=Product.objects.filter(category='BW')
  elif data == 'Highlander' or data == 'Lee' or data == 'Spykar':
    products=Product.objects.filter(category='BW').filter(brand=data)
  return render(request, 'app/bottomwear.html', {'products':products, 'totalitem': totalitem})


class CustomerRegistration(View):
    def get(self, request):
        form=CustomerCreationForm()
        return render(request,'app/customerregistration.html', {'form':form})

    def post(self, request):
        form=CustomerCreationForm(request.POST)
        if form.is_valid():
          messages.success(request, "Congratulations..!! Registered Successfully")
          form.save()
        return render(request,'app/customerregistration.html', {'form':form})

@login_required
def checkout(request):
  user=request.user
  address=Customer.objects.filter(user=user)
  cart_items=Cart.objects.filter(user=user)
  amount=0.0
  shipping_amount = 70.0
  total_amount=0.0
  if user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  cart_product=[p for p in Cart.objects.all() if p.user == request.user]
  if cart_product:
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount += tempamount
    total_amount= amount + shipping_amount

  return render(request, 'app/checkout.html',{'add':address, 'totalamount':total_amount, 'cartitems':cart_items, 'totalitem': totalitem})

@login_required
def payment_done(request):
  user=request.user
  custid=request.GET.get("cust_id")
  customer=Customer.objects.get(id=custid)
  cart=Cart.objects.filter(user=user)
  for c in cart:
    OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment='COD').save()
    c.delete()
    send_purchase_confirmation_email(customer.user.email, c.product.title, customer.name)

  return redirect("orders")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
  def get(self, request):
    totalitem=0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
    form=CustomerProfileForm()
    return render(request,'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem': totalitem})

  def post(self, request):
    form = CustomerProfileForm(request.POST)
    if form.is_valid():
      usr=request.user
      name=form.cleaned_data['name']
      locality=form.cleaned_data['locality']
      city=form.cleaned_data['city']
      state=form.cleaned_data['state']
      zipcode=form.cleaned_data['zipcode']
      reg=Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
      reg.save()
      messages.success(request, 'Congratulations!! Profile Updated Successfully')
    return render(request,'app/profile.html',{'form':form, 'active':'btn-primary'})


def send_purchase_confirmation_email(customer_email, product_name, name):
    subject = 'Purchase Confirmation'
    from_email = 'brofashion1101@gmail.com'
    to_email = [customer_email]
    
    context = {
        'product_name': product_name,
        'name': name,
    }

    html_message = render_to_string('app/purchase_confirmation.html', context)
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
    email.attach_alternative(html_message, "text/html")  
    print(email.send())
    email.send()
