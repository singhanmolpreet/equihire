import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, CandidateExtraForm, CompanyExtraForm
from .models import CustomUser

# Helper function to generate OTP
def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# --- Keep register and verify_otp views as they are ---

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Deactivate account until email confirmation
            user.save()

            # Generate and store OTP in session
            otp = generate_otp()
            request.session['registration_otp'] = otp
            request.session['registration_user_id'] = user.id
            request.session.set_expiry(300) # OTP expires in 5 minutes (300 seconds)

            # Send OTP email
            subject = 'Verify your Email Address'
            message = f'Hi {user.name},\n\nThank you for registering.\nYour OTP for email verification is: {otp}\n\nThis OTP is valid for 5 minutes.'
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                print(f"OTP email sent successfully to {user.email}") # For debugging
                # Redirect to OTP verification page
                return redirect('verify_otp')
            except Exception as e:
                print(f"Error sending OTP email: {e}") # For debugging
                # Handle email sending failure (e.g., show an error message)
                user.delete() # Simple cleanup for this example
                form.add_error(None, "Could not send verification email. Please try again later.")

    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_otp(request):
    user_id = request.session.get('registration_user_id')
    stored_otp = request.session.get('registration_otp')

    if not user_id or not stored_otp:
        # Redirect if session data is missing (e.g., session expired or accessed directly)
        return redirect('signup') # Or show an error page

    try:
        user = CustomUser.objects.get(id=user_id) # Use try-except instead of 404 for better flow control here
    except CustomUser.DoesNotExist:
         # Clear potentially invalid session data and redirect
        if 'registration_user_id' in request.session: del request.session['registration_user_id']
        if 'registration_otp' in request.session: del request.session['registration_otp']
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == stored_otp:
            # OTP matches
            user.is_active = True
            user.save()

            # Clear OTP from session
            del request.session['registration_otp']
            del request.session['registration_user_id']

            # Redirect based on role
            if user.role == 'CANDIDATE':
                return redirect('candidate_register_extra', user_id=user.id)
            else:
                return redirect('company_register_extra', user_id=user.id)
        else:
            # Invalid OTP
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP. Please try again.', 'email': user.email})

    return render(request, 'verify_otp.html', {'email': user.email})


# --- Update LoginPage ---
def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
             return render(request, 'login.html', {'error': 'Please provide both email and password.'})

        # Authenticate the user first
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                # User authenticated and active, now send OTP for 2FA
                otp = generate_otp()
                request.session['login_otp'] = otp
                request.session['login_user_id'] = user.id
                request.session.set_expiry(300) # OTP expires in 5 minutes

                # Send OTP email for login
                subject = 'Your Login OTP'
                message = f'Hi {user.name},\n\nYour OTP for logging in is: {otp}\n\nThis OTP is valid for 5 minutes.'
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    print(f"Login OTP email sent successfully to {user.email}") # For debugging
                    # Redirect to login OTP verification page
                    return redirect('verify_login_otp')
                except Exception as e:
                    print(f"Error sending login OTP email: {e}") # For debugging
                    # Handle email sending failure
                    return render(request, 'login.html', {'error': 'Could not send login OTP. Please try again later.'})

            else:
                # Handle inactive user trying to log in
                return render(request, 'login.html', {'error': 'Account not activated. Please verify your email first.'})
        else:
            # Invalid credentials
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    # GET request or initial load
    return render(request, 'login.html')

# --- Add verify_login_otp view ---
def verify_login_otp(request):
    user_id = request.session.get('login_user_id')
    stored_otp = request.session.get('login_otp')

    if not user_id or not stored_otp:
        # Redirect if session data is missing (e.g., session expired or accessed directly)
        return redirect('login') # Redirect back to login page

    try:
        # Ensure user exists and is active (should be, based on LoginPage logic, but good to check)
        user = CustomUser.objects.get(id=user_id, is_active=True)
    except CustomUser.DoesNotExist:
         # Clear potentially invalid session data and redirect
        if 'login_user_id' in request.session: del request.session['login_user_id']
        if 'login_otp' in request.session: del request.session['login_otp']
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == stored_otp:
            # OTP matches - Complete the login
            # Clear OTP from session *before* logging in
            del request.session['login_otp']
            del request.session['login_user_id']

            # Log the user in
            login(request, user) # No backend needed here as user is already authenticated

            # Redirect to home/dashboard
            return redirect('home') # Or role-specific dashboard
        else:
            # Invalid OTP
            return render(request, 'verify_login_otp.html', {'error': 'Invalid OTP. Please try again.', 'email': user.email})

    # GET request
    return render(request, 'verify_login_otp.html', {'email': user.email})


# --- Keep candidate_register_extra and company_register_extra views as they are ---

def candidate_register_extra(request, user_id):
    # Ensure only active users can complete this step
    user = get_object_or_404(CustomUser, id=user_id, is_active=True)
    if request.method == 'POST':
        form = CandidateExtraForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Log the user in after completing profile (if not logged in during OTP verification)
            # Consider if login is needed here now, as they might log in via OTP later
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home') # Redirect to dashboard or home after profile completion
        else:
            pass # Let the default render handle form errors
    else:
        form = CandidateExtraForm()
    return render(request, 'candidate_extra.html', {'form': form})


def company_register_extra(request, user_id):
    # Ensure only active users can complete this step
    user = get_object_or_404(CustomUser, id=user_id, is_active=True)
    if request.method == 'POST':
        form = CompanyExtraForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Log the user in after completing profile (if not logged in during OTP verification)
            # Consider if login is needed here now, as they might log in via OTP later
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home') # Redirect to dashboard or home after profile completion
    else:
        form = CompanyExtraForm()
    return render(request, 'company_extra.html', {'form': form})

def LogoutPage(request):
    logout(request)
    return redirect('home')

