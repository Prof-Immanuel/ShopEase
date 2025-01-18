from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Customer, Cart, CartItem, Seller, Order, OrderItem
from .forms import CustomerRegistrationForm, SellerCreationForm, ProductForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
# Create your views here.


def home(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def products(request):
    # Get all products by default
    products = Product.objects.all().order_by('-created_at')

    # Filter by search query if provided
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    if search_query == "admin":
        return redirect('admin_dashboard')        

    # Filter by category if provided
    category = request.GET.get('category', '')
    if category and category != 'all':
        products = products.filter(category__name=category)  # Filter by category name

    # Default cart item count to 0
    cart_item_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = CartItem.objects.filter(cart=cart).count()  # Get the item count from the cart
        except Cart.DoesNotExist:
            pass  # If no cart exists, cart_item_count remains 0

    # Paginate the products
    paginator = Paginator(products, 12)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all available categories for the sidebar
    categories = Category.objects.all()  # Fetch Category instances instead of just strings

    return render(request, 'products.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'cart_item_count': cart_item_count
    })

    
    
def product_details(request, product_id):
    # Fetch the product object using the product ID
    product = get_object_or_404(Product, id=product_id)
    
    # Render the product details page with the product data
    return render(request, 'product_details.html', {'product': product})


@login_required(login_url='login')
def create_seller(request):
    if request.method == 'POST':
        form = SellerCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the seller to the database
            return redirect('home')  # Redirect to the admin dashboard or any desired page
    else:
        form = SellerCreationForm()

    return render(request, 'seller_registration.html', {'form': form})


