import json
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import PaintingForm, ProfileUpdateForm
from .models import Bid, Order, Painting, Follower, CartItem, AdminPainting, Profile
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Painting, Transaction
from datetime import datetime
from django.utils.timezone import now
from django.utils.timezone import make_aware
from pytz import timezone
from django.core.mail import send_mail
from django.db.models import Subquery, OuterRef
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from .forms import SignupForm, LoginForm
from .forms import LoginForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sessions.models import Session
from .models import UserSettings
from django.shortcuts import render
from django.db.models import Q
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage



def home(request):
    # Check for guest mode based on the session
    guest_mode = request.session.get('guest_mode', False)

    if not request.user.is_authenticated and not guest_mode:
        return redirect('login')

    # Get the current time
    current_time = now()

    # Fetch live auctions (ongoing)
    live_auctions = Painting.objects.filter(start_time__lte=current_time, end_time__gte=current_time)

    # Fetch upcoming auctions
    upcoming_auctions = Painting.objects.filter(start_time__gt=current_time)

    # Fetch sold paintings (past auctions with winners)
    sold_paintings = Painting.objects.filter(end_time__lt=current_time).annotate(
        winner_user=Subquery(
            Bid.objects.filter(painting=OuterRef('pk'))
            .order_by('-amount')
            .values('user__username')[:1]
        ),
        final_price=Subquery(
            Bid.objects.filter(painting=OuterRef('pk'))
            .order_by('-amount')
            .values('amount')[:1]
        )
    ).exclude(winner_user=None)

    # Fetch top 5 highest-bid paintings
    top_bid_paintings = (
        Painting.objects.annotate(highest_bid=Subquery(
            Bid.objects.filter(painting=OuterRef('pk'))
            .order_by('-amount')
            .values('amount')[:1]
        ))
        .filter(highest_bid__isnull=False)  # Exclude paintings with no bids
        .order_by('-highest_bid')[:5]  # Order by highest bid and limit to 5
    )

    # Timer for the next upcoming auction
    timer = None
    if upcoming_auctions.exists():
        next_upcoming = upcoming_auctions.order_by('start_time').first()
        timer = (next_upcoming.start_time - current_time).total_seconds()

    return render(request, 'home.html', {
        'live_auctions': live_auctions,
        'upcoming_auctions': upcoming_auctions,
        'sold_paintings': sold_paintings,
        'featured_paintings': top_bid_paintings,  # Top 5 highest-bid paintings
        'timer': timer,
        'guest_mode': guest_mode,
    })

#logger = logging.getLogger(__name__)

def user_login(request):
    # Check if user is already in guest mode
    if 'guest_mode' in request.session:
        del request.session['guest_mode']  # Remove guest mode from session if the user logs in

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
            else:
                # Clear the form fields on error and display error message
                form = LoginForm()  # Reset the form to empty fields
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()  # Create a new, empty form instance

    return render(request, 'login.html', {'form': form})

from django.db import IntegrityError

def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Try to create a profile but handle duplicate entry error
            try:
                Profile.objects.create(user=user)
            except IntegrityError:
                pass  # Ignore error if profile already exists

            return redirect('login')  # Redirect to login page after signup
    else:
        form = SignupForm()
    return render(request, 'register.html', {'form': form})




def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

def set_guest_mode(request):
    request.session['guest_mode'] = True
    return redirect('home')

def search_paintings(request):
    query = request.GET.get('q', '')  # Get the search query from the URL parameter 'q'
    paintings = Painting.objects.all()

    if query:
        # Search in both title and description
        paintings = paintings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'search_results.html', {'paintings': paintings, 'query': query})

@login_required
def upload_painting(request):
    if request.method == "POST":
        form = PaintingForm(request.POST, request.FILES)
        if form.is_valid():
            painting = form.save(commit=False)
            painting.user = request.user
            painting.save()

            # Fetch all followers of the user
            followers = Follower.objects.filter(user=request.user)

            # Send email notification to followers
            for follower in followers:
                if follower.follower.email:  # Ensure follower has an email
                    send_mail(
                        subject=f"Exciting News! { request.user.username } Just Uploaded a New Painting!",
                        message=f"Dear {follower.follower.username},\n\n"
                                f"We have some exciting news for you! 🎨\n\n"
                                f"{request.user.username} has just uploaded a brand-new painting titled '{painting.title}'.\n"
                                f"This painting is set to start its auction on {painting.start_time}.\n\n"
                                f"Don't miss your chance to bid on this exclusive artwork and add it to your collection! 🖼️\n\n"
                                f"🔗 View Auction: http://127.0.0.1:8000/painting/{painting.id}\n\n"
                                f"Best regards,\n"
                                f"Art Auction Portal Team\n"
                                f"📩 Contact us: artauctions.nj@gmail.com",
                        from_email="artauctions.nj@gmail.com",
                        recipient_list=[follower.follower.email],
                    )

            return redirect("upload_painting")  # Adjust as needed

    else:
        form = PaintingForm()

    return render(request, "upload_painting.html", {"form": form})


