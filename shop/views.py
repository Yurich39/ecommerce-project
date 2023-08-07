from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Category, Product, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from .forms import SignUpForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


# Create your views here.

def home(request, category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category_page, available=True)
    else:
        products = Product.objects.all().filter(available=True)
    # функция возвращает home.html и обьекты: category, products
    return render(request, 'home.html', {'category': category_page, 'products': products})


def product(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    return render(request, 'product.html', {'product': product})


def _cart_id(request):  # возвращает текущую или новую сессию
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# Добавление продукта в корзину
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        # Пытаемся получить корзину из текущей сессии
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Создаем пустую корзину
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    try:
        # Если продукт есть в текущей корзине, то получим его и увеличим счетчик продуктов
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # Если продукта в текущей корзине не существует, то создаем продукт в текущей корзине 1 раз (quantity=1)
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()

    return redirect('cart_detail')  # 'cart_detail' - название метода


# Обновляет детали в текущей корзине
def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter))


# Удаляем обьект из корзины по одному
def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # ищем корзину
    product = get_object_or_404(Product, id=product_id)  # ищем товар
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')


# Полностью удаляем обьект из корзины
def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # ищем корзину
    product = get_object_or_404(Product, id=product_id)  # ищем товар
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')


# Управление запросом Sign Up - создание нового пользователя
def signUpView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) # данные из POST запроса (поля в форме в html) передаем в класс
        if form.is_valid(): # запускаем проверку данных из запроса POST на корректность
            form.save() # сохраняем запись в БД о новом пользователе
            username = form.cleaned_data.get('username') # cleaned_data - словарь с данными, которые ушли в БД
            signup_user = User.objects.get(username=username) # получаем ЭК класса auth.User из БД (auth_user)
            user_group = Group.objects.get(name='User') # получаем группу пользователь User (auth_group)
            user_group.user_set.add(signup_user) # нового пользователя из POST запроса добавляем в группу User
            # т.е. таблица auth_user_group это таблица, которая связывает пользователя и группу
            # в то время как таблицы auth_user и auth_group не знают друг о друге.
            # т.е. мы осуществляем связь между моделями many to many через использование вспомагательной таблицы в БД
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('signup')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signoutView(request):
    logout(request)
    return redirect('login')