def customer_signup(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            login(request, customer) 
            return redirect('products') 
    else:
        form = CustomerRegistrationForm()

    return render(request, 'customer_signup.html', {'form': form})

@login_required(login_url='login')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Request.FILES is needed to handle file uploads
        if form.is_valid():
            form.save()
            return redirect('products')  # Redirect to the list of products or any other page you like
    else:
        form = ProductForm()

    return render(request, 'product_create.html', {'form': form})



def get_cart(request):
    """ Retrieve the user's cart, or create a new one if not existing """
    if request.user.is_authenticated:
        try:
           
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            return cart
        except Exception as e:
            
            return None
    else:
       
        return None


def cart_add(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=product_id)
            
            # Ensure the user has a cart; create one if it doesn't exist
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Add product to cart or update quantity if it already exists
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            
            # Calculate the number of unique products in the cart
            cart_item_count = CartItem.objects.filter(cart=cart).count()
            
            return JsonResponse({"message": "Product added to cart successfully!", "cart_item_count": cart_item_count}, status=200)
        
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method."}, status=400)


@login_required(login_url='welcome')    
def cart_detail(request):
    """ Display the cart contents """
    cart = get_cart(request)
    if cart:
        cart_items = cart.items.all()
        total_price = cart.total_price()
    else:
        cart_items = []
        total_price = 0
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
    
 
def update_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get("action")

        if action == "increment":
            item.quantity += 1
        elif action == "decrement" and item.quantity > 1:
            item.quantity -= 1
        else:
            return JsonResponse({"error": "Invalid action or quantity"}, status=400)

        item.save()

        # Calculate new totals
        cart_total = sum(i.total_price() for i in CartItem.objects.filter(cart=item.cart))  # Add parentheses if total_price is a method
        return JsonResponse({
            "new_quantity": item.quantity,
            "item_total": item.total_price(),  # Add parentheses if total_price is a method
            "cart_total": cart_total
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

        

def cart_remove(request, item_id):
    if request.method == "POST":
        try:
            # Ensure the item exists and belongs to the current user's cart
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart = item.cart
            item.delete()

            # Recalculate the total price of the cart
            cart_items = CartItem.objects.filter(cart=cart)
            cart_total = sum(i.total_price() for i in cart_items)

            return JsonResponse({
                "message": "Item removed successfully",
                "cart_total": cart_total,
            }, status=200)
        except CartItem.DoesNotExist:
            return JsonResponse({"error": "Item not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)


def checkout_page(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if not logged in

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        # Calculate total price, delivery fee, and grand total
        total_price = sum(item.total_price() for item in cart_items)
        delivery_fee = Decimal("25.00")  # Ensure delivery fee is a Decimal
        grand_total = total_price + delivery_fee

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'delivery_fee': delivery_fee,
            'grand_total': grand_total,
        }

        return render(request, 'checkout.html', context)

    except Cart.DoesNotExist:
        return render(request, 'checkout.html', {'cart_items': []})




def checkout_confirm(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        # Get the customer's name (assuming the user model has a first_name or username)
        customer_name = request.user.first_name if request.user.first_name else request.user.username

        # Calculate totals
        total_price = sum(item.total_price() for item in cart_items)
        delivery_fee = Decimal("25.00")
        grand_total = total_price + delivery_fee

        # Create an order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            delivery_fee=delivery_fee,
            grand_total=grand_total
        )

        # Add items to the order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product.name,
                quantity=item.quantity,
                price=item.total_price()
            )

        # Send order details via email
        email_subject = f"New Order Received from {customer_name}"
        email_body = f"Order Details for {customer_name} ({request.user.username}):\n\n"

        for item in cart_items:
            seller_name = item.product.seller.company_name if item.product.seller else "ShopEase"
            email_body += f"- {item.product.name} (x{item.quantity}): K{item.total_price()} (Seller: {seller_name})\n"

        email_body += f"\nTotal Price: K{total_price}\nDelivery Fee: K{delivery_fee}\nGrand Total: K{grand_total}\n"
        email_body += "\nThank you,\nShopEase"

        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            ["shopeasezm@gmail.com"],
        )

        # Clear the cart after confirming the order
        cart_items.delete()
        
        context = {
            "order_items": order.items.all(),
            "subtotal":  total_price,
            "delivery_fee": delivery_fee,
            "grand_total": grand_total,
        }

        return render(request, 'order_confirmation.html', context)

    except Cart.DoesNotExist:
        return JsonResponse({'error': 'No items in cart'}, status=400)

    
    


@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_superuser:  
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    sellers = Seller.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {
        'sellers': sellers,
        'categories': categories,
        'products': products,
    })
    
@login_required(login_url='login')
def create_seller(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        Seller.objects.create(company_name=company_name)
        return redirect('admin_dashboard')

@login_required(login_url='login')
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(name=name)
        return redirect('admin_dashboard')




@login_required(login_url='login')
def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = get_object_or_404(Category, id=request.POST.get('category'))
        seller = get_object_or_404(Seller, id=request.POST.get('seller'))
        price = request.POST.get('price')
        description = request.POST.get('description')
        in_stock = request.POST.get('in_stock') == 'on'  # Checkbox returns 'on' if checked

        # Handle image upload
        image = request.FILES.get('image', None)

        # Create the Product
        Product.objects.create(
            name=name,
            category=category,
            seller=seller,
            price=price,
            description=description,
            in_stock=in_stock,
            image=image  # Use the uploaded file directly
        )
        return redirect('admin_dashboard')

    # If GET, render a form page (if applicable)
    return render(request, 'create_product.html')


# Edit and Delete Views (Omitted for brevity, but would follow similar patterns for edit and delete)

@login_required(login_url='login')
def delete_seller(request, seller_id):
    """
    Delete a specific seller by ID.
    """
    seller = get_object_or_404(Seller, id=seller_id)
    seller_name = seller.company_name  # Save the name for messages
    seller.delete()
    messages.success(request, f"Seller '{seller_name}' was successfully deleted.")
    return redirect('admin_dashboard')  # Redirect to the admin dashboard or desired page

@login_required(login_url='login')
def delete_category(request, category_id):
    """
    Delete a specific category by ID.
    """
    category = get_object_or_404(Category, id=category_id)
    category_name = category.name  # Save the name for messages
    category.delete()
    messages.success(request, f"Category '{category_name}' was successfully deleted.")
    return redirect('admin_dashboard')  # Redirect to the admin dashboard or desired page

@login_required(login_url='login')
def delete_product(request, product_id):
    """
    Delete a specific product by ID.
    """
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name  # Save the name for messages
    product.delete()
    messages.success(request, f"Product '{product_name}' was successfully deleted.")
    return redirect('admin_dashboard')  # Redirect to the admin dashboard or desired page



@login_required(login_url='login')
def edit_seller(request, seller_id):
    """
    Edit a specific seller by ID.
    """
    seller = get_object_or_404(Seller, id=seller_id)

    if request.method == 'POST':
        seller.founder = request.POST.get('founder')
        seller.company_name = request.POST.get('company_name')
        seller.phone_number = request.POST.get('phone_number')
        seller.save()
        messages.success(request, f"Seller '{seller.company_name}' was successfully updated.")
        return redirect('admin_dashboard')  # Redirect to admin dashboard or desired page

    return render(request, 'edit_seller.html', {'seller': seller})


@login_required(login_url='login')
def edit_category(request, category_id):
    """
    Edit a specific category by ID.
    """
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        messages.success(request, f"Category '{category.name}' was successfully updated.")
        return redirect('admin_dashboard')  # Redirect to admin dashboard or desired page

    return render(request, 'edit_category.html', {'category': category})


@login_required(login_url='login')
def edit_product(request, product_id):
    """
    Edit a specific product by ID.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = get_object_or_404(Category, id=request.POST.get('category'))
        product.seller = get_object_or_404(Seller, id=request.POST.get('seller'))
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        product.image = request.FILES.get('image') or product.image  # Retain existing image if no new one
        product.in_stock = request.POST.get('in_stock') == 'on'  # Checkbox handling
        product.save()
        messages.success(request, f"Product '{product.name}' was successfully updated.")
        return redirect('admin_dashboard')  # Redirect to admin dashboard or desired page

    categories = Category.objects.all()
    sellers = Seller.objects.all()
    return render(request, 'edit_product.html', {
        'product': product,
        'categories': categories,
        'sellers': sellers,
    })




def user_login(request):
    if request.method == "POST":
        login_field = request.POST.get("username")  # Can be username or phone_number
        password = request.POST.get("password")

        # Check if the input matches a phone number
        try:
            customer = Customer.objects.get(phone_number=login_field)
            login_field = customer.username  # Use the username for authentication
            print(f"Using username for login: {login_field}")
        except Customer.DoesNotExist:
            print("Input is not a phone number; treating as username")

        # Authenticate user
        user = authenticate(request, username=login_field, password=password)
        print(f"Authenticated user: {user}")

        if user:
            login(request, user)
            return redirect("products")  # Replace "home" with your homepage URL name
        else:
            messages.error(request, "Invalid username, phone number, or password")
    
    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("home")