def continue_without_login(request):
    # Set the guest mode in the session
    request.session['guest_mode'] = True  # Set session variable for guest mode

    # Redirect the user to the home page or any other page they can browse
    return redirect('home')

def guest_upload_painting(request):
    if request.session.get('guest_mode', False):
        messages.warning(request, "You need to log in to upload a painting.")
        return redirect('home')
    else:
        return redirect('login')

# Upcoming Auctions
# Define the IST timezone
IST = timezone('Asia/Kolkata')

# Upcoming Auctions
def upcoming_auction(request, painting_id=None):
    IST = timezone('Asia/Kolkata')
    current_time = now().astimezone(IST)

    if painting_id:
        # Fetch a specific painting
        painting = get_object_or_404(Painting, id=painting_id, start_time__gt=current_time)
        return render(request, 'upcoming_auction.html', {'painting': painting})

    # Fetch all upcoming paintings
    upcoming_paintings = Painting.objects.filter(start_time__gt=current_time)
    return render(request, 'upcoming_auction.html', {'upcoming_auctions': upcoming_paintings})

# Live Auctions
IST = timezone('Asia/Kolkata')

def live_auction(request):
    current_time = now().astimezone(IST)

    # Get live paintings
    live_paintings = Painting.objects.filter(
        start_time__lte=current_time, 
        end_time__gt=current_time
    )

    # Annotate painting objects with their bids sorted by amount
    for painting in live_paintings:
        painting.start_time = painting.start_time.astimezone(IST)
        painting.end_time = painting.end_time.astimezone(IST)
        # Get related bids directly in the template without assigning here
        painting.sorted_bids = Bid.objects.filter(painting=painting).order_by('-amount')

    return render(request, 'live_auction.html', {'live_auctions': live_paintings})

@login_required
def place_bid(request, painting_id):
    if not request.user.is_authenticated:
        messages.error(request, "Login required to place a bid.")
        return redirect(f"{reverse('login')}?next={reverse('live_auction')}")

    if request.method == 'POST':
        painting = get_object_or_404(Painting, id=painting_id)

        try:
            bid_amount = float(request.POST.get('bid_amount'))
        except (ValueError, TypeError):
            messages.error(request, 'Invalid bid amount.')
            return redirect('live_auction')

        if painting.user == request.user:
            messages.error(request, 'You cannot bid on your own painting.')
            return redirect('live_auction')

        latest_bid = Bid.objects.filter(painting=painting).order_by('-amount').first()

        if latest_bid and bid_amount <= latest_bid.amount:
            messages.error(request, 'Your bid must be higher than the current price.')
        else:
            # Create a new bid
            bid = Bid.objects.create(painting=painting, user=request.user, amount=bid_amount)

            # Update the painting's current price and winner
            painting.current_price = bid_amount
            painting.winner = request.user
            painting.save()

            messages.success(request, 'Your bid was placed successfully!')

        return redirect('live_auction')

    messages.error(request, 'Invalid request method.')
    return redirect('live_auction')




@login_required
def buy(request):
    return render(request, 'buy.html')

@login_required
def sell(request):
    return render(request, 'sell.html')

from django.urls import reverse
from django.utils.timezone import now
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render
from myApp.models import Painting, Bid

from django.core.mail import send_mail
from django.utils.timezone import now
from django.shortcuts import render
from myApp.models import Painting

def auction_results(request):
    completed_paintings = Painting.objects.filter(end_time__lt=now())

    sold_paintings = []
    passed_paintings = []

    for painting in completed_paintings:
        if painting.is_sold():  # Update sold status
            sold_paintings.append(painting)

            # ✅ Check if email has already been sent before sending again
            if painting.winner and not painting.payment_email_sent:  
                winner_email = painting.winner.email
                payment_link = f"http://127.0.0.1:8000/payment_simulation/{painting.id}/"
                subject = "Congratulations! You won the auction 🎉"
                message = (
                    f"Dear {painting.winner.username},\n\n"
                    f"Congratulations! You have won the auction for '{painting.title}' 🎨.\n"
                    f"The final price is ₹{painting.current_price}.\n\n"
                    f"To proceed with your purchase, please complete the payment here:\n"
                    f"{payment_link}\n\n"
                    f"Thank you for participating in the auction!\n"
                    f"- Art Vault Auctions Team"
                )

                send_mail(subject, message, 'no-reply@artvault.com', [winner_email])

                # ✅ Mark that email has been sent, so it won't send again
                painting.payment_email_sent = True  
                painting.save(update_fields=["payment_email_sent"])

        else:
            # ✅ Skip email sending for passed paintings and update status
            painting.status = "Passed"
            painting.save(update_fields=["status"])
            passed_paintings.append(painting)

    return render(request, 'auction_results.html', {
        'sold_paintings': sold_paintings,
        'passed_paintings': passed_paintings,
    })





# Detailed painting view
def painting_detail(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    bids = Bid.objects.filter(painting=painting).order_by('-amount')
    return render(request, 'painting_detail.html', {'painting': painting, 'bids': bids})




def update_painting_status(painting):
    if painting.bids.count() == 0:
        painting.status = 'Passed'
    else:
        painting.status = 'Sold'
    painting.save()


def payment_simulation(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)

    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if user is not authenticated

    # Simulating the payment process for this painting
    if request.method == 'POST':
        buyer = request.user
        seller = painting.user

        # Ensure amount_paid is a Decimal, and it is based on the painting's current price
        amount_paid = painting.current_price

        # Format the amount with ₹ symbol
        formatted_price = f"₹{amount_paid:,.2f}"

        # Calculate the admin commission (e.g., 10%) and convert to Decimal
        admin_fee = Decimal('0.10')  # 10% fee
        admin_amount = amount_paid * admin_fee  # Admin fee

        # Define taxes and charges (e.g., 18% tax and 5% handling fee)
        tax_rate = Decimal('0.18')  # 18% tax rate
        handling_fee_rate = Decimal('0.05')  # 5% handling fee

        # Calculate tax and handling fee
        tax_amount = amount_paid * tax_rate
        handling_fee = amount_paid * handling_fee_rate

        # Calculate the final amount (including tax, handling fee, and subtracting the admin fee)
        final_price = amount_paid + tax_amount + handling_fee  # This is the price the buyer will pay

        # Format the final price with ₹ symbol
        formatted_final_price = f"₹{final_price:,.2f}"

        # Subtract admin commission from the seller's payment
        seller_payment = final_price - admin_amount

        # Create the transaction record with admin commission
        transaction = Transaction.objects.create(
            painting=painting,
            seller=seller,
            buyer=buyer,
            amount_paid=final_price,  # The total amount buyer will pay (including tax and handling fee)
            admin_commission=admin_amount,  # Admin's commission
        )

        # Update transaction status to 'Completed'
        transaction.transaction_status = 'Completed'
        transaction.save()

        # Update the painting as sold
        painting.status = 'Sold'
        painting.save()

        # Render the payment success page
        return render(request, 'payment_success.html', {
            'transaction': transaction,
            'seller_payment': seller_payment,
            'admin_fee': admin_amount,
            'tax_amount': tax_amount,
            'handling_fee': handling_fee,
            'formatted_price': formatted_price,
            'formatted_final_price': formatted_final_price,  # Display final price with taxes and charges
            'painting_current_price': f"₹{painting.current_price:,.2f}",  # Add current price of the painting
        })

    # If the method is GET, calculate additional details and render the payment simulation page
    tax_rate = Decimal('0.18')  # 18% tax rate
    handling_fee_rate = Decimal('0.05')  # 5% handling fee

    tax_amount = painting.current_price * tax_rate
    handling_fee = painting.current_price * handling_fee_rate
    final_price = painting.current_price + tax_amount + handling_fee

    return render(request, 'payment_simulation.html', {
        'painting': painting,
        'tax_amount': tax_amount,
        'handling_fee': handling_fee,
        'formatted_final_price': f"₹{final_price:,.2f}",  # Pass formatted final price
    })




def calculate_commission(amount, rate=0.10):
    return amount * rate


def confirm_payment(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.transaction_status = 'Paid'
    transaction.save()
    # Update Painting and notify users



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserSettings, Painting, Bid, Profile

@login_required
def update_user_settings(request):
    if request.method == 'POST':
        selected_visibility = request.POST.get('visibility')

        user_settings, created = UserSettings.objects.get_or_create(user=request.user)
        user_settings.visibility = selected_visibility
        user_settings.save()

        return redirect('user_profile_settings')

    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    return render(request, 'profile_settings.html', {'settings': user_settings})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from myApp.models import Profile

@login_required
def update_profile_picture(request):
    if request.method == "POST":
        user = request.user

        # Ensure the user has a profile
        profile, created = Profile.objects.get_or_create(user=user)

        if "profile_image" in request.FILES:
            profile.image = request.FILES["profile_image"]
            profile.save()
            messages.success(request, "Profile picture updated successfully!")
        else:
            messages.error(request, "No image uploaded.")

    return redirect("user_profile")


@login_required
def user_profile(request):
    # Get the authenticated user
    user = request.user


    # Fetch paintings uploaded by the user
    uploaded_paintings = Painting.objects.filter(user=user)

    # Fetch paintings won by the user
    won_paintings = Painting.objects.filter(winner=user)

    # Fetch bid history for the user
    bid_history = Bid.objects.filter(user=user).select_related('painting').order_by('-timestamp')

    # Fetch user settings
    # Ensure user has a profile
    profile, created = Profile.objects.get_or_create(user=user)

# Ensure user settings exist
    user_settings, created = UserSettings.objects.get_or_create(user=user)

    # Render the profile settings page with the relevant context
    return render(request, 'profile_settings.html', {
        'user': user,
        'profile': profile,
        'uploaded_paintings': uploaded_paintings,
        'won_paintings': won_paintings,
        'bid_history': bid_history,
        'settings': user_settings,
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def profile_view(request, username):
    follow_user = get_object_or_404(User, username=username)

    # Get the IDs of users the logged-in user is following
    following_ids = set(request.user.following.values_list('id', flat=True))  

    return render(request, 'profile.html', {
        'follow_user': follow_user,
        'following_ids': following_ids  # Passing as a set for faster lookup
    })


def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def approve_painting(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    painting.approve()
    messages.success(request, f'Painting "{painting.title}" has been approved!')
    return redirect('admin:app_painting_changelist')

@login_required
@user_passes_test(is_admin)
def reject_painting(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    painting.reject()
    messages.error(request, f'Painting "{painting.title}" has been rejected!')
    return redirect('admin:app_painting_changelist')

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.templatetags.static import static  # Import static
from myApp.models import Profile

def search_users(request):
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        results = []

        if query:
            users = User.objects.filter(username__icontains=query)[:10]
            for user in users:
                # Ensure profile exists
                profile, created = Profile.objects.get_or_create(user=user)

                # Check if the user has a valid profile picture
                if profile.image and profile.image.name != "default.jpg":
                    profile_pic = profile.image.url  # Use uploaded image
                else:
                    profile_pic = static('images/default.jpg')  # Use static default image

                results.append({
                    'username': user.username,
                    'profile_pic': profile_pic
                })

        return JsonResponse({'results': results})



@login_required
def user_paintings(request, username):
    user = get_object_or_404(User, username=username)
    
    # Fetch paintings uploaded by the user
    uploaded_paintings = Painting.objects.filter(user=user)

    # Check if the logged-in user is following this user
    is_following = Follower.objects.filter(user=user, follower=request.user).exists()

    # Get follower counts
    followers_count = Follower.objects.filter(user=user).count()
    following_count = Follower.objects.filter(follower=user).count()

    return render(request, 'user_paintings.html', {
        'user': user,
        'uploaded_paintings': uploaded_paintings,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def toggle_follow(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user == user_to_follow:
            return JsonResponse({"error": "You cannot follow yourself"}, status=400)

        # Check if already following
        follow_instance, created = Follower.objects.get_or_create(user=user_to_follow, follower=request.user)

        if not created:
            # Unfollow if already following
            follow_instance.delete()
            status = "unfollowed"
        else:
            status = "followed"

        # Return updated followers count
        followers_count = Follower.objects.filter(user=user_to_follow).count()

        return JsonResponse({"status": status, "followers_count": followers_count})

    return JsonResponse({"error": "Invalid request"}, status=400)

def profile_settings(request, username):
    user = request.user
    uploaded_paintings = user.painting_set.all()
    followers_count = user.followers.count()
    following_count = user.following.count()

    context = {
        'user': user,
        'uploaded_paintings': uploaded_paintings,
        'followers_count': followers_count,
        'following_count': following_count
    }
    return render(request, 'profile_settings.html', context)

def follow_list(request, username, follow_type):
    user = get_object_or_404(User, username=username)

    if follow_type == "followers":
        follow_users = [f.follower for f in Follower.objects.filter(user=user)]
    elif follow_type == "following":
        follow_users = [f.user for f in Follower.objects.filter(follower=user)]
    else:
        return render(request, "404.html")  # Handle incorrect URL

    # Get a set of IDs of users the logged-in user follows (optimized for faster lookup)
    following_ids = set(Follower.objects.filter(follower=request.user).values_list('user_id', flat=True)) if request.user.is_authenticated else set()

    return render(request, "follow_list.html", {
        "user": user,
        "follow_users": follow_users,
        "follow_type": follow_type.capitalize(),
        "following_ids": following_ids,  # Pass this to the template
    })


def follow_list_profile(request, username, follow_type):
    user = get_object_or_404(User, username=username)

    if follow_type == "followers":
        follow_users = [f.follower for f in Follower.objects.filter(user=user)]
    elif follow_type == "following":
        follow_users = [f.user for f in Follower.objects.filter(follower=user)]
    else:
        return render(request, "404.html")  # Handle incorrect URL

    following = [f.user for f in Follower.objects.filter(follower=request.user)] if request.user.is_authenticated else []

    return render(request, "follow_list_profile.html", {
        "user": user,
        "follow_users": follow_users,
        "follow_type": follow_type.capitalize(),
        "following": following
    })


from django.views.decorators.csrf import csrf_exempt

@require_POST
@login_required
@csrf_exempt  # Temporarily disable CSRF (use a proper solution later)
def follow_user(request, username):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in"}, status=403)

        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if request.user == user_to_follow:
            return JsonResponse({"error": "You cannot follow yourself"}, status=400)

        # Check if already following
        existing_follow = Follower.objects.filter(user=user_to_follow, follower=request.user)
        
        if existing_follow.exists():
            existing_follow.delete()  # Unfollow
            following = False
        else:
            Follower.objects.create(user=user_to_follow, follower=request.user)  # Follow
            following = True

        followers_count = Follower.objects.filter(user=user_to_follow).count()

        return JsonResponse({"success": True, "following": following, "followers_count": followers_count})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def buy_paintings(request):
    """Display paintings uploaded by admin for direct purchase."""
    paintings = AdminPainting.objects.filter(available=True)
    return render(request, 'buy.html', {'paintings': paintings})

@login_required
def add_to_cart(request, painting_id):
    # Ensure painting exists before adding to the cart
    painting = get_object_or_404(AdminPainting, id=painting_id)

    # Check if the painting is already in the user's cart
    cart_item, created = CartItem.objects.get_or_create(user=request.user, painting=painting)
    
    # If item already exists, increase quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('view_cart')

@login_required
def complete_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Update order status to "Completed"
    order.status = "Completed"
    order.save()

    return render(request, "checkout_success.html", {"order": order})

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.painting.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    """Remove a specific item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart') 

@login_required
def checkout(request):
    """Handles checkout process"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return redirect('view_cart')  # If cart is empty, go back to cart

    total_amount = sum(item.painting.price * item.quantity for item in cart_items)

    if request.method == "POST":
        # Create an order for each item in the cart
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                painting=item.painting,
                amount_paid=item.painting.price * item.quantity,
                status="Pending Payment",
            )
        cart_items.delete()  # Clear the cart after order is placed
        return redirect('order_success')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})


@login_required
def buy_now(request, painting_id):
    painting = get_object_or_404(AdminPainting, id=painting_id)

    # Create an order
    order = Order.objects.create(
        user=request.user,
        painting=painting,
        amount_paid=painting.price,
        status="Pending Payment"
    )

    # Redirect to payment gateway (fake URL for now)
    return redirect('payment_page', order_id=order.id)

@login_required
def checkout(request):
    """Handle the checkout process."""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Simulate order completion
    for item in cart_items:
        item.painting.available = False  # Mark painting as sold
        item.painting.save()
    
    cart_items.delete()  # Empty cart after checkout
    return render(request, 'checkout_success.html')

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment.html', {'order': order})

@login_required
def complete_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Update order status to "Completed"
    order.status = "Completed"
    order.save()

    return redirect('order_success')

def order_success(request):
    return render(request, "checkout_success.html")


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

